#pragma once
// Read-only view of the EXISTING protocol4 mapping's version3 scene store.
// No new wire, renderer types, process-memory dereference or coordinate changes.
#include "../../tools/scene_bridge/scene_capacity.h"
#include <array>
#include <atomic>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace sfc_source_view {
constexpr uint32_t MappingBytes=16*1024*1024,SceneOffset=scene_capacity::SceneOffset;
constexpr uint32_t Owners=scene_capacity::Owners,Assets=scene_capacity::Assets,Frames=8;
using Row=std::array<uint32_t,96>;
struct Header {
    uint32_t magic,version,bytes,pid,session[4];
    volatile uint32_t stopped,frame,published,dropped,invalid,asset_ready,asset_rejected,closed_frame;
};
struct Frame {
    uint64_t sequence,offered;
    uint32_t frame,anchor,revision,count;
    Row rows[Owners];
    std::array<uint32_t,5> damage[Owners]; // Original owner/revision/scalar/family/qualified words.
    uint64_t checksum;
};
struct alignas(64) FrameSlot {volatile uint32_t guard;uint32_t reserved;Frame packet;uint8_t padding[16];};
struct Asset {
    uint32_t id,path_id,owner,revision,model,source,geometry_bytes,image_bytes;
    uint8_t content[32];uint64_t replay_hash,textures_hash,checksum;
};
struct alignas(64) AssetSlot {volatile uint32_t guard,ack;Asset packet;uint8_t padding[32];};
struct Store {Header header;FrameSlot frames[Frames];AssetSlot assets[Assets];};
static_assert(sizeof(Asset)==88&&sizeof(AssetSlot)==128);
static_assert(sizeof(Header)==64&&sizeof(Frame)==40+Owners*404&&SceneOffset+sizeof(Store)<MappingBytes);
inline uint64_t hash(const void* data,size_t bytes){
    uint64_t result=14695981039346656037ull;
    for(size_t i=0;i<bytes;++i)result=(result^static_cast<const uint8_t*>(data)[i])*1099511628211ull;
    return result;
}
inline uint32_t load(const volatile uint32_t& word){
    const uint32_t value=word;std::atomic_thread_fence(std::memory_order_acquire);return value;
}
inline uint64_t sequence(const Row& row){return row[94]|(uint64_t(row[95])<<32);}
inline bool valid(const Frame& f){
    if(!f.sequence||!f.offered||!f.frame||!f.anchor||!f.revision||!f.count||f.count>Owners||
       f.checksum!=hash(&f,offsetof(Frame,checksum)))return false;
    bool anchor=false;
    for(uint32_t i=0;i<f.count;++i){
        const auto& r=f.rows[i];
        if(!r[1]||r[2]!=f.frame||r[4]!=1||!r[5]||!r[6]||!r[7]||r[48]!=1)return false;
        if(r[1]==f.anchor&&r[7]==f.revision){if(sequence(r)!=f.sequence)return false;anchor=true;}
        for(uint32_t j=0;j<i;++j)if(f.rows[j][1]==r[1])return false;
        if(i&&std::memcmp(r.data()+49,f.rows[0].data()+49,40*4))return false;
        const auto& d=f.damage[i];
        if(d[4]&&(d[4]!=1||d[0]!=r[1]||d[1]!=r[7]||d[3]>=3))return false;
    }
    return anchor;
}
enum class Status {Empty,Retry,Unchanged,Ready,InvalidHeader,InvalidFrame,Stopped};
inline Status catalog(const void* base,size_t bytes,uint32_t index,Asset& result){
    if(!base||bytes<MappingBytes||index>=Assets)return Status::InvalidHeader;
    const auto* store=reinterpret_cast<const Store*>(static_cast<const uint8_t*>(base)+SceneOffset);
    const auto& slot=store->assets[index];const auto before=load(slot.guard);
    if(!before)return Status::Empty;if(before&1)return Status::Retry;
    std::memcpy(&result,&slot.packet,sizeof(result));std::atomic_thread_fence(std::memory_order_acquire);
    if(load(slot.guard)!=before)return Status::Retry;
    bool content=false;for(auto byte:result.content)content|=byte!=0;
    return result.id==index+1&&result.path_id&&result.path_id<=Assets&&result.owner&&result.revision&&
        result.model&&result.source&&result.geometry_bytes&&result.geometry_bytes<=2*1024*1024&&
        result.image_bytes<=128*1024*1024&&content&&result.replay_hash&&result.textures_hash&&
        result.checksum==hash(&result,offsetof(Asset,checksum))?Status::Ready:Status::InvalidFrame;
}
inline Status owner_state(const void* base,size_t bytes,uint32_t index,Row& result){
    if(!base||bytes<MappingBytes||index>=Owners)return Status::InvalidHeader;
    const auto* slot=static_cast<const uint8_t*>(base)+scene_capacity::StateOffset+index*scene_capacity::StateStride;
    const auto& guard=*reinterpret_cast<const volatile uint32_t*>(slot);const auto before=load(guard);
    if(!before)return Status::Empty;if(before&1)return Status::Retry;
    std::memcpy(result.data(),slot+4,sizeof(result));std::atomic_thread_fence(std::memory_order_acquire);
    if(load(guard)!=before)return Status::Retry;
    return result[45]==index&&result[1]&&(result[4]==1||result[4]==2)?Status::Ready:Status::InvalidFrame;
}
inline Status snapshot(const void* base,size_t bytes,const std::array<uint32_t,4>& session,uint32_t pid,
                       uint64_t last_sequence,Frame& result){
    if(!base||bytes<MappingBytes||!pid)return Status::InvalidHeader;
    const auto* common=static_cast<const uint32_t*>(base);
    if(common[0]!=0x31424c53||common[1]!=scene_capacity::Version||common[2]!=MappingBytes||
       std::memcmp(common+4,session.data(),16))return Status::InvalidHeader;
    // Protocol4 common word3 is the LiveScene WORKER STATUS, not a PID:
    // 0 passive, 1 running, 2 stopped, 3 failed. The scene header below owns PID.
    const auto worker=load(*reinterpret_cast<const volatile uint32_t*>(common+3));
    if(!worker){
        // The session owner may cancel before the native producer attaches.
        // Only a valid same-session, unclaimed-or-matching header can stop us.
        const auto& h=reinterpret_cast<const Store*>(static_cast<const uint8_t*>(base)+SceneOffset)->header;
        if(h.magic==0x31534d53&&h.version==3&&h.bytes==sizeof(Store)&&
           !std::memcmp(h.session,session.data(),16)&&(!h.pid||h.pid==pid)&&load(h.stopped))return Status::Stopped;
        return Status::Empty;
    }
    if(worker==2)return Status::Stopped;
    if(worker!=1)return Status::InvalidHeader;
    const auto* store=reinterpret_cast<const Store*>(static_cast<const uint8_t*>(base)+SceneOffset);
    const auto& h=store->header;
    if(h.magic!=0x31534d53||h.version!=3||h.bytes!=sizeof(Store)||std::memcmp(h.session,session.data(),16))return Status::InvalidHeader;
    if(h.pid&&h.pid!=pid)return Status::InvalidHeader;
    if(load(h.stopped))return Status::Stopped;
    if(!h.pid)return Status::Empty;
    const uint32_t number=load(h.frame);if(!number)return Status::Empty;
    const auto& slot=store->frames[number%Frames];const uint32_t before=load(slot.guard);
    if(!before||(before&1))return Status::Retry;
    std::memcpy(&result,&slot.packet,sizeof(result));std::atomic_thread_fence(std::memory_order_acquire);
    if(load(slot.guard)!=before)return Status::Retry;
    // The writer closes a reused slot before publishing the new header frame.
    // A reader may observe that short interval without any corrupt source data.
    if(result.frame!=number)return Status::Retry;
    if(!valid(result))return Status::InvalidFrame;
    return result.sequence>last_sequence?Status::Ready:Status::Unchanged;
}
// Stored rows are column-vector matrices in native units. The affine flag
// bypasses the stored bottom row, as the pinned source routine does.
inline bool matrix(const Row& row,unsigned offset,std::array<double,16>& result){
    if(offset+17>row.size())return false;
    const uint32_t flag=(row[offset+16]>>8)&255;if(flag>1)return false;
    for(unsigned i=0;i<16;++i){float value;std::memcpy(&value,&row[offset+i],4);if(!std::isfinite(value))return false;result[i]=value;}
    if(flag){result[12]=result[13]=result[14]=0;result[15]=1;}
    return true;
}
struct Pose {std::array<double,16> model{},view{},projection{};std::array<double,6> viewport{};};
inline bool camera(const Row& row,Pose& result){
    if(!matrix(row,49,result.view)||!matrix(row,66,result.projection))return false;
    for(unsigned i=0;i<6;++i){float value;std::memcpy(&value,&row[83+i],4);result.viewport[i]=value;}
    const auto& v=result.viewport;
    for(double n:v)if(!std::isfinite(n))return false;
    return v[0]>=0&&v[1]>=0&&v[2]>=1&&v[3]>=1&&v[2]<=4096&&v[3]<=4096&&
        std::abs(v[2]-2*v[4])<=.001&&std::abs(v[3]-2*v[5])<=.001;
}
inline bool pose(const Row& row,Pose& result){
    return !row[42]&&!row[43]&&!row[44]&&matrix(row,8,result.model)&&camera(row,result);
}
inline const Row* find(const Frame& frame,uint32_t owner,uint32_t revision,uint32_t model,uint32_t source){
    for(uint32_t i=0;i<frame.count;++i){const auto& r=frame.rows[i];
        if(r[1]==owner&&r[7]==revision&&r[5]==model&&r[6]==source)return &r;
    }
    return nullptr;
}
}
