// Neutral, bounded membership proof for multi-owner native insertion.
// Existing GPU triplet and same-process ticket ABI remain unchanged.
#pragma once
#include "gate_contract.h"
#include "../d3d9_proof/multi_scene_wire.h"
namespace native_cohort {
constexpr DWORD Magic=0x31434e53,Version=2,Offset=scene_capacity::CohortOffset;
struct Member {DWORD owner=0,revision=0,model=0,source=0,asset=0;BYTE content[32]{};};
struct Manifest {DWORD session[4]{},frame=0,anchor=0,revision=0,count=0;uint64_t sequence=0,hash=0,output=0;Member members[multi_scene::Owners]{};uint64_t checksum=0;};
struct alignas(64) Cell {volatile LONG guard=0;DWORD reserved=0;Manifest value{};BYTE padding[56]{};};
struct Header {DWORD magic=0,version=0,bytes=0,pid=0,session[4]{};volatile LONG inserted=0,suppressed=0,unavailable=0,omitted=0;DWORD reserved[4]{};};
struct OwnerStats {DWORD owner=0,revision=0,model=0,source=0;volatile LONG inserted=0,suppressed=0,unavailable=0,lastFrame=0;};
struct Store {Header header{};Cell upstream{},slots[2]{};OwnerStats owners[multi_scene::Owners]{};};
static_assert(sizeof(Manifest)==64+52*multi_scene::Owners&&sizeof(Cell)==sizeof(Manifest)+64&&sizeof(Header)==64);
static_assert(Offset>=scene_capacity::StateOffset+scene_capacity::StateBytes&&Offset+sizeof(Store)<=multi_scene::Offset);
inline bool requested(){wchar_t v[2]{};return native_gate::requested()&&GetEnvironmentVariableW(L"SFC_NATIVE_INSERTION_ALL_SHIPS",v,2)==1&&v[0]==L'1';}
inline uint64_t checksum(const Manifest& m){return frame_ingress::hash(&m,offsetof(Manifest,checksum));}
inline bool valid(const Manifest& m,const DWORD* session){
 if(memcmp(m.session,session,16)||!m.frame||!m.anchor||!m.revision||!m.sequence||!m.hash||!m.output||!m.count||m.count>multi_scene::Owners||m.checksum!=checksum(m))return false;
 for(DWORD i=0;i<m.count;++i){const auto& x=m.members[i];if(!x.owner||!x.revision||!x.model||!x.source||!x.asset||x.asset>multi_scene::Assets)return false;
  for(DWORD j=0;j<i;++j)if(m.members[j].owner==x.owner)return false;}
 return true;
}
inline bool valid(const Header& h,const DWORD* session,DWORD pid){return h.magic==Magic&&h.version==Version&&h.bytes==sizeof(Store)&&h.pid==pid&&!memcmp(h.session,session,16);}
inline void initialize(Store& s,const DWORD* session,DWORD pid){memset(&s,0,sizeof(s));s.header.version=Version;s.header.bytes=sizeof(s);s.header.pid=pid;memcpy(s.header.session,session,16);MemoryBarrier();InterlockedExchange(reinterpret_cast<volatile LONG*>(&s.header.magic),Magic);}
inline void write(Cell& c,const Manifest& m){InterlockedIncrement(&c.guard);c.value=m;MemoryBarrier();InterlockedIncrement(&c.guard);}
inline bool read(Cell& c,Manifest& m){const auto g=InterlockedCompareExchange(&c.guard,0,0);if(!g||(g&1))return false;m=c.value;MemoryBarrier();return g==InterlockedCompareExchange(&c.guard,0,0);}
inline bool contains(const Manifest& m,const native_gate::Ticket& t){if(m.frame!=t.frame||m.sequence!=t.sequence||m.hash!=t.hash)return false;
 for(DWORD i=0;i<m.count;++i){const auto& x=m.members[i];if(x.owner==t.owner&&x.revision==t.revision&&x.model==t.model&&x.source==t.source)return true;}return false;}
// Only use on the receiver's private,already coherently validated frame copy.
// Matching later owners must not reread a mutable shared ring slot.
inline bool retainedRow(const multi_scene::Frame& f,const native_gate::Ticket& t,live_owner::Row& out){
 if(f.frame!=t.frame||f.sequence!=t.sequence||f.checksum!=t.hash||f.count>multi_scene::Owners)return false;
 for(DWORD i=0;i<f.count;++i){const auto& r=f.rows[i];
  if(r[1]==t.owner&&r[7]==t.revision&&r[5]==t.model&&r[6]==t.source&&r[2]==t.frame&&r[47]==t.thread){out=r;return true;}}
 return false;
}
inline bool qualifies(const Manifest& m,multi_scene::Store& catalog,const multi_scene::Frame& f){
 if(!valid(m,catalog.header.session)||m.frame!=f.frame||m.sequence!=f.sequence||m.hash!=f.checksum||m.anchor!=f.anchor||m.revision!=f.revision)return false;
 for(DWORD i=0;i<m.count;++i){const auto& x=m.members[i];bool found=false;
  for(DWORD j=0;j<f.count;++j){const auto& r=f.rows[j];if(r[1]==x.owner&&r[7]==x.revision&&r[5]==x.model&&r[6]==x.source){found=true;break;}}
  multi_scene::Asset a{};if(!found||!multi_scene::read(catalog.assets[x.asset-1],a)||a.id!=x.asset||a.owner!=x.owner||a.revision!=x.revision||a.model!=x.model||a.source!=x.source||memcmp(a.content,x.content,32))return false;
 }return true;
}
inline void count(Store& s,const native_gate::Ticket& t,bool inserted,bool suppressed){OwnerStats* out=nullptr;
 for(auto& x:s.owners)if(x.owner==t.owner&&x.revision==t.revision){out=&x;break;}
 if(!out)for(auto& x:s.owners)if(!x.owner){x.owner=t.owner;x.revision=t.revision;x.model=t.model;x.source=t.source;out=&x;break;}
 if(!out){InterlockedIncrement(&s.header.omitted);return;}out->lastFrame=static_cast<LONG>(t.frame);
 if(inserted){InterlockedIncrement(&out->inserted);InterlockedIncrement(&s.header.inserted);}
 else if(suppressed){InterlockedIncrement(&out->suppressed);InterlockedIncrement(&s.header.suppressed);}
 else{InterlockedIncrement(&out->unavailable);InterlockedIncrement(&s.header.unavailable);}
}
}
