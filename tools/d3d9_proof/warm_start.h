// External host only: initialize once, then sleep until a qualified scene arrives.
#pragma once
#include "startup_ticket.h"
namespace warm_start {
constexpr uint32_t Magic=0x31524157;
using Activation=startup_ticket::Activation;
struct Cancelled{};
inline bool requested(){wchar_t flag[2]{};return GetEnvironmentVariableW(L"SFC_D3D9_PREWARM",flag,2)==1&&flag[0]==L'1';}
inline std::array<uint32_t,4> session(){
 wchar_t name[128]{};const auto size=GetEnvironmentVariableW(L"SFC_REMIX_CALIBRATION_SCENE",name,128);
 require(size>32&&size<128,"warm session");std::array<uint32_t,4> words{};
 for(unsigned i=0;i<4;++i){wchar_t* end=nullptr;const auto part=std::wstring(name+size-32+i*8,8);words[i]=wcstoul(part.c_str(),&end,16);require(end&&!*end,"warm session hex");}return words;
}
template<class Pump,class Observe> inline void wait(const fs::path& root,Pump pump,Observe observe){
 const auto words=session();wchar_t pidText[16]{};GetEnvironmentVariableW(L"SFC_D3D9_GAME_PID",pidText,16);const auto pid=wcstoul(pidText,nullptr,10);
 require(pid!=0,"warm verified game PID");HANDLE game=OpenProcess(SYNCHRONIZE,FALSE,pid);require(game!=nullptr,"warm game liveness");
 struct Close {HANDLE h;~Close(){CloseHandle(h);}} close{game};
 (void)root;
 sfc_calibration::Reader bridge;
 require(bridge.prepare()&&bridge.requested,"warm explicit existing session mapping");
 struct MappingClose {sfc_calibration::Reader& r;~MappingClose(){r.close();}} mappingClose{bridge};
 auto* base=reinterpret_cast<BYTE*>(bridge.mailbox)-sfc_calibration::Offset;
 auto& cell=*reinterpret_cast<startup_ticket::Store*>(base+startup_ticket::Offset);
 require(startup_ticket::valid(cell,words.data(),pid),"warm startup cell identity");
 HANDLE producer=OpenProcess(SYNCHRONIZE,FALSE,cell.producer);require(producer!=nullptr,"warm supervisor liveness");Close producerClose{producer};
 if(startup_ticket::load(&cell.state)==startup_ticket::Cancelled)throw Cancelled{};
 require(InterlockedCompareExchange(&cell.ready,-1,0)==0,"one startup host per session");
 LARGE_INTEGER now{};QueryPerformanceCounter(&now);cell.host=GetCurrentProcessId();cell.readyQpc=static_cast<uint64_t>(now.QuadPart);InterlockedExchange(&cell.ready,1);
 const auto limit=GetTickCount64()+180000;
 HANDLE liveness[]={game,producer};
 for(;;){
  const auto state=startup_ticket::load(&cell.state);
  if(state==startup_ticket::Cancelled||WaitForMultipleObjects(2,liveness,FALSE,0)!=WAIT_TIMEOUT)throw Cancelled{};
  require(state>=startup_ticket::Empty&&state<=startup_ticket::Published,"warm startup state");
  require(GetTickCount64()<limit,"warm activation180s limit");
  pump(); // Optional external-host work only;normal idle does no disk access.
  if(state==startup_ticket::Published){
   observe("activation_seen",0);
   const Activation a=cell.ticket;
   observe("activation_read",0);
   if(!startup_ticket::valid(cell,words.data(),pid)||!startup_ticket::valid(a,cell)){
    InterlockedCompareExchange(&cell.state,startup_ticket::Rejected,startup_ticket::Published);
    require(false,"warm activation identity/checksum");
   }
   if(WaitForMultipleObjects(2,liveness,FALSE,0)!=WAIT_TIMEOUT)throw Cancelled{};
   if(InterlockedCompareExchange(&cell.state,startup_ticket::Accepted,startup_ticket::Published)!=startup_ticket::Published)throw Cancelled{};
   QueryPerformanceCounter(&now);cell.acceptedQpc=static_cast<uint64_t>(now.QuadPart);
   observe("activation_validated",0);
   unsigned applied=0;
   auto set=[&](const wchar_t* key,const std::wstring& value){observe("activation_env_begin",applied);require(SetEnvironmentVariableW(key,value.c_str())!=FALSE,"warm environment apply");observe("activation_env_end",applied++);};
   set(L"SFC_D3D9_EXPECTED_MODEL",std::to_wstring(a.model));set(L"SFC_D3D9_EXPECTED_SOURCE",std::to_wstring(a.source));
   wchar_t hex[65]{};swprintf_s(hex,L"%llx",a.mask);set(L"SFC_D3D9_INITIAL_ASSET_MASK",hex);swprintf_s(hex,L"%llx",a.cookie);set(L"SFC_D3D9_REBIND_COOKIE",hex);
   bool any=false;for(unsigned i=0;i<32;++i){swprintf_s(hex+i*2,65-i*2,L"%02x",unsigned(a.asset[i]));any|=a.asset[i]!=0;}require(any,"warm asset identity");set(L"SFC_D3D9_ASSET_SHA256",hex);set(L"SFC_D3D9_OFFSET_X",std::to_wstring(a.offset));
   return;
  }
  const auto tick=GetTickCount64();require(tick<limit,"warm activation180s limit");
  const auto remaining=limit-tick;
  if(WaitForMultipleObjects(2,liveness,FALSE,static_cast<DWORD>((std::min)(remaining,10ull)))!=WAIT_TIMEOUT)throw Cancelled{}; // Existing bounded idle cadence;never a game callback.
 }
}
template<class Pump>inline void wait(const fs::path& root,Pump pump){wait(root,pump,[](const char*,unsigned){});}
inline void wait(const fs::path& root){wait(root,[]{});}
}
