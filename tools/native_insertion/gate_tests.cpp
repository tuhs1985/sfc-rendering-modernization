#include "gate_wait.h"
#include <iostream>
#include <thread>
#include <atomic>
#include <vector>
#include <memory>
using namespace native_gate;
static unsigned checks=0;
static void test(bool b){++checks;if(!b){std::cerr<<"Gate check "<<checks<<" failed\n";std::exit(1);}}
static Ticket ticket(Store& s,DWORD frame){begin(s,frame,GetCurrentThreadId());Ticket t{};
 memcpy(t.session,s.header.session,16);t.pid=s.header.pid;t.thread=GetCurrentThreadId();t.frame=frame;t.owner=7;t.revision=4;t.model=10;t.source=11;t.manager=12;t.count=1;t.primary=13;
 t.generation=s.header.generation;t.sequence=frame;t.hash=123;t.frameStart=s.header.frameStart;t.offered=now();t.deadline=deadline(s.header,t.frameStart);return t;}
int main(){
 auto s=std::make_unique<Store>();DWORD session[]{1,2,3,4};initialize(*s,session,GetCurrentProcessId(),Policy::Strict);
 Events e;e.create(session);HANDLE process=CreateEventW(nullptr,TRUE,FALSE,nullptr);test(process!=nullptr);
 test(valid(s->header,session,GetCurrentProcessId()));auto t=ticket(*s,1);test(valid(t,s->header));
 test(t.deadline==t.frameStart+(s->header.frequency+59)/60);
 auto result=acquire(t,*s,e,process,[]{return true;});test(result==Result::Acquired&&s->header.active==0&&s->header.maxActive==1);
 auto bad=t;++bad.revision;bad.hash=0;test(acquire(bad,*s,e,process,[]{return true;})==Result::Invalid);
 t=ticket(*s,2);t.frameStart-=s->header.frequency;t.deadline=deadline(s->header,t.frameStart);t.offered=t.frameStart;
 test(acquire(t,*s,e,process,[]{return true;})==Result::Timeout);
 t=ticket(*s,3);std::atomic<bool> available{false};
 std::thread producer([&]{Sleep(3);available.store(true,std::memory_order_release);SetEvent(e.ready);});
 result=acquire(t,*s,e,process,[&]{return available.load(std::memory_order_acquire);});producer.join();test(result==Result::Acquired);
 t=ticket(*s,4);std::thread stopping([&]{Sleep(2);SetEvent(e.stop);});
 result=acquire(t,*s,e,process,[]{return false;});stopping.join();test(result==Result::Stopped);ResetEvent(e.stop);
 t=ticket(*s,5);SetEvent(process);test(acquire(t,*s,e,process,[]{return false;})==Result::Disconnected);ResetEvent(process);
 // A stream of stale wakeups cannot extend this frame's fixed deadline.
 t=ticket(*s,6);std::atomic<bool> done{false};std::thread spurious([&]{while(!done.load()){SetEvent(e.ready);Sleep(1);}});
 const auto began=now();result=acquire(t,*s,e,process,[]{return false;});done=true;spurious.join();
 test(result==Result::Timeout&&now()-began<s->header.frequency/5);
 t=ticket(*s,7);std::thread recycled([&]{Sleep(2);InterlockedIncrement(reinterpret_cast<volatile LONG*>(&s->header.generation));SetEvent(e.ready);});
 result=acquire(t,*s,e,process,[]{return false;});recycled.join();test(result==Result::Invalid&&s->header.active==0);
 // Deterministic deadline arithmetic/replay:600 source frames per policy, with
 // identical ready/continuation costs and no backlog hidden by resetting time.
 for(Policy p:{Policy::Strict,Policy::ExtraFrame}){
  initialize(*s,session,GetCurrentProcessId(),p);unsigned misses=0;uint64_t lastPresent=0,maxBacklog=0;
  for(unsigned frame=1;frame<=600;++frame){
   const uint64_t nominal=uint64_t(frame)*16667,start=(std::max)(nominal,lastPresent),ready=start+((frame%37)==0?24000:((frame%19)==0?18000:10000));
   Header model{};model.frequency=1000000;model.policy=DWORD(p);
   const auto limit=deadline(model,start);const bool late=ready>=limit;misses+=late;
   const auto finish=(late?limit:ready)+1500;maxBacklog=(std::max)(maxBacklog,start-nominal);
   lastPresent=finish;test(limit-start==(p==Policy::Strict?16667u:33334u));
  }
  test(misses==(p==Policy::Strict?47u:0u)&&maxBacklog>0&&lastPresent<601ull*16667);
  std::cout<<"POLICY_ARITHMETIC policy="<<DWORD(p)<<" misses="<<misses<<" maximum_start_drift_us="<<maxBacklog<<" final_backlog=0 synthetic_only=1\n";
 }
 // Explicit60Hz budgets:late samples are rejected by Strict,admitted by ExtraFrame.
 Header h{};h.frequency=1000000;h.policy=1;test(deadline(h,0)==16667);h.policy=2;test(deadline(h,0)==33334);
 CloseHandle(process);std::cout<<"Native gate core PASS "<<checks<<" checks;event wait deadline stop disconnect and600frame policy arithmetic\n";
}
