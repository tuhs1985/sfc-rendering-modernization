// Opt-in retained scene depth for the EXISTING additive display only.
// No original-draw suppression and no claims about tactical grid draw policy.
#pragma once
#include "ship_live_request.h"
#include "ship_triplet_consumer.h"
namespace ship_scene_depth {
using Microsoft::WRL::ComPtr;
constexpr unsigned Offset=2048,Magic=0x31504453;
struct Data {
 uint32_t magic=Magic,version=1,bytes=sizeof(Data),reserved=0;
 volatile LONG draws=0,found=0,missing=0,wrongThread=0,ambiguous=0,unsupported=0;
 volatile LONG frames=0,qualified=0,stateMismatch=0,displayed=0,epoch=0,failed=0;
 uint32_t width=0,height=0,samples=0,engineFrame=0;
 uint32_t reservedTail[12]{};
};
static_assert(sizeof(Data)==128&&Offset+sizeof(Data)<4096);
inline Data& data(return_path::Mapping& m){return *reinterpret_cast<Data*>(reinterpret_cast<BYTE*>(m.state)+Offset);}
inline bool supported(const D3D11_TEXTURE2D_DESC& d){return d.Width&&d.Height&&d.Width<=1920&&d.Height<=1080&&
 d.MipLevels==1&&d.ArraySize==1&&d.Format==DXGI_FORMAT_R32_TYPELESS&&d.SampleDesc.Count==8&&d.SampleDesc.Quality==0&&
 (d.BindFlags&D3D11_BIND_DEPTH_STENCIL)&&(d.BindFlags&D3D11_BIND_SHADER_RESOURCE);}
class Source {
 ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context;
 ComPtr<ID3D11Texture2D> texture,viewTexture;ComPtr<ID3D11ShaderResourceView> view;
 Data& stats;DWORD thread=GetCurrentThreadId(),frame=0;bool seen=false,mixed=false,bad=false;
public:
 Source(ID3D11Device* d,Data& s):device(d),stats(s){s=Data{};d->GetImmediateContext(&context);}
 void cleared(uint64_t nativeContext){
  if(nativeContext==reinterpret_cast<uintptr_t>(context.Get())&&GetCurrentThreadId()==thread&&seen)bad=true;
 }
 void observe(uint64_t nativeContext,sfc_calibration::Mailbox* mailbox){
  if(nativeContext!=reinterpret_cast<uintptr_t>(context.Get()))return;
  if(GetCurrentThreadId()!=thread){InterlockedIncrement(&stats.wrongThread);return;}
  InterlockedIncrement(&stats.draws);
  ComPtr<ID3D11DepthStencilView> depth;context->OMGetRenderTargets(0,nullptr,&depth);
  if(!depth){InterlockedIncrement(&stats.missing);return;}
  ComPtr<ID3D11Resource> r;depth->GetResource(&r);ComPtr<ID3D11Texture2D> t;
  D3D11_TEXTURE2D_DESC d{};D3D11_DEPTH_STENCIL_VIEW_DESC v{};depth->GetDesc(&v);
  if(FAILED(r.As(&t))){InterlockedIncrement(&stats.unsupported);bad=true;return;}
  t->GetDesc(&d);
  if(!supported(d)||v.Format!=DXGI_FORMAT_D32_FLOAT||v.ViewDimension!=D3D11_DSV_DIMENSION_TEXTURE2DMS||v.Flags){InterlockedIncrement(&stats.unsupported);bad=true;return;}
  const DWORD f=sfc_calibration::frame(mailbox);
  if(!f||f==0xffffffffu||(seen&&frame!=f)||(seen&&texture.Get()!=t.Get()))mixed=true;
  frame=f;seen=true;texture=t;InterlockedIncrement(&stats.found);
 }
 ID3D11ShaderResourceView* finish(uint32_t currentFrame,uint32_t width,uint32_t height){
  InterlockedIncrement(&stats.frames);
  const bool accepted=seen&&!mixed&&!bad&&frame==currentFrame;
  seen=mixed=bad=false;frame=0;
  if(!accepted){InterlockedIncrement(&stats.ambiguous);return nullptr;}
  D3D11_TEXTURE2D_DESC d{};texture->GetDesc(&d);
  if(d.Width!=width||d.Height!=height){InterlockedIncrement(&stats.unsupported);return nullptr;}
  // Outside the original draw callback;one SRV per observed resource epoch.
  // Never infer that an old pointer label revives a released source.
  if(viewTexture.Get()!=texture.Get()){
   view.Reset();viewTexture.Reset();D3D11_SHADER_RESOURCE_VIEW_DESC s{};
   s.Format=DXGI_FORMAT_R32_FLOAT;s.ViewDimension=D3D11_SRV_DIMENSION_TEXTURE2DMS;
   if(FAILED(device->CreateShaderResourceView(texture.Get(),&s,&view))){InterlockedIncrement(&stats.failed);return nullptr;}
   viewTexture=texture;InterlockedIncrement(&stats.epoch);
  }
  stats.width=d.Width;stats.height=d.Height;stats.samples=8;stats.engineFrame=currentFrame;
  InterlockedIncrement(&stats.qualified);return view.Get();
 }
 void discardFrame(){seen=mixed=bad=false;frame=0;}
};
}
