#include "early_runtime.h"
extern "C" void __cdecl EarlyModelStartup() {}
#pragma comment(linker,"/EXPORT:EarlyModelStartup=_EarlyModelStartup,@1")
namespace {
early_model::Targets targets(){
 using namespace early_model;
 struct Check {Word address;const char* bytes;};
 const Check checks[]={
  {0x004156F9,"\xB8\xD2\xBA\x75\x00\xE8\x51\x0B\x32\x00"},
  {0x0042F51A,"\xB8\xFA\xCC\x75\x00\xE8\x30\x6D\x30\x00"},
  {0x0042FEF9,"\xB8\x18\xCD\x75\x00\xE8\x51\x63\x30\x00"},
  {0x00413A8D,"\x56\x8B\xF1\x8B\x4C\x24\x08\x85\xC9\x89"},
  {0x004162B9,"\x55\x8B\xEC\x83\xEC\x50\xF6\x05\xC6\x0B"},
  {0x0042E4B2,"\x55\x8B\xEC\x83\xEC\x38\x53\x56\x8B\x75"},
  {0x0042F918,"\xB8\x0C\xCD\x75\x00\xE8\x32\x69\x30\x00"},
  {0x004146A7,"\xB8\x9E\xBA\x75\x00\xE8\xA3\x1B\x32\x00"},
  {0x004158C1,"\xB8\x13\xBB\x75\x00\xE8\x89\x09\x32\x00"}};
 if(reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr))!=0x400000)return {};
 for(const auto& c:checks){std::array<char,10> b{};if(!read(c.address,b.data(),b.size())||memcmp(b.data(),c.bytes,b.size()))return {};}
 return {reinterpret_cast<One>(0x004156F9),reinterpret_cast<Loader>(0x0042F51A),reinterpret_cast<One>(0x0042FEF9),reinterpret_cast<One>(0x00413A8D),reinterpret_cast<One>(0x004162B9),reinterpret_cast<Four>(0x0042E4B2),reinterpret_cast<Zero>(0x0042F918),reinterpret_cast<Zero>(0x004146A7),reinterpret_cast<Zero>(0x004158C1)};
}
DWORD WINAPI worker(void*){
 using namespace early_model;
 wchar_t output[1024]{},session[128]{},expected[1024]{},actual[1024]{};
 if(!GetEnvironmentVariableW(L"SFC_EARLY_OUTPUT",output,1024))return 0;
 if(!GetEnvironmentVariableW(L"SFC_REMIX_RETURN_SESSION",session,128)||!GetEnvironmentVariableW(L"SFC_REMIX_EXPECTED_IMAGE",expected,1024)||!GetModuleFileNameW(nullptr,actual,1024)||CompareStringOrdinal(actual,-1,expected,-1,TRUE)!=CSTR_EQUAL)return 1;
 try{
  auto* mapping=new return_path::Mapping(false,session);auto& state=*mapping->state;
  state.gamePid=GetCurrentProcessId();state.startupRestored=1;state.startupVerified=1;
  Targets t{};wchar_t fixture[4]{};
  if(GetEnvironmentVariableW(L"SFC_EARLY_FIXTURE",fixture,4)==1&&fixture[0]==L'1'){
   const std::wstring image(actual);if(image.find(L"\\artifacts\\remix-runtime\\runs\\")==std::wstring::npos||image.substr(image.find_last_of(L"\\/")+1)!=L"d3d11_return_fixture.exe"){return_path::write(state.error,225);return 1;}
   using Factory=BOOL(__cdecl*)(Targets*);const auto factory=reinterpret_cast<Factory>(GetProcAddress(GetModuleHandleW(nullptr),"EarlyFixtureConfig"));
   if(!factory||!factory(&t)){return_path::write(state.error,226);return 1;}fixtureMode=true;
  }else t=targets();
  if(!t.request){return_path::write(state.error,223);return 1;}
  sink=collect;if(!runtime.prepare(&state,output)){return_path::write(state.error,224);return 1;}
  return runtime.work(t);
 }catch(...){return 1;}
}
}
BOOL WINAPI DllMain(HMODULE,DWORD reason,LPVOID){
 if(DetourIsHelperProcess())return TRUE;
 if(reason==DLL_PROCESS_ATTACH){if(!DetourRestoreAfterWith())return FALSE;wchar_t value[1024]{};const auto n=GetEnvironmentVariableW(L"SFC_EARLY_OUTPUT",value,1024);if(!n)return TRUE;if(n>=1024)return FALSE;
  const auto h=CreateThread(nullptr,0,worker,nullptr,0,nullptr);if(!h)return FALSE;CloseHandle(h);}
 return TRUE;
}
