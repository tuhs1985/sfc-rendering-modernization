// x86 read-only engine-phase search. Startup install, worker detach, no disk I/O.
#pragma once
#include <windows.h>
#include <tlhelp32.h>
#include <d3d11.h>
#include <wrl/client.h>
#include <detours.h>
#include <cstring>
#include "depth_search_wire.h"
namespace depth_search {
using Microsoft::WRL::ComPtr;
inline void* targets[4]{};inline void* originals[4]{};
inline volatile LONG captureEnabled=0;
inline void* afterFlushResume=nullptr;
class Search;
inline Search* current=nullptr;
inline void sample(uint32_t phase);
// Preserve complete state around our observer, including flags/DF and FP/SIMD.
// The inactive path also restores flags before jumping to original control flow.
#define DEPTH_STUB(number) \
 __asm {pushfd} \
 __asm {cmp dword ptr [captureEnabled],0} \
 __asm {jne observe} \
 __asm {popfd} \
 __asm {jmp dword ptr [originals + number*4]} \
 __asm {observe: popfd} \
 __asm {pushfd} \
 __asm {pushad} \
 __asm {cld} \
 __asm {sub esp,544} \
 __asm {mov eax,esp} \
 __asm {add eax,15} \
 __asm {and eax,0FFFFFFF0h} \
 __asm {fxsave [eax]} \
 __asm {push number} \
 __asm {call sample} \
 __asm {add esp,4} \
 __asm {mov eax,esp} \
 __asm {add eax,15} \
 __asm {and eax,0FFFFFFF0h} \
 __asm {fxrstor [eax]} \
 __asm {add esp,544} \
 __asm {popad} \
 __asm {popfd} \
 __asm {jmp dword ptr [originals + number*4]}
__declspec(naked) inline void beginStub(){DEPTH_STUB(0)}
__declspec(naked) inline void endStub(){DEPTH_STUB(1)}
// The stolen bytes contain a CALL: keep its return path in this resident DLL,
// never in a trampoline that a concurrent detach could free.
__declspec(naked) inline void flushStub(){
 __asm {pushfd}
 __asm {cmp dword ptr [captureEnabled],0}
 __asm {jne observe}
 __asm {popfd}
 __asm {jmp executeOriginalCall}
 __asm {observe: popfd}
 __asm {pushfd}
 __asm {pushad}
 __asm {cld}
 __asm {sub esp,544}
 __asm {mov eax,esp}
 __asm {add eax,15}
 __asm {and eax,0FFFFFFF0h}
 __asm {fxsave [eax]}
 __asm {push 2}
 __asm {call sample}
 __asm {add esp,4}
 __asm {mov eax,esp}
 __asm {add eax,15}
 __asm {and eax,0FFFFFFF0h}
 __asm {fxrstor [eax]}
 __asm {add esp,544}
 __asm {popad}
 __asm {popfd}
 __asm {executeOriginalCall: call dword ptr [ecx+28h]}
 __asm {test eax,eax}
 __asm {jmp dword ptr [afterFlushResume]}
}
__declspec(naked) inline void presentStub(){DEPTH_STUB(3)}
#undef DEPTH_STUB
inline void* stubs[]={reinterpret_cast<void*>(&beginStub),reinterpret_cast<void*>(&endStub),reinterpret_cast<void*>(&flushStub),reinterpret_cast<void*>(&presentStub)};
class Search {
  SRWLOCK guard=SRWLOCK_INIT;
  ComPtr<ID3D11DeviceContext> context;
  HANDLE worker=nullptr;volatile LONG* stop=nullptr;volatile LONG* armed=nullptr;
  Data* data=nullptr;
  void startWorker(){
    if(context&&!worker&&read(data->status)==Installed){
      worker=CreateThread(nullptr,0,run,this,0,nullptr);
      if(!worker){write(data->error,5);write(data->status,Failed);return;}
      write(captureEnabled,1);
    }
  }
  static DWORD WINAPI run(void* p){
    auto& self=*static_cast<Search*>(p);
    while(!read(*self.stop))Sleep(20);
    write(captureEnabled,0);write(self.data->status,Stopping);
    const bool ok=self.detach();self.data->endTick=GetTickCount();
    write(self.data->status,ok?Removed:Failed);return ok?0:1;
  }
  bool detach(){
    if(read(data->installedMask)!=15){write(data->error,7);return false;}
    // Outside render callbacks and loader lock. Detours enrolls/suspends threads
    // and adjusts instruction pointers atomically; abort resumes enrolled threads.
    if(DetourTransactionBegin()!=NO_ERROR){write(data->error,8);return false;}
    HANDLE list=CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD,0);
    if(list==INVALID_HANDLE_VALUE){DetourTransactionAbort();write(data->error,9);return false;}
    THREADENTRY32 entry{};entry.dwSize=sizeof(entry);bool ok=Thread32First(list,&entry)!=FALSE;
    while(ok){
      if(entry.th32OwnerProcessID==GetCurrentProcessId()&&entry.th32ThreadID!=GetCurrentThreadId()){
        HANDLE h=OpenThread(THREAD_SUSPEND_RESUME|THREAD_GET_CONTEXT|THREAD_SET_CONTEXT|THREAD_QUERY_INFORMATION,FALSE,entry.th32ThreadID);
        if(!h){ok=false;break;}
        const auto result=DetourUpdateThread(h);
        // Detours retains HANDLE until commit, close only after commit/abort.
        if(result!=NO_ERROR){CloseHandle(h);ok=false;break;}
        enrolled[enrolledCount++]=h;
        if(enrolledCount==256){ok=false;break;}
      }
      if(!Thread32Next(list,&entry)){ok=GetLastError()==ERROR_NO_MORE_FILES;break;}
    }
    CloseHandle(list);
    for(unsigned i=0;ok&&i<4;++i)ok=DetourDetach(&originals[i],stubs[i])==NO_ERROR;
    if(ok)ok=DetourTransactionCommit()==NO_ERROR;else DetourTransactionAbort();
    for(unsigned i=0;i<enrolledCount;++i)CloseHandle(enrolled[i]);enrolledCount=0;
    if(ok){
      for(unsigned i=0;i<4;++i)if(std::memcmp(targets[i],saved[i],lengths[i]))ok=false;
      if(ok)write(data->restoredMask,15);
    }
    if(!ok)write(data->error,10);return ok;
  }
  HANDLE enrolled[256]{};unsigned enrolledCount=0;
  BYTE saved[4][9]{};unsigned lengths[4]{};
public:
  ~Search(){if(worker)CloseHandle(worker);}
  void prepare(void* mapping,volatile LONG& stopFlag,volatile LONG& armedFlag){
    data=reinterpret_cast<Data*>(static_cast<BYTE*>(mapping)+256);ZeroMemory(data,sizeof(*data));
    data->magic=Magic;data->version=Version;data->bytes=sizeof(Data);data->capacity=Capacity;
    stop=&stopFlag;armed=&armedFlag;current=this;write(data->status,Prepared);
  }
  bool install(void* const* functions,bool fixture){
    const BYTE common[]={0x53,0x56,0x8B,0xF1,0x57};
    const BYTE afterFlush[]={0xFF,0x51,0x28,0x85,0xC0};
    const BYTE present[]={0x56,0x8B,0xF1,0x8A,0x86,0x28,0x3C,0,0};
    if(!data||read(data->status)!=Prepared)return false;
    // Main-image code only. Never adopt pointers from another DLL or session.
    for(unsigned i=0;i<4;++i){
      HMODULE owner=nullptr;
      if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,reinterpret_cast<LPCWSTR>(functions[i]),&owner)||owner!=GetModuleHandleW(nullptr)){write(data->error,1);write(data->status,Failed);return false;}
      lengths[i]=fixture?5:(i==3?9:5);
      const auto* expected=i==2?afterFlush:((!fixture&&i==3)?present:common);
      if(std::memcmp(functions[i],expected,lengths[i])){write(data->error,2);write(data->status,Failed);return false;}
      targets[i]=originals[i]=functions[i];std::memcpy(saved[i],functions[i],lengths[i]);
    }
    afterFlushResume=static_cast<BYTE*>(targets[2])+5;
    if(DetourTransactionBegin()!=NO_ERROR){write(data->error,3);write(data->status,Failed);return false;}
    bool ok=DetourUpdateThread(GetCurrentThread())==NO_ERROR;
    for(unsigned i=0;ok&&i<4;++i)ok=DetourAttach(&originals[i],stubs[i])==NO_ERROR;
    if(ok)ok=DetourTransactionCommit()==NO_ERROR;else DetourTransactionAbort();
    if(!ok){write(data->error,4);write(data->status,Failed);return false;}
    write(data->installedMask,15);write(data->status,Installed);startWorker();return true;
  }
  void setContext(ID3D11DeviceContext* value){
    AcquireSRWLockExclusive(&guard);context=value;
    if(value){data->contextThread=GetCurrentThreadId();++data->epoch;}
    ReleaseSRWLockExclusive(&guard);
    if(value)startWorker();
  }
  void observe(uint32_t phase){
    if(!data||phase>=Phases||!read(*armed)||read(*stop))return;
    if(!valid(*data)){write(data->error,11);write(captureEnabled,0);return;}
    if(!data->startTick)data->startTick=GetTickCount();
    auto& c=data->phases[phase];c.lastTick=GetTickCount();InterlockedIncrement(&c.calls);InterlockedOr(&data->seenMask,1u<<phase);
    if(!TryAcquireSRWLockShared(&guard)){InterlockedIncrement(&c.busy);return;}
    if(!context){InterlockedIncrement(&c.noContext);ReleaseSRWLockShared(&guard);return;}
    if(GetCurrentThreadId()!=data->contextThread){InterlockedIncrement(&c.wrongThread);ReleaseSRWLockShared(&guard);return;}
    ComPtr<ID3D11DepthStencilView> view;context->OMGetRenderTargets(0,nullptr,&view);
    if(!view)InterlockedIncrement(&c.missing);
    else{
      ComPtr<ID3D11Resource> resource;view->GetResource(&resource);ComPtr<ID3D11Texture2D> texture;
      if(FAILED(resource.As(&texture)))InterlockedIncrement(&c.invalid);
      else{
        D3D11_TEXTURE2D_DESC desc{};texture->GetDesc(&desc);D3D11_DEPTH_STENCIL_VIEW_DESC vd{};view->GetDesc(&vd);
        Resource r{};r.epoch=data->epoch;r.resourceLabel=static_cast<uint32_t>(reinterpret_cast<uintptr_t>(resource.Get()));r.viewLabel=static_cast<uint32_t>(reinterpret_cast<uintptr_t>(view.Get()));
        r.width=desc.Width;r.height=desc.Height;r.format=desc.Format;r.viewFormat=vd.Format;r.flags=desc.BindFlags;r.samples=desc.SampleDesc.Count;
        InterlockedIncrement(&c.found);retain(*data,r,phase,GetTickCount());
      }
    }
    ReleaseSRWLockShared(&guard);
  }
};
inline void sample(uint32_t phase){if(current)current->observe(phase);}
}
