#include "shield_scope_hooks.h"
#include "shield_controller.h"
#include <iostream>
#include <cstring>
#include <xmmintrin.h>
using namespace native_foreground;
namespace hooks=native_foreground::shield_hooks;
static unsigned checks;
static void require(bool b,const char* why){++checks;if(!b)throw std::runtime_error(why);}
static unsigned entries,exits,flushes,qualifiedFlushes,bodyQualified;
static bool argsGood=true;
using Word=hooks::Word;
static bool depthWrite=true;
static const Identity identity{1,5,7,9};
static Word __declspec(noinline) __fastcall sourceDepth(void* manager,void*,Word value) {
    argsGood&=reinterpret_cast<Word>(manager)==0x33;
    ++flushes;if(hooks::qualified(identity,42,true,depthWrite,true,true))++qualifiedFlushes;
    depthWrite=value!=0;SetLastError(321);return 0x12340000+value;
}
static Word __declspec(noinline) __fastcall sourceShield(void* self,void*,Word manager) {
    argsGood&=reinterpret_cast<Word>(self)==0x22&&manager==0x33;
    const auto off=sourceDepth(reinterpret_cast<void*>(manager),nullptr,0);
    argsGood&=off==0x12340000&&GetLastError()==321;
    if(hooks::qualified(identity,42,true,depthWrite,true,true))++bodyQualified;
    const auto on=sourceDepth(reinterpret_cast<void*>(manager),nullptr,1);
    argsGood&=on==0x12340001&&GetLastError()==321;
    SetLastError(987);
    __asm {mov eax,012345678h
        movd xmm0,eax}
    return 0xf00dface;
}
static bool __cdecl resolve(Word ship,Word shield,Word manager,hooks::Owner* out) {
    if(ship!=0x11||shield!=0x22||manager!=0x33)return false;
    *out={identity,ship,shield,manager,42};return true;
}
static void __cdecl notify(bool begin,const hooks::Owner*) {
    if(begin)++entries;else ++exits;
    _mm_setcsr((_mm_getcsr()&~_MM_ROUND_MASK)|_MM_ROUND_TOWARD_ZERO);
    __asm pxor xmm0,xmm0
}
// Reproduce the native CALL with owner in EBX, shield in ECX and one stack arg.
static Word __declspec(naked) invoke(Word,Word,Word) {
    __asm {
        push ebx
        mov ebx,[esp+8]
        mov ecx,[esp+12]
        lea eax,returnHere
        mov hooks::callerReturn,eax
        push dword ptr[esp+16]
        xor edx,edx
        call sourceShield
    returnHere:
        pop ebx
        ret
    }
}
int main(){try {
    BYTE shieldBytes[12]{},depthBytes[12]{};
    memcpy(shieldBytes,reinterpret_cast<void*>(sourceShield),12);memcpy(depthBytes,reinterpret_cast<void*>(sourceDepth),12);
    hooks::originalShield=reinterpret_cast<void*>(sourceShield);
    hooks::originalDepth=reinterpret_cast<hooks::Depth>(sourceDepth);
    hooks::resolve=resolve;hooks::notify=notify;
    require(hooks::transaction(true)==NO_ERROR,"install fixture-only native hooks");
    InterlockedExchange(&hooks::enabled,1);
    const unsigned originalCSR=_mm_getcsr();
    const auto result=invoke(0x11,0x22,0x33);
    Word returnedXmm{};__asm movd returnedXmm,xmm0
    const unsigned returnedCSR=_mm_getcsr();
    require(result==0xf00dface,"original shield EAX return preserved");
    require(GetLastError()==987,"original shield LastError preserved");
    require(returnedXmm==0x12345678,"original shield SSE result preserved across exit callback");
    require(returnedCSR==originalCSR,"FP control state preserved despite callback modification");
    require(argsGood,"ECX manager argument and original setter results preserved");
    require(entries==1&&exits==1,"one owner-qualified entry exit");
    require(flushes==2&&qualifiedFlushes==1,"entry flush excluded restore flush included");
    require(bodyQualified==1,"native body selected after original setter completes");
    require(hooks::active==0&&!hooks::current(),"native callbacks and scope drained");
    entries=exits=flushes=qualifiedFlushes=bodyQualified=0;
    require(invoke(0x12,0x22,0x33)==0xf00dface,"other owner original function still executes");
    require(!entries&&!exits&&!qualifiedFlushes&&!bodyQualified,"other owner never qualified");
    require(hooks::active==0,"rejected owner drains");
    InterlockedExchange(&hooks::enabled,0);
    require(hooks::transaction(false)==NO_ERROR,"detach fixture hooks");
    require(!memcmp(shieldBytes,reinterpret_cast<void*>(sourceShield),12),"shield original bytes restored");
    require(!memcmp(depthBytes,reinterpret_cast<void*>(sourceDepth),12),"setter original bytes restored");
    require(invoke(0x11,0x22,0x33)==0xf00dface,"native function operates after detach");
    std::cout<<"Native shield ABI hook PASS "<<checks<<" checks; fixture only, no SFC launched\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
