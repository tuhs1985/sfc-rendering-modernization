// Standalone one-surface GPU ownership qualification, NOT an SFC frame contract.
#pragma once
#include <windows.h>
#include <sddl.h>
#include <objbase.h>
#include <d3d11.h>
#include <dxgi.h>
#include <wrl/client.h>
#include <array>
#include <string>
#include <stdexcept>
#include <cstdint>

namespace output_probe {
constexpr uint32_t kMagic=0x53464352, kVersion=1, kDimension=256;
constexpr wchar_t kPrefix[]=L"Local\\SFC-Remix-Output-";
struct alignas(64) State {
  uint32_t magic,version,bytes,creatorPid,width,height,format,reserved;
  uint64_t sharedHandle,expectedHash,consumedHash,centroidNumerator;
  uint32_t greenPixels,renderFrame;
  volatile LONG ready,produced,consumed,stop,error;
  std::array<unsigned char,36> padding;
};
static_assert(sizeof(State)==128);
inline LONG load(volatile LONG& value){return InterlockedCompareExchange(&value,0,0);}
inline void store(volatile LONG& value,LONG next){InterlockedExchange(&value,next);}
inline bool valid(const State& s){
  return s.magic==kMagic&&s.version==kVersion&&s.bytes==sizeof(State)&&s.creatorPid&&
    s.width==kDimension&&s.height==kDimension&&s.format==DXGI_FORMAT_B8G8R8A8_UNORM&&
    !s.reserved;
}
inline bool canPublish(State& s,LONG next){return valid(s)&&next>=1&&next<=2&&load(s.produced)==next-1&&load(s.consumed)==next-1&&!load(s.stop)&&!load(s.error);}
inline bool canConsume(State& s,LONG last,LONG next){return valid(s)&&next==last+1&&next<=2&&next>=1;}
inline void checked(HRESULT result,const char* stage){if(FAILED(result))throw std::runtime_error(stage);}
struct Handle {
  HANDLE value=nullptr;
  Handle()=default;Handle(const Handle&)=delete;Handle& operator=(const Handle&)=delete;
  ~Handle(){if(value&&value!=INVALID_HANDLE_VALUE)CloseHandle(value);}
};
struct Channel {
  Handle mapping,job,process;State* state=nullptr;std::wstring name;
  Channel(const Channel&)=delete;Channel& operator=(const Channel&)=delete;
  explicit Channel(bool create,const wchar_t* existing=nullptr){
    if(create){
      GUID guid{};checked(CoCreateGuid(&guid),"session GUID");
      wchar_t text[40]{};if(!StringFromGUID2(guid,text,40))throw std::runtime_error("GUID string");
      name=std::wstring(kPrefix)+text;
      Handle token;if(!OpenProcessToken(GetCurrentProcess(),TOKEN_QUERY,&token.value))throw std::runtime_error("user token");
      alignas(TOKEN_USER) std::array<unsigned char,1024> user{};DWORD size=0;
      if(!GetTokenInformation(token.value,TokenUser,user.data(),static_cast<DWORD>(user.size()),&size))throw std::runtime_error("user SID");
      LPWSTR sid=nullptr;
      if(!ConvertSidToStringSidW(reinterpret_cast<TOKEN_USER*>(user.data())->User.Sid,&sid))throw std::runtime_error("SID string");
      const auto sddl=std::wstring(L"D:P(A;;GA;;;")+sid+L")";LocalFree(sid);
      PSECURITY_DESCRIPTOR descriptor=nullptr;
      if(!ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl.c_str(),SDDL_REVISION_1,&descriptor,nullptr))throw std::runtime_error("user-only DACL");
      SECURITY_ATTRIBUTES sa{sizeof(sa),descriptor,FALSE};
      mapping.value=CreateFileMappingW(INVALID_HANDLE_VALUE,&sa,PAGE_READWRITE,0,4096,name.c_str());
      const auto error=GetLastError();LocalFree(descriptor);
      if(!mapping.value||error==ERROR_ALREADY_EXISTS)throw std::runtime_error("unique mapping");
    }else{
      if(!existing)throw std::runtime_error("missing session name");name=existing;
      const std::wstring prefix(kPrefix);
      if(name.size()!=prefix.size()+38||name.compare(0,prefix.size(),prefix))throw std::runtime_error("invalid session name");
      GUID guid{};checked(CLSIDFromString(name.c_str()+prefix.size(),&guid),"invalid session GUID");
      mapping.value=OpenFileMappingW(FILE_MAP_ALL_ACCESS,FALSE,name.c_str());
      if(!mapping.value)throw std::runtime_error("open user mapping");
    }
    state=static_cast<State*>(MapViewOfFile(mapping.value,FILE_MAP_ALL_ACCESS,0,0,4096));
    if(!state)throw std::runtime_error("map state");
    if(create){
      ZeroMemory(state,sizeof(*state));state->magic=kMagic;state->version=kVersion;state->bytes=sizeof(State);
      state->creatorPid=GetCurrentProcessId();state->width=256;state->height=256;state->format=DXGI_FORMAT_B8G8R8A8_UNORM;
    }else if(!valid(*state)){UnmapViewOfFile(state);state=nullptr;throw std::runtime_error("invalid channel header");}
  }
  ~Channel(){
    if(state)store(state->stop,1);
    if(process.value&&WaitForSingleObject(process.value,2000)==WAIT_TIMEOUT)TerminateJobObject(job.value,99);
    if(state)UnmapViewOfFile(state);
  }
  void start(const wchar_t* consumerSwitch=L"--consumer",bool x86=false){
    job.value=CreateJobObjectW(nullptr,nullptr);if(!job.value)throw std::runtime_error("owned job");
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits{};limits.BasicLimitInformation.LimitFlags=JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
    if(!SetInformationJobObject(job.value,JobObjectExtendedLimitInformation,&limits,sizeof(limits)))throw std::runtime_error("job limits");
    wchar_t exe[32768]{};const auto n=GetModuleFileNameW(nullptr,exe,32768);
    if(!n||n==32768)throw std::runtime_error("own executable path");
    std::wstring executable(exe);
    if(x86){const auto slash=executable.find_last_of(L"\\/");if(slash==std::wstring::npos)throw std::runtime_error("consumer sibling path");executable.resize(slash+1);executable+=L"output_consumer_x86.exe";}
    auto command=L"\""+executable+L"\" "+consumerSwitch+L" \""+name+L"\"";
    STARTUPINFOW startup{};startup.cb=sizeof(startup);PROCESS_INFORMATION child{};
    if(!CreateProcessW(executable.c_str(),command.data(),nullptr,nullptr,FALSE,CREATE_SUSPENDED|CREATE_NO_WINDOW,nullptr,nullptr,&startup,&child))throw std::runtime_error("owned consumer");
    process.value=child.hProcess;Handle thread;thread.value=child.hThread;
    if(!AssignProcessToJobObject(job.value,process.value)){TerminateProcess(process.value,98);throw std::runtime_error("consumer job assignment");}
    if(ResumeThread(thread.value)==static_cast<DWORD>(-1))throw std::runtime_error("resume consumer");
    wait(state->ready,1,5000);
    if(!valid(*state)||!state->sharedHandle)throw std::runtime_error("consumer resource descriptor");
  }
  void wait(volatile LONG& field,LONG expected,ULONGLONG timeout){
    const auto end=GetTickCount64()+timeout;
    while(load(field)!=expected){
      if(load(state->error)||load(state->stop)||GetTickCount64()>end||
         (process.value&&WaitForSingleObject(process.value,0)==WAIT_OBJECT_0))throw std::runtime_error("consumer disconnected/timeout/error");
      Sleep(1);
    }
  }
  void publish(LONG sequence,uint32_t frame,uint64_t hash){
    if(!canPublish(*state,sequence))throw std::runtime_error("ownership sequence");
    state->expectedHash=hash;state->renderFrame=frame;store(state->produced,sequence);
    wait(state->consumed,sequence,5000);
    if(state->consumedHash!=hash||!state->greenPixels)throw std::runtime_error("consumer pixels disagree");
  }
  void finish(){
    store(state->stop,1);
    if(WaitForSingleObject(process.value,5000)!=WAIT_OBJECT_0)throw std::runtime_error("consumer shutdown timeout");
    DWORD code=1;if(!GetExitCodeProcess(process.value,&code)||code)throw std::runtime_error("consumer abnormal exit");
  }
};
inline int consume(const wchar_t* name,int fault=0){
  using Microsoft::WRL::ComPtr;
  Channel channel(false,name);auto& state=*channel.state;
  try{
    ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context;
    checked(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&device,nullptr,&context),"consumer D3D11");
    D3D11_TEXTURE2D_DESC desc{};desc.Width=256;desc.Height=256;desc.MipLevels=1;desc.ArraySize=1;
    desc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;desc.SampleDesc.Count=1;desc.BindFlags=D3D11_BIND_SHADER_RESOURCE|D3D11_BIND_RENDER_TARGET;
    desc.MiscFlags=D3D11_RESOURCE_MISC_SHARED;
    ComPtr<ID3D11Texture2D> texture;checked(device->CreateTexture2D(&desc,nullptr,&texture),"consumer output allocation");
    ComPtr<IDXGIResource> resource;checked(texture.As(&resource),"consumer DXGI");HANDLE shared=nullptr;checked(resource->GetSharedHandle(&shared),"consumer export");
    state.sharedHandle=reinterpret_cast<uintptr_t>(shared);
    desc.Usage=D3D11_USAGE_STAGING;desc.BindFlags=0;desc.MiscFlags=0;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
    ComPtr<ID3D11Texture2D> staging;checked(device->CreateTexture2D(&desc,nullptr,&staging),"consumer verification staging");
    store(state.ready,1);const auto deadline=GetTickCount64()+110000;
    LONG last=0;
    while(!load(state.stop)){
      if(GetTickCount64()>deadline)throw std::runtime_error("consumer duration cap");
      const auto sequence=load(state.produced);
      if(sequence==last){Sleep(1);continue;}
      if(!canConsume(state,last,sequence))throw std::runtime_error("invalid consumer sequence/header");
      if(fault==1)Sleep(6000); // Explicit standalone slow-consumer fault, not production behavior.
      if(fault==2)return 9; // Owned consumer exits during an in-flight output.
      context->CopyResource(staging.Get(),texture.Get());context->Flush();
      D3D11_MAPPED_SUBRESOURCE pixels{};checked(context->Map(staging.Get(),0,D3D11_MAP_READ,0,&pixels),"consumer GPU completion");
      uint64_t hash=14695981039346656037ULL,sumX=0;uint32_t green=0;
      for(unsigned y=0;y<256;++y){const auto* row=static_cast<const unsigned char*>(pixels.pData)+y*pixels.RowPitch;
        for(unsigned x=0;x<256;++x){for(unsigned b=0;b<4;++b){hash^=row[x*4+b];hash*=1099511628211ULL;}
          if(row[x*4+1]>row[x*4]+20&&row[x*4+1]>row[x*4+2]+20){++green;sumX+=x;}}}
      context->Unmap(staging.Get(),0); // GPU copy/read completed before acknowledgment.
      if(hash!=state.expectedHash||!green)throw std::runtime_error("consumer image/provenance mismatch");
      state.consumedHash=hash;state.greenPixels=green;state.centroidNumerator=sumX;
      last=sequence;store(state.consumed,last);
    }
    return last==2?0:4;
  }catch(...){store(state.error,1);return 3;}
}
}
