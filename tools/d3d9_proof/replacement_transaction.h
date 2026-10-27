// Default-off replacement transaction. No renderer/API pointers in shared state.
#pragma once
#include <windows.h>
#include <cstdint>
#include <cstring>
#include <algorithm>
namespace replacement {
constexpr DWORD Offset=12*1024*1024-64*1024,Bytes=64*1024,Magic=0x31525053,Version=1,Frames=64;
enum Mode:DWORD {Priming=0,Active=1,Recovering=2,LatchedOriginal=3};
enum Flags:DWORD {Suppressed=1,Invalid=2,Seen=4};
struct Control {DWORD mode=Priming,generation=1,owner=0,revision=0,model=0,source=0,thread=0,epoch=0,permit=0;
 DWORD reason=0;uint64_t expires=0;};
struct Receipt {DWORD frame=0,generation=0,owner=0,revision=0,model=0,source=0,thread=0,flags=0,primary=0,secondary=0;};
struct Binding {uint64_t output=0,sourceSequence=0,stateHash=0;DWORD frame=0,generation=0,owner=0,revision=0,epoch=0,reserved=0;};
template<class T>struct alignas(64) Cell {volatile LONG sequence=0;DWORD reserved=0;T value{};BYTE padding[64-(8+sizeof(T))%64]{};};
struct alignas(64) Store {DWORD magic=0,version=0,bytes=0,pid=0,session[4]{};DWORD reserved[8]{};
 Cell<Control> control;Cell<Receipt> receipt[Frames];Cell<Binding> output[2];
 volatile LONG native_capable=0,renderer_capable=0,suppressed=0,rejected=0,committed=0,repeated=0,recovered=0,native_stop=0,native_restored_frame=0,repeat_max=0,native_frame=0;BYTE padding[20]{};};
static_assert(sizeof(Store)<=Bytes&&Offset+Bytes==12*1024*1024);
static_assert(sizeof(Store)==4416&&offsetof(Store,suppressed)==4360,"versioned Python receipt layout");
template<class T>inline bool read(const Cell<T>& c,T& out){
 for(unsigned i=0;i<3;++i){auto* seq=const_cast<volatile LONG*>(&c.sequence);const LONG a=InterlockedCompareExchange(seq,0,0);if(a&1)continue;
  memcpy(&out,&c.value,sizeof(out));MemoryBarrier();if(a==InterlockedCompareExchange(seq,0,0))return a!=0;}return false;
}
template<class T>inline void write(Cell<T>& c,const T& value){InterlockedIncrement(&c.sequence);memcpy(&c.value,&value,sizeof(value));MemoryBarrier();InterlockedIncrement(&c.sequence);}
inline bool valid(const Store* s,const DWORD* session,DWORD pid){return s&&s->magic==Magic&&s->version==Version&&s->bytes==sizeof(Store)&&s->pid==pid&&memcmp(s->session,session,16)==0;}
inline void initialize(Store& s,const DWORD* session,DWORD pid){memset(&s,0,sizeof(s));s.magic=Magic;s.version=Version;s.bytes=sizeof(s);s.pid=pid;memcpy(s.session,session,16);write(s.control,Control{});}
inline uint64_t now(){LARGE_INTEGER q{};QueryPerformanceCounter(&q);return static_cast<uint64_t>(q.QuadPart);}
inline bool requested(){wchar_t flag[2]{};return GetEnvironmentVariableW(L"SFC_D3D9_PLAYER_REPLACEMENT",flag,2)==1&&flag[0]==L'1';}
inline bool sample(const Store& s,DWORD frame,Receipt& r){return read(s.receipt[frame%Frames],r)&&r.frame==frame;}
inline void begin(Store& s,DWORD frame,DWORD thread){Control c{};Receipt r{};r.frame=frame;r.thread=thread;
 if(read(s.control,c)){r.generation=c.generation;r.owner=c.owner;r.revision=c.revision;r.model=c.model;r.source=c.source;}
 write(s.receipt[frame%Frames],r);
 InterlockedExchange(&s.native_frame,static_cast<LONG>(frame));
}
inline void invalidate(Store& s,DWORD frame){Receipt r{};if(sample(s,frame,r)){r.flags|=Invalid;write(s.receipt[frame%Frames],r);}InterlockedIncrement(&s.rejected);}
inline bool sameFrame(const Control& c,DWORD frame,DWORD owner,DWORD revision,DWORD model,DWORD source,DWORD thread){
 return c.mode==Active&&c.permit==frame&&c.owner==owner&&c.revision==revision&&c.model==model&&c.source==source&&c.thread==thread&&c.epoch;
}
inline bool eligible(const Control& c,DWORD frame,DWORD owner,DWORD revision,DWORD model,DWORD source,DWORD thread,uint64_t time){
 return time&&c.expires&&time<=c.expires&&sameFrame(c,frame,owner,revision,model,source,thread);
}
// Capture and source/list validation happen BEFORE this decision. No waiting/IO.
inline bool suppress(Store& s,DWORD frame,DWORD owner,DWORD revision,DWORD model,DWORD source,DWORD thread,bool primary,uint64_t time){
 Control c{};Receipt r{};if(!read(s.control,c)||!sample(s,frame,r)||c.owner!=owner)return false;
 r.flags|=Seen;
 // The first qualified list fixes this source frame's decision. Expiration
 // between primary and secondary must not split one model. Revocation or any
 // identity/list ambiguity still invalidates the entire buffered transaction.
 const bool allowed=(r.flags&Suppressed)?sameFrame(c,frame,owner,revision,model,source,thread):eligible(c,frame,owner,revision,model,source,thread,time);
 if(InterlockedCompareExchange(&s.native_stop,0,0)||!allowed||r.generation!=c.generation||r.flags&Invalid){
  if(c.mode==Active){r.flags|=Invalid;InterlockedIncrement(&s.rejected);}write(s.receipt[frame%Frames],r);return false;}
 r.flags|=Suppressed;if(primary)++r.primary;else ++r.secondary;write(s.receipt[frame%Frames],r);InterlockedIncrement(&s.suppressed);return true;
}
struct Policy {
 Mode mode=Priming;DWORD repeats=0;bool complete=false;
 void completed(){complete=true;repeats=0;}
 bool miss(bool hard=false){if(!complete)return false;++repeats;if(hard||repeats>=2)mode=Recovering;return true;}
 void nativeRecovery(){mode=LatchedOriginal;repeats=0;}
};
inline bool bindingMatches(const Binding& b,const Receipt& r,uint64_t output,uint64_t sequence,uint64_t hash,DWORD epoch){
 return !(r.flags&Invalid)&&(r.flags&Suppressed)&&b.frame==r.frame&&b.generation==r.generation&&b.owner==r.owner&&b.revision==r.revision&&
 b.output==output&&b.sourceSequence==sequence&&b.stateHash==hash&&b.epoch==epoch;
}
}
