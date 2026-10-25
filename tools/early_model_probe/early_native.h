#pragma once
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <tlhelp32.h>
#include <detours.h>
#include <atomic>
#include <cstring>
#include <intrin.h>
#include "early_core.h"
namespace early_model {
using Zero=Word(__thiscall*)(void*);using One=Word(__thiscall*)(void*,Word);
using Four=Word(__thiscall*)(void*,Word,Word,Word,Word);using Loader=Word(__cdecl*)(Word);
struct Targets {One request=nullptr;Loader load=nullptr;One parse=nullptr,attach=nullptr,render=nullptr;Four mesh=nullptr;Zero visualRetire=nullptr,born=nullptr,retire=nullptr;};
inline Targets native;inline std::atomic<bool> observing{false},uncertain{false};
inline std::atomic<unsigned> active{0},busy{0},faults{0};inline std::atomic<uint64_t> tokens{0},callbackTicks{0};
inline SRWLOCK bookLock=SRWLOCK_INIT;inline Book owners,visuals;inline thread_local Stack stack;
inline Word shipVt=0x00796F0C,visualVt=0x007985A4,meshVt=0x007983E8,expectedCaller=0x0042FDD5;
inline bool fixtureMode=false;inline std::atomic<bool> gated{false};
using Sink=void(*)(Record);inline Sink sink=nullptr;
inline uint64_t ticks(){LARGE_INTEGER n{};QueryPerformanceCounter(&n);return static_cast<uint64_t>(n.QuadPart);}
inline Word ptr(void* p){return reinterpret_cast<Word>(p);}
inline bool read(Word p,void* out,size_t n){if(!p||n>4096||n>UINT32_MAX-p)return false;__try{std::memcpy(out,reinterpret_cast<void*>(p),n);return true;}__except(EXCEPTION_EXECUTE_HANDLER){return false;}}
inline Word word(Word p,bool& ok){Word n=0;if(!read(p,&n,4))ok=false;return n;}
inline Record record(Kind kind,Word owner=0,Word visual=0){Record r;r.kind=kind;r.owner=owner;r.visual=visual;r.qpc=ticks();r.thread=GetCurrentThreadId();r.depth=stack.depth;r.token=stack.current().token;if(fixtureMode)r.flags|=Fixture;if(uncertain)r.flags|=Uncertain;return r;}
inline void emit(Record r){if(sink&&observing)sink(r);}
inline void name(Record& r,Word p){
 if(!p){r.flags|=NameBad;return;}for(unsigned i=0;i<r.name.size();++i){char c=0;if(p>UINT32_MAX-i||!read(p+i,&c,1)){r.flags|=ReadBad;break;}if(!c){if(!i)r.flags|=NameBad;return;}if(c<32||c>126){r.flags|=NameBad;break;}r.name[i]=c;}
 r.name.back()=0;r.flags|=NameBad;
}
inline Entry entry(Book& book,Word p,unsigned action=0,bool qualified=false){
 if(!TryAcquireSRWLockExclusive(&bookLock)){++busy;uncertain=true;return {};}
 Entry e=action==1?book.birth(p,qualified):action==2?book.retire(p):book.current(p);ReleaseSRWLockExclusive(&bookLock);
 if(action==1&&!e.epoch)uncertain=true;return e;
}
inline void identities(Record& r){const auto o=entry(owners,r.owner),v=entry(visuals,r.visual);r.data[0]=o.epoch;r.data[1]=v.epoch;if(!o.qualified||!v.qualified)r.flags|=MissingIdentity;}
// Intrinsic scalar snapshot only: no geometry arrays, image data or manager reads.
inline void snapshot(Record& r){
 bool ok=true;if(!r.visual){r.flags|=Unsupported;return;}r.data[2]=word(r.visual,ok);
 if(r.data[2]!=visualVt){r.flags|=Unsupported;return;}
 r.data[3]=word(r.visual+0x11C,ok);r.data[4]=word(r.visual+0x15C,ok);r.data[5]=word(r.visual+0x158,ok);r.data[6]=word(r.visual+0x154,ok);
 r.data[7]=word(r.visual+0x178,ok);r.data[8]=word(r.visual+0x120,ok);r.data[9]=word(r.visual+0x124,ok);
 if(!r.data[3]||r.data[3]>4||r.data[4]>256||!r.data[5]||!r.data[6]){r.flags|=Unsupported;return;}
 for(Word i=0;i<r.data[3];++i){const auto child=word(r.visual+0x160+4*i,ok);r.data[10+i]=child;if(!child||word(child,ok)!=meshVt)r.flags|=Unsupported;}
 // Counts/pointers for actual selected child, or LOD0 if not drawing yet.
 const auto m=r.mesh?r.mesh:r.data[10];
 if(m){r.data[14]=word(m+8,ok);r.data[15]=word(m+0xC,ok);r.data[16]=word(m+0x10,ok);r.data[17]=word(m+0x14,ok);r.data[18]=word(m+0x20,ok);
  if(!r.data[14]||r.data[14]>65536||r.data[16]>8192||!r.data[15]||!r.data[17])r.flags|=Unsupported;}
 const auto groups=r.data[4],source=r.data[5];
 for(Word i=0;i<groups;++i){std::array<Word,9> s{};const uint64_t address=uint64_t(source)+uint64_t(i)*36;
  if(address>UINT32_MAX||!read(static_cast<Word>(address),s.data(),36)){ok=false;break;}
  if(s[5])++r.data[19];else ++r.data[21];if(s[0]&0x20){++r.data[20];if(!s[7])++r.data[21];}if(s[5]>4096||s[7]>4096)++r.data[22];
  if(i<8){r.data[24+2*i]=s[5];r.data[25+2*i]=s[7];}
 }
 if(!ok){r.flags|=ReadBad;++faults;}
}
struct Active {Active(){++active;}~Active(){--active;}};
struct LastError {DWORD before=GetLastError(),after=before;void enter(){SetLastError(before);}void leave(){after=GetLastError();}~LastError(){SetLastError(after);}};
struct Scope {
 bool normal=false;Record begin;uint64_t started=ticks();
 explicit Scope(Record r,Word role):begin(r){begin.parent=stack.current().token;begin.token=++tokens;
  if(!stack.push({r.owner,r.visual,begin.token,role,0})){begin.flags|=Overflow;uncertain=true;}emit(begin);}
 ~Scope(){if(!normal){auto r=begin;r.kind=Exception;r.qpc=ticks();r.flags|=OriginalException;emit(r);}stack.pop();callbackTicks+=ticks()-started;}
 void finish(Record r){r.token=begin.token;r.parent=begin.parent;emit(r);normal=true;}
};
inline Word __fastcall onRequest(void* p,void*,Word text){
 LastError last;Active activeCall;if(!observing){last.enter();const auto v=native.request(p,text);last.leave();return v;}
 auto r=record(Request,ptr(p));r.caller=ptr(_ReturnAddress());name(r,text);r.data[0]=entry(owners,ptr(p)).epoch;Scope s(r,Request);
 last.enter();const auto result=native.request(p,text);last.leave();auto end=record(RequestEnd,ptr(p));end.data[2]=result;s.finish(end);return result;
}
inline Word __cdecl onLoad(Word text){
 LastError last;Active activeCall;if(!observing){last.enter();const auto v=native.load(text);last.leave();return v;}
 auto r=record(Load,stack.current().owner);r.caller=ptr(_ReturnAddress());name(r,text);Scope s(r,Load);
 last.enter();const auto v=native.load(text);last.leave();auto end=record(LoadEnd,r.owner,v);end.data[23]=stack.parses();
 if(v){auto e=entry(visuals,v);if(end.data[23]||!e.epoch)e=entry(visuals,v,1,end.data[23]!=0);end.data[1]=e.epoch;if(!e.qualified)end.flags|=MissingIdentity;snapshot(end);}
 end.data[0]=entry(owners,r.owner).epoch;s.finish(end);return v;
}
inline Word __fastcall onParse(void* p,void*,Word text){
 LastError last;Active activeCall;if(!observing){last.enter();const auto v=native.parse(p,text);last.leave();return v;}
 stack.parsed();auto r=record(Parse,stack.current().owner,ptr(p));name(r,text);Scope s(r,Parse);
 last.enter();const auto v=native.parse(p,text);last.leave();auto end=record(ParseEnd,r.owner,ptr(p));end.data[2]=v&255;
 if(v&255){bool ok=true;end.data[3]=word(ptr(p)+0x160,ok);if(end.data[3])end.data[4]=word(end.data[3]+0xC,ok);if(!ok)end.flags|=ReadBad;}
 s.finish(end);return v;
}
inline Word __fastcall onAttach(void* p,void*,Word visual){
 LastError last;Active activeCall;last.enter();const auto v=native.attach(p,visual);last.leave();
 if(observing){bool ok=true;auto r=record(Attach,ptr(p),visual);r.data[23]=word(ptr(p)+0x88,ok);if(!ok)r.flags|=ReadBad;if(r.data[23]!=visual)r.flags|=Mismatch;
  if(word(ptr(p),ok)!=shipVt)r.flags|=Unsupported;
  if(TryAcquireSRWLockExclusive(&bookLock)){owners.rebound(ptr(p));ReleaseSRWLockExclusive(&bookLock);}else{++busy;uncertain=true;}
  identities(r);snapshot(r);emit(r);}
 return v;
}
inline Word __fastcall onBorn(void* p,void*){
 LastError last;Active activeCall;last.enter();const auto v=native.born(p);last.leave();
 if(observing){const auto e=entry(owners,ptr(p),1,true);auto r=record(OwnerBorn,ptr(p));r.data[0]=e.epoch;emit(r);}return v;
}
inline Word __fastcall onRetire(void* p,void*){
 LastError last;Active activeCall;if(observing){auto r=record(OwnerRetire,ptr(p));r.data[0]=entry(owners,ptr(p),2).epoch;emit(r);}
 last.enter();const auto v=native.retire(p);last.leave();return v;
}
inline Word __fastcall onVisualRetire(void* p,void*){
 LastError last;Active activeCall;if(observing){auto r=record(VisualRetire,0,ptr(p));r.data[1]=entry(visuals,ptr(p),2).epoch;emit(r);}
 last.enter();const auto v=native.visualRetire(p);last.leave();return v;
}
inline Word __fastcall onRender(void* p,void*,Word manager){
 LastError last;Active activeCall;bool ok=true;const auto owner=ptr(p),visual=observing?word(owner+0x88,ok):0;
 if(!observing){last.enter();const auto v=native.render(p,manager);last.leave();return v;}
 if(!ok||word(owner,ok)!=shipVt||word(visual,ok)!=visualVt){
  stack.push({});struct PopUnknown {~PopUnknown(){stack.pop();}} popUnknown;
  last.enter();const auto v=native.render(p,manager);last.leave();return v;}
 // No per-frame event: only scope context and the first tactical marker.
 if(!gated.exchange(true)){auto r=record(Gate,owner,visual);identities(r);emit(r);}
 const bool pushed=stack.push({owner,visual,0,FirstDraw,0});if(!pushed)uncertain=true;
 struct Pop {~Pop(){stack.pop();}} pop;
 last.enter();const auto v=native.render(p,manager);last.leave();return v;
}
inline Word __fastcall onMesh(void* p,void*,Word manager,Word source,Word a,Word b){
 LastError last;Active activeCall;const auto c=stack.current();bool ok=true;const auto caller=ptr(_ReturnAddress());
 if(observing&&c.role==FirstDraw&&mainline(fixtureMode?expectedCaller:caller,expectedCaller,c.visual,source,word(c.visual+0x158,ok))&&word(ptr(p),ok)==meshVt){
  auto r=record(FirstDraw,c.owner,c.visual);r.mesh=ptr(p);r.caller=caller;identities(r);
  if(TryAcquireSRWLockExclusive(&bookLock)){const bool first=owners.first(c.owner,r.data[0],ptr(p));ReleaseSRWLockExclusive(&bookLock);
   if(first){snapshot(r);bool child=false;for(unsigned i=10;i<14;++i)child|=r.data[i]==r.mesh;if(!child)r.flags|=Mismatch;if(!ok)r.flags|=ReadBad;emit(r);}}
  else{++busy;uncertain=true;}
 }
 last.enter();const auto v=native.mesh(p,manager,source,a,b);last.leave();return v;
}
// Same pinned Detours transaction/enrollment pattern as the accepted observer.
inline LONG transaction(bool attach){
 LONG error=DetourTransactionBegin();if(error)return error;std::array<HANDLE,256> handles{};unsigned used=0;
 auto snapshot=CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD,0);THREADENTRY32 t{};t.dwSize=sizeof(t);
 if(snapshot==INVALID_HANDLE_VALUE){DetourTransactionAbort();return ERROR_INVALID_HANDLE;}
 bool more=Thread32First(snapshot,&t)!=FALSE;if(!more)error=GetLastError();
 while(more&&!error){if(t.th32OwnerProcessID==GetCurrentProcessId()&&t.th32ThreadID!=GetCurrentThreadId()){
  if(used==handles.size()){error=ERROR_BUFFER_OVERFLOW;break;}auto h=OpenThread(THREAD_SUSPEND_RESUME|THREAD_GET_CONTEXT|THREAD_SET_CONTEXT|THREAD_QUERY_INFORMATION,FALSE,t.th32ThreadID);
  if(!h){error=GetLastError();break;}handles[used++]=h;error=DetourUpdateThread(h);}
  more=Thread32Next(snapshot,&t)!=FALSE;if(!more&&GetLastError()!=ERROR_NO_MORE_FILES)error=GetLastError();}
 CloseHandle(snapshot);if(!error)error=DetourUpdateThread(GetCurrentThread());
#define EARLY_HOOK(field,callback) if(!error)error=attach?DetourAttach(reinterpret_cast<PVOID*>(&native.field),reinterpret_cast<PVOID>(callback)):DetourDetach(reinterpret_cast<PVOID*>(&native.field),reinterpret_cast<PVOID>(callback))
 EARLY_HOOK(request,onRequest);EARLY_HOOK(load,onLoad);EARLY_HOOK(parse,onParse);EARLY_HOOK(attach,onAttach);EARLY_HOOK(render,onRender);EARLY_HOOK(mesh,onMesh);EARLY_HOOK(visualRetire,onVisualRetire);EARLY_HOOK(born,onBorn);EARLY_HOOK(retire,onRetire);
#undef EARLY_HOOK
 if(!error)error=DetourTransactionCommit();else DetourTransactionAbort();for(unsigned i=0;i<used;++i)CloseHandle(handles[i]);return error;
}
}
