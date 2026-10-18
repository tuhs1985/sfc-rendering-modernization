// Reusable native receiver. No game hooks, waits, readbacks, file I/O or shaders.
#pragma once
#include "ship_triplet_wire.h"
#include <d3d11.h>
#include <dxgi.h>
#include <wrl/client.h>
namespace ship_triplet {
using Microsoft::WRL::ComPtr;
inline void checked(HRESULT h,const char* s){if(FAILED(h))throw std::runtime_error(s);}
class Consumer {
 Wire& wire;ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context;
 ComPtr<ID3D11Query> complete;LONG pending=0;
 bool queued=false;
 Resources resources{};
public:
 std::array<ComPtr<ID3D11Texture2D>,3> textures;
 std::array<ComPtr<ID3D11ShaderResourceView>,3> views;
 explicit Consumer(Wire& w,ID3D11Device* d):wire(w),device(d){
  if(!valid(w)||!load(w.ready)||d->GetFeatureLevel()<D3D_FEATURE_LEVEL_10_1)throw std::runtime_error("triplet descriptor/device");
  resources=describe(w);
  ComPtr<IDXGIDevice> dx;ComPtr<IDXGIAdapter> adapter;DXGI_ADAPTER_DESC desc{};
  checked(d->QueryInterface(IID_PPV_ARGS(&dx)),"triplet DXGI device");checked(dx->GetAdapter(&adapter),"triplet adapter");checked(adapter->GetDesc(&desc),"triplet LUID");
  if(desc.AdapterLuid.LowPart!=w.adapterLow||static_cast<uint32_t>(desc.AdapterLuid.HighPart)!=w.adapterHigh)throw std::runtime_error("triplet adapter mismatch");
  d->GetImmediateContext(&context);
  for(unsigned i=0;i<3;++i){
   checked(d->OpenSharedResource(reinterpret_cast<HANDLE>(static_cast<uintptr_t>(w.handles[i])),IID_PPV_ARGS(&textures[i])),"triplet open shared");
   D3D11_TEXTURE2D_DESC t{};textures[i]->GetDesc(&t);
   if(t.Width!=w.width||t.Height!=w.height||static_cast<uint32_t>(t.Format)!=w.formats[i]||t.MipLevels!=1||t.ArraySize!=1||t.SampleDesc.Count!=1||t.Usage!=D3D11_USAGE_DEFAULT||
      !(t.BindFlags&D3D11_BIND_SHADER_RESOURCE)||!(t.MiscFlags&D3D11_RESOURCE_MISC_SHARED))throw std::runtime_error("triplet texture mismatch");
   checked(d->CreateShaderResourceView(textures[i].Get(),nullptr,&views[i]),"triplet SRV");
  }
  D3D11_QUERY_DESC q{D3D11_QUERY_EVENT,0};checked(d->CreateQuery(&q,&complete),"triplet receiver fence");
 }
 bool acquire(const Key& current){if(pending)return false;
  if(!claim(wire,current,return_path::now(),&resources))return false;pending=load(wire.sequence);queued=false;return true;}
 bool acquireBuffered(const Key& current){if(pending)return false;
  if(!claimBuffered(wire,current,return_path::now(),&resources))return false;pending=load(wire.sequence);queued=false;return true;}
 // Call after caller has queued its shader use/copies on this immediate context.
 void submitted(){if(!pending||queued)throw std::runtime_error("triplet absent/already submitted lease");context->End(complete.Get());queued=true;}
 bool poll(){if(!pending||!queued)return false;BOOL done=FALSE;
  const HRESULT h=context->GetData(complete.Get(),&done,sizeof(done),D3D11_ASYNC_GETDATA_DONOTFLUSH);
  if(FAILED(h)){store(wire.error,1);return false;}if(h!=S_OK||!done)return false;
  if(!finish(wire,pending,true)){
   // A busy metadata guard does not invalidate completed consumer GPU work.
   if(load(wire.lease)==Reading&&load(wire.sequence)==pending&&load(wire.ack)<pending)return false;
   store(wire.error,2);return false;
  }pending=0;queued=false;return true;
 }
};
}
