// Exact-current-frame additive display. Shared GPU leases,NO stale-image hold.
// Imports happen on an owned worker;immediate context is render-thread-only.
#pragma once
#include "../d3d9_proof/game_output_wire.h"
#include "../d3d9_proof/live_owner_wire.h"
#include "../d3d9_proof/camera_left.h"
#include "ship_triplet_compositor.h"
#include "ship_scene_depth.h"
#include "scene_frame_buffer.h"
#include "game_gpu_read_lease.h"
#include "../d3d9_proof/multi_scene_wire.h"
#include <thread>
#include <atomic>
namespace d3d9_game {
class Receiver {
 static bool wantsBuffer(){wchar_t value[2]{};return GetEnvironmentVariableW(L"SFC_D3D9_SYNC_BUFFER",value,2)==1&&value[0]==L'1';}
 struct Source:sfc_calibration::Reader{~Source(){close();}};
 return_path::Mapping& mapping;Source source;game_output::Pool* pool=nullptr;
 Microsoft::WRL::ComPtr<ID3D11Device> device;Microsoft::WRL::ComPtr<ID3D11DeviceContext> context;
 ship_triplet::Compositor compositor;ship_scene_depth::Source depth;
 struct Import {Microsoft::WRL::ComPtr<ID3D11Texture2D> textures[3];Microsoft::WRL::ComPtr<ID3D11ShaderResourceView> views[3];Microsoft::WRL::ComPtr<ID3D11Query> query;game_gpu::ReadLease lease;output_wire::Packet identity{};std::atomic<bool> ready{false};bool pending=false;};
 Import imported[2];std::atomic<bool> stopping{false};std::thread worker;HANDLE receiver=nullptr;
 DWORD thread=GetCurrentThreadId();sfc_calibration::Snapshot snapshot{};
 bool buffered=false;std::unique_ptr<scene_frame_buffer::History> history;synchronized_frame::Store* bufferAudit=nullptr;
 Microsoft::WRL::ComPtr<ID3D11DeviceContext4> fencedContext;
 multi_scene::Store* cohort=nullptr;multi_scene::Frame cohortFrame{};
 void resetHistory(){if(history)history->reset();}
 void audit(synchronized_frame::Audit a){if(bufferAudit)synchronized_frame::append(*bufferAudit,a);}
 void imports(){
  try{while(!stopping.load()){
   if(InterlockedCompareExchange(&pool->header.ready,0,0)&&game_output::valid(pool->header,source.session,GetCurrentProcessId())){
    if(!receiver){receiver=OpenProcess(SYNCHRONIZE,FALSE,pool->header.receiver_pid);if(!receiver)throw std::runtime_error("D3D9 receiver lifetime");}
    if(InterlockedCompareExchange(&pool->header.stopped,0,0))break;
    if(WaitForSingleObject(receiver,0)!=WAIT_TIMEOUT){InterlockedExchange(&pool->header.ready,0);InterlockedExchange(&pool->header.stopped,1);break;}
    for(unsigned slot=0;slot<2;++slot){auto& item=imported[slot];auto& wire=pool->slots[slot];
     if(item.ready.load(std::memory_order_acquire)){
      if(buffered&&item.lease.retire()){InterlockedIncrement(reinterpret_cast<volatile LONG*>(&pool->reserved[0]));InterlockedExchange(&wire.state,output_wire::idle);}
      continue;
     }
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
      if(buffered)item.lease.prepare(device.Get());
      else{D3D11_QUERY_DESC q{D3D11_QUERY_EVENT,0};ship_triplet::checked(device->CreateQuery(&q,&item.query),"game GPU lease fence");}item.identity=p;
      InterlockedExchange(&wire.state,output_wire::idle);item.ready.store(true,std::memory_order_release);
     }catch(...){InterlockedExchange(&wire.state,output_wire::idle);throw;}
    }
   }Sleep(1);
  }}catch(...){InterlockedIncrement(&pool->stats.resource_failed);InterlockedExchange(&pool->header.error,1);}
 }
public:
 Receiver(return_path::Mapping& m,ID3D11Device* d,ID3D11Texture2D* back=nullptr):mapping(m),device(d),compositor(d,true,true,wantsBuffer()),depth(d,ship_scene_depth::data(m)){
  if(d->GetCreationFlags()&D3D11_CREATE_DEVICE_SINGLETHREADED)throw std::runtime_error("Game device disallows worker imports");
  if(!source.prepare()||!source.requested)throw std::runtime_error("Explicit semantic source required for D3D9 insertion");
  pool=reinterpret_cast<game_output::Pool*>(reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset+game_output::Offset);d->GetImmediateContext(&context);
  buffered=wantsBuffer();if(buffered){
   ship_triplet::checked(context.As(&fencedContext),"Buffered game context fence support");
   if(!back)throw std::runtime_error("Buffered scene requires explicit game target");
   auto* base=reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset;bufferAudit=reinterpret_cast<synchronized_frame::Store*>(base+synchronized_frame::Offset);
   auto& h=bufferAudit->header;
   if(!h.magic){memset(bufferAudit,0,sizeof(*bufferAudit));h.magic=synchronized_frame::Magic;h.version=1;h.bytes=sizeof(*bufferAudit);h.pid=GetCurrentProcessId();memcpy(h.session,source.session,16);}
   else if(h.magic!=synchronized_frame::Magic||h.version!=1||h.bytes!=sizeof(*bufferAudit)||h.pid!=GetCurrentProcessId()||memcmp(h.session,source.session,16))throw std::runtime_error("Buffered scene audit identity");
   D3D11_TEXTURE2D_DESC shape{};back->GetDesc(&shape);
   if(shape.Width==1920&&shape.Height==1080)history=std::make_unique<scene_frame_buffer::History>(d,back);
   // Unsupported resize remains original drawing only,until a fresh runtime.
  }
  wchar_t multi[2]{};if(GetEnvironmentVariableW(L"SFC_D3D9_MULTISCENE",multi,2)==1&&multi[0]==L'1'){
   if(!buffered)throw std::runtime_error("Multi-scene requires paired buffer");
   cohort=reinterpret_cast<multi_scene::Store*>(reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset+multi_scene::Offset);
   const auto& h=cohort->header;
   // Presentation initializes BEFORE the native semantic component attaches.
   // Only the native producer claims pid;step requires its confirmed identity.
   if(h.magic!=multi_scene::Magic||h.version!=1||h.bytes!=sizeof(*cohort)||memcmp(h.session,source.session,16)||
      (h.pid&&h.pid!=GetCurrentProcessId()))throw std::runtime_error("Multi-scene game mapping identity");
  }
  worker=std::thread([this]{imports();});
 }
 ~Receiver(){stop();source.close();if(receiver)CloseHandle(receiver);}
 void stop(){stopping.store(true);if(worker.joinable())worker.join();if(pool)InterlockedExchange(&pool->header.stopped,1);}
 void observe(uint64_t native){if(!stopping.load())depth.observe(native,source.mailbox);}
 void cleared(uint64_t native){if(!stopping.load())depth.cleared(native);}
 void retire(){
  if(buffered||GetCurrentThreadId()!=thread)return;
  for(unsigned i=0;i<2;++i){auto& item=imported[i];if(!item.ready.load(std::memory_order_acquire)||!item.pending)continue;
   BOOL done=FALSE;const auto status=context->GetData(item.query.Get(),&done,sizeof(done),D3D11_ASYNC_GETDATA_DONOTFLUSH);
   if(FAILED(status)){InterlockedIncrement(&pool->stats.invalid);InterlockedExchange(&pool->header.error,1);continue;}
   if(status==S_OK&&done){item.pending=false;InterlockedExchange(&pool->slots[i].state,output_wire::idle);}else InterlockedIncrement(&pool->stats.gpu_busy);
  }
 }
 void step(ID3D11RenderTargetView* target){
  retire();if(stopping.load()||GetCurrentThreadId()!=thread||!target||!return_path::read(mapping.state->armed)||!return_path::read(mapping.state->enabled)||return_path::read(mapping.state->stop)){resetHistory();return;}
  if(!InterlockedCompareExchange(&pool->header.ready,0,0)){InterlockedIncrement(&pool->stats.not_ready);depth.discardFrame();resetHistory();return;}
  if(!game_output::valid(pool->header,source.session,GetCurrentProcessId())||pool->header.stopped||pool->header.error){depth.discardFrame();resetHistory();return;}
  if(!sfc_calibration::read(source.mailbox,snapshot)){InterlockedIncrement(&pool->stats.not_ready);depth.discardFrame();resetHistory();return;}
  auto* base=reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset;
  auto* live=reinterpret_cast<live_owner::Store*>(base+live_owner::Offset);const auto chosen=static_cast<uint64_t>(InterlockedCompareExchange64(&live->header.selected,0,0));
  if(!live_owner::header_valid(live->header,source.session)||live->header.pid!=GetCurrentProcessId()||frame_ingress::state(&live->header.stopped)||static_cast<DWORD>(frame_ingress::state(&live->header.bad_frame))==snapshot.frame){InterlockedIncrement(&pool->stats.retired);depth.discardFrame();resetHistory();return;}
  const live_owner::Row* row=nullptr;for(const auto& r:snapshot.owner)if(r[1]==DWORD(chosen)&&r[7]==DWORD(chosen>>32)&&r[2]==snapshot.frame&&r[4]==1&&r[47]==thread&&r[48]==1&&!r[42]&&!r[43]&&!r[44]){row=&r;break;}
  const auto* currentRow=row;
    uint64_t currentHash=row?live_owner::row_hash(*row):0;
    if(cohort&&row){if(!multi_scene::valid(cohort->header,source.session,GetCurrentProcessId())||!multi_scene::read(*cohort,(*row)[2],live_owner::sequence(*row),cohortFrame)){row=nullptr;currentRow=nullptr;currentHash=0;}else currentHash=cohortFrame.checksum;}
    uint64_t expectedHash=currentHash;
  auto* nativeDepth=depth.finish(snapshot.frame,1920,1080);
  synchronized_frame::Audit delayed{};
  if(buffered){
   try{
   LARGE_INTEGER q{};QueryPerformanceCounter(&q);delayed.current=snapshot.frame;delayed.qpc=static_cast<uint64_t>(q.QuadPart);
   // The saved N-1 scene is being consumed now. Never start new work for that
   // scene after its actual callback;N remains eligible until the next callback.
   if(cohort&&snapshot.frame)InterlockedExchange(&cohort->header.closed_frame,static_cast<LONG>(snapshot.frame-1));
   if(!history||!row||!nativeDepth){resetHistory();delayed.status=4;audit(delayed);return;}
   auto* previous=history->prior();const auto current=*row;
   const bool valid=previous&&synchronized_frame::adjacent(previous->row,current,previous->captured,delayed.qpc,mapping.state->qpcFrequency);
   if(!valid){if(previous)++pool->stats.reserved[3];resetHistory();previous=nullptr;}
   Microsoft::WRL::ComPtr<ID3D11Resource> resource;target->GetResource(&resource);Microsoft::WRL::ComPtr<ID3D11Texture2D> back;
   ship_triplet::checked(resource.As(&back),"Buffered game target texture");
   history->capture(back.Get(),nativeDepth,current,delayed.qpc,currentHash);
   if(!previous){++pool->stats.reserved[2];delayed.status=3;audit(delayed);return;}
   // Capture CURRENT untouched frame before replacing it with the complete
   // PREVIOUS scene. HUD/background/depth/camera/ship identity now move together.
   history->restore(back.Get(),*previous);row=&previous->row;nativeDepth=previous->depthView.Get();
   expectedHash=previous->stateHash;
   delayed.scene=(*row)[2];delayed.owner=(*row)[1];delayed.revision=(*row)[7];delayed.input_sequence=live_owner::sequence(*row);delayed.expected_hash=expectedHash;
   delayed.age_us=static_cast<DWORD>((delayed.qpc-previous->captured)*1000000/mapping.state->qpcFrequency);delayed.status=2;
   ++pool->stats.reserved[0];pool->stats.reserved[5]=(std::max)(pool->stats.reserved[5],static_cast<uint32_t>(delayed.age_us));pool->stats.reserved[6]=delayed.scene;
   }catch(...){
    // A failed history resource/command must never escape into the game's
    // Present callback. Park this instance;leave subsequent native frames alone.
    if(bufferAudit)++bufferAudit->header.failed;InterlockedIncrement(&pool->stats.resource_failed);history.reset();depth.discardFrame();return;
   }
  }
  for(unsigned slot=0;slot<2;++slot){auto& item=imported[slot];if(!item.ready.load(std::memory_order_acquire)||item.pending||item.lease.pending())continue;auto& wire=pool->slots[slot];
   if(InterlockedCompareExchange(&wire.state,output_wire::acquired,output_wire::ready)!=output_wire::ready)continue;
   const auto p=wire.packet;const auto meta=game_output::metadata(wire);
   const auto& expected=item.identity;
   const bool resource=output_wire::valid(p,expected.session,pool->header.receiver_pid)&&p.scene_hash==expected.scene_hash&&p.resource_epoch==expected.resource_epoch&&p.width==expected.width&&p.height==expected.height&&memcmp(p.handles,expected.handles,sizeof(p.handles))==0;
   // The next matching frame may already be ready. Keep its lease for the next
   // presentation instead of discarding it merely because we display N-1 now.
   if(buffered&&resource&&currentRow&&game_output::matches(p,meta,currentRow->data(),source.session,currentHash,live_owner::sequence(*currentRow))){InterlockedExchange(&wire.state,output_wire::ready);continue;}
   if(!resource||!row||!game_output::matches(p,meta,row->data(),source.session,expectedHash,live_owner::sequence(*row))){InterlockedIncrement(resource?&pool->stats.stale:&pool->stats.invalid);InterlockedExchange(&wire.state,output_wire::idle);continue;}
   if(!nativeDepth){InterlockedIncrement(&pool->stats.depth_missing);InterlockedExchange(&wire.state,output_wire::idle);continue;}
   ship_triplet::Key key{};memcpy(key.session,source.session,16);memcpy(key.sourceSession,source.session,16);memcpy(key.asset,pool->asset,32);
   key.owner=p.owner;key.objectId=p.owner;key.revision=p.revision;key.frame=DWORD(p.source_frame);key.pose=key.camera=p.source_state_hash;
   key.width=p.width;key.height=p.height;key.resourceEpoch=DWORD(p.resource_epoch);key.depthConvention=1;key.sourcePid=GetCurrentProcessId();key.diagnosticMode=pool->diagnostic_mode;
   float view[16]{};memcpy(view,row->data()+49,64);
   const bool aligned=cohort&&pool->reserved[2]==1&&pool->diagnostic_mode==0&&pool->camera_offset[0]==0;
   if(pool->camera_offset[1]!=0||pool->camera_offset[2]!=0||(!aligned&&!diagnostic_offset::camera_left(view,-pool->camera_offset[0],key.worldOffset))){InterlockedIncrement(&pool->stats.invalid);InterlockedExchange(&wire.state,output_wire::idle);continue;}
   float viewport[4]{};memcpy(viewport,row->data()+83,16);bool valid=true;for(unsigned i=0;i<4;++i){valid&=std::isfinite(viewport[i])&&viewport[i]>=0&&viewport[i]<=1920&&fabs(viewport[i]-round(viewport[i]))<.001f;key.viewport[i]=valid?static_cast<DWORD>(viewport[i]):0;}
   ID3D11ShaderResourceView* views[]={item.views[0].Get(),item.views[1].Get(),item.views[2].Get()};const D3D11_VIEWPORT full{0,0,1920,1080,0,1};
   if(!valid||!compositor.draw(target,views,key,full,nativeDepth)){InterlockedIncrement(&pool->stats.invalid);InterlockedExchange(&wire.state,output_wire::idle);continue;}
   if(buffered){try{item.lease.signal(fencedContext.Get());}catch(...){InterlockedExchange(&pool->header.error,1);InterlockedIncrement(&pool->stats.resource_failed);resetHistory();return;}}
   else{context->End(item.query.Get());item.pending=true;}pool->stats.frame=key.frame;InterlockedIncrement(&pool->stats.drawn);InterlockedIncrement(&mapping.state->drawCount);
   if(buffered){++pool->stats.reserved[1];delayed.status=1;delayed.output=static_cast<DWORD>(p.source_frame);delayed.output_sequence=meta.source_sequence;delayed.returned_hash=p.source_state_hash;audit(delayed);}
   return;
  }
  if(buffered){++pool->stats.reserved[4];audit(delayed);}
 }
};
}
