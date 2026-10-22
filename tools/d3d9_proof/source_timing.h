// Bounded metadata-only probe. Not a source-frame seal or live delivery protocol.
#pragma once
#include "../m1_component/m1_present_calibration.h"
#include <cstdint>
#include <cstddef>
namespace source_timing {
constexpr uint32_t Magic=0x31545344,Version=1,Offset=12*1024*1024,Capacity=32768,DetailOwners=8;
struct Record {
 uint32_t stage,frame,callback,owner,revision,status,source_thread,reserved;
 uint64_t first_qpc,last_qpc,observed_qpc,pose_hash,camera_hash;
 uint32_t model,source;
};
struct alignas(64) Header {
 uint32_t magic,version,bytes,capacity,producer_pid,thread,count,dropped;
 uint32_t callbacks,wrong_thread,invalid,snapshot_miss;
 uint64_t frequency;
 uint32_t session[4];
 uint32_t missing_stamp,ambiguous,owner_limit,reserved;
 uint8_t padding[40];
};
struct Store {Header header;Record records[Capacity];};
static_assert(sizeof(Record)==80&&sizeof(Header)==128&&sizeof(Store)==2621568);
static_assert(Offset+sizeof(Store)<=16*1024*1024);
inline uint64_t hash(const DWORD* p,size_t words){uint64_t h=14695981039346656037ull;const auto* b=reinterpret_cast<const unsigned char*>(p);for(size_t i=0;i<words*4;++i){h^=b[i];h*=1099511628211ull;}return h;}
inline void initialize(Store& s,uint32_t pid,uint32_t thread,uint64_t frequency,const DWORD* session){
 ZeroMemory(&s,sizeof(s));auto& h=s.header;h.magic=Magic;h.version=Version;h.bytes=sizeof(Store);h.capacity=Capacity;h.producer_pid=pid;h.thread=thread;h.frequency=frequency;memcpy(h.session,session,16);
}
inline void append(Store& s,const sfc_calibration::Snapshot& snap,uint32_t stage,uint32_t thread,uint64_t now){
 auto& h=s.header;++h.callbacks;
 if(thread!=h.thread){++h.wrong_thread;return;}
 if((stage!=1&&stage!=2)||snap.magic!=sfc_calibration::Magic||snap.version!=sfc_calibration::Version||snap.bytes!=sizeof(snap)||!snap.frame||!snap.rows||snap.rows>32||memcmp(snap.session,h.session,16)){++h.invalid;return;}
 unsigned actual=0;for(unsigned i=0;i<32;++i)if(snap.owner[i][1]){++actual;for(unsigned j=0;j<i;++j)if(snap.owner[j][1]==snap.owner[i][1]){++h.invalid;return;}}
 if(actual!=snap.rows){++h.invalid;return;}
 uint32_t detailed=0;
 for(unsigned i=0;i<32;++i){const auto& r=snap.owner[i];if(!r[1])continue;
  if(r[4]==3){++h.ambiguous;continue;}
  if(r[2]!=snap.frame||r[4]!=1||!r[7]||r[45]!=i||r[47]!=thread||r[48]!=1||!r[5]||!r[6]){++h.invalid;continue;}
  if(r[93]!=sfc_calibration::TimingMagic){++h.missing_stamp;continue;}
  const uint64_t first=r[89]|(uint64_t(r[90])<<32),last=r[91]|(uint64_t(r[92])<<32);
  if(!first||first>last||last>now){++h.invalid;continue;}
  if(detailed++>=DetailOwners){++h.owner_limit;continue;}
  if(h.count>=Capacity){++h.dropped;continue;}
  Record record{stage,snap.frame,h.callbacks,r[1],r[7],r[4],r[47],0,first,last,now,hash(r.data()+8,17),hash(r.data()+49,40),r[5],r[6]};
  s.records[h.count]=record;MemoryBarrier();++h.count;
 }
}
}
