// Standalone x86 producer/x64 receiver. Synthetic poses,not SFC or GPU timing.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "frame_ingress.h"
#include <sddl.h>
#include <objbase.h>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <stdexcept>
using namespace frame_ingress;
static void need(bool b,const char* why){if(!b)throw std::runtime_error(why);}
static uint64_t ticks(){LARGE_INTEGER t{};need(QueryPerformanceCounter(&t)!=FALSE,"QPC");return static_cast<uint64_t>(t.QuadPart);}
static uint64_t frequency(){LARGE_INTEGER t{};need(QueryPerformanceFrequency(&t)!=FALSE,"frequency");return static_cast<uint64_t>(t.QuadPart);}
static Packet sample(uint64_t session,uint64_t sequence,uint64_t now,uint64_t freq){
 Packet p{};p.key={session,sequence,sequence+100,0,sequence<61?44ull:55ull,sequence<61?2u:3u,sequence<61?1u:2u};
 p.offered_qpc=now;p.deadline_qpc=now+freq/60;
 p.model[0]=p.model[5]=p.model[10]=p.model[15]=1;p.model[12]=static_cast<float>(sequence);
 memcpy(p.view,p.model,sizeof(p.view));memcpy(p.projection,p.model,sizeof(p.projection));
 p.viewport[2]=1720;p.viewport[3]=1020;p.key.state_hash=state_hash(p);p.checksum=checksum(p);return p;
}
struct Resources {
 HANDLE mapping=nullptr,child=nullptr;Channel* channel=nullptr;
 ~Resources(){
  if(channel)InterlockedExchange(&channel->stopped,1);
  if(child){if(WaitForSingleObject(child,3000)==WAIT_TIMEOUT){TerminateProcess(child,9);WaitForSingleObject(child,3000);}CloseHandle(child);}
  if(channel)UnmapViewOfFile(channel);if(mapping)CloseHandle(mapping);
 }
};
static int writer(const wchar_t* name,uint64_t session,const std::wstring& mode){
 Resources r;r.mapping=OpenFileMappingW(FILE_MAP_READ|FILE_MAP_WRITE,FALSE,name);need(r.mapping!=nullptr,"child mapping");
 r.channel=static_cast<Channel*>(MapViewOfFile(r.mapping,FILE_MAP_READ|FILE_MAP_WRITE,0,0,sizeof(Channel)));need(r.channel&&channel_valid(*r.channel,session),"child channel");
 Producer producer;const auto freq=frequency();unsigned sent=0;const auto limit=mode==L"disconnect"?60u:240u;
 if(mode==L"malformed"){
  auto& s=r.channel->slots[0];need(InterlockedCompareExchange(&s.state,Writing,Free)==Free,"malformed slot");
  s.packet=sample(session,1,ticks(),freq);s.packet.checksum^=1;InterlockedExchange(&s.state,Ready);Sleep(50);
 }
 for(unsigned i=1;i<=limit&&!state(&r.channel->stopped);++i){auto p=sample(session,i,ticks(),freq);sent+=producer.publish(*r.channel,p)?1u:0u;Sleep(1);}
 std::cout<<"INGRESS_SOURCE pointer_bits="<<sizeof(void*)*8<<" sent="<<sent<<" stopped="<<state(&r.channel->stopped)<<'\n';
 // Parent owns stop/unmap. Child normal exit must not invalidate still-ready
 // packets before parent drains them. Release our view without setting stop.
 UnmapViewOfFile(r.channel);r.channel=nullptr;return 0;
}
static int parent(const wchar_t* exe,const std::wstring& mode,const wchar_t* receipt){
 need(mode==L"normal"||mode==L"slow"||mode==L"disconnect"||mode==L"malformed"||mode==L"stop","fixture mode");
 DWORD binaryType=0;need(GetBinaryTypeW(exe,&binaryType)!=FALSE&&binaryType==SCS_32BIT_BINARY,"x86 producer required");
 Resources r;GUID guid{};need(SUCCEEDED(CoCreateGuid(&guid)),"GUID");uint64_t session=0;memcpy(&session,&guid,8);need(session!=0,"session");
 wchar_t id[40]{};need(StringFromGUID2(guid,id,40)>0,"GUID string");const auto name=std::wstring(L"Local\\SFC-Frame-Ingress-")+id;
 HANDLE token=nullptr;need(OpenProcessToken(GetCurrentProcess(),TOKEN_QUERY,&token)!=FALSE,"token");DWORD bytes=0;GetTokenInformation(token,TokenUser,nullptr,0,&bytes);std::vector<BYTE> storage(bytes);
 const BOOL got=GetTokenInformation(token,TokenUser,storage.data(),bytes,&bytes);CloseHandle(token);need(got!=FALSE,"token user");
 LPWSTR sid=nullptr;need(ConvertSidToStringSidW(reinterpret_cast<TOKEN_USER*>(storage.data())->User.Sid,&sid)!=FALSE,"SID");const auto sddl=std::wstring(L"D:P(A;;GA;;;")+sid+L")";LocalFree(sid);
 PSECURITY_DESCRIPTOR sd=nullptr;need(ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl.c_str(),SDDL_REVISION_1,&sd,nullptr)!=FALSE,"ACL");SECURITY_ATTRIBUTES sa{sizeof(sa),sd,FALSE};
 r.mapping=CreateFileMappingW(INVALID_HANDLE_VALUE,&sa,PAGE_READWRITE,0,sizeof(Channel),name.c_str());const auto error=GetLastError();LocalFree(sd);need(r.mapping&&error!=ERROR_ALREADY_EXISTS,"unique private mapping");
 r.channel=static_cast<Channel*>(MapViewOfFile(r.mapping,FILE_MAP_READ|FILE_MAP_WRITE,0,0,sizeof(Channel)));need(r.channel!=nullptr,"parent view");
 *r.channel=Channel{};r.channel->session=session;
 std::wstring command=L"\""+std::wstring(exe)+L"\" --writer \""+name+L"\" "+std::to_wstring(session)+L" "+mode;
 STARTUPINFOW si{};si.cb=sizeof(si);PROCESS_INFORMATION pi{};need(CreateProcessW(exe,command.data(),nullptr,nullptr,FALSE,CREATE_NO_WINDOW,nullptr,nullptr,&si,&pi)!=FALSE,"x86 producer process");
 r.child=pi.hProcess;CloseHandle(pi.hThread);const auto began=GetTickCount64();Consumer consumer;TakeStats stats{};
 uint64_t last=0;unsigned received=0,late=0;bool exited=false,stopSent=false;
 for(;;){
  need(GetTickCount64()-began<5000,"fixture5s bound");Packet p{};
  if(consumer.take(*r.channel,session,ticks(),p,stats)){
   need(p.key.sequence>last,"monotonic sequence");const auto expected=sample(session,p.key.sequence,p.offered_qpc,frequency());
   need(!memcmp(&p,&expected,sizeof(Packet)),"cross-process pose/identity bytes");last=p.key.sequence;++received;
   // Deliberate one-frame-late completion must fail exact current expectation.
   auto next=p.key;++next.source_frame;++next.sequence;
   need(!usable(p,next,ticks(),true),"old pose must not match new frame");
   if(mode==L"slow"){Sleep(35);need(!usable(p,p.key,ticks(),true),"late completion rejected");++late;}
   if(mode==L"stop"&&received>=10&&!stopSent){InterlockedExchange(&r.channel->stopped,1);stopSent=true;}
  }else if(exited)break;
  const auto status=WaitForSingleObject(r.child,0);need(status!=WAIT_FAILED,"child wait");exited=status==WAIT_OBJECT_0;
  Sleep(1); // Standalone worker ONLY,never a source callback.
 }
 DWORD code=1;need(GetExitCodeProcess(r.child,&code)!=FALSE&&code==0,"producer exit");need(received>0,"received data");
 need(stats.invalid==(mode==L"malformed"?1u:0u),"malformed count");
 if(mode==L"stop")need(stopSent,"stopped source");
 else if(mode!=L"slow")need(last==(mode==L"disconnect"?60ull:240ull),"latest final packet received");
 if(mode==L"slow")need(late>0&&received<240&&last>180,"backlog bounded and catch-up");
 InterlockedExchange(&r.channel->stopped,1);
 std::ofstream file(receipt);need(bool(file),"receipt file");
 file<<"{\"result\":\"INGRESS_TRANSPORT_FIXTURE_PASS\",\"synthetic\":true,\"sfc_launched\":false,\"gpu_rendered\":false,\"mapping_bytes\":"<<sizeof(Channel)
     <<",\"producer_pointer_bits\":32,\"consumer_pointer_bits\":"<<sizeof(void*)*8<<",\"received\":"<<received<<",\"last_sequence\":"<<last
     <<",\"expired\":"<<stats.expired<<",\"obsolete\":"<<stats.obsolete<<",\"invalid\":"<<stats.invalid<<",\"late_completions_rejected\":"<<late
     <<",\"source_exit\":"<<code<<",\"stop_sent\":"<<(stopSent?"true":"false")<<"}\n";need(bool(file),"receipt write");
 std::cout<<"INGRESS_TRANSPORT_PASS received="<<received<<" latest="<<last<<" late_rejected="<<late<<" invalid="<<stats.invalid<<'\n';return 0;
}
int wmain(int argc,wchar_t** argv){
 try{if(argc==5&&std::wstring(argv[1])==L"--writer")return writer(argv[2],_wcstoui64(argv[3],nullptr,10),argv[4]);
  need(argc==4,"child exe,mode,receipt required");return parent(argv[1],argv[2],argv[3]);
 }catch(const std::exception& e){std::cerr<<"INGRESS_FIXTURE_FAIL "<<e.what()<<'\n';return 1;}
}
