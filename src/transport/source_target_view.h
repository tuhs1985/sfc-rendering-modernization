#pragma once
// Read-only view of the existing native target notice. No graphics API types,
// interlocked writes, new mapping or dependency on model/texture readiness.
#include "source_scene_view.h"
namespace sfc_source_view {
constexpr uint32_t TargetOffset=4352;
struct alignas(8) NativeTarget {
    uint32_t magic,version,bytes,pid,session[4];
    uint64_t observed;
    uint32_t width,height,device,generation;
    uint64_t checksum;
};
struct alignas(64) TargetSlot {volatile uint32_t sequence;uint8_t reserved[60];NativeTarget notice;};
static_assert(sizeof(NativeTarget)==64&&sizeof(TargetSlot)==128&&offsetof(NativeTarget,checksum)==56);
inline Status target(const void* base,size_t bytes,const std::array<uint32_t,4>& session,uint32_t pid,NativeTarget& out){
    if(!base||bytes<MappingBytes||!pid)return Status::InvalidHeader;
    const auto& slot=*reinterpret_cast<const TargetSlot*>(static_cast<const uint8_t*>(base)+TargetOffset);
    const auto before=load(slot.sequence);if(!before)return Status::Empty;if(before&1)return Status::Retry;
    NativeTarget value{};std::memcpy(&value,&slot.notice,sizeof(value));std::atomic_thread_fence(std::memory_order_acquire);
    if(load(slot.sequence)!=before)return Status::Retry;
    if(value.magic!=0x31544754||value.version!=1||value.bytes!=sizeof(value)||value.pid!=pid||
       std::memcmp(value.session,session.data(),16))return Status::InvalidHeader;
    if(value.checksum!=hash(&value,offsetof(NativeTarget,checksum))||!value.observed||!value.device||!value.generation)return Status::InvalidFrame;
    if(!value.width&&!value.height)return Status::Stopped;
    if(!value.width||!value.height||value.width>3840||value.height>2160)return Status::InvalidFrame;
    out=value;return Status::Ready;
}
}
