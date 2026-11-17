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
std::array<Word,64> quadVertices{};
Targets calls;volatile LONG originals=0;bool nested=false,mismatch=false,raiseException=false;
Word ptr(void* p){return reinterpret_cast<Word>(p);}
void put(void* p,unsigned offset,Word value){std::memcpy(static_cast<BYTE*>(p)+offset,&value,4);}
__declspec(noinline) Word __fastcall fakeBorn(void* p,void*){InterlockedIncrement(&originals);put(p,0,0x11111111);return ptr(p);}
__declspec(noinline) Word __fastcall fakeRetire(void*,void*){InterlockedIncrement(&originals);return 0x1234FEDC;}
__declspec(noinline) Word __fastcall fakeSelect(void* p,void*,Word id){InterlockedIncrement(&originals);put(p,0x1F24,id<=4096?id:0);return 0xAABBCCDD;}
__declspec(noinline) void __fastcall fakeFlush(void*,void*){
 InterlockedIncrement(&originals);put(manager.data(),0x3C00,0);put(manager.data(),0x3BFC,0);
}
__declspec(noinline) Word __fastcall fakePresent(void*,void*){InterlockedIncrement(&originals);return 1;}
__declspec(noinline) Word __fastcall fakeSceneBegin(void* renderer,void*){
 InterlockedIncrement(&originals);return renderer==manager.data()?1u:0u;
}
__declspec(noinline) Word __fastcall fakeAppend(void* p,void*,Word corners,Word,Word,Word){
 calls.flush(manager.data()+BatchOffset); // preceding batch must not claim this sample
 const uint16_t indices[]{0,1,2,0,2,3};
 std::memcpy(manager.data()+0x3A4C,indices,sizeof(indices));
 for(unsigned i=0;i<4;++i)
  std::memcpy(manager.data()+BatchOffset+i*32,quadVertices.data()+i*16+5,32);
 put(p,0x3C00,corners-2);put(p,0x3BFC,corners);put(p,0x3C08,4);put(p,0x3C0C,1);
 return 1;
}
__declspec(noinline) Word __fastcall fakePolygon(void* p,void*,Word,Word id,Word count){
 InterlockedIncrement(&originals);
 if(calls.append)calls.append(p,count,0,id,0);
 return id+count;
}
__declspec(noinline) Word __fastcall fakeFinalize(void* p,void*,Word end){InterlockedIncrement(&originals);return calls.polygon(p,end,1,4);}
__declspec(noinline) Word __fastcall fakeDraw(void* p,void*,Word m){
 if(raiseException)RaiseException(0xE0420011,0,0,nullptr);
 InterlockedIncrement(&originals);calls.select(reinterpret_cast<void*>(m),1);
 if(nested&&p==object.data())calls.draw(other.data(),m);
 calls.finalize(reinterpret_cast<void*>(mismatch?m+4:m),1);SetLastError(412);return 0x2468ABCD;
}
DWORD WINAPI work(void*){return runtime.work(calls);}
DWORD WINAPI drainWork(void* context){return static_cast<Runtime*>(context)->work({},false);}

void testFinalResourceDrain(const wchar_t* output){
 return_path::Mapping channel(true);
 auto observer=std::make_unique<Runtime>();
 const auto path=std::wstring(output)+L".drain";
 if(!observer->prepare(channel.state,path.c_str())){check(false,"final drain prepare");return;}
 const auto worker=CreateThread(nullptr,0,drainWork,observer.get(),0,nullptr);
 if(!worker){check(false,"final drain worker");return;}
 const auto deadline=GetTickCount64()+3000;
 while(!return_path::read(channel.state->ready)&&GetTickCount64()<deadline)Sleep(1);
 const bool paused=channel.state->ready&&SuspendThread(worker)!=static_cast<DWORD>(-1);
 check(paused,"queue resource with paused writer");
 if(paused){
  return_path::write(channel.state->armed,1);
  observer->emit(Resource,ptr(object.data()),ptr(manager.data()),
                 {1,1,1,registryPointer,ptr(image.data()),ptr(entry.data()),entry[1]});
  return_path::write(channel.state->armed,0);
 }
 return_path::write(channel.state->stop,1);
 if(paused)ResumeThread(worker);
 const bool closed=WaitForSingleObject(worker,5000)==WAIT_OBJECT_0;
 CloseHandle(worker);
 check(closed,"final drain worker exited");
 if(!closed)std::exit(1);
 std::ifstream file(std::filesystem::path(path),std::ios::binary);
 file.seekg(sizeof(Header));
 Record row{};unsigned names=0;
 while(file.read(reinterpret_cast<char*>(&row),sizeof(row))){
  if(row.kind!=Name)continue;
  check(row.args[0]==1&&row.args[1]==1&&row.args[2]==names,"final drain keeps resource provenance");
  ++names;
 }
 check(names==4,"resolve accepted resource after stop and disarm");
 check(observer->header->status==3&&!observer->header->dropped,"final drain closes without drops");
}
bool exceptionalDraw(){__try{calls.draw(object.data(),ptr(manager.data()));}__except(GetExceptionCode()==0xE0420011?EXCEPTION_EXECUTE_HANDLER:EXCEPTION_CONTINUE_SEARCH){return true;}return false;}
void setupQuad(){
 for(unsigned i=0;i<quadVertices.size();++i)quadVertices[i]=i+1;
 const uint16_t indices[]{0,1,2,3};std::memcpy(manager.data()+0x14,indices,sizeof(indices));
 put(manager.data(),4,ptr(quadVertices.data()));
}
void setup(){
 setupQuad();
 calls={reinterpret_cast<Zero>(fakeBorn),reinterpret_cast<Zero>(fakeRetire),reinterpret_cast<One>(fakeDraw),reinterpret_cast<One>(fakeSelect),reinterpret_cast<One>(fakeFinalize),reinterpret_cast<Three>(fakePolygon)};
 registryPointer=ptr(resources.data());put(resources.data(),0,0x00795C54);put(resources.data(),12,ptr(image.data()));std::memcpy(image.data()+8,"assets/textures/fx0.bmp",23);
 entry[1]=0x123456;put(manager.data(),0x3F60,ptr(entry.data()));put(manager.data(),0x1EEC,7);put(manager.data(),0x1EF0,4);
}
std::array<std::array<unsigned char,16>,10> injectedBefore{};
std::array<void*,10> injectedAddresses(){
 return {reinterpret_cast<void*>(calls.born),reinterpret_cast<void*>(calls.retire),reinterpret_cast<void*>(calls.draw),
  reinterpret_cast<void*>(calls.select),reinterpret_cast<void*>(calls.finalize),reinterpret_cast<void*>(calls.polygon),
  reinterpret_cast<void*>(calls.append),reinterpret_cast<void*>(calls.flush),reinterpret_cast<void*>(calls.present),
  reinterpret_cast<void*>(calls.sceneBegin)};
}
struct JoinFixture {
 HANDLE mapping=nullptr;
 BYTE* view=nullptr;
 ~JoinFixture(){if(view)UnmapViewOfFile(view);if(mapping)CloseHandle(mapping);}
 bool publish(const wchar_t* name){
  mapping=OpenFileMappingW(FILE_MAP_READ|FILE_MAP_WRITE,FALSE,name);
  if(!mapping)return false;
  view=static_cast<BYTE*>(MapViewOfFile(mapping,FILE_MAP_READ|FILE_MAP_WRITE,0,0,16*1024*1024));
  if(!view)return false;
  const auto* session=reinterpret_cast<const DWORD*>(view+16);
  auto* store=reinterpret_cast<multi_scene::Store*>(view+multi_scene::Offset);
  live_owner::Source source;
  if(!source.attach(view,session))return false;
  multi_scene::Source cohort;
  if(!cohort.attach(view,session))return false;
  source.begin(42);
  check(!select_acknowledged_anchor(source.store->header,0,0,7,1),"unpublished asset cannot select anchor");
  check(!select_acknowledged_anchor(source.store->header,2,1,7,1),"stale acknowledgement cannot select anchor");
  if(!select_acknowledged_anchor(source.store->header,2,2,7,1))return false;
  check(!select_acknowledged_anchor(source.store->header,3,3,8,1),"acknowledgement cannot replace anchor");
  FrameStamp stamp{};memcpy(stamp.session,session,16);
  stamp.pid=GetCurrentProcessId();stamp.thread=GetCurrentThreadId();stamp.manager=ptr(manager.data());stamp.frame=42;
  LARGE_INTEGER q{};if(!QueryPerformanceCounter(&q))return false;stamp.scene_start=q.QuadPart;
  live_owner::Row row{};row[1]=7;row[2]=42;row[4]=row[48]=1;row[5]=70;row[6]=71;row[7]=1;row[47]=stamp.thread;
  if(!QueryPerformanceCounter(&q))return false;
  row[89]=static_cast<DWORD>(q.QuadPart);row[90]=static_cast<DWORD>(uint64_t(q.QuadPart)>>32);
  live_owner::Packet packet{};
  if(!source.prepare(row,packet))return false;
  cohort.begin();cohort.offer(row);
  if(!cohort.publish(live_owner::selection(7,1))||!source.commit(packet)||!stamp_now(stamp))return false;
  stamp.sequence=cohort.pending.sequence;stamp.checksum=cohort.pending.checksum;
  if(store->header.frame!=42)return false;
  publish_stamp(*reinterpret_cast<StampSlot*>(view+StampOffset),stamp);
  return true;
 }
};
}
extern "C" __declspec(dllexport) BOOL __cdecl EffectFixtureConfig(Targets* targets,Word* reg,Word* vt){
 setup();*targets=calls;*reg=ptr(&registryPointer);*vt=0x12345678;
 wchar_t batch[2]{};
 if(GetEnvironmentVariableW(L"SFC_EFFECT_BATCH_OBSERVATION",batch,2)==1&&batch[0]==L'1'){
  calls.append=reinterpret_cast<Four>(fakeAppend);calls.flush=reinterpret_cast<Flush>(fakeFlush);calls.present=reinterpret_cast<Zero>(fakePresent);
  if(!GetEnvironmentVariableW(L"SFC_EFFECT_JOIN_SCENE",nullptr,0))calls.sceneBegin=reinterpret_cast<Zero>(fakeSceneBegin);
  *targets=calls;
  for(unsigned i=0;i<4;++i)quadVertices[i*16+11]=i%2?0x3F7F0000:0x3F400000;
 }
 const auto addresses=injectedAddresses();
 for(unsigned i=0;i<addresses.size();++i)if(addresses[i])std::memcpy(injectedBefore[i].data(),addresses[i],16);
 return TRUE;
}
#pragma comment(linker,"/EXPORT:EffectFixtureConfig=_EffectFixtureConfig")
int wmain(int argc,wchar_t** argv){
 wchar_t fixture[4]{};
 if(GetEnvironmentVariableW(L"SFC_EFFECT_INJECTED_FIXTURE",fixture,4)==1&&fixture[0]==L'1'){
  wchar_t session[128]{};if(!GetEnvironmentVariableW(L"SFC_REMIX_RETURN_SESSION",session,128))return 3;
  return_path::Mapping channel(false,session);const auto until=GetTickCount64()+5000;
  while(!return_path::read(channel.state->ready)&&!return_path::read(channel.state->error)&&GetTickCount64()<until)Sleep(1);
  check(channel.state->ready&&!channel.state->error,"startup-injected DLL/native hooks ready");
  const auto addresses=injectedAddresses();
  if(calls.append){
   for(unsigned i=0;i<addresses.size();++i)
    if(addresses[i])check(!memcmp(injectedBefore[i].data(),addresses[i],16),"passive batch observer preserves gate restore bytes");
  }
  if(failed)return 4;return_path::write(channel.state->armed,1);
  if(calls.append){
   const auto armed=GetTickCount64()+5000;
   while(return_path::read(channel.state->ready)!=2&&!channel.state->error&&GetTickCount64()<armed)Sleep(1);
   check(return_path::read(channel.state->ready)==2&&!channel.state->error,"batch hooks attached after gate arming");
   check(memcmp(injectedBefore[6].data(),addresses[6],16)!=0,"batch enqueue hook installed");
   if(failed)return 4;
  }
  calls.born(object.data());put(object.data(),0,0x12345678);calls.born(other.data());put(other.data(),0,0x12345678);nested=true;
  JoinFixture join;
  wchar_t joinName[128]{};
  if(GetEnvironmentVariableW(L"SFC_EFFECT_JOIN_SCENE",joinName,128)){
   check(join.publish(joinName),"publish retained frame and authoritative stamp");
   nested=false;
  }else if(calls.append){
   nested=false;
   check(calls.sceneBegin(other.data())==0,"failed native scene begin");
   calls.draw(object.data(),ptr(manager.data()));calls.flush(manager.data()+BatchOffset);calls.present(manager.data());
   check(calls.sceneBegin(manager.data())==1,"successful native scene begin");
  }
  check(calls.draw(object.data(),ptr(manager.data()))==0x2468ABCD,"injected original/nested draw");
  if(calls.append){calls.flush(manager.data()+BatchOffset);calls.present(other.data());calls.present(manager.data());}
  raiseException=true;check(exceptionalDraw(),"injected exception passes through");raiseException=false;
  calls.retire(object.data());calls.born(object.data());put(object.data(),0,0x12345678);calls.draw(object.data(),ptr(manager.data()));
  calls.finalize(manager.data(),1);Sleep(100);return_path::write(channel.state->stop,1);
  const auto stop=GetTickCount64()+5000;
  while(!return_path::read(*reinterpret_cast<volatile LONG*>(channel.state->padding.data()))&&GetTickCount64()<stop)Sleep(1);
  check(return_path::read(*reinterpret_cast<volatile LONG*>(channel.state->padding.data()))&&!channel.state->error,"injected worker detached/drained/file closed");
  for(unsigned i=0;i<addresses.size();++i)if(addresses[i])check(!memcmp(injectedBefore[i].data(),addresses[i],16),"injected hook restored");
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
 setupQuad();quadObservation=true;quadReturnSite=0;
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
 check(quadAttempts==QuadLimit,"bounded corner sampling under slow writer");
 testFinalResourceDrain(argv[1]);
 std::cout<<"Effect native "<<(failed?"FAIL":"PASS")<<" checks="<<checks<<" records="<<runtime.header->written<<" drops="<<runtime.header->dropped<<"\n";
 return failed?1:0;
}
