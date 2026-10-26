// Offline bounded supervisor. Never call these waits/launches from SFC callbacks.
#pragma once
#include "output_channel.h"
#include <sddl.h>
#include <string>
#include "pipeline_mode.h"
#include "asset_service.h"
struct OutputPeer {
 HANDLE mapping=nullptr,process=nullptr,readyEvent=nullptr,doneEvent=nullptr;output_wire::Channel* channel=nullptr;uint64_t session=0;bool disconnected=false;std::wstring mode;
 ~OutputPeer(){
  if(channel)InterlockedExchange(&channel->state,output_wire::stopped);
  if(readyEvent)SetEvent(readyEvent);
  if(process){if(WaitForSingleObject(process,5000)==WAIT_TIMEOUT){TerminateProcess(process,9);WaitForSingleObject(process,5000);}CloseHandle(process);}
  if(channel)UnmapViewOfFile(channel);if(mapping)CloseHandle(mapping);if(readyEvent)CloseHandle(readyEvent);if(doneEvent)CloseHandle(doneEvent);
 }
 void start(const fs::path& exe,const fs::path& root,const std::wstring& selected){
  mode=selected;GUID guid{};ok(CoCreateGuid(&guid),"unique output session");memcpy(&session,&guid,8);require(session!=0,"session nonce");
  wchar_t id[40]{};require(StringFromGUID2(guid,id,40)>0,"session string");const auto name=std::wstring(L"Local\\SFC-D3D9-")+id;
  HANDLE token=nullptr;require(OpenProcessToken(GetCurrentProcess(),TOKEN_QUERY,&token)!=0,"user token");DWORD bytes=0;GetTokenInformation(token,TokenUser,nullptr,0,&bytes);std::vector<BYTE> storage(bytes);
  const BOOL got=GetTokenInformation(token,TokenUser,storage.data(),bytes,&bytes);CloseHandle(token);require(got!=0,"user identity");
  LPWSTR sid=nullptr;require(ConvertSidToStringSidW(reinterpret_cast<TOKEN_USER*>(storage.data())->User.Sid,&sid)!=0,"user SID");const auto sddl=std::wstring(L"D:P(A;;GA;;;")+sid+L")";LocalFree(sid);
  PSECURITY_DESCRIPTOR security=nullptr;require(ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl.c_str(),SDDL_REVISION_1,&security,nullptr)!=0,"private ACL");SECURITY_ATTRIBUTES sa{sizeof(sa),security,FALSE};
  mapping=CreateFileMappingW(INVALID_HANDLE_VALUE,&sa,PAGE_READWRITE,0,sizeof(output_wire::Channel),name.c_str());const auto error=GetLastError();
  readyEvent=CreateEventW(&sa,FALSE,FALSE,(name+L".ready").c_str());const auto readyError=GetLastError();doneEvent=CreateEventW(&sa,FALSE,FALSE,(name+L".done").c_str());const auto doneError=GetLastError();LocalFree(security);
  require(mapping&&error!=ERROR_ALREADY_EXISTS&&readyEvent&&doneEvent&&readyError!=ERROR_ALREADY_EXISTS&&doneError!=ERROR_ALREADY_EXISTS,"unique private channel/events");
  channel=static_cast<output_wire::Channel*>(MapViewOfFile(mapping,FILE_MAP_READ|FILE_MAP_WRITE,0,0,sizeof(output_wire::Channel)));require(channel!=nullptr,"producer mapping");memset(channel,0,sizeof(*channel));
  std::wstring command=L"\""+exe.wstring()+L"\" \""+name+L"\" "+std::to_wstring(session)+L" "+std::to_wstring(GetCurrentProcessId())+L" \""+root.wstring()+L"\" "+mode;
  STARTUPINFOW si{};si.cb=sizeof(si);PROCESS_INFORMATION pi{};require(CreateProcessW(exe.c_str(),command.data(),nullptr,nullptr,FALSE,CREATE_NO_WINDOW,nullptr,root.c_str(),&si,&pi)!=0,"launch x86 receiver");process=pi.hProcess;CloseHandle(pi.hThread);
  std::cout<<"OUTPUT_PEER_STARTED pid="<<pi.dwProcessId<<" mapping_bytes="<<sizeof(output_wire::Channel)<<" current_user_only=1\n";
 }
 bool publish(output_wire::Packet p,AssetService* service=nullptr){
  if(disconnected)return false;
  require(output_wire::state(channel)==output_wire::idle,"surface is still owned by receiver");
  if(WaitForSingleObject(process,0)!=WAIT_TIMEOUT){disconnected=true;std::cout<<"OUTPUT_PEER_DISCONNECTED before_publish=1\n";return false;}
  p.magic_value=output_wire::magic;p.version_value=output_wire::version;p.bytes=sizeof(p);p.producer_pid=GetCurrentProcessId();p.session=session;p.resource_epoch=1;
  if(mode==L"invalid")p.width=1921;
  LARGE_INTEGER q{};QueryPerformanceCounter(&q);p.published_qpc=static_cast<uint64_t>(q.QuadPart);p.checksum=output_wire::checksum(p);channel->packet=p;InterlockedExchange(&channel->state,output_wire::ready);require(SetEvent(readyEvent)!=FALSE,"notify receiver");
  const auto deadline=GetTickCount64()+10000;const auto began=GetTickCount64();
  for(;;){const auto state=output_wire::state(channel);
   if(state==output_wire::acknowledged){if(!output_wire::valid_ack(*channel,p)){require(mode==L"stale-ack","ACK identity mismatch");std::cout<<"OUTPUT_STALE_ACK_REJECTED\n";disconnected=true;break;}
    InterlockedExchange(&channel->state,output_wire::idle);if(!pipeline_mode::performance())std::cout<<"OUTPUT_ACK sequence="<<p.sequence<<" held_ms="<<GetTickCount64()-began<<'\n';return true;}
   if(state==output_wire::rejected){require(mode==L"invalid","receiver rejected valid output");std::cout<<"OUTPUT_INVALID_REJECTED\n";disconnected=true;break;}
   if(WaitForSingleObject(process,0)!=WAIT_TIMEOUT){require(mode==L"disconnect"||mode==L"exit-acquired","receiver exited unexpectedly");std::cout<<"OUTPUT_PEER_DISCONNECTED acquired="<<(state==output_wire::acquired)<<'\n';disconnected=true;break;}
   require(GetTickCount64()<deadline,"receiver ACK10s limit");
   if(service)service->tick(AssetService::Peer);
   const HANDLE waits[]={process,doneEvent};require(WaitForMultipleObjects(2,waits,FALSE,service&&service->enabled?1:100)!=WAIT_FAILED,"receiver notification wait");
  }
  // Receiver death/rejection:retire this generation;never re-use its textures.
  InterlockedExchange(&channel->state,output_wire::stopped);SetEvent(readyEvent);require(WaitForSingleObject(process,5000)==WAIT_OBJECT_0,"receiver must retire before surface release");return false;
 }
 void finish(){
  if(!process)return;InterlockedExchange(&channel->state,output_wire::stopped);SetEvent(readyEvent);require(WaitForSingleObject(process,5000)==WAIT_OBJECT_0,"receiver shutdown5s");DWORD code=0;require(GetExitCodeProcess(process,&code)!=0,"receiver exit receipt");
  require(code==(mode==L"invalid"?1u:0u),"unexpected receiver exit code");std::cout<<"OUTPUT_PEER_RETIRED exit="<<code<<" disconnected="<<disconnected<<'\n';
 }
};
