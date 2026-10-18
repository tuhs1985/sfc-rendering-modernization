// Version2 is a diagnostic image contract, not a ship-replacement contract.
#pragma once
#include <windows.h>
#include <sddl.h>
#include <objbase.h>
#include <array>
#include <string>
#include <stdexcept>
#include <cstdint>
#include <cmath>
namespace return_path {
constexpr uint32_t Magic=0x53465232,Version=2,Format=87,Dimension=256;
constexpr wchar_t Prefix[]=L"Local\\SFC-Remix-Return-";
struct alignas(64) State {
  uint32_t magic,version,bytes,creatorPid,gamePid,width,height,format;
  uint64_t sharedHandle,qpcFrequency,renderedAt,renderFrame;
  volatile LONG epoch,ready,armed,enabled,stop,produced,acknowledged,presented,error;
  volatile LONG copyCount,drawCount,staleCount,skipCount,clearCount,lastWidth,lastHeight;
  volatile LONG startupRestored,startupVerified,renderEpoch,presentedEpoch;
  // Optional read-only visibility observation in formerly reserved bytes.
  // Mandatory v2 prefix unchanged; version0 means extension absent/off.
  volatile LONG visibilityVersion,visibilitySamples,depthPresentSamples;
  volatile LONG depthWidth,depthHeight,depthFormat,depthBindFlags,depthMultisamples;
  volatile LONG visibilityScope; // 0 legacy/absent,1 overlay,2 pre-effects Present
  volatile LONG depthViewFormat;
  std::array<unsigned char,72> padding;
};
static_assert(sizeof(State)==256);
static_assert(offsetof(State,sharedHandle)==32&&offsetof(State,epoch)==64);
static_assert(offsetof(State,visibilityVersion)==144);
static_assert(offsetof(State,visibilityScope)==176);
inline LONG read(volatile LONG& value){return InterlockedCompareExchange(&value,0,0);}
inline void write(volatile LONG& value,LONG next){InterlockedExchange(&value,next);}
inline uint64_t now(){LARGE_INTEGER n{};QueryPerformanceCounter(&n);return static_cast<uint64_t>(n.QuadPart);}
inline bool valid(const State& s){return s.magic==Magic&&s.version==Version&&s.bytes==sizeof(State)&&s.creatorPid&&s.width==Dimension&&s.height==Dimension&&s.format==Format&&s.qpcFrequency;}
inline bool fresh(uint64_t captured,uint64_t current,uint64_t frequency){return captured&&current>=captured&&frequency&&current-captured<=frequency;}
inline bool displaySupported(float width,float height){return std::isfinite(width)&&std::isfinite(height)&&width>=544&&height>=384&&width<=1920&&height<=1080;}
struct Mapping {
  HANDLE handle=nullptr;State* state=nullptr;std::wstring name;
  Mapping(const Mapping&)=delete;Mapping& operator=(const Mapping&)=delete;
  explicit Mapping(bool create,const wchar_t* existing=nullptr){
    if(create){
      GUID guid{};if(FAILED(CoCreateGuid(&guid)))throw std::runtime_error("return GUID");
      wchar_t text[40]{};if(!StringFromGUID2(guid,text,40))throw std::runtime_error("return GUID string");name=std::wstring(Prefix)+text;
      HANDLE token=nullptr;if(!OpenProcessToken(GetCurrentProcess(),TOKEN_QUERY,&token))throw std::runtime_error("return token");
      alignas(TOKEN_USER) std::array<unsigned char,1024> user{};DWORD n=0;
      const BOOL got=GetTokenInformation(token,TokenUser,user.data(),static_cast<DWORD>(user.size()),&n);CloseHandle(token);
      if(!got)throw std::runtime_error("return SID");
      LPWSTR sid=nullptr;if(!ConvertSidToStringSidW(reinterpret_cast<TOKEN_USER*>(user.data())->User.Sid,&sid))throw std::runtime_error("return SID string");
      const auto textDacl=std::wstring(L"D:P(A;;GA;;;")+sid+L")";LocalFree(sid);
      PSECURITY_DESCRIPTOR sd=nullptr;if(!ConvertStringSecurityDescriptorToSecurityDescriptorW(textDacl.c_str(),SDDL_REVISION_1,&sd,nullptr))throw std::runtime_error("return DACL");
      SECURITY_ATTRIBUTES sa{sizeof(sa),sd,FALSE};handle=CreateFileMappingW(INVALID_HANDLE_VALUE,&sa,PAGE_READWRITE,0,4096,name.c_str());const auto error=GetLastError();LocalFree(sd);
      if(!handle||error==ERROR_ALREADY_EXISTS){if(handle)CloseHandle(handle);handle=nullptr;throw std::runtime_error("unique return mapping");}
    }else{
      if(!existing)throw std::runtime_error("missing return mapping");name=existing;const std::wstring prefix(Prefix);GUID guid{};
      if(name.size()!=prefix.size()+38||name.compare(0,prefix.size(),prefix)||FAILED(CLSIDFromString(name.c_str()+prefix.size(),&guid)))throw std::runtime_error("invalid return name");
      handle=OpenFileMappingW(FILE_MAP_ALL_ACCESS,FALSE,name.c_str());if(!handle)throw std::runtime_error("open return mapping");
    }
    state=static_cast<State*>(MapViewOfFile(handle,FILE_MAP_ALL_ACCESS,0,0,4096));
    if(!state){CloseHandle(handle);handle=nullptr;throw std::runtime_error("map return state");}
    if(create){ZeroMemory(state,4096);state->magic=Magic;state->version=Version;state->bytes=sizeof(State);state->creatorPid=GetCurrentProcessId();state->width=state->height=Dimension;state->format=Format;LARGE_INTEGER f{};QueryPerformanceFrequency(&f);state->qpcFrequency=f.QuadPart;}
    else if(!valid(*state)){UnmapViewOfFile(state);CloseHandle(handle);state=nullptr;handle=nullptr;throw std::runtime_error("return header mismatch");}
  }
  ~Mapping(){if(state)UnmapViewOfFile(state);if(handle)CloseHandle(handle);}
};
}
