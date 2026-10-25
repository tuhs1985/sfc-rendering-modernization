#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <tlhelp32.h>
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <memory>
#include <sstream>
#include <reshade.hpp>
#include <detours.h>
#include "../remix_runtime/return_wire.h"
#include "survey_events.h"
#include "survey_native.h"
extern "C" __declspec(dllimport) bool ReShadeRegisterAddon(void*,uint32_t);
extern "C" __declspec(dllexport) const char* NAME="SFC metadata rendering-family survey";
extern "C" __declspec(dllexport) const char* DESCRIPTION="Read-only;no ship geometry,images,rendering or replacement.";
namespace {
std::unique_ptr<return_path::Mapping> mapping;bool registered=false;
void init(reshade::api::effect_runtime* runtime){
 if(!mapping)return;auto& s=*mapping->state;
 uint32_t width=0,height=0;runtime->get_screenshot_width_and_height(&width,&height);
 s.gamePid=GetCurrentProcessId();s.lastWidth=width;s.lastHeight=height;return_path::write(s.ready,1);
}
void destroy(reshade::api::effect_runtime*){if(mapping)return_path::write(mapping->state->ready,0);}
DWORD WINAPI modules(void* value){
 const std::filesystem::path output=static_cast<const wchar_t*>(value);std::ofstream file(output);
 if(!file){return_path::write(mapping->state->error,91);return 1;}
 uint64_t written=0;unsigned snapshots=0;
 while(mapping&&!return_path::read(mapping->state->stop)&&snapshots++<286){
  const auto snap=CreateToolhelp32Snapshot(TH32CS_SNAPMODULE,GetCurrentProcessId());
  if(snap==INVALID_HANDLE_VALUE){return_path::write(mapping->state->error,92);return 1;}
  MODULEENTRY32W row{};row.dwSize=sizeof(row);unsigned entries=0;
  if(Module32FirstW(snap,&row))do{
   if(++entries>256){return_path::write(mapping->state->error,93);break;}
   char path[4096]{};const int n=WideCharToMultiByte(CP_UTF8,WC_ERR_INVALID_CHARS,row.szExePath,-1,path,sizeof(path),nullptr,nullptr);
   if(!n){return_path::write(mapping->state->error,94);break;}
   std::ostringstream line;line<<"{\"qpc\":"<<return_path::now()<<",\"base\":"<<reinterpret_cast<uintptr_t>(row.modBaseAddr)<<",\"bytes\":"<<row.modBaseSize<<",\"path\":"<<std::quoted(path)<<"}\n";
   const auto text=line.str();if(written+text.size()>4*1024*1024){return_path::write(mapping->state->error,95);break;}file<<text;written+=text.size();
  }while(Module32NextW(snap,&row));
  CloseHandle(snap);file.flush();if(!file){return_path::write(mapping->state->error,96);break;}
  for(unsigned i=0;i<100&&!return_path::read(mapping->state->stop);++i)Sleep(10);
 }
 return 0;
}
wchar_t modulePath[1100]{};
std::wstring nativeOutput;
DWORD WINAPI nativeWorker(void*){
 auto& control=*mapping->state;
 auto* header=reinterpret_cast<survey_trace::Header*>(reinterpret_cast<BYTE*>(&control)+256);
 LONG error=0;bool installed=false,restored=false;
 std::array<std::array<BYTE,12>,4> original{};std::array<void*,4> addresses{};
 if(!survey_native::configure())error=ERROR_REVISION_MISMATCH;
 if(!error){
  const auto& t=survey_native::targets;addresses={reinterpret_cast<void*>(t.set),reinterpret_cast<void*>(t.enable),reinterpret_cast<void*>(t.gate),reinterpret_cast<void*>(t.dispatch)};
  for(unsigned i=0;i<4;++i)std::memcpy(original[i].data(),addresses[i],12);
  error=survey_native::transaction(true);installed=error==NO_ERROR;
 }
 if(installed){InterlockedExchange(reinterpret_cast<volatile LONG*>(&header->reserved[0]),15);survey_native::enabled=true;
  while(!return_path::read(control.stop)&&return_path::read(header->status)<3)Sleep(2);
  survey_native::enabled=false;error=survey_native::transaction(false);
  while(survey_native::active.load())Sleep(0);
  restored=error==NO_ERROR;
  for(unsigned i=0;i<4&&restored;++i)restored=std::memcmp(original[i].data(),addresses[i],12)==0;
  if(!restored&&!error)error=ERROR_INVALID_DATA;
 }
 if(error){return_path::write(control.error,97);return_path::write(header->reason,4);}
 try{const auto temp=nativeOutput+L".tmp";std::ofstream file(temp);file<<"{\"installed\":"<<(installed?"true":"false")<<",\"restored\":"<<(restored?"true":"false")
  <<",\"error\":"<<error<<",\"faults\":"<<survey_native::faults.load()<<",\"busy\":"<<survey_native::busy.load()
  <<",\"census_overflow\":"<<survey_native::overflow.load()<<",\"observations\":"<<survey_native::tokens.load()<<"}";
  file.close();if(!file||!MoveFileExW(temp.c_str(),nativeOutput.c_str(),MOVEFILE_REPLACE_EXISTING))return_path::write(control.error,98);
 }catch(...){return_path::write(control.error,98);}
 InterlockedExchange(reinterpret_cast<volatile LONG*>(&header->reserved[1]),restored?15:0);InterlockedExchange(reinterpret_cast<volatile LONG*>(&header->reserved[2]),error);return 0;
}
BOOL attach(HMODULE module){
 if(!&ReShadeRegisterAddon)return FALSE;
 wchar_t expected[1024]{},actual[1024]{},session[128]{},output[1024]{};
 const auto e=GetEnvironmentVariableW(L"SFC_REMIX_EXPECTED_IMAGE",expected,1024),s=GetEnvironmentVariableW(L"SFC_REMIX_RETURN_SESSION",session,128),p=GetEnvironmentVariableW(L"SFC_REMIX_BROAD_OUTPUT",output,1024);
 if(!p)return TRUE; // Default off; no unrelated process observation.
 if(!e||e>=1024||!s||s>=128||p>=1024||!GetModuleFileNameW(nullptr,actual,1024)||CompareStringOrdinal(expected,-1,actual,-1,TRUE)!=CSTR_EQUAL)return FALSE;
 const BOOL restored=DetourRestoreAfterWith();if(!restored)return FALSE;
 try{mapping=std::make_unique<return_path::Mapping>(false,session);}catch(...){return FALSE;}
 auto& control=*mapping->state;control.gamePid=GetCurrentProcessId();control.startupRestored=1;control.startupVerified=1;
 wchar_t durationText[16]{};GetEnvironmentVariableW(L"SFC_SURVEY_DURATION_MS",durationText,16);
 const uint64_t duration=_wtoi64(durationText);if(duration!=10000&&duration!=90000)return FALSE;
 if(!survey_events::trace.prepare(&control,output,survey_trace::HardBytes,duration))return FALSE;
 if(!reshade::register_addon(module))return FALSE;registered=true;
 survey_events::events(true);reshade::register_event<reshade::addon_event::init_effect_runtime>(init);reshade::register_event<reshade::addon_event::destroy_effect_runtime>(destroy);
 if(swprintf_s(modulePath,L"%s.modules.jsonl",output)<0)return FALSE;
 const auto worker=CreateThread(nullptr,0,modules,modulePath,0,nullptr);if(!worker)return FALSE;CloseHandle(worker);
 nativeOutput=std::wstring(output)+L".native.json";
 const auto native=CreateThread(nullptr,0,nativeWorker,nullptr,0,nullptr);if(!native)return FALSE;CloseHandle(native);
 return TRUE;
}
}
BOOL WINAPI DllMain(HMODULE module,DWORD reason,LPVOID){
 if(DetourIsHelperProcess())return TRUE;
 if(reason==DLL_PROCESS_ATTACH)return attach(module);
 if(reason==DLL_PROCESS_DETACH&&registered){survey_events::events(false);reshade::unregister_event<reshade::addon_event::init_effect_runtime>(init);reshade::unregister_event<reshade::addon_event::destroy_effect_runtime>(destroy);reshade::unregister_addon(module);}
 return TRUE;
}
