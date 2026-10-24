// Default-off raw OWNER transport;never a complete multi-object frame seal.
#pragma once
#include "frame_ingress.h"
#include <array>
namespace live_owner {
constexpr DWORD Offset=10*1024*1024,Magic=0x314f4c53,AuditCapacity=12000;
using Row=std::array<DWORD,96>;
struct Packet {DWORD session[4]{};uint64_t sequence=0,offered=0,state_hash=0;Row row{};uint64_t checksum=0;};
struct Completion {DWORD session[4]{};uint64_t sequence=0,offered=0,completed=0,state_hash=0;DWORD frame=0,owner=0,revision=0,reserved=0;uint64_t checksum=0;};
template<class T,unsigned Padding>struct alignas(64) Slot {volatile LONG state=0;LONG reserved=0;T packet{};BYTE padding[Padding]{};};
struct Audit {DWORD frame=0,owner=0,revision=0,status=0;uint64_t present=0,offered=0,completed=0,input_sequence=0,completed_sequence=0,expected_hash=0,returned_hash=0;DWORD returned_frame=0,returned_owner=0,returned_revision=0,flags=0;BYTE padding[8]{};};
struct alignas(64) Header {
 DWORD magic=Magic,version=1,bytes=0,session[4]{},pid=0;
 alignas(8) volatile LONG64 selected=0;
 volatile LONG stopped=0,frame=0,bad_frame=0;
 DWORD source_thread=0,published=0,replaced=0,source_rejected=0,audits=0,audit_dropped=0,completion_invalid=0;
 BYTE padding[48]{};
};
struct Store {Header header{};Slot<Packet,72> input[4]{};Slot<Completion,48> output[4]{};Audit audits[AuditCapacity]{};};
static_assert(sizeof(Packet)==432&&sizeof(Completion)==72&&sizeof(Audit)==96&&sizeof(Header)==128);
static_assert(sizeof(Slot<Packet,72>)==512&&sizeof(Slot<Completion,48>)==128);
static_assert(Offset+sizeof(Store)<12*1024*1024);
inline uint64_t row_hash(Row row){
 row[0]=row[3]=row[45]=row[47]=0;for(unsigned i=89;i<96;++i)row[i]=0;
 return frame_ingress::hash(row.data(),sizeof(row));
}
template<class T>inline uint64_t checksum(const T& p){return frame_ingress::hash(&p,offsetof(T,checksum));}
inline bool same_session(const DWORD* a,const DWORD* b){return !memcmp(a,b,16);}
inline uint64_t sequence(const Row& r){return r[94]|(uint64_t(r[95])<<32);}
inline uint64_t selection(DWORD owner,DWORD revision){return owner|(uint64_t(revision)<<32);}
inline bool valid(const Packet& p,const Header& h){return same_session(p.session,h.session)&&p.sequence&&p.offered&&p.row[1]&&p.row[2]&&p.row[4]==1&&p.row[5]&&p.row[6]&&p.row[7]&&p.row[48]==1&&sequence(p.row)==p.sequence&&p.state_hash==row_hash(p.row)&&p.checksum==checksum(p);}
inline bool valid(const Completion& p,const Header& h){return same_session(p.session,h.session)&&p.sequence&&p.offered&&p.completed>=p.offered&&p.state_hash&&p.frame&&p.owner&&p.revision&&!p.reserved&&p.checksum==checksum(p);}
template<class T,unsigned P>inline bool publish(Slot<T,P>(&slots)[4],const T& packet,DWORD& replaced){
 for(unsigned pass=0;pass<2;++pass)for(auto& s:slots){const LONG expected=pass?frame_ingress::Ready:frame_ingress::Free;
  if(InterlockedCompareExchange(&s.state,frame_ingress::Writing,expected)!=expected)continue;
  s.packet=packet;InterlockedExchange(&s.state,frame_ingress::Ready);if(pass)++replaced;return true;
 }return false;
}
template<class T,unsigned P>inline bool take(Slot<T,P>(&slots)[4],const Header& h,T& packet,uint64_t& last,DWORD& invalid){
 bool found=false;for(auto& s:slots){if(InterlockedCompareExchange(&s.state,frame_ingress::Reading,frame_ingress::Ready)!=frame_ingress::Ready)continue;
  T p=s.packet;InterlockedExchange(&s.state,frame_ingress::Free);
  if(!valid(p,h)){++invalid;continue;}if(p.sequence<=last)continue;
  packet=p;last=p.sequence;found=true;
 }return found;
}
inline bool header_valid(const Header& h,const DWORD* session){return h.magic==Magic&&(h.version==1||h.version==2)&&h.bytes==sizeof(Store)&&same_session(h.session,session);}
struct Source {
 Store* store=nullptr;uint64_t counter=0;
 bool attach(BYTE* mapping,const DWORD* session){
  store=reinterpret_cast<Store*>(mapping+Offset);if(!header_valid(store->header,session)||frame_ingress::state(&store->header.stopped)){store=nullptr;return false;}
  store->header.pid=GetCurrentProcessId();return true;
 }
 void begin(DWORD frame){if(store)InterlockedExchange(&store->header.frame,static_cast<LONG>(frame));}
 void reject(DWORD frame){if(store){InterlockedExchange(&store->header.bad_frame,static_cast<LONG>(frame));++store->header.source_rejected;}}
 void retire(DWORD owner,DWORD frame){if(store&&static_cast<DWORD>(InterlockedCompareExchange64(&store->header.selected,0,0))==owner)InterlockedExchange(&store->header.bad_frame,static_cast<LONG>(frame));}
 bool prepare(Row& row,Packet& p){
  if(!store)return false;auto& h=store->header;if(frame_ingress::state(&h.stopped))return false;
  const auto selected=static_cast<uint64_t>(InterlockedCompareExchange64(&h.selected,0,0));
  if(selected!=selection(row[1],row[7]))return false;
  if(h.source_thread&&h.source_thread!=GetCurrentThreadId()){reject(row[2]);return false;}h.source_thread=GetCurrentThreadId();
  if(row[4]!=1||!row[48]){reject(row[2]);return false;}
  LARGE_INTEGER q{};if(!QueryPerformanceCounter(&q)){reject(row[2]);return false;}
  p={};memcpy(p.session,h.session,16);p.sequence=++counter;p.offered=static_cast<uint64_t>(q.QuadPart);
  row[94]=static_cast<DWORD>(p.sequence);row[95]=static_cast<DWORD>(p.sequence>>32);p.row=row;p.state_hash=row_hash(row);p.checksum=checksum(p);
  return true;
 }
 bool commit(const Packet& p){
  if(!store||frame_ingress::state(&store->header.stopped))return false;auto& h=store->header;
  if(!valid(p,h)||!publish(store->input,p,h.replaced)){reject(p.row[2]);return false;}++h.published;return true;
 }
 void offer(Row& row){Packet p{};if(prepare(row,p)&&!commit(p))row[94]=row[95]=0;
 }
 void close(){if(store)InterlockedExchange(&store->header.stopped,1);store=nullptr;}
};
struct PresentObserver {
 Store* store=nullptr;Completion latest{};uint64_t last=0;
 void observe(const Row* row,DWORD frame,DWORD thread,uint64_t now){
  if(!store||frame_ingress::state(&store->header.stopped))return;auto& h=store->header;
  take(store->output,h,latest,last,h.completion_invalid);
  if(!InterlockedCompareExchange64(&h.selected,0,0))return;
  if(h.audits>=AuditCapacity){++h.audit_dropped;return;}
  Audit a{};a.frame=frame;a.present=now;a.completed=latest.completed;a.completed_sequence=latest.sequence;a.offered=latest.offered;
  a.returned_hash=latest.state_hash;a.returned_frame=latest.frame;a.returned_owner=latest.owner;a.returned_revision=latest.revision;
  const auto chosen=static_cast<uint64_t>(InterlockedCompareExchange64(&h.selected,0,0));
  const bool eligible=row&&row->at(1)==static_cast<DWORD>(chosen)&&row->at(7)==static_cast<DWORD>(chosen>>32)&&row->at(2)==frame&&row->at(4)==1&&row->at(47)==thread&&sequence(*row)&&
   static_cast<DWORD>(frame_ingress::state(&h.frame))==frame&&static_cast<DWORD>(frame_ingress::state(&h.bad_frame))!=frame;
  if(!eligible)a.status=5;
  else{a.owner=(*row)[1];a.revision=(*row)[7];a.input_sequence=sequence(*row);a.expected_hash=row_hash(*row);
   if(!latest.sequence)a.status=4;
   else if(latest.sequence!=a.input_sequence||latest.frame!=frame||latest.owner!=a.owner||latest.revision!=a.revision)a.status=2;
   else if(latest.state_hash!=a.expected_hash)a.status=3;
   else if(latest.completed>now)a.status=6;
   else a.status=1;
  }
  store->audits[h.audits]=a;MemoryBarrier();++h.audits;
 }
};
}
