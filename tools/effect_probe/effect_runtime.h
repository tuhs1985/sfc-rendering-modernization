#pragma once
#include <string>
#include "effect_native.h"
#include "../remix_runtime/return_wire.h"
namespace effect_probe {
constexpr Word Magic=0x45524631,Hard=16*1024*1024,Capacity=8192;
struct Record {uint64_t sequence,qpc;Word kind,thread;uint64_t object,manager,args[11];};
struct Header {
 Word magic,version,recordBytes,headerBytes;volatile LONG status,error,reason,warning,attempts,dropped,written,queued;
 Word pid,reserved[3];uint64_t frequency,startQpc,gateQpc,endQpc,fileBytes,hardBytes,warningBytes,durationMs;
};
static_assert(sizeof(Header)==128&&sizeof(Record)==128);
inline bool bounds(uint64_t size,uint64_t extra,uint64_t hard=Hard){return size<=hard&&extra<=hard-size;}
class Runtime {
 SRWLOCK guard=SRWLOCK_INIT;Record* ring=nullptr;
 std::atomic<unsigned> head{0},tail{0};std::atomic<bool> accepting{false};
 std::array<std::array<Word,6>,4096> resolved{};
 std::array<std::array<char,256>,4096> resolvedNames{};
public:
 return_path::State* control=nullptr;Header* header=nullptr;std::wstring path;
 bool hooked=false;Targets original{};
 bool prepare(return_path::State* state,const wchar_t* output){
  if(!state||!return_path::valid(*state)||!output||wcslen(output)>=1024)return false;
  control=state;header=reinterpret_cast<Header*>(reinterpret_cast<BYTE*>(state)+256);path=output;
  ZeroMemory(header,sizeof(Header));header->magic=Magic;header->version=1;header->recordBytes=header->headerBytes=128;
  header->pid=GetCurrentProcessId();header->frequency=state->qpcFrequency;header->startQpc=return_path::now();
  header->hardBytes=Hard;header->warningBytes=Hard/2;header->durationMs=90000;header->status=1;
  ring=static_cast<Record*>(VirtualAlloc(nullptr,Capacity*sizeof(Record),MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));
  return ring!=nullptr;
 }
 void emit(Kind kind,Word object,Word manager,const std::array<uint64_t,11>& args){
  if(!accepting)return;
  if(kind!=Born&&kind!=Retired&&kind!=Stopped&&kind!=Statistics&&!return_path::read(control->armed))return;
  InterlockedIncrement(&header->attempts);
  if(!TryAcquireSRWLockExclusive(&guard)){InterlockedIncrement(&header->dropped);return;}
  const auto n=head.load(std::memory_order_relaxed);
  if(n-tail.load(std::memory_order_acquire)==Capacity){InterlockedIncrement(&header->dropped);ReleaseSRWLockExclusive(&guard);return;}
  Record r{};r.sequence=uint64_t(n)+1;r.qpc=return_path::now();r.kind=kind;r.thread=GetCurrentThreadId();r.object=object;r.manager=manager;
  std::memcpy(r.args,args.data(),sizeof(r.args));ring[n%Capacity]=r;head.store(n+1,std::memory_order_release);ReleaseSRWLockExclusive(&guard);
 }
 void resolve(const Record& r){
  const auto id=static_cast<Word>(r.args[2]),reg=static_cast<Word>(r.args[3]),obj=static_cast<Word>(r.args[4]);
  const auto entry=static_cast<Word>(r.args[5]),surface=static_cast<Word>(r.args[6]);
  if(!id||id>4096||!reg||!obj||!entry||!surface)return;
  std::array<char,256> name{};bool valid=false;unsigned length=0;Word hash=2166136261u;
  for(unsigned i=0;i<name.size();++i){if(!read(obj+8+i,&name[i],1))break;if(!name[i]){valid=i!=0;length=i;break;}if(name[i]<32||name[i]>126)break;hash=(hash^static_cast<unsigned char>(name[i]))*16777619u;}
  if(word(registryAddress)!=reg||word(reg)!=0x00795C54||word(reg+12+(id-1)*20)!=obj||word(static_cast<Word>(r.manager)+0x3F60+(id-1)*4)!=entry||word(entry+4)!=surface)valid=false;
  std::array<char,256> again{};if(!valid||!read(obj+8,again.data(),length+1)||again!=name)valid=false;
  // Exact current snapshot/recheck, not proof of unobserved allocation epochs.
  if(!valid){emit(Fault,static_cast<Word>(r.object),static_cast<Word>(r.manager),{r.sequence,id,1});return;}
  if(word(registryAddress)!=reg||word(reg+12+(id-1)*20)!=obj||word(static_cast<Word>(r.manager)+0x3F60+(id-1)*4)!=entry||word(entry+4)!=surface){emit(Fault,static_cast<Word>(r.object),static_cast<Word>(r.manager),{r.sequence,id,1});return;}
  const std::array<Word,6> key{static_cast<Word>(r.manager),reg,obj,entry,surface,hash};if(resolved[id-1]==key&&resolvedNames[id-1]==name)return;resolved[id-1]=key;resolvedNames[id-1]=name;
  for(unsigned chunk=0;chunk<4;++chunk){std::array<uint64_t,11> args{r.sequence,id,chunk};std::memcpy(args.data()+3,name.data()+64*chunk,64);emit(Name,static_cast<Word>(r.object),static_cast<Word>(r.manager),args);}
 }
 LONG stop(){
  observing=false;LONG error=hooked?transaction(false):NO_ERROR;
  if(!error)hooked=false;
  const auto until=GetTickCount64()+2000;while(active.load()&&GetTickCount64()<until)Sleep(1);
  if(active.load()&&!error)error=WAIT_TIMEOUT;
  emit(Stopped,0,0,{static_cast<Word>(error),active.load()});
  emit(Statistics,0,0,{faults.load(),busy.load(),unscoped.load(),registry.serial,identityUncertain.load()});
  if(error){header->error=static_cast<LONG>(error);return_path::write(control->error,120);}
  return error;
 }
 DWORD work(Targets targets,bool install=true){
  auto file=CreateFileW(path.c_str(),GENERIC_WRITE,FILE_SHARE_READ,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
  if(file==INVALID_HANDLE_VALUE){header->error=1;header->status=4;return_path::write(control->error,121);return 1;}
  DWORD bytes=0;uint64_t size=128;bool ok=WriteFile(file,header,128,&bytes,nullptr)&&bytes==128;
  native=original=targets;accepting=true;
  LONG error=ok&&install?transaction(true):ok?NO_ERROR:ERROR_WRITE_FAULT;
  hooked=install&&!error;observing=!error;header->error=error;header->status=error?4:2;
  if(error){return_path::write(control->error,122);accepting=false;}
  else return_path::write(control->ready,1);
  bool stopping=error!=0;
  while(ok){
   const auto now=return_path::now();if(!header->gateQpc&&return_path::read(control->armed))header->gateQpc=now;
   if(return_path::read(control->stop))header->reason=3;
   if(header->gateQpc&&now-header->gateQpc>=header->frequency*header->durationMs/1000)header->reason=1;
   if(now-header->startQpc>285*header->frequency)header->reason=6;
   if((header->reason||!ok)&&!stopping){stopping=true;stop();accepting=false;}
   auto n=tail.load(std::memory_order_relaxed);const auto end=head.load(std::memory_order_acquire);
   unsigned batch=0;
   while(n!=end&&batch++<256){
    const auto r=ring[n%Capacity];
    if(!bounds(size,128)){header->reason=2;InterlockedIncrement(&header->dropped);}
    else{ok=WriteFile(file,&r,128,&bytes,nullptr)&&bytes==128;if(!ok)break;size+=128;++header->written;if(!stopping&&r.kind==Resource)resolve(r);}
    ++n;
   }
   tail.store(n,std::memory_order_release);header->queued=static_cast<LONG>(head.load()-n);header->fileBytes=size;
   if(size>=Hard/2)header->warning=1;
   if(stopping&&n==head.load())break;
   if(!ok){header->error=ERROR_WRITE_FAULT;break;}Sleep(2);
  }
  if(!stopping){stop();accepting=false;}
  return_path::write(control->ready,0);header->endQpc=return_path::now();header->status=header->error?4:3;
  LARGE_INTEGER zero{};ok=SetFilePointerEx(file,zero,nullptr,FILE_BEGIN)&&WriteFile(file,header,128,&bytes,nullptr)&&bytes==128&&ok;
  FlushFileBuffers(file);CloseHandle(file);
  return_path::write(*reinterpret_cast<volatile LONG*>(control->padding.data()),1); // effects-only worker/file closed extension
  return ok&&!header->error?0:1;
 }
};
inline Runtime runtime;
inline void collect(Kind kind,Word object,Word manager,const std::array<uint64_t,11>& args){runtime.emit(kind,object,manager,args);}
}
