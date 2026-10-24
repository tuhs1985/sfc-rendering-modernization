// Optional, external-worker-only startup measurements. No SFC callback work.
#pragma once
#include <psapi.h>
#pragma comment(lib,"psapi.lib")
struct StartupProfile {
 struct Point {const char* label=nullptr;uint64_t qpc=0,privateBytes=0,workingSet=0,commit=0,limit=0;unsigned index=0;};
 std::array<Point,128> points{};size_t used=0;bool enabled=false;uint64_t frequency=0;
 StartupProfile(){wchar_t value[2]{};enabled=GetEnvironmentVariableW(L"SFC_D3D9_STARTUP_PROFILE",value,2)==1&&value[0]==L'1';
  LARGE_INTEGER f{};QueryPerformanceFrequency(&f);frequency=static_cast<uint64_t>(f.QuadPart);mark("host_entry");}
 void mark(const char* label,unsigned index=0,bool memory=true){
  if(!enabled||used==points.size())return;
  auto& p=points[used++];p.label=label;p.index=index;LARGE_INTEGER q{};QueryPerformanceCounter(&q);p.qpc=static_cast<uint64_t>(q.QuadPart);
  if(memory){PROCESS_MEMORY_COUNTERS_EX m{};m.cb=sizeof(m);if(GetProcessMemoryInfo(GetCurrentProcess(),reinterpret_cast<PROCESS_MEMORY_COUNTERS*>(&m),sizeof(m))){p.privateBytes=m.PrivateUsage;p.workingSet=m.WorkingSetSize;}
   PERFORMANCE_INFORMATION s{};s.cb=sizeof(s);if(GetPerformanceInfo(&s,sizeof(s))){p.commit=uint64_t(s.CommitTotal)*s.PageSize;p.limit=uint64_t(s.CommitLimit)*s.PageSize;}}
 }
 ~StartupProfile(){if(enabled)for(size_t i=0;i<used;++i){const auto& p=points[i];std::cout<<"STARTUP_PROFILE stage="<<p.label<<" index="<<p.index<<" qpc="<<p.qpc<<" frequency="<<frequency<<" private_bytes="<<p.privateBytes<<" working_set="<<p.workingSet<<" system_commit="<<p.commit<<" commit_limit="<<p.limit<<'\n';}}
};
