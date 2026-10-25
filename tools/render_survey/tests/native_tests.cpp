#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <atomic>
#include <cstring>
#include <string>
#include <iostream>
#include "../survey_trace.h"
namespace survey_events {inline survey_trace::Trace trace;}
#include "../survey_native.h"
#include "../survey_native_fixture.h"
static bool exceptional(){
 __try{const auto setter=reinterpret_cast<survey_native::Set>(&survey_native_fixture::set);setter(survey_native_fixture::manager.data(),63,0);return false;}
 __except(GetExceptionCode()==0xE0420042?EXCEPTION_EXECUTE_HANDLER:EXCEPTION_CONTINUE_SEARCH){return true;}
}
int wmain(){
 using namespace survey_native;unsigned checks=0;
 auto check=[&](bool ok){++checks;if(!ok)throw std::runtime_error("native survey check");};
 return_path::Mapping mapping(true);auto& s=*mapping.state;
 auto* h=reinterpret_cast<survey_trace::Header*>(reinterpret_cast<BYTE*>(&s)+256);
 const auto path=std::wstring(L"native-tests-")+std::to_wstring(GetCurrentProcessId())+L".bin";
 check(survey_events::trace.prepare(&s,path.c_str(),1024*1024,1000));
 auto until=GetTickCount64()+3000;while(h->status==1&&GetTickCount64()<until)Sleep(1);check(h->status==2);
 targets=survey_native_fixture::setup();
 std::array<void*,4> ptrs{reinterpret_cast<void*>(targets.set),reinterpret_cast<void*>(targets.enable),reinterpret_cast<void*>(targets.gate),reinterpret_cast<void*>(targets.dispatch)};
 std::array<std::array<BYTE,12>,4> before{};for(unsigned i=0;i<4;++i)memcpy(before[i].data(),ptrs[i],12);
 check(transaction(true)==NO_ERROR);enabled=true;
 for(unsigned i=0;i<100;++i)check(survey_native_fixture::tick(i));
 check(faults==0&&busy==0&&overflow==0);check(tokens>=400);
 check(exceptional());check(active==0);check(survey_native_fixture::tick(100));
 const auto manager=reinterpret_cast<Word>(survey_native_fixture::manager.data());
 const auto error=GetLastError();light(manager,64,0,1);check(faults==0&&GetLastError()==error);
 light(1,0,0,1);check(faults>0); // explicit invalid snapshot, original path unaffected
 check(survey_native_fixture::tick(101));
 survey_native_fixture::b[1]=survey_native_fixture::head;
 check(survey_native_fixture::tick(102));check(overflow==1); // cycle terminates, original dispatch continues
 survey_native_fixture::b[1]=0;
 enabled=false;check(transaction(false)==NO_ERROR);while(active.load())Sleep(0);
 for(unsigned i=0;i<4;++i)check(memcmp(before[i].data(),ptrs[i],12)==0);
 return_path::write(s.stop,1);until=GetTickCount64()+3000;while(h->status<3&&GetTickCount64()<until)Sleep(1);
 check(h->status==3&&h->error==0&&h->dropped==0);
 std::cout<<"Survey native light/census PASS "<<checks<<" checks;four hooks restored;invalid observation was expected\n";
}
