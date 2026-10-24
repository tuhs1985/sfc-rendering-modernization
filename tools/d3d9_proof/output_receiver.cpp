// Standalone x86 native D3D11 receiver. Readback is OFFLINE verification only.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "output_channel.h"
#include <d3d11.h>
#include <dxgi.h>
#include <wrl/client.h>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
using Microsoft::WRL::ComPtr;
static void check(bool b,const char* m){if(!b)throw std::runtime_error(m);}
static void hr(HRESULT h,const char* m){if(FAILED(h)){std::cerr<<"HRESULT "<<std::hex<<static_cast<unsigned long>(h)<<' ';throw std::runtime_error(m);}}
static uint64_t ticks(){LARGE_INTEGER q{};check(QueryPerformanceCounter(&q)!=FALSE,"receiver timestamp");return static_cast<uint64_t>(q.QuadPart);}
#include "game_output_writer.h"
#include "worker_gpu_fence.h"
#include "deferred_diagnostics.h"
#include "pipeline_mode.h"
int wmain(int argc,wchar_t** argv){
 const bool detailed=!pipeline_mode::performance();
 auto* outbuf=std::cout.rdbuf();auto* errbuf=std::cerr.rdbuf();
 std::ofstream log;if(argc==6){log.open(std::filesystem::path(argv[4])/L"receiver.log");if(!log)return 2;std::cout.rdbuf(log.rdbuf());std::cerr.rdbuf(log.rdbuf());}
 wchar_t buffered[2]{};const bool bufferedDiagnostics=GetEnvironmentVariableW(L"SFC_D3D9_LIVE_TIMING",buffered,2)==1&&buffered[0]==L'1';
 DeferredDiagnostics diagnosticLog(std::cout,bufferedDiagnostics,2*1024*1024);
 std::cout.setf(std::ios::unitbuf);HANDLE mapping=nullptr,parent=nullptr,readyEvent=nullptr,doneEvent=nullptr;output_wire::Channel* channel=nullptr;int result=1;
 try{
  check(argc==6,"mapping,session,parent PID,output directory,mode required");
  const uint64_t session=std::stoull(argv[2]);const auto pid=static_cast<DWORD>(std::stoul(argv[3]));const std::wstring mode=argv[5];
  wchar_t paced[16]{};GetEnvironmentVariableW(L"SFC_DIRECT64_PACED_FRAMES",paced,16);const bool sampleOnly=_wtoi(paced)>0;
  wchar_t timingOnly[2]{};const bool noReadback=GetEnvironmentVariableW(L"SFC_DIRECT64_TIMING_ONLY",timingOnly,2)==1&&timingOnly[0]==L'1';
  GameOutputWriter game;game.start();check(!game.enabled||noReadback,"game output forbids continuous readback");
  mapping=OpenFileMappingW(FILE_MAP_READ|FILE_MAP_WRITE,FALSE,argv[1]);check(mapping!=nullptr,"open private mapping");
  readyEvent=OpenEventW(SYNCHRONIZE,FALSE,(std::wstring(argv[1])+L".ready").c_str());doneEvent=OpenEventW(EVENT_MODIFY_STATE,FALSE,(std::wstring(argv[1])+L".done").c_str());check(readyEvent&&doneEvent,"open private notifications");
  channel=static_cast<output_wire::Channel*>(MapViewOfFile(mapping,FILE_MAP_READ|FILE_MAP_WRITE,0,0,sizeof(output_wire::Channel)));check(channel!=nullptr,"map wire");
  parent=OpenProcess(SYNCHRONIZE,FALSE,pid);check(parent!=nullptr,"open parent lifetime");
  ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context;ComPtr<ID3D11Query> query;WorkerGpuFence copyFence;
  ComPtr<ID3D11Texture2D> textures[3],cache[3],staging[3];uint64_t last=0,epoch=0;output_wire::Packet previous{};unsigned received=0;
  wchar_t live[2]{};const bool liveMode=GetEnvironmentVariableW(L"SFC_D3D9_LIVE_TIMING",live,2)==1&&live[0]==L'1';
  const auto deadline=GetTickCount64()+output_wire::receiver_lifetime_ms(liveMode,game.enabled);
  for(;;){
   check(GetTickCount64()<deadline,game.enabled?"receiver130s additive timeout":liveMode?"receiver110s live timeout":"receiver60s timeout");check(WaitForSingleObject(parent,0)==WAIT_TIMEOUT,"producer disconnected");
   const auto state=output_wire::state(channel);if(state==output_wire::stopped){check(received>0,"no images received");result=0;break;}
   if(state!=output_wire::ready){const HANDLE waits[]={parent,readyEvent};check(WaitForMultipleObjects(2,waits,FALSE,100)!=WAIT_FAILED,"producer notification wait");continue;}
   if(InterlockedCompareExchange(&channel->state,output_wire::acquired,output_wire::ready)!=output_wire::ready)continue;
   const auto p=channel->packet;
   check(output_wire::valid(p,session,pid)&&p.sequence==last+1,"malformed/session/sequence packet");
   if(mode==L"exit-acquired"){std::cout<<"RECEIVER_DISCONNECT_ACQUIRED\n";result=0;break;}
   if(!device){
    ComPtr<IDXGIFactory1> factory;hr(CreateDXGIFactory1(IID_PPV_ARGS(&factory)),"factory");ComPtr<IDXGIAdapter1> selected;
    for(UINT i=0;i<16;++i){ComPtr<IDXGIAdapter1> a;if(factory->EnumAdapters1(i,&a)==DXGI_ERROR_NOT_FOUND)break;DXGI_ADAPTER_DESC1 d{};hr(a->GetDesc1(&d),"adapter");if(d.AdapterLuid.LowPart==p.luid_low&&d.AdapterLuid.HighPart==p.luid_high){selected=a;break;}}
    check(bool(selected),"same GPU required");D3D_FEATURE_LEVEL level{};
    hr(D3D11CreateDevice(selected.Get(),D3D_DRIVER_TYPE_UNKNOWN,nullptr,D3D11_CREATE_DEVICE_BGRA_SUPPORT,nullptr,0,D3D11_SDK_VERSION,&device,&level,&context),"receiver device");check(level>=D3D_FEATURE_LEVEL_11_0,"feature level");
    D3D11_QUERY_DESC q{D3D11_QUERY_EVENT,0};hr(device->CreateQuery(&q,&query),"receiver query");
    if(game.enabled)copyFence.start(device.Get(),context.Get());
   }
   if(!epoch){
    for(unsigned i=0;i<3;++i){hr(device->OpenSharedResource(reinterpret_cast<HANDLE>(static_cast<uintptr_t>(p.handles[i])),IID_PPV_ARGS(&textures[i])),"open shared GPU image");
     D3D11_TEXTURE2D_DESC d{};textures[i]->GetDesc(&d);check(d.Width==p.width&&d.Height==p.height&&d.Format==(i?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM)&&d.MipLevels==1&&d.ArraySize==1&&d.SampleDesc.Count==1,"shared texture descriptor");
     if(!game.enabled){d.MiscFlags=0;hr(device->CreateTexture2D(&d,nullptr,&cache[i]),"receiver private GPU cache");}
     if(!noReadback){d.BindFlags=d.MiscFlags=0;d.Usage=D3D11_USAGE_STAGING;d.CPUAccessFlags=D3D11_CPU_ACCESS_READ;hr(device->CreateTexture2D(&d,nullptr,&staging[i]),"verification staging");}
    }epoch=p.resource_epoch;
   }else check(p.resource_epoch==epoch&&p.width==previous.width&&p.height==previous.height&&p.luid_low==previous.luid_low&&p.luid_high==previous.luid_high&&p.handles[0]==previous.handles[0]&&p.handles[1]==previous.handles[1]&&p.handles[2]==previous.handles[2],"resource changed without retirement");
   if(mode==L"slow")Sleep(200);
   const bool verify=!noReadback&&(!sampleOnly||p.sequence==1||p.sequence%output_wire::verification_stride==0);
   int gameSlot=-1;const auto copyStarted=ticks();
   if(game.enabled){ID3D11Texture2D* images[]={textures[0].Get(),textures[1].Get(),textures[2].Get()};gameSlot=game.copy(device.Get(),context.Get(),p,game_output::metadata(*channel),images);}
   else for(unsigned i=0;i<3;++i){context->CopyResource(cache[i].Get(),textures[i].Get());if(verify)context->CopyResource(staging[i].Get(),cache[i].Get());}
   if(game.enabled)copyFence.wait();else{
    context->End(query.Get());context->Flush();const auto gpuDeadline=GetTickCount64()+5000;BOOL complete=FALSE;HRESULT status;
    do{status=context->GetData(query.Get(),&complete,sizeof(complete),0);hr(status,"receiver completion");check(GetTickCount64()<gpuDeadline,"receiver GPU5s timeout");if(status==S_FALSE||!complete)Sleep(1);}while(status==S_FALSE||!complete);
   }
   const auto copyCompleted=ticks();
   if(verify)for(unsigned i=0;i<3;++i){D3D11_MAPPED_SUBRESOURCE map{};hr(context->Map(staging[i].Get(),0,D3D11_MAP_READ,0,&map),"verification map");
    const auto path=std::filesystem::path(argv[4])/(L"receiver-"+std::to_wstring(p.sequence-1)+L"-"+std::to_wstring(i)+L".raw32");
    std::ofstream file(path,std::ios::binary);file.write(reinterpret_cast<const char*>(&p.width),4);file.write(reinterpret_cast<const char*>(&p.height),4);
    for(UINT y=0;y<p.height;++y)file.write(static_cast<const char*>(map.pData)+size_t(y)*map.RowPitch,p.width*4);
    context->Unmap(staging[i].Get(),0);check(bool(file),"receiver write");
   }
   if(game.enabled)game.publish(gameSlot,p,game_output::metadata(*channel));
   const auto poolPublished=ticks();
   channel->reserved=game.enabled&&gameSlot<0?1:0;
   channel->ack_session=p.session;channel->ack_epoch=p.resource_epoch;channel->ack_sequence=p.sequence+(mode==L"stale-ack"?1:0);
   InterlockedExchange(&channel->state,output_wire::acknowledged);check(SetEvent(doneEvent)!=FALSE,"acknowledgement notification");last=p.sequence;previous=p;++received;
   if(detailed)std::cout<<"RECEIVED sequence="<<p.sequence<<" source_frame="<<p.source_frame<<" owner="<<p.owner<<" revision="<<p.revision<<" gpu_complete="<<(!game.enabled||gameSlot>=0)<<" game_slot="<<gameSlot<<" copy_started_qpc="<<copyStarted<<" copy_completed_qpc="<<copyCompleted<<" pool_published_qpc="<<poolPublished<<'\n';
   if(mode==L"disconnect"){result=0;break;}
  }
  if(context){context->ClearState();context->Flush();hr(device->GetDeviceRemovedReason(),"receiver healthy");}
  std::cout<<"RECEIVER_RETIRED frames="<<received<<" result="<<result<<'\n';
 }catch(const std::exception& e){std::cerr<<"RECEIVER_REJECTED "<<e.what()<<'\n';if(channel)InterlockedExchange(&channel->state,output_wire::rejected);if(doneEvent)SetEvent(doneEvent);}
 if(channel)UnmapViewOfFile(channel);if(mapping)CloseHandle(mapping);if(parent)CloseHandle(parent);if(readyEvent)CloseHandle(readyEvent);if(doneEvent)CloseHandle(doneEvent);diagnosticLog.finish();std::cout.rdbuf(outbuf);std::cerr.rdbuf(errbuf);return result;
}
