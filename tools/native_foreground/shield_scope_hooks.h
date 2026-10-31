#pragma once
#if !defined(_M_IX86)
#error Native shield scope is x86 only
#endif
#include <windows.h>
#include <tlhelp32.h>
#include <detours.h>
#include "producer_scope.h"
#include "shield_fixture_contract.h"

namespace native_foreground::shield_hooks {
struct Owner {Identity identity{};Word ship{},shield{},manager{},resource{};};
using Resolve=bool(__cdecl*)(Word,Word,Word,Owner*);
using Notify=void(__cdecl*)(bool,const Owner*);
using Reject=void(__cdecl*)(Word,Word,Word);
inline void* originalShield{};
inline Depth originalDepth{};
inline Resolve resolve{};
inline Notify notify{};
inline Reject reject{};
inline volatile LONG active{};
inline volatile LONG enabled{};
inline Word callerReturn=0x004165AF;
struct Local {ProducerScope producer;Owner owner{};unsigned nesting{};};
inline thread_local Local local;
inline bool qualified(const Identity& id,Word resource,bool depthTest,bool depthWrite,bool additive,bool triangles) noexcept {
    return enabled&&local.nesting&&local.producer.qualifies(id,resource,depthTest,depthWrite,additive,triangles);
}
inline const Owner* current() noexcept {return enabled&&local.nesting?&local.owner:nullptr;}
inline void __cdecl onScopeEnter(const Word* saved) noexcept {
    const DWORD error=GetLastError();InterlockedIncrement(&active);
    Owner owner{};
    // PUSHFD/PUSHAD: EBX=word4,ECX=word6,original return=word9,arg1=word10.
    const bool valid=enabled&&saved[9]==callerReturn&&resolve&&resolve(saved[4],saved[6],saved[10],&owner);
    if(enabled&&!valid&&reject)reject(saved[4],saved[6],saved[10]);
    if(!local.nesting)local.owner=valid?owner:Owner{};
    ++local.nesting;local.producer.enter(valid?owner.identity:Identity{},valid?owner.resource:0);
    if(notify&&local.nesting>1)notify(false,nullptr);
    if(notify&&valid&&local.nesting==1)notify(true,&owner);
    SetLastError(error);
}
inline void __cdecl onScopeLeave() noexcept {
    const DWORD error=GetLastError();
    if(local.nesting) {
        if(notify&&local.nesting==1&&local.owner.identity.valid())notify(false,&local.owner);
        local.producer.leave();if(!--local.nesting)local.owner={};
    }
    InterlockedDecrement(&active);SetLastError(error);
}
inline void __declspec(naked) shield() {
    __asm {
        pushfd
        pushad
        mov ebx,esp
        sub esp,528
        lea eax,[esp+15]
        and eax,0fffffff0h
        fxsave [eax]
        push eax
        push ebx
        call onScopeEnter
        add esp,4
        pop eax
        fxrstor [eax]
        add esp,528
        popad
        popfd
        push dword ptr[esp+4]
        call dword ptr[originalShield]
        pushfd
        pushad
        sub esp,528
        lea eax,[esp+15]
        and eax,0fffffff0h
        fxsave [eax]
        push eax
        call onScopeLeave
        pop eax
        fxrstor [eax]
        add esp,528
        popad
        popfd
        ret 4
    }
}
inline Word __fastcall depth(void* manager,void*,Word value) {
    const DWORD before=GetLastError();InterlockedIncrement(&active);
    const bool ours=enabled&&local.nesting&&local.owner.manager==reinterpret_cast<Word>(manager);
    if(ours)local.producer.beforeDepthWrite(value!=0);
    SetLastError(before);const Word result=originalDepth(manager,value);const DWORD after=GetLastError();
    if(ours)local.producer.afterDepthWrite(value!=0);
    InterlockedDecrement(&active);SetLastError(after);return result;
}
// Setup/teardown worker only. Suspend/update all other process threads through
// Detours; no transaction, enumeration or wait in an observed render callback.
inline LONG transaction(bool attach) {
    LONG error=DetourTransactionBegin();if(error!=NO_ERROR)return error;
    HANDLE threads[256]{};unsigned used=0;
    HANDLE snapshot=CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD,0);
    if(snapshot==INVALID_HANDLE_VALUE){DetourTransactionAbort();return GetLastError();}
    THREADENTRY32 item{};item.dwSize=sizeof(item);BOOL more=Thread32First(snapshot,&item);
    if(!more)error=GetLastError();
    while(more&&error==NO_ERROR) {
        if(item.th32OwnerProcessID==GetCurrentProcessId()&&item.th32ThreadID!=GetCurrentThreadId()) {
            if(used==256){error=ERROR_BUFFER_OVERFLOW;break;}
            HANDLE thread=OpenThread(THREAD_SUSPEND_RESUME|THREAD_GET_CONTEXT|THREAD_SET_CONTEXT|THREAD_QUERY_INFORMATION,FALSE,item.th32ThreadID);
            if(!thread){error=GetLastError();break;}threads[used++]=thread;error=DetourUpdateThread(thread);
        }
        more=Thread32Next(snapshot,&item);if(!more&&GetLastError()!=ERROR_NO_MORE_FILES)error=GetLastError();
    }
    CloseHandle(snapshot);if(error==NO_ERROR)error=DetourUpdateThread(GetCurrentThread());
    if(error==NO_ERROR)error=attach?DetourAttach(&originalShield,reinterpret_cast<void*>(shield)):DetourDetach(&originalShield,reinterpret_cast<void*>(shield));
    if(error==NO_ERROR)error=attach?DetourAttach(reinterpret_cast<void**>(&originalDepth),reinterpret_cast<void*>(depth)):DetourDetach(reinterpret_cast<void**>(&originalDepth),reinterpret_cast<void*>(depth));
    if(error==NO_ERROR)error=DetourTransactionCommit();else DetourTransactionAbort();
    for(unsigned i=0;i<used;++i)CloseHandle(threads[i]);return error;
}
} // namespace native_foreground::shield_hooks
