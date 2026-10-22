// Renderer-neutral one-frame history contract. Never accept an old overlay
// against a new background;the saved scene and metadata advance together.
#pragma once
#include "game_output_wire.h"
#include "live_owner_wire.h"
#include <algorithm>
namespace synchronized_frame {
constexpr DWORD Offset=game_output::Offset+4096,Magic=0x31424653,Capacity=8192;
struct Header {DWORD magic=Magic,version=1,bytes=0,pid=0,session[4]{},count=0,dropped=0,max_age_us=0,failed=0,reserved[4]{};};
struct Audit {DWORD current=0,scene=0,output=0,status=0,owner=0,revision=0,age_us=0,reserved=0;
 uint64_t input_sequence=0,output_sequence=0,expected_hash=0,returned_hash=0,qpc=0;};
struct Store {Header header{};Audit rows[Capacity]{};};
static_assert(sizeof(Header)==64&&sizeof(Audit)==72&&Offset+sizeof(Store)<12*1024*1024);
inline bool adjacent(const live_owner::Row& previous,const live_owner::Row& current,uint64_t captured,uint64_t now,uint64_t frequency){
 return previous[2]&&previous[2]!=UINT32_MAX&&current[2]==previous[2]+1&&previous[1]==current[1]&&previous[7]==current[7]&&
  previous[5]==current[5]&&previous[6]==current[6]&&previous[4]==1&&current[4]==1&&
  live_owner::sequence(previous)&&live_owner::sequence(current)&&captured&&now>=captured&&frequency&&
  now-captured<=frequency/20; // At most one adjacent game frame AND50ms,never indefinite.
}
inline void append(Store& s,Audit a){if(s.header.count>=Capacity){++s.header.dropped;return;}
 s.rows[s.header.count]=a;s.header.max_age_us=(std::max)(s.header.max_age_us,a.age_us);MemoryBarrier();++s.header.count;}
}
