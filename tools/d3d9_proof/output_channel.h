// Experimental offline GPU-output ownership wire. No pointers,SDK types or pixels.
#pragma once
#include <windows.h>
#include <cstdint>
#include <cstddef>
namespace output_wire {
constexpr uint32_t magic=0x314f4653,version=1;
constexpr unsigned verification_stride=59; // prime to 3/4snapshot cycles
// Live source runs up to90s; receiver includes startup/shutdown margin without
// extending that source or its enclosing bounded-job deadline. Offline stays60s.
constexpr uint64_t receiver_lifetime_ms(bool live,bool game=false,bool tuning=false){return tuning?1980000ull:game?130000ull:live?110000ull:60000ull;}
// Adapter qualification,not a neutral scene-format restriction. 1280x360 has
// confirmed scrambled returned layout;other extents need explicit offline proof.
inline bool qualified_extent(uint32_t w,uint32_t h){return (w==960&&h==540)||(w==640&&h==960)||(w==1920&&h==1080);}
enum State:LONG {idle=0,ready=1,acquired=2,acknowledged=3,stopped=4,rejected=5};
struct alignas(8) Packet {
 uint32_t magic_value,version_value,bytes,producer_pid;
 uint64_t session,resource_epoch,sequence,source_frame;
 uint32_t owner,revision,width,height;
 uint32_t luid_low;int32_t luid_high;
 uint64_t handles[3];
 uint64_t source_state_hash,scene_hash,published_qpc,checksum;
};
struct alignas(64) Channel {
 volatile LONG state;LONG reserved;
 uint64_t ack_session,ack_epoch,ack_sequence;
 Packet packet;
 uint8_t padding[32];
};
static_assert(sizeof(Packet)==128&&sizeof(Channel)==192);
static_assert(offsetof(Channel,packet)==32&&offsetof(Packet,handles)==72);
inline uint64_t hash(const void* data,size_t bytes){
 uint64_t h=14695981039346656037ull;auto* b=static_cast<const unsigned char*>(data);
 for(size_t i=0;i<bytes;++i){h^=b[i];h*=1099511628211ull;}return h;
}
inline uint64_t checksum(const Packet& p){return hash(&p,offsetof(Packet,checksum));}
inline bool valid(const Packet& p,uint64_t session,uint32_t pid){
 return p.magic_value==magic&&p.version_value==version&&p.bytes==sizeof(Packet)&&p.producer_pid==pid&&
 p.session==session&&session&&p.resource_epoch&&p.sequence&&p.source_frame&&p.owner&&p.revision&&
 p.width&&p.height&&p.width<=1920&&p.height<=1080&&uint64_t(p.width)*p.height*12<=128ull*1024*1024&&
 p.handles[0]&&p.handles[1]&&p.handles[2]&&p.handles[0]<=UINT32_MAX&&p.handles[1]<=UINT32_MAX&&p.handles[2]<=UINT32_MAX&&p.source_state_hash&&p.scene_hash&&p.published_qpc&&p.checksum==checksum(p);
}
inline bool valid_ack(const Channel& c,const Packet& p){return c.ack_session==p.session&&c.ack_epoch==p.resource_epoch&&c.ack_sequence==p.sequence;}
inline LONG state(Channel* c){return InterlockedCompareExchange(&c->state,0,0);}
}
