// External host only: initialize once, then sleep until a qualified scene arrives.
#pragma once
#include <fstream>
namespace warm_start {
constexpr uint32_t Magic=0x31524157;
struct Activation {uint32_t magic,version,bytes,pid,session[4],model,source;uint64_t mask,cookie;BYTE asset[32];float offset;uint32_t reserved;uint64_t checksum;};
static_assert(sizeof(Activation)==104,"warm activation layout");
struct Cancelled{};
inline bool requested(){wchar_t flag[2]{};return GetEnvironmentVariableW(L"SFC_D3D9_PREWARM",flag,2)==1&&flag[0]==L'1';}
inline std::array<uint32_t,4> session(){
 wchar_t name[128]{};const auto size=GetEnvironmentVariableW(L"SFC_REMIX_CALIBRATION_SCENE",name,128);
 require(size>32&&size<128,"warm session");std::array<uint32_t,4> words{};
 for(unsigned i=0;i<4;++i){wchar_t* end=nullptr;const auto part=std::wstring(name+size-32+i*8,8);words[i]=wcstoul(part.c_str(),&end,16);require(end&&!*end,"warm session hex");}return words;
}
template<class Pump> inline void wait(const fs::path& root,Pump pump){
 const auto words=session();wchar_t pidText[16]{};GetEnvironmentVariableW(L"SFC_D3D9_GAME_PID",pidText,16);const auto pid=wcstoul(pidText,nullptr,10);
 require(pid!=0,"warm verified game PID");HANDLE game=OpenProcess(SYNCHRONIZE,FALSE,pid);require(game!=nullptr,"warm game liveness");
 struct Close {HANDLE h;~Close(){CloseHandle(h);}} close{game};
 LARGE_INTEGER now{};QueryPerformanceCounter(&now);
 std::array<uint64_t,2> ready{static_cast<uint64_t>(now.QuadPart),GetCurrentProcessId()};
 {std::ofstream file(root/L"renderer-ready.bin",std::ios::binary);file.write(reinterpret_cast<const char*>(ready.data()),sizeof(ready));require(bool(file),"warm readiness receipt");}
 const auto limit=GetTickCount64()+180000;
 for(;;){
  if(fs::exists(root/L"renderer-cancel")||WaitForSingleObject(game,0)!=WAIT_TIMEOUT)throw Cancelled{};
  require(GetTickCount64()<limit,"warm activation180s limit");
  pump(); // Optional external-host work only;normal idle uses the empty callback.
  if(fs::exists(root/L"renderer-activate.bin")){
   const auto raw=read(root/L"renderer-activate.bin",sizeof(Activation));require(raw.size()==sizeof(Activation),"warm activation length");Activation a{};memcpy(&a,raw.data(),sizeof(a));
   require(a.magic==Magic&&a.version==1&&a.bytes==sizeof(a)&&a.pid==pid&&!memcmp(a.session,words.data(),16)&&a.model&&a.source&&a.mask&&a.cookie&&!a.reserved&&std::isfinite(a.offset)&&a.offset<=0&&a.offset>=-1e6f&&a.checksum==output_wire::hash(raw.data(),raw.size()-8),"warm activation identity/checksum");
   auto set=[](const wchar_t* key,const std::wstring& value){require(SetEnvironmentVariableW(key,value.c_str())!=FALSE,"warm environment apply");};
   set(L"SFC_D3D9_EXPECTED_MODEL",std::to_wstring(a.model));set(L"SFC_D3D9_EXPECTED_SOURCE",std::to_wstring(a.source));
   wchar_t hex[65]{};swprintf_s(hex,L"%llx",a.mask);set(L"SFC_D3D9_INITIAL_ASSET_MASK",hex);swprintf_s(hex,L"%llx",a.cookie);set(L"SFC_D3D9_REBIND_COOKIE",hex);
   bool any=false;for(unsigned i=0;i<32;++i){swprintf_s(hex+i*2,65-i*2,L"%02x",unsigned(a.asset[i]));any|=a.asset[i]!=0;}require(any,"warm asset identity");set(L"SFC_D3D9_ASSET_SHA256",hex);set(L"SFC_D3D9_OFFSET_X",std::to_wstring(a.offset));
   return;
  }
  Sleep(10); // No Presents, image generation, busy spin or game callback waits.
 }
}
inline void wait(const fs::path& root){wait(root,[]{});}
}
