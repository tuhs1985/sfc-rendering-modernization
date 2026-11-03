// Default-off external renderer diagnostics. No game callbacks or file opens.
#pragma once
#include <array>
#include <exception>
#include <iostream>
namespace slow_completion {
struct Record {uint64_t id=0,begin=0,total=0,query=0,queryMax=0,service=0,serviceMax=0,pause=0,calls=0;DWORD frame=0;bool failed=false;};
struct Recorder {
 bool enabled=false;uint64_t frequency=1,next=0,dropped=0;size_t used=0;std::array<Record,64> records{};
 Recorder(){wchar_t flag[2]{};enabled=GetEnvironmentVariableW(L"SFC_D3D9_SLOW_COMPLETION",flag,2)==1&&flag[0]==L'1';LARGE_INTEGER f{};QueryPerformanceFrequency(&f);frequency=uint64_t(f.QuadPart);}
 uint64_t clock()const{if(!enabled)return 0;LARGE_INTEGER t{};QueryPerformanceCounter(&t);return uint64_t(t.QuadPart);}
 void retain(const Record& r){if(!enabled||(!r.failed&&r.total<frequency/10))return;if(used<records.size())records[used++]=r;else ++dropped;}
 void flush(std::ostream& out=std::cout){if(!enabled)return;for(size_t i=0;i<used;++i){const auto& r=records[i];
  out<<"SLOW_COMPLETION id="<<r.id<<" source_frame="<<r.frame<<" begin_qpc="<<r.begin<<" frequency="<<frequency<<" failed="<<r.failed
   <<" total_us="<<r.total*1000000/frequency<<" query_us="<<r.query*1000000/frequency<<" query_max_us="<<r.queryMax*1000000/frequency
   <<" service_us="<<r.service*1000000/frequency<<" service_max_us="<<r.serviceMax*1000000/frequency<<" pause_us="<<r.pause*1000000/frequency<<" polls="<<r.calls<<'\n';}
  if(dropped)out<<"SLOW_COMPLETION_DROPPED count="<<dropped<<'\n';used=0;dropped=0;
 }
};
inline Recorder& recorder(){static thread_local Recorder value;return value;}
struct Scope {
 Recorder& owner;Record value{};int exceptions=0;
 explicit Scope(DWORD frame):owner(recorder()){if(owner.enabled){value.frame=frame;value.id=++owner.next;value.begin=owner.clock();exceptions=std::uncaught_exceptions();}}
 uint64_t clock()const{return owner.clock();}
 void query(uint64_t before){if(owner.enabled){const auto elapsed=clock()-before;value.query+=elapsed;value.queryMax=(std::max)(value.queryMax,elapsed);++value.calls;}}
 void service(uint64_t before){if(owner.enabled){const auto elapsed=clock()-before;value.service+=elapsed;value.serviceMax=(std::max)(value.serviceMax,elapsed);}}
 void pause(uint64_t before){if(owner.enabled)value.pause+=clock()-before;}
 ~Scope(){if(owner.enabled){value.total=clock()-value.begin;value.failed=std::uncaught_exceptions()>exceptions;owner.retain(value);}}
};
}
