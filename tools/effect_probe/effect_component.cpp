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
  {0x006AC900,"\x51\x53\x55\x56\x8B\xF1",6},{0x006AC830,"\x8B\x44\x24\x0C\x56\x83\xF8\x03\x57",9}};
 if(reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr))!=0x400000)return {};
 for(const auto& c:checks){std::array<char,16> bytes{};if(!read(c.address,bytes.data(),c.size)||memcmp(bytes.data(),c.bytes,c.size))return {};}
 return {reinterpret_cast<Zero>(0x004ECD72),reinterpret_cast<Zero>(0x004ECDD6),reinterpret_cast<One>(0x004EFA4A),reinterpret_cast<One>(0x006AD3E0),reinterpret_cast<One>(0x006AC900),reinterpret_cast<Three>(0x006AC830)};
}
DWORD WINAPI worker(void*){
 wchar_t session[128]{},output[1024]{},expected[1024]{},actual[1024]{};
 if(!GetEnvironmentVariableW(L"SFC_EFFECT_OUTPUT",output,1024))return 0;
 if(!GetEnvironmentVariableW(L"SFC_REMIX_RETURN_SESSION",session,128)||!GetEnvironmentVariableW(L"SFC_REMIX_EXPECTED_IMAGE",expected,1024)||!GetModuleFileNameW(nullptr,actual,1024)||CompareStringOrdinal(actual,-1,expected,-1,TRUE)!=CSTR_EQUAL)return 1;
 try{
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
  }else t=targets();
  if(!t.born){return_path::write(state.error,123);return 1;}
  effect_probe::sink=effect_probe::collect;
  if(!effect_probe::runtime.prepare(&state,output)){return_path::write(state.error,124);return 1;}
  return effect_probe::runtime.work(t);
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
