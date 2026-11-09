// Offline bounded supervisor. Never call these waits/launches from SFC callbacks.
#pragma once
#include "output_channel.h"
#include <sddl.h>
#include <string>
#include "pipeline_mode.h"
#include "asset_service.h"
#include "startup_profile.h"
#include "output_startup.h"
#include "receiver_activation.h"
struct OutputPeer {
 HANDLE mapping=nullptr,process=nullptr,readyEvent=nullptr,doneEvent=nullptr;output_wire::Channel* channel=nullptr;uint64_t session=0,resourceEpoch=1;bool disconnected=false,passive=false;DWORD receiverPid=0;std::wstring mode;
 ~OutputPeer(){
  if(channel)InterlockedExchange(&channel->state,output_wire::stopped);
  if(readyEvent)SetEvent(readyEvent);
  if(process){if(WaitForSingleObject(process,5000)==WAIT_TIMEOUT){TerminateProcess(process,9);WaitForSingleObject(process,5000);}CloseHandle(process);}
  if(channel)UnmapViewOfFile(channel);if(mapping)CloseHandle(mapping);if(readyEvent)CloseHandle(readyEvent);if(doneEvent)CloseHandle(doneEvent);
 }
 void check_alive(){require(process&&WaitForSingleObject(process,0)==WAIT_TIMEOUT,"prepared output receiver exited");}
 void wait_state(LONG expected){
  const auto deadline=GetTickCount64()+10000;
  for(;;){check_alive();const auto state=output_wire::state(channel);if(state==expected)return;
   require(state!=output_wire::rejected&&state!=output_wire::stopped&&GetTickCount64()<deadline,"output receiver startup rejected/timeout");
   const HANDLE h[]={process,doneEvent};require(WaitForMultipleObjects(2,h,FALSE,100)!=WAIT_FAILED,"receiver startup notification");}
 }
 void activate(){
  require(passive&&output_wire::state(channel)==output_startup::Passive,"one receiver activation");
  const auto before=output_startup::read(*channel);require(output_startup::valid(before,GetCurrentProcessId(),session)&&before.receiver==receiverPid&&before.readyQpc,"receiver passive identity");
  startup_ticket::Activation expected{};
  if(before.flags&output_startup::Ticket){ReceiverActivation source;require(source.open(GetCurrentProcessId())&&source.accepted(expected),"accepted receiver source ticket");
   wchar_t text[66]{};require(GetEnvironmentVariableW(L"SFC_D3D9_ASSET_SHA256",text,66)==64,"host activated content identity");BYTE asset[32]{};
   for(unsigned i=0;i<64;++i){const auto ch=text[i];require((ch>=L'0'&&ch<=L'9')||(ch>=L'a'&&ch<=L'f'),"host activated asset hex");asset[i/2]=static_cast<BYTE>(asset[i/2]*16+(ch<=L'9'?ch-L'0':ch-L'a'+10));}
   require(!memcmp(asset,expected.asset,32),"accepted asset changed before receiver activation");}
  InterlockedExchange(&channel->state,output_startup::Activate);require(SetEvent(readyEvent)!=FALSE,"activate existing receiver");wait_state(output_wire::idle);
  const auto after=output_startup::read(*channel);require(output_startup::valid(after,GetCurrentProcessId(),session)&&after.receiver==receiverPid&&after.flags==before.flags&&after.readyQpc==before.readyQpc&&after.activatedQpc,"receiver activation receipt");
  if(before.flags&output_startup::Ticket)require(after.game==expected.pid&&!memcmp(after.sourceSession,expected.session,16)&&!memcmp(after.asset,expected.asset,32)&&!memcmp(&after.offset,&expected.offset,4),"receiver late asset/session receipt");
  passive=false;
 }
 void start(const fs::path& exe,const fs::path& root,const std::wstring& selected,StartupProfile* profile=nullptr,bool early=false){
  const auto mark=[&](const char* stage){if(profile)profile->mark(stage,0,false);};mark("peer_start_begin");
  mode=selected;GUID guid{};ok(CoCreateGuid(&guid),"unique output session");memcpy(&session,&guid,8);require(session!=0,"session nonce");
  wchar_t id[40]{};require(StringFromGUID2(guid,id,40)>0,"session string");const auto name=std::wstring(L"Local\\SFC-D3D9-")+id;
  mark("peer_guid_ready");HANDLE token=nullptr;require(OpenProcessToken(GetCurrentProcess(),TOKEN_QUERY,&token)!=0,"user token");DWORD bytes=0;GetTokenInformation(token,TokenUser,nullptr,0,&bytes);std::vector<BYTE> storage(bytes);
  const BOOL got=GetTokenInformation(token,TokenUser,storage.data(),bytes,&bytes);CloseHandle(token);require(got!=0,"user identity");
  LPWSTR sid=nullptr;require(ConvertSidToStringSidW(reinterpret_cast<TOKEN_USER*>(storage.data())->User.Sid,&sid)!=0,"user SID");const auto sddl=std::wstring(L"D:P(A;;GA;;;")+sid+L")";LocalFree(sid);
  PSECURITY_DESCRIPTOR security=nullptr;require(ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl.c_str(),SDDL_REVISION_1,&security,nullptr)!=0,"private ACL");SECURITY_ATTRIBUTES sa{sizeof(sa),security,FALSE};
  mark("peer_security_ready");mapping=CreateFileMappingW(INVALID_HANDLE_VALUE,&sa,PAGE_READWRITE,0,sizeof(output_wire::Channel),name.c_str());const auto error=GetLastError();mark("peer_mapping_created");
  readyEvent=CreateEventW(&sa,FALSE,FALSE,(name+L".ready").c_str());const auto readyError=GetLastError();doneEvent=CreateEventW(&sa,FALSE,FALSE,(name+L".done").c_str());const auto doneError=GetLastError();LocalFree(security);
  require(mapping&&error!=ERROR_ALREADY_EXISTS&&readyEvent&&doneEvent&&readyError!=ERROR_ALREADY_EXISTS&&doneError!=ERROR_ALREADY_EXISTS,"unique private channel/events");
  mark("peer_events_created");channel=static_cast<output_wire::Channel*>(MapViewOfFile(mapping,FILE_MAP_READ|FILE_MAP_WRITE,0,0,sizeof(output_wire::Channel)));require(channel!=nullptr,"producer mapping");memset(channel,0,sizeof(*channel));mark("peer_mapping_initialized");
  output_startup::Control control{};control.parent=GetCurrentProcessId();control.session=session;control.flags=early?output_startup::Ticket:0;
  output_startup::write(*channel,control);InterlockedExchange(&channel->state,output_startup::Boot);
  std::wstring command=L"\""+exe.wstring()+L"\" \""+name+L"\" "+std::to_wstring(session)+L" "+std::to_wstring(GetCurrentProcessId())+L" \""+root.wstring()+L"\" "+mode;
  STARTUPINFOW si{};si.cb=sizeof(si);PROCESS_INFORMATION pi{};mark("peer_process_begin");require(CreateProcessW(exe.c_str(),command.data(),nullptr,nullptr,FALSE,CREATE_NO_WINDOW,nullptr,root.c_str(),&si,&pi)!=0,"launch x86 receiver");mark("peer_process_created");process=pi.hProcess;receiverPid=pi.dwProcessId;CloseHandle(pi.hThread);
  std::cout<<"OUTPUT_PEER_STARTED pid="<<pi.dwProcessId<<" mapping_bytes="<<sizeof(output_wire::Channel)<<" current_user_only=1\n";
  wait_state(output_startup::Passive);passive=true;mark("peer_passive_ready");if(!early)activate();mark("peer_start_complete");
 }
 bool publish(output_wire::Packet p,AssetService* service=nullptr){
  if(disconnected)return false;
  require(output_wire::state(channel)==output_wire::idle,"surface is still owned by receiver");
  if(WaitForSingleObject(process,0)!=WAIT_TIMEOUT){disconnected=true;std::cout<<"OUTPUT_PEER_DISCONNECTED before_publish=1\n";return false;}
  p.magic_value=output_wire::magic;p.version_value=output_wire::version;p.bytes=sizeof(p);p.producer_pid=GetCurrentProcessId();p.session=session;p.resource_epoch=resourceEpoch;
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
 void retire_generation(uint64_t next){
  require(next>resourceEpoch&&next<=INT32_MAX&&output_wire::state(channel)==output_wire::idle,"Output generation retirement requires idle previous epoch");
  if(channel->packet.magic_value!=output_wire::magic){resourceEpoch=next;return;} // no GPU output has ever been published
  const auto sequence=channel->packet.sequence;
  channel->reserved=static_cast<LONG>(next);InterlockedExchange(&channel->state,output_wire::retiring);SetEvent(readyEvent);
  const auto deadline=GetTickCount64()+5000;
  for(;;){check_alive();const auto state=output_wire::state(channel);
   if(state==output_wire::retired){require(channel->ack_session==session&&channel->ack_epoch==next&&channel->ack_sequence==sequence,"Retirement acknowledgement identity");break;}
   require(state!=output_wire::rejected&&state!=output_wire::stopped&&GetTickCount64()<deadline,"Output generation drain5s limit");
   HANDLE waits[]={process,doneEvent};require(WaitForMultipleObjects(2,waits,FALSE,100)!=WAIT_FAILED,"Output retirement notification");
  }
  resourceEpoch=next;InterlockedExchange(&channel->state,output_wire::idle);
 }
 void finish(){
  if(!process)return;InterlockedExchange(&channel->state,output_wire::stopped);SetEvent(readyEvent);require(WaitForSingleObject(process,5000)==WAIT_OBJECT_0,"receiver shutdown5s");DWORD code=0;require(GetExitCodeProcess(process,&code)!=0,"receiver exit receipt");
  require(code==(mode==L"invalid"?1u:0u),"unexpected receiver exit code");std::cout<<"OUTPUT_PEER_RETIRED exit="<<code<<" disconnected="<<disconnected<<'\n';
 }
};
