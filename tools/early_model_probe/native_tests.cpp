#include "early_runtime.h"
#include <iostream>
#include <float.h>
#include <xmmintrin.h>
using namespace early_model;
namespace {
unsigned checks=0;bool failed=false;
void check(bool ok,const char* what){++checks;if(!ok){std::cout<<"FAIL "<<what<<'\n';failed=true;}}
std::array<unsigned char,0x188> visual{},secondary{};std::array<unsigned char,0x3c> mesh{},secondMesh{};
std::array<std::array<unsigned char,0x100>,6> ships{};std::array<Word,18> sources{};
Targets calls;volatile LONG originals=0;bool nested=false,earlyCache=false;std::atomic<bool> throwParse{false};
HANDLE parseEntered=nullptr,parseResume=nullptr;std::atomic<bool> holdParse{false};
void put(void* p,Word offset,Word value){std::memcpy(static_cast<BYTE*>(p)+offset,&value,4);}
__declspec(noinline) Word __fastcall fakeBorn(void* p,void*){InterlockedIncrement(&originals);put(p,0,shipVt);put(p,0x88,0);return ptr(p);}
__declspec(noinline) Word __fastcall fakeRetire(void*,void*){InterlockedIncrement(&originals);return 0x1234FEDC;}
__declspec(noinline) Word __fastcall fakeVisualRetire(void*,void*){InterlockedIncrement(&originals);return 0x98765432;}
__declspec(noinline) Word __fastcall fakeParse(void* p,void*,Word text){
 InterlockedIncrement(&originals);if(throwParse)RaiseException(0xE0420075,0,0,nullptr);
 if(holdParse){SetEvent(parseEntered);WaitForSingleObject(parseResume,1500);}
 if(!strcmp(reinterpret_cast<char*>(text),"badparse"))return 0;
 const auto child=p==visual.data()?ptr(mesh.data()):ptr(secondMesh.data());put(p,0,visualVt);put(p,0x11C,1);put(p,0x154,0x34567890);put(p,0x158,ptr(sources.data()));put(p,0x15C,2);put(p,0x160,child);put(p,0x120,UINT32_MAX);put(p,0x124,0);put(p,0x178,0x3F800000);
 auto* m=reinterpret_cast<void*>(child);put(m,0,meshVt);put(m,8,3);put(m,0xC,0x11110000);put(m,0x10,1);put(m,0x14,0x22220000);put(m,0x20,0);
 if(earlyCache&&p==visual.data()){calls.load(ptr(const_cast<char*>("cached")));check(!visuals.current(ptr(p)).qualified,"cache return before enclosing parse is unqualified");}
 if(nested&&p==visual.data())calls.load(ptr(const_cast<char*>("nested")));
 SetLastError(309);return 1;
}
__declspec(noinline) Word __cdecl fakeLoad(Word text){
 InterlockedIncrement(&originals);const auto* s=reinterpret_cast<char*>(text);
 if(!strcmp(s,"allocation-fail"))return 0;
 if(!strcmp(s,"cached"))return ptr(visual.data());
 auto* p=!strcmp(s,"nested")?secondary.data():visual.data();
 if(!(calls.parse(p,text)&255)){calls.visualRetire(p);return 0;}
 // Simulate the native post-parse scaling step changing position storage.
 auto* m=p==visual.data()?mesh.data():secondMesh.data();put(m,0x20,0x11110000);put(m,0xC,0x33330000);
 return ptr(p);
}
__declspec(noinline) Word __fastcall fakeAttach(void* p,void*,Word v){InterlockedIncrement(&originals);put(p,0x88,v);return 0xAABBCCDD;}
__declspec(noinline) Word __fastcall fakeRequest(void* p,void*,Word text){InterlockedIncrement(&originals);const auto v=calls.load(text);calls.attach(p,v);SetLastError(412);return 0x2468ABCD;}
__declspec(noinline) Word __fastcall fakeMesh(void*,void*,Word manager,Word source,Word a,Word b){InterlockedIncrement(&originals);return manager^source^a^b;}
__declspec(noinline) Word __fastcall fakeRender(void* p,void*,Word manager){
 InterlockedIncrement(&originals);bool ok=true;const auto v=word(ptr(p)+0x88,ok),m=word(v+0x160,ok),source=word(v+0x158,ok);
 return m?calls.mesh(reinterpret_cast<void*>(m),manager,source,3,4):0;
}
Targets setup(){sources[0]=0x20;sources[5]=1;sources[7]=2;sources[9+5]=3;
 return {reinterpret_cast<One>(fakeRequest),fakeLoad,reinterpret_cast<One>(fakeParse),reinterpret_cast<One>(fakeAttach),reinterpret_cast<One>(fakeRender),reinterpret_cast<Four>(fakeMesh),reinterpret_cast<Zero>(fakeVisualRetire),reinterpret_cast<Zero>(fakeBorn),reinterpret_cast<Zero>(fakeRetire)};}
std::array<void*,9> addresses(Targets t){return {reinterpret_cast<void*>(t.request),reinterpret_cast<void*>(t.load),reinterpret_cast<void*>(t.parse),reinterpret_cast<void*>(t.attach),reinterpret_cast<void*>(t.render),reinterpret_cast<void*>(t.mesh),reinterpret_cast<void*>(t.visualRetire),reinterpret_cast<void*>(t.born),reinterpret_cast<void*>(t.retire)};}
std::array<std::array<BYTE,16>,9> before{};
void remember(){const auto a=addresses(calls);for(unsigned i=0;i<a.size();++i)std::memcpy(before[i].data(),a[i],16);}
void restored(){const auto a=addresses(calls);for(unsigned i=0;i<a.size();++i)check(!memcmp(before[i].data(),a[i],16),"byte exact hook restoration");}
bool exceptional(){__try{calls.request(ships[0].data(),ptr(const_cast<char*>("exception")));}__except(GetExceptionCode()==0xE0420075?EXCEPTION_EXECUTE_HANDLER:EXCEPTION_CONTINUE_SEARCH){return true;}return false;}
DWORD WINAPI worker(void*){return runtime.work(calls);}
DWORD WINAPI parallel(void* p){calls.born(p);calls.request(p,ptr(const_cast<char*>("cached")));calls.render(p,0x123456);calls.retire(p);return 0;}
DWORD WINAPI longLoad(void*){calls.load(ptr(const_cast<char*>("long.mod")));return 0;}
void exercise(bool negative){
 check(calls.born(ships[0].data())==ptr(ships[0].data()),"constructor EAX");
 const auto csr=_mm_getcsr();unsigned cw=0;_controlfp_s(&cw,0,0);
 nested=true;earlyCache=negative;check(calls.request(ships[0].data(),ptr(const_cast<char*>("fresh.mod")))==0x2468ABCD,"request EAX/thiscall stack");nested=false;earlyCache=false;
 check(GetLastError()==412,"LastError preserved");unsigned after=0;_controlfp_s(&after,0,0);check(cw==after&&csr==_mm_getcsr(),"FPU/SSE control preserved");
 check(calls.render(ships[0].data(),0x123456)==(0x123456^ptr(sources.data())^3^4),"mesh four-argument calling convention");
 check(owners.current(ptr(ships[0].data())).qualified,"observed owner constructor qualified");
 const auto asset=visuals.current(ptr(visual.data()));check(asset.qualified,"fresh parse qualified");
 check(calls.load(ptr(const_cast<char*>("cached")))==ptr(visual.data())&&visuals.current(ptr(visual.data())).epoch==asset.epoch,"cache hit retains asset epoch");
 const auto previous=owners.current(ptr(ships[0].data())).epoch;
 check(calls.retire(ships[0].data())==0x1234FEDC&&!owners.current(ptr(ships[0].data())).epoch,"owner retire");
 calls.born(ships[0].data());check(owners.current(ptr(ships[0].data())).epoch>previous,"owner pointer reuse fresh epoch");
 calls.request(ships[0].data(),ptr(const_cast<char*>("cached")));calls.render(ships[0].data(),0x123456);
 check(calls.load(ptr(const_cast<char*>("allocation-fail")))==0,"allocation failure preserved");
 calls.visualRetire(visual.data());check(!visuals.current(ptr(visual.data())).epoch,"visual retired before reuse");
 check(calls.load(ptr(const_cast<char*>("badparse")))==0,"parse failure preserved");
 calls.request(ships[0].data(),ptr(const_cast<char*>("fresh_BRK.mod")));calls.render(ships[0].data(),0x123456);
 check(visuals.current(ptr(visual.data())).epoch>asset.epoch,"visual pointer reuse fresh epoch");
 std::array<HANDLE,3> threads{};for(unsigned i=0;i<threads.size();++i)threads[i]=CreateThread(nullptr,0,parallel,ships[i+1].data(),0,nullptr);
 for(auto h:threads){check(h&&WaitForSingleObject(h,3000)==WAIT_OBJECT_0,"concurrent cached owners");if(h)CloseHandle(h);}
 if(negative){throwParse=true;check(exceptional(),"original SEH propagates");throwParse=false;check(!stack.depth&&!stack.excess&&!active.load(),"SEH scope counters unwind");}
 check(!stack.depth&&!stack.excess,"nested scope balanced");
 Record badName;name(badName,0);check((badName.flags&NameBad)!=0,"invalid bounded name is explicit");
 Record unsupported;unsupported.visual=ptr(visual.data());put(visual.data(),0x15C,257);snapshot(unsupported);put(visual.data(),0x15C,2);check((unsupported.flags&Unsupported)!=0,"oversize source count rejected without array walk");
}
}
extern "C" __declspec(dllexport) BOOL __cdecl EarlyFixtureConfig(Targets* t){calls=setup();*t=calls;remember();return TRUE;}
#pragma comment(linker,"/EXPORT:EarlyFixtureConfig=_EarlyFixtureConfig")
int wmain(int argc,wchar_t** argv){
 wchar_t fixture[4]{};const bool injected=GetEnvironmentVariableW(L"SFC_EARLY_FIXTURE",fixture,4)==1&&fixture[0]==L'1';
 if(injected){wchar_t session[128]{};if(!GetEnvironmentVariableW(L"SFC_REMIX_RETURN_SESSION",session,128))return 2;return_path::Mapping channel(false,session);
  const auto until=GetTickCount64()+5000;while(!return_path::read(channel.state->ready)&&!return_path::read(channel.state->error)&&GetTickCount64()<until)Sleep(1);
  check(channel.state->ready&&!channel.state->error,"injected hook worker ready");if(failed)return 3;
  // Fixture-side bookkeeping is distinct from the injected DLL's registry.
  const auto expected=0x123456^ptr(sources.data())^3^4;
  calls.born(ships[0].data());nested=true;check(calls.request(ships[0].data(),ptr(const_cast<char*>("fresh.mod")))==0x2468ABCD,"injected fresh/nested request");nested=false;
  check(calls.render(ships[0].data(),0x123456)==expected,"injected selected child");
  calls.request(ships[0].data(),ptr(const_cast<char*>("cached")));calls.render(ships[0].data(),0x123456);
  calls.retire(ships[0].data());calls.born(ships[0].data());calls.request(ships[0].data(),ptr(const_cast<char*>("cached")));calls.render(ships[0].data(),0x123456);
  calls.load(ptr(const_cast<char*>("allocation-fail")));calls.load(ptr(const_cast<char*>("badparse")));calls.request(ships[0].data(),ptr(const_cast<char*>("fresh_BRK.mod")));calls.render(ships[0].data(),0x123456);
  calls.retire(ships[0].data());Sleep(100);return_path::write(channel.state->stop,1);
  const auto stop=GetTickCount64()+5000;while(!return_path::read(*reinterpret_cast<volatile LONG*>(channel.state->padding.data()))&&GetTickCount64()<stop)Sleep(1);
  check(return_path::read(*reinterpret_cast<volatile LONG*>(channel.state->padding.data()))&&!channel.state->error,"injected worker stopped/file closed");restored();
  std::cout<<"Early injected "<<(failed?"FAIL":"PASS")<<" checks="<<checks<<'\n';return failed?1:0;
 }
 if(argc!=2)return 2;
 Book b;auto first=b.birth(100,true);check(first.epoch&&b.current(100).epoch==first.epoch,"book birth");check(b.first(100,first.epoch,200)&&!b.first(100,first.epoch,200),"first draw only once");b.rebound(100);check(b.first(100,first.epoch,200),"attachment resets first draw");b.retire(100);check(b.birth(100,true).epoch>first.epoch,"book pointer reuse");
 Stack s;for(unsigned i=0;i<8;++i)check(s.push({1,2,i+1,Load,0}),"bounded nested push");check(!s.push({})&&!s.current().owner,"scope overflow cannot inherit owner");for(unsigned i=0;i<9;++i)s.pop();check(!s.depth&&!s.excess,"overflow unwinds");
 check(bounds(Hard-512,512)&&!bounds(Hard-511,512)&&!bounds(UINT64_MAX,512),"wire cap arithmetic");
 check(mainline(5,5,1,2,2)&&!mainline(4,5,1,2,2)&&!mainline(5,5,1,2,3),"caller/source qualification");
 calls=setup();remember();fixtureMode=true;return_path::Mapping channel(true);check(runtime.prepare(channel.state,argv[1]),"preallocated private channel/ring");sink=collect;
 const auto thread=CreateThread(nullptr,0,worker,nullptr,0,nullptr);check(thread!=nullptr,"worker created");const auto until=GetTickCount64()+5000;
 while(!return_path::read(channel.state->ready)&&!return_path::read(channel.state->error)&&GetTickCount64()<until)Sleep(1);
 check(channel.state->ready&&!channel.state->error,"actual nine-hook transaction ready");if(failed)return 4;
 exercise(true);Sleep(100);check(SuspendThread(thread)!=static_cast<DWORD>(-1),"pause standalone writer");const auto begin=GetTickCount64();
 for(unsigned i=0;i<2500;++i)calls.load(ptr(const_cast<char*>("cached")));
 check(runtime.header->dropped>0&&GetTickCount64()-begin<2000,"slow receiver drops without delaying original");ResumeThread(thread);
 Sleep(100);parseEntered=CreateEventW(nullptr,TRUE,FALSE,nullptr);parseResume=CreateEventW(nullptr,TRUE,FALSE,nullptr);holdParse=true;
 const auto loading=CreateThread(nullptr,0,longLoad,nullptr,0,nullptr);check(loading&&WaitForSingleObject(parseEntered,2000)==WAIT_OBJECT_0,"original load in flight before stop");
 return_path::write(channel.state->stop,1);Sleep(50);check(!return_path::read(*reinterpret_cast<volatile LONG*>(channel.state->padding.data())),"worker does not close storage while callback active");
 SetEvent(parseResume);check(WaitForSingleObject(loading,3000)==WAIT_OBJECT_0,"original in-flight load completes during stop");CloseHandle(loading);CloseHandle(parseEntered);CloseHandle(parseResume);holdParse=false;
 check(WaitForSingleObject(thread,5000)==WAIT_OBJECT_0,"stop detaches/drains");DWORD code=1;GetExitCodeThread(thread,&code);CloseHandle(thread);
 check(!code&&!runtime.header->error&&!runtime.hooked&&!active.load(),"clean worker and callbacks");restored();
 std::cout<<"Early native "<<(failed?"FAIL":"PASS")<<" checks="<<checks<<" records="<<runtime.header->written<<" drops="<<runtime.header->dropped<<'\n';return failed?1:0;
}
