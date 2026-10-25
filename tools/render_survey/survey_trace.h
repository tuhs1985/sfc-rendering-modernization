// Public full-support ReShade events only. Fixed storage; no callback I/O/waits.
#pragma once
#include <atomic>
#include <array>
#include <cstring>
#include "return_wire.h"
namespace survey_trace {
constexpr uint32_t Magic=0x53525631,Version=2,Capacity=131072;
// 2 GiB TOTAL run envelope: leave 32 MiB for sidecars/summary/owned logs.
constexpr uint64_t HardBytes=2113929216ull;
enum Event:uint32_t {Device=1,DeviceEnd,Resource,ResourceEnd,View,ViewEnd,
 Command,CommandEnd,CommandReset,Targets,Draw,Indexed,ClearDepth,ClearColor,
 Copy,CopyTexture,Resolve,Present,Viewport,Pipeline,States,Execute,Gate};
struct Record {
 uint64_t sequence,qpc;uint32_t event,thread;uint64_t object,device,args[11];
};
struct Header {
 uint32_t magic,version,recordBytes,headerBytes;
 volatile LONG status,error,reason,warning,attempts,dropped,written,queued;
 uint32_t pid,reserved[3];
 uint64_t frequency,startQpc,gateQpc,endQpc,fileBytes,hardBytes,warningBytes,durationMs;
};
static_assert(sizeof(Record)==128&&sizeof(Header)==128);
inline bool fits(uint64_t bytes,uint64_t extra,uint64_t limit){return bytes<=limit&&extra<=limit-bytes;}
class Trace {
 SRWLOCK guard=SRWLOCK_INIT;Record* ring=nullptr;HANDLE thread=nullptr;
 return_path::State* control=nullptr;Header* header=nullptr;
 std::atomic<uint32_t> head{0},tail{0};
 std::atomic<bool> accepting{false};wchar_t path[1024]{};
 std::atomic<uint32_t> active{0};
 static DWORD WINAPI run(void* value){return static_cast<Trace*>(value)->work();}
 DWORD work(){
  auto file=CreateFileW(path,GENERIC_WRITE,FILE_SHARE_READ,nullptr,CREATE_NEW,
    FILE_ATTRIBUTE_NORMAL,nullptr);
  if(file==INVALID_HANDLE_VALUE){return_path::write(header->error,1);return_path::write(header->status,4);accepting=false;return 1;}
  DWORD bytes=0;bool ok=WriteFile(file,header,sizeof(Header),&bytes,nullptr)&&bytes==sizeof(Header);
  uint64_t size=sizeof(Header);std::array<Record,256> batch{};
  return_path::write(header->status,ok?2:4);
  while(ok){
   const auto now=return_path::now();
   if(!header->gateQpc&&return_path::read(control->armed)){
    header->gateQpc=now;
   }
   if(return_path::read(control->stop))return_path::write(header->reason,3);
   if(header->gateQpc&&now-header->gateQpc>=header->frequency*header->durationMs/1000)
    return_path::write(header->reason,1);
   if(now-header->startQpc>header->frequency*285) return_path::write(header->reason,6);
   if(return_path::read(header->reason))accepting=false;
   unsigned n=0;
   auto next=tail.load(std::memory_order_relaxed);const auto end=head.load(std::memory_order_acquire);
   while(n<batch.size()&&next!=end)batch[n++]=ring[next++%Capacity];
   tail.store(next,std::memory_order_release);
   return_path::write(header->queued,static_cast<LONG>(end-next));
   if(n){
    // Fixed record aligned hard limit; never write a batch over budget.
    unsigned allowed=n;
    while(allowed&&!fits(size,uint64_t(allowed)*sizeof(Record),header->hardBytes))--allowed;
    if(allowed<n){return_path::write(header->reason,2);accepting=false;InterlockedExchangeAdd(&header->dropped,n-allowed);}
    const DWORD length=allowed*sizeof(Record);
    if(length){ok=WriteFile(file,batch.data(),length,&bytes,nullptr)&&bytes==length;size+=bytes;
     InterlockedExchangeAdd(&header->written,allowed);}
    header->fileBytes=size;if(size>=header->warningBytes)return_path::write(header->warning,1);
   }
   if(!accepting){
    if(active.load()){Sleep(0);continue;}
    // Drain already accepted records; hard-limit remainder is counted as loss.
    AcquireSRWLockExclusive(&guard);const auto remaining=head.load()-tail.load();ReleaseSRWLockExclusive(&guard);
    if(!remaining)break;
   }
   Sleep(n?0:2);
  }
  accepting=false;if(!ok){return_path::write(header->error,2);return_path::write(header->reason,4);}
  header->endQpc=return_path::now();header->fileBytes=size;
  Header final{};std::memcpy(&final,header,sizeof(final));final.status=ok?3:4;
  LARGE_INTEGER zero{};
  if(!SetFilePointerEx(file,zero,nullptr,FILE_BEGIN)||
     !WriteFile(file,&final,sizeof(Header),&bytes,nullptr)||bytes!=sizeof(Header))return_path::write(header->error,3);
  CloseHandle(file);return_path::write(header->status,return_path::read(header->error)?4:3);
  return return_path::read(header->error)?1:0;
 }
public:
 // Storage remains resident until process termination; no hot unload/free races.
 bool prepare(return_path::State* s,const wchar_t* output,uint64_t hard=HardBytes,uint64_t duration=90000){
  if(!s||!output||wcslen(output)>=1024||hard<sizeof(Header)+sizeof(Record)||hard>HardBytes||!duration||duration>90000)return false;
  control=s;header=reinterpret_cast<Header*>(reinterpret_cast<BYTE*>(s)+256);
  ZeroMemory(header,sizeof(Header));header->magic=Magic;header->version=Version;
  header->recordBytes=sizeof(Record);header->headerBytes=sizeof(Header);
  header->frequency=s->qpcFrequency;header->startQpc=return_path::now();header->hardBytes=hard;
  header->warningBytes=hard/2;header->durationMs=duration;header->pid=GetCurrentProcessId();
  wcscpy_s(path,output);ring=static_cast<Record*>(VirtualAlloc(nullptr,sizeof(Record)*Capacity,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
  if(!ring){return_path::write(header->error,5);return_path::write(header->status,4);return false;}
  accepting=true;return_path::write(header->status,1);thread=CreateThread(nullptr,0,run,this,0,nullptr);
  if(!thread){accepting=false;return_path::write(header->error,6);return_path::write(header->status,4);return false;}return true;
 }
 uint64_t emit(uint32_t event,uint64_t object,uint64_t device,const std::array<uint64_t,11>& args={},bool lifecycle=false){
  struct Scope {std::atomic<uint32_t>& n;Scope(std::atomic<uint32_t>& value):n(value){++n;}~Scope(){--n;}} scope(active);
  if(!accepting)return 0;
  // Resource lifecycle prelude starts before tactical gate; full detail afterward.
  if(!lifecycle&&!return_path::read(control->armed))return 0;
  InterlockedIncrement(&header->attempts);
  if(!TryAcquireSRWLockExclusive(&guard)){InterlockedIncrement(&header->dropped);return 0;}
  if(!accepting){InterlockedIncrement(&header->dropped);ReleaseSRWLockExclusive(&guard);return 0;}
  const auto next=head.load(std::memory_order_relaxed);
  if(next-tail.load(std::memory_order_acquire)==Capacity){InterlockedIncrement(&header->dropped);ReleaseSRWLockExclusive(&guard);return 0;}
  Record r{};r.sequence=uint64_t(next)+1;r.qpc=return_path::now();r.event=event;r.thread=GetCurrentThreadId();r.object=object;r.device=device;
  std::memcpy(r.args,args.data(),sizeof(r.args));ring[next%Capacity]=r;head.store(next+1,std::memory_order_release);
  ReleaseSRWLockExclusive(&guard);return r.sequence;
 }
};
}
