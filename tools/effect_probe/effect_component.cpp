#include "effect_runtime.h"
extern "C" void __cdecl EffectProbeStartup() {} // Detours startup import ordinal1;never a callback
#pragma comment(linker,"/EXPORT:EffectProbeStartup=_EffectProbeStartup,@1")
namespace {
effect_probe::Targets targets(){
 using namespace effect_probe;
 struct Check {Word address;const char* bytes;size_t size;};
 const Check checks[]={
  {0x004ECD72,"\x8B\xC1\x33\xD2\xD9\xE8",6},{0x004ECDD6,"\x8B\x41\x04\xC7\x01\x70\x98\x7A\x00",9},
  {0x004EFA4A,"\x55\x8B\xEC\x81\xEC\xD8\x00\x00\x00",9},{0x006AD3E0,"\x8B\x44\x24\x04\x3D\x00\x10\x00\x00",9},
  {0x006AC900,"\x51\x53\x55\x56\x8B\xF1",6},{0x006AC830,"\x8B\x44\x24\x0C\x56\x83\xF8\x03\x57",9},
  {0x006AB410,"\x83\xEC\x14\x53\x8B\xD9",6},{0x006AB380,"\x56\x8B\xF1\x8B\x86\xC0\x1C\x00\x00",9},
  {0x0069EB90,"\x56\x8B\xF1\x8A\x86\x28\x3C\x00\x00",9},
  {0x0069E300,"\x53\x56\x8B\xF1\x57",5}};
 if(reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr))!=0x400000)return {};
 for(const auto& c:checks){
  if(joinView&&c.address==0x0069E300)continue; // M1 owns this site in join mode.
  std::array<char,16> bytes{};if(!read(c.address,bytes.data(),c.size)||memcmp(bytes.data(),c.bytes,c.size))return {};
 }
 return {reinterpret_cast<Zero>(0x004ECD72),reinterpret_cast<Zero>(0x004ECDD6),reinterpret_cast<One>(0x004EFA4A),reinterpret_cast<One>(0x006AD3E0),reinterpret_cast<One>(0x006AC900),reinterpret_cast<Three>(0x006AC830),
  batchObservation?reinterpret_cast<Four>(0x006AB410):nullptr,
  batchObservation?reinterpret_cast<Flush>(0x006AB380):nullptr,
  batchObservation?reinterpret_cast<Zero>(0x0069EB90):nullptr,
  batchObservation&&!joinView?reinterpret_cast<Zero>(0x0069E300):nullptr};
}
DWORD WINAPI worker(void*){
 wchar_t session[128]{},output[1024]{},expected[1024]{},actual[1024]{};
 if(!GetEnvironmentVariableW(L"SFC_EFFECT_OUTPUT",output,1024))return 0;
 if(!GetEnvironmentVariableW(L"SFC_REMIX_RETURN_SESSION",session,128)||!GetEnvironmentVariableW(L"SFC_REMIX_EXPECTED_IMAGE",expected,1024)||!GetModuleFileNameW(nullptr,actual,1024)||CompareStringOrdinal(actual,-1,expected,-1,TRUE)!=CSTR_EQUAL)return 1;
 try{
  wchar_t quad[2]{};effect_probe::quadObservation=GetEnvironmentVariableW(L"SFC_EFFECT_QUAD_OBSERVATION",quad,2)==1&&quad[0]==L'1';
  wchar_t batch[2]{};effect_probe::batchObservation=GetEnvironmentVariableW(L"SFC_EFFECT_BATCH_OBSERVATION",batch,2)==1&&batch[0]==L'1';
  effect_probe::quadObservation|=effect_probe::batchObservation;
  wchar_t joinName[128]{};
  const auto joinLength=GetEnvironmentVariableW(L"SFC_EFFECT_JOIN_SCENE",joinName,128);
  struct SceneView {
   HANDLE handle=nullptr;BYTE* view=nullptr;
   ~SceneView(){if(view)UnmapViewOfFile(view);if(handle)CloseHandle(handle);}
  } scene;
  if(joinLength){
   if(joinLength>=128||!effect_probe::batchObservation)return 1;
   scene.handle=OpenFileMappingW(FILE_MAP_READ|FILE_MAP_WRITE,FALSE,joinName);
   if(!scene.handle)return 1;
   scene.view=static_cast<BYTE*>(MapViewOfFile(scene.handle,FILE_MAP_READ|FILE_MAP_WRITE,0,0,16*1024*1024));
   if(!scene.view)return 1;
   memcpy(effect_probe::joinSession,scene.view+16,16);effect_probe::joinView=scene.view;
   if(!live_owner::header_valid(reinterpret_cast<live_owner::Store*>(scene.view+live_owner::Offset)->header,effect_probe::joinSession))return 1;
  }
  // Intentionally process-lifetime storage: never unload a live callback/worker.
  auto* mapping=new return_path::Mapping(false,session);auto& state=*mapping->state;
  state.gamePid=GetCurrentProcessId();state.startupRestored=1;state.startupVerified=1;
  effect_probe::Targets t{};wchar_t fixture[4]{};
  if(GetEnvironmentVariableW(L"SFC_EFFECT_INJECTED_FIXTURE",fixture,4)==1&&fixture[0]==L'1'){
   // Explicit owned standalone executable only. Never accepts arbitrary target
   // addresses supplied in environment variables or the live SFC process.
   const std::wstring image(actual);
   if(image.find(L"\\artifacts\\remix-runtime\\runs\\")==std::wstring::npos||image.substr(image.find_last_of(L"\\/")+1)!=L"d3d11_return_fixture.exe"){return_path::write(state.error,125);return 1;}
   using Factory=BOOL(__cdecl*)(effect_probe::Targets*,effect_probe::Word*,effect_probe::Word*);
   const auto factory=reinterpret_cast<Factory>(GetProcAddress(GetModuleHandleW(nullptr),"EffectFixtureConfig"));
   if(!factory||!factory(&t,&effect_probe::registryAddress,&effect_probe::concreteVtable)){return_path::write(state.error,126);return 1;}
   effect_probe::quadReturnSite=0; // Owned synthetic fixture has no game call site.
   effect_probe::batchFixture=true;
  }else t=targets();
  if(!t.born){return_path::write(state.error,123);return 1;}
  effect_probe::sink=effect_probe::collect;
  if(!effect_probe::runtime.prepare(&state,output)){return_path::write(state.error,124);return 1;}
  const auto result=effect_probe::runtime.work(t,true,effect_probe::batchObservation);
  // A failed detach can leave callbacks installed until process exit.
  if(effect_probe::runtime.hooked||effect_probe::active.load()){scene.view=nullptr;scene.handle=nullptr;}
  else effect_probe::joinView=nullptr;
  return result;
 }catch(...){return 1;}
}
}
BOOL WINAPI DllMain(HMODULE,DWORD reason,LPVOID){
 if(DetourIsHelperProcess())return TRUE;
 if(reason==DLL_PROCESS_ATTACH){
  if(!DetourRestoreAfterWith())return FALSE;
  wchar_t enabled[1024]{};const auto n=GetEnvironmentVariableW(L"SFC_EFFECT_OUTPUT",enabled,1024);
  if(!n)return TRUE;if(n>=1024)return FALSE;
  const auto h=CreateThread(nullptr,0,worker,nullptr,0,nullptr);if(!h)return FALSE;CloseHandle(h);
 }
 return TRUE;
}
