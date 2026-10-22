// Exact-current-frame additive display. Shared GPU leases,NO stale-image hold.
// Imports happen on an owned worker;immediate context is render-thread-only.
#pragma once
#include "../d3d9_proof/game_output_wire.h"
#include "../d3d9_proof/live_owner_wire.h"
#include "../d3d9_proof/camera_left.h"
#include "ship_triplet_compositor.h"
#include "ship_scene_depth.h"
#include <thread>
#include <atomic>
namespace d3d9_game {
class Receiver {
 struct Source:sfc_calibration::Reader{~Source(){close();}};
 return_path::Mapping& mapping;Source source;game_output::Pool* pool=nullptr;
 Microsoft::WRL::ComPtr<ID3D11Device> device;Microsoft::WRL::ComPtr<ID3D11DeviceContext> context;
 ship_triplet::Compositor compositor;ship_scene_depth::Source depth;
 struct Import {Microsoft::WRL::ComPtr<ID3D11Texture2D> textures[3];Microsoft::WRL::ComPtr<ID3D11ShaderResourceView> views[3];Microsoft::WRL::ComPtr<ID3D11Query> query;output_wire::Packet identity{};std::atomic<bool> ready{false};bool pending=false;};
 Import imported[2];std::atomic<bool> stopping{false};std::thread worker;HANDLE receiver=nullptr;
 DWORD thread=GetCurrentThreadId();sfc_calibration::Snapshot snapshot{};
 void imports(){
  try{while(!stopping.load()){
   if(InterlockedCompareExchange(&pool->header.ready,0,0)&&game_output::valid(pool->header,source.session,GetCurrentProcessId())){
    if(!receiver){receiver=OpenProcess(SYNCHRONIZE,FALSE,pool->header.receiver_pid);if(!receiver)throw std::runtime_error("D3D9 receiver lifetime");}
    if(InterlockedCompareExchange(&pool->header.stopped,0,0)||WaitForSingleObject(receiver,0)!=WAIT_TIMEOUT)break;
    for(unsigned slot=0;slot<2;++slot){auto& item=imported[slot];if(item.ready.load(std::memory_order_acquire))continue;auto& wire=pool->slots[slot];
     if(InterlockedCompareExchange(&wire.state,output_wire::acquired,output_wire::ready)!=output_wire::ready)continue;
     try{const auto p=wire.packet;
      if(!output_wire::valid(p,p.session,pool->header.receiver_pid)||p.width!=1920||p.height!=1080||p.resource_epoch!=slot+1)throw std::runtime_error("D3D9 imported descriptor");
      Microsoft::WRL::ComPtr<IDXGIDevice> dx;Microsoft::WRL::ComPtr<IDXGIAdapter> adapter;DXGI_ADAPTER_DESC desc{};
      ship_triplet::checked(device.As(&dx),"game GPU interface");ship_triplet::checked(dx->GetAdapter(&adapter),"game GPU");ship_triplet::checked(adapter->GetDesc(&desc),"game GPU identity");
      if(desc.AdapterLuid.LowPart!=p.luid_low||desc.AdapterLuid.HighPart!=p.luid_high)throw std::runtime_error("D3D9/game GPU mismatch");
      for(unsigned i=0;i<3;++i){ship_triplet::checked(device->OpenSharedResource(reinterpret_cast<HANDLE>(static_cast<uintptr_t>(p.handles[i])),IID_PPV_ARGS(&item.textures[i])),"game shared image");
       D3D11_TEXTURE2D_DESC d{};item.textures[i]->GetDesc(&d);
       if(d.Width!=p.width||d.Height!=p.height||d.Format!=(i?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM)||d.MipLevels!=1||d.ArraySize!=1||d.SampleDesc.Count!=1)throw std::runtime_error("game shared image shape");
       ship_triplet::checked(device->CreateShaderResourceView(item.textures[i].Get(),nullptr,&item.views[i]),"game image view");
      }
      D3D11_QUERY_DESC q{D3D11_QUERY_EVENT,0};ship_triplet::checked(device->CreateQuery(&q,&item.query),"game GPU lease fence");item.identity=p;
      InterlockedExchange(&wire.state,output_wire::idle);item.ready.store(true,std::memory_order_release);
     }catch(...){InterlockedExchange(&wire.state,output_wire::idle);throw;}
    }
   }Sleep(1);
  }}catch(...){InterlockedIncrement(&pool->stats.resource_failed);InterlockedExchange(&pool->header.error,1);}
 }
public:
 Receiver(return_path::Mapping& m,ID3D11Device* d):mapping(m),device(d),compositor(d,true,true),depth(d,ship_scene_depth::data(m)){
  if(d->GetCreationFlags()&D3D11_CREATE_DEVICE_SINGLETHREADED)throw std::runtime_error("Game device disallows worker imports");
  if(!source.prepare()||!source.requested)throw std::runtime_error("Explicit semantic source required for D3D9 insertion");
  pool=reinterpret_cast<game_output::Pool*>(reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset+game_output::Offset);d->GetImmediateContext(&context);
  worker=std::thread([this]{imports();});
 }
 ~Receiver(){stop();source.close();if(receiver)CloseHandle(receiver);}
 void stop(){stopping.store(true);if(worker.joinable())worker.join();if(pool)InterlockedExchange(&pool->header.stopped,1);}
 void observe(uint64_t native){if(!stopping.load())depth.observe(native,source.mailbox);}
 void cleared(uint64_t native){if(!stopping.load())depth.cleared(native);}
 void retire(){
  if(GetCurrentThreadId()!=thread)return;
  for(unsigned i=0;i<2;++i){auto& item=imported[i];if(!item.ready.load(std::memory_order_acquire)||!item.pending)continue;
   BOOL done=FALSE;const auto status=context->GetData(item.query.Get(),&done,sizeof(done),D3D11_ASYNC_GETDATA_DONOTFLUSH);
   if(FAILED(status)){InterlockedIncrement(&pool->stats.invalid);InterlockedExchange(&pool->header.error,1);continue;}
   if(status==S_OK&&done){item.pending=false;InterlockedExchange(&pool->slots[i].state,output_wire::idle);}else InterlockedIncrement(&pool->stats.gpu_busy);
  }
 }
 void step(ID3D11RenderTargetView* target){
  retire();if(stopping.load()||GetCurrentThreadId()!=thread||!target||!return_path::read(mapping.state->armed)||!return_path::read(mapping.state->enabled)||return_path::read(mapping.state->stop))return;
  if(!InterlockedCompareExchange(&pool->header.ready,0,0)){InterlockedIncrement(&pool->stats.not_ready);depth.discardFrame();return;}
  if(!game_output::valid(pool->header,source.session,GetCurrentProcessId())||pool->header.stopped||pool->header.error){depth.discardFrame();return;}
  if(!sfc_calibration::read(source.mailbox,snapshot)){InterlockedIncrement(&pool->stats.not_ready);depth.discardFrame();return;}
  auto* base=reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset;
  auto* live=reinterpret_cast<live_owner::Store*>(base+live_owner::Offset);const auto chosen=static_cast<uint64_t>(InterlockedCompareExchange64(&live->header.selected,0,0));
  if(!live_owner::header_valid(live->header,source.session)||live->header.pid!=GetCurrentProcessId()||frame_ingress::state(&live->header.stopped)){InterlockedIncrement(&pool->stats.retired);depth.discardFrame();return;}
  const live_owner::Row* row=nullptr;for(const auto& r:snapshot.owner)if(r[1]==DWORD(chosen)&&r[7]==DWORD(chosen>>32)&&r[2]==snapshot.frame&&r[4]==1&&r[47]==thread&&r[48]==1&&!r[42]&&!r[43]&&!r[44]){row=&r;break;}
  auto* nativeDepth=depth.finish(snapshot.frame,1920,1080);
  for(unsigned slot=0;slot<2;++slot){auto& item=imported[slot];if(!item.ready.load(std::memory_order_acquire)||item.pending)continue;auto& wire=pool->slots[slot];
   if(InterlockedCompareExchange(&wire.state,output_wire::acquired,output_wire::ready)!=output_wire::ready)continue;
   const auto p=wire.packet;const auto meta=game_output::metadata(wire);
   const auto& expected=item.identity;
   const bool resource=output_wire::valid(p,expected.session,pool->header.receiver_pid)&&p.scene_hash==expected.scene_hash&&p.resource_epoch==expected.resource_epoch&&p.width==expected.width&&p.height==expected.height&&memcmp(p.handles,expected.handles,sizeof(p.handles))==0;
   if(!resource||!row||!game_output::matches(p,meta,row->data(),source.session,live_owner::row_hash(*row),live_owner::sequence(*row))){InterlockedIncrement(resource?&pool->stats.stale:&pool->stats.invalid);InterlockedExchange(&wire.state,output_wire::idle);continue;}
   if(!nativeDepth){InterlockedIncrement(&pool->stats.depth_missing);InterlockedExchange(&wire.state,output_wire::idle);continue;}
   ship_triplet::Key key{};memcpy(key.session,source.session,16);memcpy(key.sourceSession,source.session,16);memcpy(key.asset,pool->asset,32);
   key.owner=p.owner;key.objectId=p.owner;key.revision=p.revision;key.frame=DWORD(p.source_frame);key.pose=key.camera=p.source_state_hash;
   key.width=p.width;key.height=p.height;key.resourceEpoch=DWORD(p.resource_epoch);key.depthConvention=1;key.sourcePid=GetCurrentProcessId();key.diagnosticMode=pool->diagnostic_mode;
   float view[16]{};memcpy(view,row->data()+49,64);
   if(pool->camera_offset[1]!=0||pool->camera_offset[2]!=0||!diagnostic_offset::camera_left(view,-pool->camera_offset[0],key.worldOffset)){InterlockedIncrement(&pool->stats.invalid);InterlockedExchange(&wire.state,output_wire::idle);continue;}
   float viewport[4]{};memcpy(viewport,row->data()+83,16);bool valid=true;for(unsigned i=0;i<4;++i){valid&=std::isfinite(viewport[i])&&viewport[i]>=0&&viewport[i]<=1920&&fabs(viewport[i]-round(viewport[i]))<.001f;key.viewport[i]=valid?static_cast<DWORD>(viewport[i]):0;}
   ID3D11ShaderResourceView* views[]={item.views[0].Get(),item.views[1].Get(),item.views[2].Get()};const D3D11_VIEWPORT full{0,0,1920,1080,0,1};
   if(!valid||!compositor.draw(target,views,key,full,nativeDepth)){InterlockedIncrement(&pool->stats.invalid);InterlockedExchange(&wire.state,output_wire::idle);continue;}
   context->End(item.query.Get());item.pending=true;pool->stats.frame=key.frame;InterlockedIncrement(&pool->stats.drawn);InterlockedIncrement(&mapping.state->drawCount);
   return;
  }
 }
};
}
