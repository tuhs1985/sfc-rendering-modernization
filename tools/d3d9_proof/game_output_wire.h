// Default-off two-slot GPU handoff within existing current-user semantic mapping.
// Immutable source identity is distinct from ordinary Remix picking/material IDs.
#pragma once
#include "output_channel.h"
#include <cstring>
namespace game_output {
constexpr uint32_t Magic=0x314f4753,Version=2,Offset=11*1024*1024+128*1024;
constexpr LONG Writing=6;
struct Metadata {uint64_t source_sequence;DWORD source_session[4];uint64_t checksum;};
static_assert(sizeof(Metadata)==32);
inline uint64_t checksum(const Metadata& m){return output_wire::hash(&m,24);}
inline bool valid(const Metadata& m,const DWORD* session){return m.source_sequence&&memcmp(m.source_session,session,16)==0&&m.checksum==checksum(m);}
inline Metadata metadata(const output_wire::Channel& slot){Metadata m{};memcpy(&m,slot.padding,sizeof(m));return m;}
inline void metadata(output_wire::Channel& slot,const Metadata& m){memcpy(slot.padding,&m,sizeof(m));}
struct alignas(64) Header {
 uint32_t magic,version,bytes,game_pid;DWORD session[4];uint32_t receiver_pid,host_pid;
 volatile LONG stopped,ready,published,overwritten,busy,error;
};
struct alignas(64) Stats {volatile LONG drawn,stale,invalid,not_ready,retired,gpu_busy,resource_failed,depth_missing;DWORD frame;uint32_t reserved[7];};
struct alignas(64) Pool {Header header;BYTE asset[32];float camera_offset[3];uint32_t diagnostic_mode,reserved[4];output_wire::Channel slots[2];Stats stats;};
static_assert(sizeof(Header)==64&&sizeof(Stats)==64&&sizeof(Pool)==576&&Offset+sizeof(Pool)<12*1024*1024);
inline bool valid(const Header& h,const DWORD* session,uint32_t game){return h.magic==Magic&&h.version==Version&&h.bytes==sizeof(Pool)&&h.game_pid==game&&game&&h.receiver_pid&&h.host_pid&&memcmp(h.session,session,16)==0;}
inline int reserve(Pool& pool){
 if(InterlockedCompareExchange(&pool.header.stopped,0,0))return -1;
 for(unsigned pass=0;pass<2;++pass)for(unsigned i=0;i<2;++i){const LONG prior=pass?output_wire::ready:output_wire::idle;
  if(InterlockedCompareExchange(&pool.slots[i].state,Writing,prior)==prior){if(pass)InterlockedIncrement(&pool.header.overwritten);return static_cast<int>(i);}
 }InterlockedIncrement(&pool.header.busy);return -1;
}
inline bool matches(const output_wire::Packet& packet,const Metadata& meta,const DWORD* row,const DWORD* session,uint64_t hash,uint64_t sequence){
 return valid(meta,session)&&meta.source_sequence==sequence&&packet.owner==row[1]&&packet.revision==row[7]&&packet.source_frame==row[2]&&packet.source_state_hash==hash;
}
}
