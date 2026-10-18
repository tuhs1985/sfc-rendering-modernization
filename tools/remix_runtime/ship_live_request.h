// Current-frame request contract. No relaxed frame/pose equivalence.
#pragma once
#include "ship_triplet_wire.h"
#include "../m1_component/m1_present_calibration.h"
namespace ship_live {
using namespace ship_triplet;
constexpr uint32_t Offset=1024,Magic=0x31515253,Version=1;
struct Seed {Key key{};uint32_t model=0,source=0,lod=0,reserved=0;uint64_t meshHash=0;};
static_assert(sizeof(Seed)==176);
struct Command {uint32_t magic=Magic,version=Version,bytes=sizeof(Command),sequence=0;
 uint64_t observedAt=0;Key key{};std::array<uint32_t,96> row{};
 volatile LONG offered=0,invalid=0,acquired=0,drawn=0,late=0,failed=0,rendered=0,cancelled=0;
};
static_assert(sizeof(Command)==592 && Offset+sizeof(Command)<4096);
constexpr uint32_t RegistrationOffset=1792;
struct Registration {Seed seed{};volatile LONG ready=0;uint32_t reserved=0;};
static_assert(sizeof(Registration)==184 && RegistrationOffset+sizeof(Registration)<4096);
inline Registration& registration(return_path::Mapping& m){return *reinterpret_cast<Registration*>(reinterpret_cast<BYTE*>(m.state)+RegistrationOffset);}
inline Command& command(return_path::Mapping& m){return *reinterpret_cast<Command*>(reinterpret_cast<BYTE*>(m.state)+Offset);}
// Map the complete SDK camera image back to its ORIGINAL native viewport.
// The world-space diagnostic displacement is already rendered by the host;
// never add a second pixel offset,fit-to-window operation,or corner placement.
inline bool displayRect(const Key& key,float width,float height,float (&rect)[4]){
 if(!validKey(key)||!std::isfinite(width)||!std::isfinite(height)||width<800||width>1920||height<600||height>1080||
    uint64_t(key.viewport[0])+key.viewport[2]>width||uint64_t(key.viewport[1])+key.viewport[3]>height)return false;
 rect[0]=static_cast<float>(key.viewport[0]);rect[1]=static_cast<float>(key.viewport[1]);
 rect[2]=rect[0]+key.viewport[2];rect[3]=rect[1]+key.viewport[3];return true;
}
inline bool valid(const Command& c){return c.magic==Magic&&c.version==Version&&c.bytes==sizeof(Command);}
inline bool makeKey(const Seed& seed,const sfc_calibration::Snapshot& snap,uint32_t pid,uint32_t thread,Key& out,std::array<uint32_t,96>& row){
 if(!validKey(seed.key)||!seed.model||!seed.source||seed.reserved||!seed.meshHash||
    snap.magic!=sfc_calibration::Magic||snap.version!=sfc_calibration::Version||snap.bytes!=sizeof(snap)||
    !snap.frame||!snap.rows||snap.rows>32||snap.reserved[0]||snap.reserved[1]||snap.reserved[2]||memcmp(snap.session,seed.key.sourceSession,16)||pid!=seed.key.sourcePid)return false;
 unsigned rows=0;for(const auto& r:snap.owner)if(r[1])++rows;if(rows!=snap.rows)return false;
 const std::array<DWORD,96>* found=nullptr;
 for(unsigned i=0;i<32;++i)if(snap.owner[i][1]==seed.key.owner){if(found)return false;found=&snap.owner[i];if((*found)[45]!=i)return false;}
 if(!found)return false;memcpy(row.data(),found->data(),sizeof(row));
 if(row[2]!=snap.frame||row[4]!=1||row[5]!=seed.model||row[6]!=seed.source||row[7]!=seed.key.revision||
    row[46]!=seed.lod||row[47]!=thread||row[48]!=1||row[42]||row[43]||row[44])return false;
 for(unsigned i=8;i<89;++i)if(i!=24&&i!=41&&i!=65&&i!=82&&!(i>=42&&i<=48)){
  float f=0;memcpy(&f,&row[i],4);if(!std::isfinite(f))return false;}
 out=seed.key;out.frame=snap.frame;out.pose=hash(row.data()+8,17*4);out.camera=hash(row.data()+49,40*4);
 for(unsigned i=0;i<4;++i){float f=0;memcpy(&f,&row[83+i],4);
  if(f<0||f>1920||std::abs(f-std::round(f))>.001f)return false;out.viewport[i]=static_cast<uint32_t>(std::round(f));}
 return validKey(out);
}
inline bool describes(const Key& k,const std::array<uint32_t,96>& row){
 return row[1]==k.owner&&row[2]==k.frame&&row[7]==k.revision&&row[4]==1&&row[48]==1&&
  hash(row.data()+8,17*4)==k.pose&&hash(row.data()+49,40*4)==k.camera;
}
inline bool offer(Wire& w,Command& c,const Key& key,const std::array<uint32_t,96>& row,uint64_t now){
 Lock lock(w);if(!lock.held||!ship_triplet::valid(w)||!valid(c)||!validKey(key)||load(w.stop)||load(w.error)||!load(w.ready)||
    !policyMatches(w,key)||key.width!=w.width||key.height!=w.height||key.resourceEpoch!=w.resourceEpoch||memcmp(key.session,w.session,16)||c.sequence==UINT32_MAX||!describes(key,row))return false;
 w.requested=key;c.key=key;c.row=row;c.observedAt=now;++c.sequence;InterlockedIncrement(&c.offered);return true;
}
inline bool begin(Wire& w,Command& c,Key& key,std::array<uint32_t,96>& row,uint64_t now){
 Lock lock(w);if(!lock.held||!ship_triplet::valid(w)||!valid(c)||!load(w.ready)||load(w.stop)||load(w.error)||
    load(w.lease)!=Idle||load(w.sequence)!=load(w.ack)||load(w.sequence)==LONG_MAX||!validKey(c.key)||!policyMatches(w,c.key)||!same(c.key,w.requested)||
    !return_path::fresh(c.observedAt,now,w.frequency)||!describes(c.key,c.row))return false;
 key=c.key;row=c.row;store(w.lease,Rendering);return true;
}
}
