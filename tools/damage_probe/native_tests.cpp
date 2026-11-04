#include "../early_model_probe/early_runtime.h"
#include <iostream>
#include <xmmintrin.h>
using namespace early_model;
namespace {
unsigned checks=0;bool failed=false;
void check(bool v,const char* why){++checks;if(!v){failed=true;std::cout<<"FAIL "<<why<<'\n';}}
std::array<BYTE,0x100> ship{};std::array<BYTE,0x188> visual{};std::array<Word,16> mesh{};
std::array<BYTE,0x2000> manager{};std::array<Word,9> material{};
std::array<std::array<float,3>,3> positions{{{0,0,0},{1,0,0},{0,1,0}}};
std::array<Word,7> primary{},secondary{};std::array<Word,1> primaryList{},secondaryList{};
std::array<std::array<Word,7>,3> corners{};
Targets calls;Three wrapper=nullptr;Word scalar=0x3F000000;unsigned primaryCalls=0,secondaryCalls=0;
std::array<void*,10> addresses{};std::array<std::array<BYTE,16>,10> bytes{};
void put(void* p,unsigned offset,Word v){memcpy(static_cast<BYTE*>(p)+offset,&v,4);}
__declspec(noinline) Word __fastcall born(void* p,void*){put(p,0,shipVt);return 11;}
__declspec(noinline) Word __fastcall retire(void* p,void*){put(p,0x10,0);return 12;}
__declspec(noinline) Word __fastcall visualRetire(void* p,void*){put(p,0x10,0);return 13;}
__declspec(noinline) Word __fastcall parse(void* p,void*,Word text){put(p,0,visualVt);put(p,0x11C,1);put(p,0x154,1);put(p,0x158,ptr(material.data()));put(p,0x15C,1);put(p,0x160,ptr(mesh.data()));put(p,0x120,UINT32_MAX);return text?1:0;}
__declspec(noinline) Word __cdecl load(Word text){return calls.parse(visual.data(),text)?ptr(visual.data()):0;}
__declspec(noinline) Word __fastcall attach(void* p,void*,Word v){put(p,0x88,v);return 14;}
__declspec(noinline) Word __fastcall request(void* p,void*,Word text){calls.attach(p,calls.load(text));SetLastError(412);return 15;}
__declspec(noinline) Word __fastcall wrap(void*,void*,Word count,Word list,Word mode){if(list==ptr(primaryList.data()))++primaryCalls;else if(list==ptr(secondaryList.data()))++secondaryCalls;SetLastError(712);return count^mode;}
__declspec(noinline) Word __fastcall drawMesh(void* p,void*,Word m,Word source,Word a,Word){
 put(reinterpret_cast<void*>(m),0x554,ptr(positions.data()));put(reinterpret_cast<void*>(m),0x558,source);wrapper(reinterpret_cast<void*>(m),1,ptr(primaryList.data()),1);
 if(a){put(p,0x18,ptr(secondaryList.data()));std::array<Word,9> temporary{0x23,0xFFFFFFFF,0x3E99999A,0x3F800000,0,99,0,100,0};
  put(reinterpret_cast<void*>(m),0x558,ptr(temporary.data()));wrapper(reinterpret_cast<void*>(m),1,ptr(secondaryList.data()),1);}
 return 0x12345678;
}
__declspec(noinline) Word __fastcall render(void*,void*,Word m){return calls.mesh(mesh.data(),m,ptr(material.data()),scalar,0);}
Targets setup(){
 material={0x20,0xFFFFFFFF,0,0,0,1,0,2,0};mesh[0]=meshVt;mesh[2]=3;mesh[3]=ptr(positions.data());mesh[4]=1;mesh[5]=ptr(primaryList.data());
 primaryList[0]=ptr(primary.data());secondaryList[0]=ptr(secondary.data());primary={3,0,0,0,0,0,ptr(corners.data())};secondary=primary;
 for(unsigned i=0;i<3;++i){corners[i]={i,0,0,0x3F800000,0x3E800000,0x3F400000,0};}
 put(manager.data(),0,0x007B8D4C);
 wrapper=reinterpret_cast<Three>(wrap);damageWrapper=wrapper;
 Targets t{reinterpret_cast<One>(request),load,reinterpret_cast<One>(parse),reinterpret_cast<One>(attach),reinterpret_cast<One>(render),reinterpret_cast<Four>(drawMesh),reinterpret_cast<Zero>(visualRetire),reinterpret_cast<Zero>(born),reinterpret_cast<Zero>(retire)};
 addresses={reinterpret_cast<void*>(t.request),reinterpret_cast<void*>(t.load),reinterpret_cast<void*>(t.parse),reinterpret_cast<void*>(t.attach),reinterpret_cast<void*>(t.render),reinterpret_cast<void*>(t.mesh),reinterpret_cast<void*>(t.visualRetire),reinterpret_cast<void*>(t.born),reinterpret_cast<void*>(t.retire),reinterpret_cast<void*>(wrapper)};
 for(unsigned i=0;i<10;++i)memcpy(bytes[i].data(),addresses[i],16);return t;
}
void exercise(){
 check(calls.born(ship.data())==11,"original constructor return");check(calls.request(ship.data(),ptr(const_cast<char*>("fixture.mod")))==15,"load/attach owner scope");check(GetLastError()==412,"original last error");
 const auto oldMesh=mesh;const auto oldPositions=positions;const auto oldCorners=corners;const auto csr=_mm_getcsr();
 scalar=0;check(calls.render(ship.data(),ptr(manager.data()))==0x12345678,"undamaged original draw");check(primaryCalls==1&&secondaryCalls==0,"undamaged does not fabricate damage");
 scalar=0x3F000000;check(calls.render(ship.data(),ptr(manager.data()))==0x12345678,"damaged original draw");check(primaryCalls==2&&secondaryCalls==1,"both native submissions unchanged");check(GetLastError()==712,"wrapper last error");
 check(csr==_mm_getcsr(),"SSE state preserved");check(mesh[6]==ptr(secondaryList.data()),"native lazy list retained");
 check(positions==oldPositions&&corners==oldCorners,"input geometry and UV untouched");check(mesh[0]==oldMesh[0]&&mesh[4]==oldMesh[4]&&mesh[5]==oldMesh[5],"source identity unchanged");
 check(!damageContext.owner,"model context unwinds before unrelated calls");
 const auto before=secondaryCalls;check(wrapper(manager.data(),1,ptr(secondaryList.data()),1)==0&&secondaryCalls==before+1,"unowned wrapper forwards unchanged");
 for(unsigned i=0;i<10;++i)calls.render(ship.data(),ptr(manager.data()));
 calls.retire(ship.data());calls.born(ship.data());calls.request(ship.data(),ptr(const_cast<char*>("fixture.mod")));calls.render(ship.data(),ptr(manager.data()));
 calls.retire(ship.data());check(!failed,"fixture actions complete");
}
DWORD WINAPI work(void*){return runtime.work(calls);}
}
extern "C" __declspec(dllexport) BOOL __cdecl EarlyFixtureConfig(Targets* t){calls=setup();*t=calls;return TRUE;}
extern "C" __declspec(dllexport) Three __cdecl DamageFixtureWrapper(){return wrapper;}
#pragma comment(linker,"/EXPORT:EarlyFixtureConfig=_EarlyFixtureConfig")
#pragma comment(linker,"/EXPORT:DamageFixtureWrapper=_DamageFixtureWrapper")
int wmain(int argc,wchar_t** argv){
 wchar_t session[128]{};const bool injected=GetEnvironmentVariableW(L"SFC_REMIX_RETURN_SESSION",session,128)!=0;
 if(!injected&&argc!=2)return 2;
 return_path::Mapping channel(!injected,injected?session:nullptr);HANDLE worker=nullptr;
 if(!injected){calls=setup();fixtureMode=true;sink=collect;check(runtime.prepare(channel.state,argv[1]),"preallocated observer storage");worker=CreateThread(nullptr,0,work,nullptr,0,nullptr);}
 auto until=GetTickCount64()+5000;while(!channel.state->ready&&!channel.state->error&&GetTickCount64()<until)Sleep(1);check(channel.state->ready&&!channel.state->error,"hook worker ready");if(failed)return 3;
 exercise();Sleep(50);
 if(!injected){
  check(damageSnapshots[0].state.load()>=2&&damageSnapshots[0].state.load()<=3,"mapping ready or written");const auto& s=damageSnapshots[0];check(s.header[15]==99&&s.header[16]==100,"stack material copied before return");check(s.header[10]==3&&s.header[11]==1&&s.header[12]==3,"mapping exact counts");check(s.corners[0][4]==0x3E800000&&s.corners[0][5]==0x3F400000,"secondary UV exact");
  check(s.polygons[0][6]==0,"portable corner ordinal");check(damageSnapshots[1].state.load()==2||damageSnapshots[1].state.load()==3,"fresh asset epoch never reuses prior snapshot");
 }
 return_path::write(channel.state->stop,1);until=GetTickCount64()+5000;while(!return_path::read(*reinterpret_cast<volatile LONG*>(channel.state->padding.data()))&&GetTickCount64()<until)Sleep(1);
 check(return_path::read(*reinterpret_cast<volatile LONG*>(channel.state->padding.data()))&&!channel.state->error,"worker stopped and file closed");
 if(worker){check(WaitForSingleObject(worker,5000)==WAIT_OBJECT_0,"worker drained");CloseHandle(worker);check(!active.load()&&!runtime.hooked,"callbacks drained and hooks detached");}
 for(unsigned i=0;i<10;++i)check(!memcmp(bytes[i].data(),addresses[i],16),"byte exact hook restoration");
 std::cout<<"Damage "<<(injected?"injected ":"native ")<<(failed?"FAIL":"PASS")<<" checks="<<checks<<'\n';return failed?1:0;
}
