#pragma once
#include <array>
#include <cstdint>
#include <cstddef>
// UE backend output descriptor. Independent of the source-scene DLL ABI.
namespace sfc_ue_output {
constexpr uint32_t Magic=0x314f4555, Version=1;
constexpr uint32_t Replay=1, SourceFrame=2, SourceSequence=4;
constexpr uint32_t Slots=2;
constexpr uint64_t ResourceBudget=128ull*1024*1024;
// Two UE source planes, four export planes, four normalization planes,
// and six game-pool planes. Each plane occupies four bytes per pixel.
constexpr uint64_t OutputBytesPerPixel=64;
struct Identity {
    std::array<uint64_t,2> session{};
    std::array<uint8_t,32> asset{};
    uint64_t owner_epoch{},revision{},frame{},sequence{},camera_pose{},cohort{};
    uint64_t activation{},device{},target{},output{};
};
struct alignas(8) Ticket {
    uint32_t magic=Magic,version=Version,bytes=sizeof(Ticket),flags{};
    uint32_t producer{},consumer{},width{},height{};
    // Export extent is tactical-sized. The receiver places it into the full
    // native target without rescaling or changing the captured projection.
    uint32_t target_width{},target_height{},viewport_x{},viewport_y{};
    uint64_t adapter_luid{};
    Identity identity{};
    uint64_t resource_epoch{},slot_epoch{};
    uint64_t images[3]{},ready_fence{},ack_fence{},ready_value{},ack_value{};
    uint32_t formats[3]{87,41,41}; // DXGI B8G8R8A8_UNORM, R32_FLOAT, R32_FLOAT
    uint32_t slot{};
    uint64_t checksum{};
};
static_assert(sizeof(Ticket)==280 && offsetof(Ticket,checksum)==272);
inline uint64_t hash(const void* memory,size_t bytes){
    uint64_t result=14695981039346656037ull;
    const auto* data=static_cast<const uint8_t*>(memory);
    for(size_t i=0;i<bytes;++i) result=(result^data[i])*1099511628211ull;
    return result;
}
inline void seal(Ticket& ticket){ticket.checksum=hash(&ticket,offsetof(Ticket,checksum));}
inline bool same(const Identity& a,const Identity& b){
    return a.session==b.session&&a.asset==b.asset&&a.owner_epoch==b.owner_epoch&&
        a.revision==b.revision&&a.frame==b.frame&&a.sequence==b.sequence&&
        a.camera_pose==b.camera_pose&&a.cohort==b.cohort&&a.activation==b.activation&&
        a.device==b.device&&a.target==b.target&&a.output==b.output;
}
inline bool valid(const Ticket& t,const Identity& expected,uint32_t producer,uint32_t consumer,uint64_t adapter_luid,bool diagnostic=false){
    const auto& i=t.identity;
    bool asset=false;for(auto byte:i.asset)asset|=byte!=0;
    return t.magic==Magic&&t.version==Version&&t.bytes==sizeof(Ticket)&&
        !(t.flags&~(Replay|SourceFrame|SourceSequence))&&(!(t.flags&Replay)||diagnostic)&&
        ((t.flags&Replay)||(t.flags&(SourceFrame|SourceSequence))==(SourceFrame|SourceSequence))&&
        (!(t.flags&SourceFrame)||i.frame)&&(!(t.flags&SourceSequence)||i.sequence)&&
        (i.session[0]||i.session[1])&&asset&&i.owner_epoch&&i.revision&&
        i.camera_pose&&i.cohort&&i.activation&&i.device&&i.target&&i.output&&
        same(i,expected)&&producer&&consumer&&t.producer==producer&&t.consumer==consumer&&t.adapter_luid==adapter_luid&&
        t.width&&t.height&&t.width<=4096&&t.height<=4096&&
        t.target_width&&t.target_height&&t.target_width<=4096&&t.target_height<=4096&&
        uint64_t(t.viewport_x)+t.width<=t.target_width&&uint64_t(t.viewport_y)+t.height<=t.target_height&&
        uint64_t(t.target_width)*t.target_height*OutputBytesPerPixel<=ResourceBudget&&
        t.resource_epoch&&t.slot_epoch&&t.slot<Slots&&
        t.images[0]&&t.images[1]&&t.images[2]&&t.ready_fence&&t.ack_fence&&
        t.ready_value&&t.ack_value&&
        t.formats[0]==87&&t.formats[1]==41&&t.formats[2]==41&&
        t.checksum==hash(&t,offsetof(Ticket,checksum));
}
// A lease registry supplies expected after descriptor admission. Never use the
// untrusted incoming record as its own expected lease.
inline bool matches_lease(const Ticket& t,const Ticket& expected){
    if(!valid(t,expected.identity,expected.producer,expected.consumer,expected.adapter_luid))return false;
    if(t.flags!=expected.flags||t.width!=expected.width||t.height!=expected.height||
       t.target_width!=expected.target_width||t.target_height!=expected.target_height||
       t.viewport_x!=expected.viewport_x||t.viewport_y!=expected.viewport_y||
       t.resource_epoch!=expected.resource_epoch||t.slot_epoch!=expected.slot_epoch||
       t.slot!=expected.slot||t.ready_fence!=expected.ready_fence||t.ack_fence!=expected.ack_fence||
       t.ready_value!=expected.ready_value||t.ack_value!=expected.ack_value)return false;
    for(size_t n=0;n<3;++n)if(t.images[n]!=expected.images[n])return false;
    return true;
}
struct Receipt {
    Identity identity{};
    uint64_t resource_epoch{},slot_epoch{},ack_value{};
    uint32_t consumer{},slot{};
};
inline bool acknowledges(const Receipt& ack,const Ticket& ticket){
    return same(ack.identity,ticket.identity)&&ack.resource_epoch==ticket.resource_epoch&&
        ack.slot_epoch==ticket.slot_epoch&&ack.ack_value==ticket.ack_value&&
        ack.consumer==ticket.consumer&&ack.slot==ticket.slot;
}
}
