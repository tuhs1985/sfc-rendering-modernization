// Same-process callback observer;no graphics API calls,waits,allocation or I/O.
#pragma once
#include "../d3d9_proof/source_timing.h"
#include "../d3d9_proof/live_owner_wire.h"
namespace source_timing {
class Observer {
 sfc_calibration::Reader source;sfc_calibration::Snapshot scratch{};Store* store=nullptr;
 live_owner::PresentObserver live;
public:
 ~Observer(){source.close();}
 void prepare(){
  if(!source.prepare()||!source.requested)throw std::runtime_error("source timing mailbox required");
  auto* base=reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset;store=reinterpret_cast<Store*>(base+Offset);
  LARGE_INTEGER f{};if(!QueryPerformanceFrequency(&f))throw std::runtime_error("source timing QPC frequency");
  if(!store->header.magic)initialize(*store,GetCurrentProcessId(),GetCurrentThreadId(),static_cast<uint64_t>(f.QuadPart),source.session);
  else if(store->header.magic!=Magic||store->header.version!=Version||store->header.bytes!=sizeof(Store)||store->header.producer_pid!=GetCurrentProcessId()||memcmp(store->header.session,source.session,16))throw std::runtime_error("source timing existing session mismatch");
  wchar_t mode[2]{};if(GetEnvironmentVariableW(L"SFC_D3D9_LIVE_TIMING",mode,2)==1&&mode[0]==L'1'){
   live.store=reinterpret_cast<live_owner::Store*>(base+live_owner::Offset);
   if(!live_owner::header_valid(live.store->header,source.session))throw std::runtime_error("live owner store missing");
  }
 }
 void observe(uint32_t stage){
  if(!store)return;
  if(GetCurrentThreadId()!=store->header.thread){InterlockedIncrement(reinterpret_cast<volatile LONG*>(&store->header.wrong_thread));return;}
  if(!sfc_calibration::read(source.mailbox,scratch)){++store->header.snapshot_miss;return;}
  LARGE_INTEGER now{};if(!QueryPerformanceCounter(&now)){++store->header.invalid;return;}
  append(*store,scratch,stage,GetCurrentThreadId(),static_cast<uint64_t>(now.QuadPart));
  if(stage==1&&live.store){const auto chosen=static_cast<uint64_t>(InterlockedCompareExchange64(&live.store->header.selected,0,0));
   const live_owner::Row* row=nullptr;for(const auto& r:scratch.owner)if(r[1]==static_cast<DWORD>(chosen)){row=&r;break;}
   live.observe(row,scratch.frame,GetCurrentThreadId(),static_cast<uint64_t>(now.QuadPart));}
 }
};
}
