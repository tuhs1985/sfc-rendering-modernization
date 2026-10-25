#include "effect_runtime.h"
#include <iostream>
#include <float.h>
#include <xmmintrin.h>
using namespace effect_probe;
namespace {
unsigned checks=0;bool failed=false;
void check(bool v,const char* name){++checks;if(!v){std::cout<<"FAIL "<<name<<'\n';failed=true;}}
alignas(16) std::array<unsigned char,0x8000> manager{};
std::array<unsigned char,0x354> object{},other{};
std::array<unsigned char,82000> resources{};
std::array<unsigned char,264> image{};std::array<Word,2> entry{};Word registryPointer=0;
Targets calls;volatile LONG originals=0;bool nested=false,mismatch=false,raiseException=false;
Word ptr(void* p){return reinterpret_cast<Word>(p);}
void put(void* p,unsigned offset,Word value){std::memcpy(static_cast<BYTE*>(p)+offset,&value,4);}
__declspec(noinline) Word __fastcall fakeBorn(void* p,void*){InterlockedIncrement(&originals);put(p,0,0x11111111);return ptr(p);}
__declspec(noinline) Word __fastcall fakeRetire(void*,void*){InterlockedIncrement(&originals);return 0x1234FEDC;}
__declspec(noinline) Word __fastcall fakeSelect(void* p,void*,Word id){InterlockedIncrement(&originals);put(p,0x1F24,id<=4096?id:0);return 0xAABBCCDD;}
__declspec(noinline) Word __fastcall fakePolygon(void*,void*,Word,Word id,Word count){InterlockedIncrement(&originals);return id+count;}
__declspec(noinline) Word __fastcall fakeFinalize(void* p,void*,Word end){InterlockedIncrement(&originals);return calls.polygon(p,end,1,4);}
__declspec(noinline) Word __fastcall fakeDraw(void* p,void*,Word m){
 if(raiseException)RaiseException(0xE0420011,0,0,nullptr);
 InterlockedIncrement(&originals);calls.select(reinterpret_cast<void*>(m),1);
 if(nested&&p==object.data())calls.draw(other.data(),m);
 calls.finalize(reinterpret_cast<void*>(mismatch?m+4:m),1);SetLastError(412);return 0x2468ABCD;
}
DWORD WINAPI work(void*){return runtime.work(calls);}
bool exceptionalDraw(){__try{calls.draw(object.data(),ptr(manager.data()));}__except(GetExceptionCode()==0xE0420011?EXCEPTION_EXECUTE_HANDLER:EXCEPTION_CONTINUE_SEARCH){return true;}return false;}
void setup(){
 calls={reinterpret_cast<Zero>(fakeBorn),reinterpret_cast<Zero>(fakeRetire),reinterpret_cast<One>(fakeDraw),reinterpret_cast<One>(fakeSelect),reinterpret_cast<One>(fakeFinalize),reinterpret_cast<Three>(fakePolygon)};
 registryPointer=ptr(resources.data());put(resources.data(),0,0x00795C54);put(resources.data(),12,ptr(image.data()));std::memcpy(image.data()+8,"assets/textures/fx0.bmp",23);
 entry[1]=0x123456;put(manager.data(),0x3F60,ptr(entry.data()));put(manager.data(),0x1EEC,7);put(manager.data(),0x1EF0,4);
}
std::array<std::array<unsigned char,16>,6> injectedBefore{};
}
extern "C" __declspec(dllexport) BOOL __cdecl EffectFixtureConfig(Targets* targets,Word* reg,Word* vt){
 setup();*targets=calls;*reg=ptr(&registryPointer);*vt=0x12345678;
 const std::array<void*,6> addresses{reinterpret_cast<void*>(calls.born),reinterpret_cast<void*>(calls.retire),reinterpret_cast<void*>(calls.draw),reinterpret_cast<void*>(calls.select),reinterpret_cast<void*>(calls.finalize),reinterpret_cast<void*>(calls.polygon)};
 for(unsigned i=0;i<6;++i)std::memcpy(injectedBefore[i].data(),addresses[i],16);return TRUE;
}
#pragma comment(linker,"/EXPORT:EffectFixtureConfig=_EffectFixtureConfig")
int wmain(int argc,wchar_t** argv){
 wchar_t fixture[4]{};
 if(GetEnvironmentVariableW(L"SFC_EFFECT_INJECTED_FIXTURE",fixture,4)==1&&fixture[0]==L'1'){
  wchar_t session[128]{};if(!GetEnvironmentVariableW(L"SFC_REMIX_RETURN_SESSION",session,128))return 3;
  return_path::Mapping channel(false,session);const auto until=GetTickCount64()+5000;
  while(!return_path::read(channel.state->ready)&&!return_path::read(channel.state->error)&&GetTickCount64()<until)Sleep(1);
  check(channel.state->ready&&!channel.state->error,"startup-injected DLL/native hooks ready");
  if(failed)return 4;return_path::write(channel.state->armed,1);
  calls.born(object.data());put(object.data(),0,0x12345678);calls.born(other.data());put(other.data(),0,0x12345678);nested=true;
  check(calls.draw(object.data(),ptr(manager.data()))==0x2468ABCD,"injected original/nested draw");
  raiseException=true;check(exceptionalDraw(),"injected exception passes through");raiseException=false;
  calls.retire(object.data());calls.born(object.data());put(object.data(),0,0x12345678);calls.draw(object.data(),ptr(manager.data()));
  calls.finalize(manager.data(),1);Sleep(100);return_path::write(channel.state->stop,1);
  const auto stop=GetTickCount64()+5000;
  while(!return_path::read(*reinterpret_cast<volatile LONG*>(channel.state->padding.data()))&&GetTickCount64()<stop)Sleep(1);
  check(return_path::read(*reinterpret_cast<volatile LONG*>(channel.state->padding.data()))&&!channel.state->error,"injected worker detached/drained/file closed");
  const std::array<void*,6> addresses{reinterpret_cast<void*>(calls.born),reinterpret_cast<void*>(calls.retire),reinterpret_cast<void*>(calls.draw),reinterpret_cast<void*>(calls.select),reinterpret_cast<void*>(calls.finalize),reinterpret_cast<void*>(calls.polygon)};
  for(unsigned i=0;i<6;++i)check(!memcmp(injectedBefore[i].data(),addresses[i],16),"injected hook restored");
  std::cout<<"Injected effect fixture "<<(failed?"FAIL":"PASS")<<" checks="<<checks<<"\n";return failed?1:0;
 }
 if(argc!=2)return 2;
 Registry owners;auto a=owners.birth(100);check(a.epoch&&!a.late,"birth");check(owners.find(100)->epoch==a.epoch,"same living owner");
 check(owners.retire(100).epoch==a.epoch&&!owners.find(100),"retirement");auto b=owners.birth(100);check(b.epoch>a.epoch,"pointer reuse epoch");
 for(unsigned i=1;i<Owners;++i)owners.birth(i+100);check(!owners.birth(100000).epoch,"owner cap");
 Scopes scope;for(unsigned i=0;i<Nesting;++i)check(scope.push({100,i+1,200,i+1}),"nested push");
 check(!scope.push({100,10,200,10})&&!scope.current().token,"overflow cannot inherit owner");scope.pop();check(scope.current().epoch==8,"overflow unwind");
 check(!association(scope.current(),201,1)&&!association(scope.current(),200,4097),"mismatch invalid ID");
 for(unsigned i=0;i<Nesting;++i)scope.pop();check(!scope.current().epoch,"balanced scopes");
 check(bounds(Hard-128,128)&&!bounds(Hard-127,128)&&!bounds(UINT64_MAX,128),"output cap overflow arithmetic");
 AcquireSRWLockExclusive(&identityLock);check(!identity(100,true).epoch&&identityUncertain,"missed lifecycle update invalidates identities");ReleaseSRWLockExclusive(&identityLock);
 check(!identity(101).epoch,"uncertain identity never inherited");identityUncertain=false;busy=0;
 calls={reinterpret_cast<Zero>(fakeBorn),reinterpret_cast<Zero>(fakeRetire),reinterpret_cast<One>(fakeDraw),reinterpret_cast<One>(fakeSelect),reinterpret_cast<One>(fakeFinalize),reinterpret_cast<Three>(fakePolygon)};
 std::array<std::array<unsigned char,16>,6> before{};const std::array<void*,6> addresses{reinterpret_cast<void*>(calls.born),reinterpret_cast<void*>(calls.retire),reinterpret_cast<void*>(calls.draw),reinterpret_cast<void*>(calls.select),reinterpret_cast<void*>(calls.finalize),reinterpret_cast<void*>(calls.polygon)};
 for(unsigned i=0;i<6;++i)std::memcpy(before[i].data(),addresses[i],16);
 registryPointer=ptr(resources.data());registryAddress=ptr(&registryPointer);concreteVtable=0x12345678;
 put(resources.data(),0,0x00795C54);put(resources.data(),12,ptr(image.data()));std::memcpy(image.data()+8,"assets/textures/fx0.bmp",23);
 entry[1]=0x123456;put(manager.data(),0x3F60,ptr(entry.data()));put(manager.data(),0x1EEC,7);put(manager.data(),0x1EF0,4);
 return_path::Mapping channel(true);check(runtime.prepare(channel.state,argv[1]),"private channel/storage prepare");sink=collect;
 const auto thread=CreateThread(nullptr,0,work,nullptr,0,nullptr);check(thread!=nullptr,"worker");
 const auto until=GetTickCount64()+3000;while(!return_path::read(channel.state->ready)&&!return_path::read(channel.state->error)&&GetTickCount64()<until)Sleep(1);
 check(channel.state->ready&&!channel.state->error,"actual six-hook transaction");return_path::write(channel.state->armed,1);
 check(calls.born(object.data())==ptr(object.data()),"original constructor return");put(object.data(),0,concreteVtable);
 calls.born(other.data());put(other.data(),0,concreteVtable);nested=true;
 const auto epoch=registry.find(ptr(object.data()))->epoch;const auto csr=_mm_getcsr();unsigned cw=0;_controlfp_s(&cw,0,0);
 check(calls.draw(object.data(),ptr(manager.data()))==0x2468ABCD,"original draw EAX/stack convention");
 unsigned after=0;_controlfp_s(&after,0,0);check(after==cw&&_mm_getcsr()==csr,"FPU/SSE control preserved");
 check(GetLastError()==412,"original last-error preserved");check(!scopes.depth&&!scopes.excess,"native nested scope balanced");
 raiseException=true;check(exceptionalDraw(),"original SEH reaches original caller");raiseException=false;
 check(!scopes.depth&&!scopes.excess&&!active.load(),"exception scope/callback counters unwind");
 mismatch=true;calls.draw(object.data(),ptr(manager.data()));mismatch=false;
 calls.finalize(manager.data(),1);check(unscoped.load()!=0,"delayed unscoped finalizer not assigned");
 check(calls.retire(object.data())==0x1234FEDC,"original unlink return");calls.born(object.data());put(object.data(),0,concreteVtable);
 check(registry.find(ptr(object.data()))->epoch>epoch,"hooked pointer reuse");calls.draw(object.data(),ptr(manager.data()));
 Sleep(100);
 check(SuspendThread(thread)!=static_cast<DWORD>(-1),"offline pause writer");const auto stalled=GetTickCount64();
 for(unsigned i=0;i<1200;++i)calls.draw(object.data(),ptr(manager.data()));
 check(runtime.header->dropped>0&&GetTickCount64()-stalled<2000,"full/slow writer drops without blocking original calls");
 ResumeThread(thread);return_path::write(channel.state->stop,1);
 check(WaitForSingleObject(thread,5000)==WAIT_OBJECT_0,"worker stops/drains");DWORD code=1;GetExitCodeThread(thread,&code);CloseHandle(thread);
 check(!code&&runtime.header->status==3&&!runtime.header->error&&!active.load()&&!runtime.hooked,"detach and writer complete");
 for(unsigned i=0;i<6;++i)check(!memcmp(before[i].data(),addresses[i],16),"actual hook bytes restored");
 check(originals>10,"original paths executed");
 std::cout<<"Effect native "<<(failed?"FAIL":"PASS")<<" checks="<<checks<<" records="<<runtime.header->written<<" drops="<<runtime.header->dropped<<"\n";
 return failed?1:0;
}
