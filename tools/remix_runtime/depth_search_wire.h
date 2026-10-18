#pragma once
#include <windows.h>
#include <cstdint>
#include <array>
namespace depth_search {
constexpr uint32_t Magic=0x53445031,Version=1,Phases=6,Capacity=32;
enum Phase:uint32_t {SceneBegin,SceneEnd,AfterFlush,EnginePresent,DxgiPresent,Overlay};
enum Status:LONG {Absent=0,Prepared=1,Installed=2,Stopping=3,Removed=4,Failed=5};
struct Counts {volatile LONG calls,noContext,wrongThread,missing,found,invalid,busy;uint32_t lastTick;};
struct Resource {
  uint32_t epoch,resourceLabel,viewLabel,width,height,format,viewFormat,flags,samples;
  uint32_t phaseMask,firstTick,lastTick,observations;
  std::array<uint32_t,3> reserved;
};
struct Data {
  uint32_t magic,version,bytes,capacity;
  volatile LONG status,installedMask,restoredMask,error,resourceCount,overflow;
  uint32_t contextThread,epoch,startTick,endTick;
  volatile LONG seenMask,reserved;
  Counts phases[Phases];Resource resources[Capacity];
};
static_assert(sizeof(Counts)==32&&sizeof(Resource)==64&&sizeof(Data)==2304);
static_assert(256+sizeof(Data)<=4096);
inline bool valid(const Data& d){return d.magic==Magic&&d.version==Version&&d.bytes==sizeof(Data)&&d.capacity==Capacity&&d.resourceCount>=0&&d.resourceCount<=static_cast<LONG>(Capacity);}
inline LONG read(volatile LONG& v){return InterlockedCompareExchange(&v,0,0);}
inline void write(volatile LONG& v,LONG n){InterlockedExchange(&v,n);}
// Process-local pointer values are observation labels, NOT portable resources
// or lifetime guarantees. Epoch separates context recreation; no external deref.
inline bool same(const Resource& a,const Resource& b){return a.epoch==b.epoch&&a.resourceLabel==b.resourceLabel&&a.viewLabel==b.viewLabel&&a.width==b.width&&a.height==b.height&&a.format==b.format&&a.viewFormat==b.viewFormat&&a.flags==b.flags&&a.samples==b.samples;}
inline void retain(Data& d,Resource r,uint32_t phase,uint32_t tick){
  auto count=read(d.resourceCount);
  for(LONG i=0;i<count;++i)if(same(d.resources[i],r)){
    auto& old=d.resources[i];old.phaseMask|=1u<<phase;old.lastTick=tick;++old.observations;return;
  }
  if(count>=static_cast<LONG>(Capacity)){InterlockedIncrement(&d.overflow);return;}
  r.phaseMask=1u<<phase;r.firstTick=r.lastTick=tick;r.observations=1;
  d.resources[count]=r;MemoryBarrier();write(d.resourceCount,count+1);
}
}
