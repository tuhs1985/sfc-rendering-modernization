// Experimental OWNER snapshot inbox. Not a complete-scene seal or live hook.
// One producer and one consumer. Both must stop/join before unmapping storage.
#pragma once
#include <windows.h>
#include <cstdint>
#include <cstddef>
#include <cmath>
#include <cstring>

namespace frame_ingress {
constexpr uint32_t Magic=0x31494653,Version=1,Slots=4;
enum State:LONG {Free=0,Writing=1,Ready=2,Reading=3};
struct Key {
 uint64_t session,sequence,source_frame,state_hash,asset_hash;
 uint32_t owner_epoch,revision;
};
struct alignas(8) Packet {
 uint32_t magic=Magic,version=Version,bytes=sizeof(Packet),reserved=0;
 Key key{};
 uint64_t offered_qpc=0,deadline_qpc=0;
 float model[16]{},view[16]{},projection[16]{},viewport[4]{};
 uint64_t checksum=0;
};
struct alignas(64) Slot {volatile LONG state=Free;LONG reserved=0;Packet packet{};uint8_t padding[16]{};};
struct alignas(64) Channel {
 uint32_t magic=Magic,version=Version,bytes=sizeof(Channel),reserved=0;
 uint64_t session=0;volatile LONG stopped=0;LONG padding=0;uint8_t padding_bytes[32]{};
 Slot slots[Slots]{};
};
static_assert(sizeof(Key)==48&&sizeof(Packet)==296&&sizeof(Slot)==320&&sizeof(Channel)==1344);
static_assert(offsetof(Packet,checksum)==288&&offsetof(Channel,slots)==64);
inline uint64_t hash(const void* data,size_t bytes){
 uint64_t h=14695981039346656037ull;auto* p=static_cast<const unsigned char*>(data);
 for(size_t i=0;i<bytes;++i){h^=p[i];h*=1099511628211ull;}return h;
}
inline uint64_t checksum(const Packet& p){return hash(&p,offsetof(Packet,checksum));}
inline uint64_t state_hash(const Packet& p){return hash(p.model,52*sizeof(float));}
inline bool same(const Key& a,const Key& b){
 return a.session==b.session&&a.sequence==b.sequence&&a.source_frame==b.source_frame&&
 a.state_hash==b.state_hash&&a.asset_hash==b.asset_hash&&a.owner_epoch==b.owner_epoch&&a.revision==b.revision;
}
inline bool valid(const Packet& p,uint64_t session){
 if(p.magic!=Magic||p.version!=Version||p.bytes!=sizeof(Packet)||p.reserved||!session||
    p.key.session!=session||!p.key.sequence||!p.key.source_frame||!p.key.state_hash||!p.key.asset_hash||
    !p.key.owner_epoch||!p.key.revision||!p.offered_qpc||p.deadline_qpc<=p.offered_qpc||
    p.key.state_hash!=state_hash(p)||p.checksum!=checksum(p))return false;
 for(unsigned i=0;i<16;++i)if(!std::isfinite(p.model[i])||!std::isfinite(p.view[i])||!std::isfinite(p.projection[i]))return false;
 for(float f:p.viewport)if(!std::isfinite(f))return false;
 return p.viewport[0]>=0&&p.viewport[1]>=0&&p.viewport[2]>0&&p.viewport[3]>0;
}
inline LONG state(volatile LONG* p){return InterlockedCompareExchange(p,0,0);}
inline bool channel_valid(const Channel& c,uint64_t session){
 return c.magic==Magic&&c.version==Version&&c.bytes==sizeof(Channel)&&!c.reserved&&c.session==session&&session&&!c.padding;
}
// No blocking/retry loops. Only reclaim READY, never READING/WRITING storage.
// Sequence monotonicity is producer-local, not an interprocess atomic counter.
class Producer {
 uint64_t last=0;unsigned cursor=0;
public:
 bool publish(Channel& c,const Packet& p){
  if(state(&c.stopped)||!channel_valid(c,p.key.session)||!valid(p,c.session)||p.key.sequence<=last)return false;
  for(unsigned pass=0;pass<2;++pass)for(unsigned n=0;n<Slots;++n){
   auto& s=c.slots[(cursor+n)%Slots];const LONG expected=pass?Ready:Free;
   if(InterlockedCompareExchange(&s.state,Writing,expected)!=expected)continue;
   s.packet=p;InterlockedExchange(&s.state,Ready);last=p.key.sequence;cursor=(cursor+n+1)%Slots;return true;
  }
  return false; // saturated by owned slots:postpone/drop,never delay source
 }
};
struct TakeStats {uint32_t invalid=0,obsolete=0,expired=0;};
class Consumer {
 uint64_t last=0;
public:
 bool take(Channel& c,uint64_t session,uint64_t now,Packet& out,TakeStats& stats){
  if(state(&c.stopped)||!channel_valid(c,session))return false;
  bool found=false;Packet best{};
  // Copy only while we own the slot. Never inspect payload under READY:the
  // producer may reclaim it concurrently. Newer arrivals wait for next sweep.
  for(auto& s:c.slots){
   if(InterlockedCompareExchange(&s.state,Reading,Ready)!=Ready)continue;
   Packet p=s.packet;InterlockedExchange(&s.state,Free);
   // 'now' was sampled before acquisition:a concurrently published packet may
   // legitimately have a later offer timestamp. Final usability rechecks time.
   if(!valid(p,session)){++stats.invalid;continue;}
   if(p.key.sequence<=last){++stats.obsolete;continue;}
   if(now>=p.deadline_qpc){++stats.expired;continue;}
   if(found){++stats.obsolete;if(p.key.sequence<=best.key.sequence)continue;}
   best=p;found=true;
  }
  if(!found||state(&c.stopped))return false;
  out=best;last=best.key.sequence;return true;
 }
};
// Call using the authoritative current owner's expectation,not a packet's own
// claimed pose. Retirement/conflict/unqualified assets make eligible=false.
inline bool usable(const Packet& completed,const Key& expected,uint64_t now,bool eligible){
 return eligible&&valid(completed,expected.session)&&same(completed.key,expected)&&
        now>=completed.offered_qpc&&now<completed.deadline_qpc;
}
}
