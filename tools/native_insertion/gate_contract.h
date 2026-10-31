#pragma once
#include "probe_wire.h"
#include <array>
#include <cmath>
#include <stdexcept>
namespace native_gate {
constexpr DWORD Offset=replacement::Offset+50176,Magic=0x3147544e,Version=1,Capacity=64;
enum class Policy:DWORD {Strict=1,ExtraFrame=2};
enum class Action:DWORD {Acquire=1,Commit,Cancel};
enum class Result:DWORD {Original=0,Acquired=1,Inserted=2,Timeout=3,Disconnected=4,Stopped=5,Invalid=6,Partial=7};
struct Ticket {
 DWORD bytes=sizeof(Ticket),version=Version,session[4]{},pid=0,thread=0,frame=0,owner=0,revision=0,model=0,source=0;
 DWORD manager=0,count=0,primary=0,secondary=0,generation=0;
 uint64_t sequence=0,hash=0,offered=0,frameStart=0,deadline=0;
};
struct Reply {DWORD bytes=sizeof(Reply),version=Version;Result result=Result::Original;DWORD generation=0;uint64_t token=0;};
using Dispatch=DWORD (WINAPI*)(DWORD,const Ticket*,Reply*);
struct Record {
 DWORD frame=0,owner=0,revision=0,policy=0,outcome=0,queue=0,generation=0,resourceEpoch=0,reason=0,primary=0,secondary=0,flags=0;
 uint64_t offered=0;DWORD reserved[2]{};
 uint64_t start=0,entered=0,ready=0,inserted=0,ended=0,presented=0,sequence=0,hash=0;
};
struct Stamp {uint64_t sequence=0,qpc=0;};
struct alignas(64) Header {
 DWORD magic=0,version=0,bytes=0,pid=0,session[4]{},policy=0,generation=0;
 volatile LONG stop=0,error=0,frame=0,thread=0,written=0,read=0,dropped=0,requests=0,commits=0,misses=0,stale=0,invalid=0,stopWakes=0,active=0,maxActive=0,partial=0;
 DWORD pad[2]{};uint64_t frameStart=0,frequency=0;Stamp ready[2]{};BYTE padding[96]{};
};
struct Store {Header header{};Record current{};Record records[Capacity]{};};
static_assert(sizeof(Header)==256&&sizeof(Record)==128&&sizeof(Store)==8576);
static_assert(Offset>=native_insertion::Offset+sizeof(native_insertion::Store)&&Offset+sizeof(Store)<=replacement::Offset+replacement::Bytes);
inline bool requested(){wchar_t f[2]{};return GetEnvironmentVariableW(L"SFC_NATIVE_INSERTION_GATE",f,2)==1&&f[0]==L'1';}
inline uint64_t now(){LARGE_INTEGER q{};QueryPerformanceCounter(&q);return q.QuadPart;}
inline bool valid(const Header& h,const DWORD* s,DWORD pid){return h.magic==Magic&&h.version==Version&&h.bytes==sizeof(Store)&&h.pid==pid&&
 !memcmp(h.session,s,16)&&h.frequency&&(h.policy==1||h.policy==2)&&h.generation;}
inline Policy policy(){wchar_t f[32]{};GetEnvironmentVariableW(L"SFC_NATIVE_INSERTION_POLICY",f,32);
 if(!wcscmp(f,L"Strict"))return Policy::Strict;if(!wcscmp(f,L"ExtraFrame"))return Policy::ExtraFrame;throw std::runtime_error("Explicit native insertion policy required");}
inline void initialize(Store& s,const DWORD* session,DWORD pid,Policy p){memset(&s,0,sizeof(s));s.header.version=Version;s.header.bytes=sizeof(s);s.header.pid=pid;
 memcpy(s.header.session,session,16);s.header.policy=static_cast<DWORD>(p);s.header.generation=1;LARGE_INTEGER f{};QueryPerformanceFrequency(&f);s.header.frequency=f.QuadPart;
 MemoryBarrier();InterlockedExchange(reinterpret_cast<volatile LONG*>(&s.header.magic),Magic);}
inline uint64_t deadline(const Header& h,uint64_t start){return start+(h.frequency*h.policy+59)/60;}
inline bool valid(const Ticket& t,const Header& h){return t.bytes==sizeof(t)&&t.version==Version&&!memcmp(t.session,h.session,16)&&t.pid==h.pid&&t.thread&&
 t.frame&&t.owner&&t.revision&&t.model&&t.source&&t.manager&&t.count&&t.count<=65536&&t.primary&&t.generation==h.generation&&
 t.sequence&&t.hash&&t.offered&&t.frameStart&&t.deadline==deadline(h,t.frameStart)&&t.offered>=t.frameStart;}
inline void begin(Store& s,DWORD frame,DWORD thread){auto& h=s.header;if(h.stop){InterlockedExchange(&h.frame,static_cast<LONG>(frame));return;}
 const LONG prior=InterlockedCompareExchange(&h.thread,static_cast<LONG>(thread),0);if(prior&&prior!=static_cast<LONG>(thread)){InterlockedIncrement(&h.invalid);return;}
 h.frame=frame;h.frameStart=now();s.current={};s.current.frame=frame;s.current.start=h.frameStart;s.current.policy=h.policy;s.current.generation=h.generation;}
inline void append(Store& s){auto& h=s.header;const auto w=DWORD(h.written),r=DWORD(InterlockedCompareExchange(&h.read,0,0));
 if(w-r>=Capacity){InterlockedIncrement(&h.dropped);return;}s.records[w%Capacity]=s.current;MemoryBarrier();InterlockedExchange(&h.written,static_cast<LONG>(w+1));}
inline bool same(const Ticket& a,const Ticket& b){return !memcmp(&a,&b,sizeof(a));}
inline DWORD waitMilliseconds(uint64_t remaining,uint64_t frequency){const auto ms=(remaining*1000+frequency-1)/frequency;return static_cast<DWORD>((std::min)(ms,uint64_t(34)));}
}
