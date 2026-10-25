#pragma once
#include <string>
#include "early_native.h"
#include "../remix_runtime/return_wire.h"
namespace early_model {
struct Header {
 Word magic=Magic,version=1,recordBytes=512,headerBytes=128;
 volatile LONG status=0,error=0,reason=0,warning=0,attempts=0,dropped=0,written=0,queued=0;
 Word pid=0,reserved[3]{};uint64_t frequency=0,startQpc=0,gateQpc=0,endQpc=0,fileBytes=0,hardBytes=Hard,warningBytes=Hard/2,durationMs=90000;
};
static_assert(sizeof(Header)==128);
class Runtime {
 SRWLOCK guard=SRWLOCK_INIT;Record* ring=nullptr;
 std::atomic<unsigned> head{0},tail{0};std::atomic<bool> accepting{false};
 std::array<void*,9> entries{};std::array<std::array<BYTE,16>,9> originalBytes{};
public:
 return_path::State* control=nullptr;Header* header=nullptr;std::wstring path;bool hooked=false;
 bool prepare(return_path::State* state,const wchar_t* output){
  if(!state||!return_path::valid(*state)||!output||wcslen(output)>=1024)return false;
  control=state;header=reinterpret_cast<Header*>(reinterpret_cast<BYTE*>(state)+256);path=output;
  *header=Header{};header->pid=GetCurrentProcessId();header->frequency=state->qpcFrequency;header->startQpc=ticks();header->status=1;
  ring=static_cast<Record*>(VirtualAlloc(nullptr,Capacity*sizeof(Record),MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));return ring!=nullptr;
 }
 void emitRecord(Record r){
  if(!accepting)return;InterlockedIncrement(&header->attempts);
  if(!TryAcquireSRWLockExclusive(&guard)){InterlockedIncrement(&header->dropped);return;}
  const auto n=head.load(std::memory_order_relaxed);
  const auto limit=(r.kind==Stopped||r.kind==Statistics)?Capacity:Capacity-2;
  if(n-tail.load(std::memory_order_acquire)>=limit){InterlockedIncrement(&header->dropped);ReleaseSRWLockExclusive(&guard);return;}
  r.sequence=uint64_t(n)+1;ring[n%Capacity]=r;head.store(n+1,std::memory_order_release);ReleaseSRWLockExclusive(&guard);
 }
 LONG stop(){
  observing=false;const LONG error=hooked?transaction(false):NO_ERROR;if(!error)hooked=false;
  const auto until=GetTickCount64()+2000;while(active.load()&&GetTickCount64()<until)Sleep(1);
  LONG failure=error?error:active.load()?WAIT_TIMEOUT:NO_ERROR;Word restored=0;
  if(!error)for(unsigned i=0;i<entries.size();++i){std::array<BYTE,16> bytes{};if(read(ptr(entries[i]),bytes.data(),16)&&bytes==originalBytes[i])++restored;}
  if(!failure&&restored!=9)failure=ERROR_INVALID_DATA;
  auto s=record(Statistics);s.data[0]=faults.load();s.data[1]=busy.load();s.data[2]=uncertain.load();s.data[3]=owners.serial;s.data[4]=visuals.serial;
  s.token=callbackTicks.load();emitRecord(s);auto end=record(Stopped);end.data[0]=static_cast<Word>(failure);end.data[1]=active.load();end.data[2]=restored;end.data[3]=hooked;emitRecord(end);
  if(failure){header->error=failure;return_path::write(control->error,220);}return failure;
 }
 DWORD work(Targets targets){
  const auto file=CreateFileW(path.c_str(),GENERIC_WRITE,FILE_SHARE_READ,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
  if(file==INVALID_HANDLE_VALUE){header->error=ERROR_OPEN_FAILED;header->status=4;return_path::write(control->error,221);return 1;}
  DWORD nbytes=0;uint64_t size=128;bool ok=WriteFile(file,header,128,&nbytes,nullptr)&&nbytes==128;
  native=targets;entries={reinterpret_cast<void*>(targets.request),reinterpret_cast<void*>(targets.load),reinterpret_cast<void*>(targets.parse),reinterpret_cast<void*>(targets.attach),reinterpret_cast<void*>(targets.render),reinterpret_cast<void*>(targets.mesh),reinterpret_cast<void*>(targets.visualRetire),reinterpret_cast<void*>(targets.born),reinterpret_cast<void*>(targets.retire)};
  for(unsigned i=0;i<entries.size();++i)if(!read(ptr(entries[i]),originalBytes[i].data(),16))ok=false;
  accepting=true;const LONG error=ok?transaction(true):ERROR_WRITE_FAULT;hooked=!error;header->error=error;header->status=error?4:2;
  observing=!error;if(error){accepting=false;return_path::write(control->error,222);}else return_path::write(control->ready,1);
  bool stopping=error!=0;
  while(ok){
   const auto now=ticks();if(return_path::read(control->stop))header->reason=3;
   if(header->gateQpc&&now-header->gateQpc>=header->frequency*90)header->reason=1;
   if(now-header->startQpc>header->frequency*285)header->reason=6;
   if(header->reason&&!stopping){stopping=true;stop();accepting=false;}
   auto n=tail.load(std::memory_order_relaxed);const auto end=head.load(std::memory_order_acquire);unsigned batch=0;
   while(n!=end&&batch++<128){const auto r=ring[n%Capacity];
    if(r.kind==Gate&&!header->gateQpc){header->gateQpc=r.qpc;return_path::write(control->armed,1);}
    const bool terminal=r.kind==Stopped||r.kind==Statistics;
    if(!bounds(size,sizeof(Record)+(terminal?0:2*sizeof(Record)))){header->reason=2;InterlockedIncrement(&header->dropped);}
    else {ok=WriteFile(file,&r,sizeof(r),&nbytes,nullptr)&&nbytes==sizeof(r);if(!ok)break;size+=sizeof(r);++header->written;}
    ++n;
   }
   tail.store(n,std::memory_order_release);header->queued=static_cast<LONG>(head.load()-n);header->fileBytes=size;if(size>=Hard/2)header->warning=1;
   if(stopping&&n==head.load())break;if(!ok){header->error=ERROR_WRITE_FAULT;break;}Sleep(2);
  }
  if(!stopping){stop();accepting=false;}
  return_path::write(control->ready,0);header->endQpc=ticks();header->status=header->error?4:3;
  LARGE_INTEGER zero{};ok=SetFilePointerEx(file,zero,nullptr,FILE_BEGIN)&&WriteFile(file,header,128,&nbytes,nullptr)&&nbytes==128&&ok;
  FlushFileBuffers(file);CloseHandle(file);return_path::write(*reinterpret_cast<volatile LONG*>(control->padding.data()),1);
  return ok&&!header->error?0:1;
 }
};
inline Runtime runtime;
inline void collect(Record r){runtime.emitRecord(r);}
}
