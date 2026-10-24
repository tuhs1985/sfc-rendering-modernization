// Coherent qualified-registry snapshots,not a complete engine-scene seal.
// New opt-in protocol in unused scene-map space. No pointers or image bytes.
#pragma once
#include "live_owner_wire.h"
#include "source_timing.h"
namespace multi_scene {
constexpr DWORD Offset=15*1024*1024-128*1024,Magic=0x31534d53,Owners=32,Assets=64,Frames=8;
struct Header {DWORD magic=Magic,version=1,bytes=0,pid=0,session[4]{};
 volatile LONG stopped=0,frame=0,published=0,dropped=0,invalid=0,asset_ready=0,asset_rejected=0,closed_frame=0;};
struct Frame {uint64_t sequence=0,offered=0;DWORD frame=0,anchor=0,revision=0,count=0;
 live_owner::Row rows[Owners]{};uint64_t checksum=0;};
struct alignas(64) FrameSlot {volatile LONG guard=0;DWORD reserved=0;Frame packet{};BYTE padding[16]{};};
struct Asset {DWORD id=0,path_id=0,owner=0,revision=0,model=0,source=0,geometry_bytes=0,image_bytes=0;
 BYTE content[32]{};uint64_t replay_hash=0,textures_hash=0,checksum=0;};
struct alignas(64) AssetSlot {volatile LONG guard=0,ack=0;Asset packet{};BYTE padding[32]{};};
struct Store {Header header{};FrameSlot frames[Frames]{};AssetSlot assets[Assets]{};};
inline bool initial_resolved(Store& s,uint64_t mask){
 for(unsigned i=0;i<Assets;++i)if((mask&(uint64_t(1)<<i))&&!InterlockedCompareExchange(&s.assets[i].ack,0,0))return false;
 return true; // Negative ACK remains an explicit asset failure,not an infinite wait.
}
static_assert(sizeof(Header)==64&&sizeof(Frame)==12328&&sizeof(Asset)==88&&Offset+sizeof(Store)<15*1024*1024);
static_assert(source_timing::Offset+sizeof(source_timing::Store)<Offset,"multi-scene must not overlap source timing evidence");
inline bool valid(const Header& h,const DWORD* session,DWORD pid){return h.magic==Magic&&h.version==1&&h.bytes==sizeof(Store)&&
 h.pid==pid&&pid&&live_owner::same_session(h.session,session)&&!frame_ingress::state(const_cast<volatile LONG*>(&h.stopped));}
inline uint64_t checksum(const Frame& f){return frame_ingress::hash(&f,offsetof(Frame,checksum));}
inline uint64_t checksum(const Asset& a){return frame_ingress::hash(&a,offsetof(Asset,checksum));}
inline bool valid(const Frame& f){
 if(!f.sequence||!f.offered||!f.frame||!f.anchor||!f.revision||!f.count||f.count>Owners||f.checksum!=checksum(f))return false;
 bool anchor=false;for(DWORD i=0;i<f.count;++i){const auto& r=f.rows[i];
  if(r[2]!=f.frame||!r[1]||!r[7]||!r[5]||!r[6]||r[4]!=1||r[48]!=1)return false;
  if(r[1]==f.anchor&&r[7]==f.revision){if(live_owner::sequence(r)!=f.sequence)return false;anchor=true;}
  for(DWORD j=0;j<i;++j)if(f.rows[j][1]==r[1])return false;
  if(i&&memcmp(r.data()+49,f.rows[0].data()+49,40*sizeof(DWORD)))return false;
 }
 return anchor;
}
inline bool valid(const Asset& a){BYTE any=0;for(BYTE b:a.content)any|=b;return a.id&&a.id<=Assets&&a.path_id&&a.path_id<=Assets&&
 a.owner&&a.revision&&a.model&&a.source&&a.geometry_bytes&&a.geometry_bytes<=2*1024*1024&&a.image_bytes<=128*1024*1024&&any&&a.replay_hash&&a.textures_hash&&a.checksum==checksum(a);}
inline bool matches(const Asset& a,const live_owner::Row& r){return a.owner==r[1]&&a.revision==r[7]&&a.model==r[5]&&a.source==r[6];}
inline bool read(Store& s,DWORD frame,uint64_t sequence,Frame& out){auto& slot=s.frames[frame%Frames];
 const auto guard=InterlockedCompareExchange(&slot.guard,0,0);if(!guard||(guard&1))return false;
 out=slot.packet;MemoryBarrier();return guard==InterlockedCompareExchange(&slot.guard,0,0)&&out.frame==frame&&out.sequence==sequence&&valid(out);}
inline bool read(AssetSlot& s,Asset& out){const auto guard=InterlockedCompareExchange(&s.guard,0,0);if(!guard||(guard&1))return false;
 out=s.packet;MemoryBarrier();return guard==InterlockedCompareExchange(&s.guard,0,0)&&valid(out);}
struct Source {Store* store=nullptr;Frame pending{};
 bool attach(BYTE* base,const DWORD* session){store=reinterpret_cast<Store*>(base+Offset);const auto pid=GetCurrentProcessId();
  if(store->header.pid==0)store->header.pid=pid;if(!valid(store->header,session,pid)){store=nullptr;return false;}return true;}
 void begin(){pending={};}
 void offer(const live_owner::Row& r){if(store&&pending.count<Owners)pending.rows[pending.count++]=r;}
 bool publish(uint64_t selected){if(!store||frame_ingress::state(&store->header.stopped))return false;
  pending.anchor=DWORD(selected);pending.revision=DWORD(selected>>32);
  for(DWORD i=0;i<pending.count;++i)if(pending.rows[i][1]==pending.anchor&&pending.rows[i][7]==pending.revision){
   const auto& r=pending.rows[i];pending.frame=r[2];pending.sequence=live_owner::sequence(r);pending.offered=r[89]|(uint64_t(r[90])<<32);}
  pending.checksum=checksum(pending);if(!valid(pending)){InterlockedIncrement(&store->header.dropped);return false;}
  auto& slot=store->frames[pending.frame%Frames];InterlockedIncrement(&slot.guard);slot.packet=pending;MemoryBarrier();InterlockedIncrement(&slot.guard);
  InterlockedExchange(&store->header.frame,static_cast<LONG>(pending.frame));InterlockedIncrement(&store->header.published);return true;
 }
 void close(){if(store)InterlockedExchange(&store->header.stopped,1);store=nullptr;}
};
}
