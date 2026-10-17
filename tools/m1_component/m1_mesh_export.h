#pragma once
#include "m1_visual_tint.h"
#include <ostream>

namespace sfc_m1 {
// Fixed little-endian uint32 schema; no consumer dereferences native pointers.
// Header words 30..46/47..63 are unconverted native transform payloads.
enum MeshField : std::size_t {
    MeshMagic, MeshVersion, MeshBytes, MeshHash, MeshOwner, MeshThread,
    MeshFrame, MeshElapsed, MeshShip, MeshVisual, MeshModel, MeshManager,
    MeshSource, MeshCaller, MeshList, MeshVertexBase, MeshVertices, MeshPolygons,
    MeshCorners, MeshSources, MeshLodCount, MeshLodOverride, MeshLodSelected,
    MeshActualChild, MeshDispatch = 24, MeshSupplied = 30, MeshComposed = 47
};
struct MeshIdentity {
    std::uint32_t owner=0,thread=0,frame=0,elapsed=0,ship=0,visual=0,model=0,
        manager=0,source=0,caller=0,list=0,count=0;
    bool same_epoch(const MeshIdentity& b) const {
        return owner==b.owner && thread==b.thread && ship==b.ship && visual==b.visual &&
            model==b.model && manager==b.manager && source==b.source && list==b.list && count==b.count;
    }
};
enum class MeshStatus : std::uint32_t { Empty, Complete, Read, Count, Identity, Index, Nonfinite, Changed };
struct MeshPolygon {
    std::array<std::uint32_t,7> header{}; // word6 is PORTABLE corner ordinal, not pointer
    std::uint32_t native_header=0,native_corners=0; // provenance only
};
struct MeshSourceRecord { std::uint32_t index=0; std::array<std::uint32_t,9> words{}; };
template<std::uint32_t Polygons=512,std::uint32_t Corners=4096>
struct BasicMeshPacket {
    static constexpr std::uint32_t kPositions=65536,kPolygons=Polygons,kCorners=Corners,kSources=256;
    static constexpr std::uint32_t kFileLimit=2*1024*1024;
    std::array<std::uint32_t,64> header{};
    std::array<std::array<std::uint32_t,3>,kPositions> positions{};
    std::array<MeshPolygon,kPolygons> polygons{};
    std::array<std::array<std::uint32_t,7>,kCorners> corners{};
    std::array<MeshSourceRecord,kSources> sources{};
    bool complete=false;
    static bool finite(std::uint32_t bits) { return (bits&0x7f800000u)!=0x7f800000u; }
    static std::uint32_t hash_block(std::uint32_t h,const void* data,std::size_t size) {
        const auto* bytes=static_cast<const unsigned char*>(data);
        for(std::size_t i=0;i<size;++i){h^=bytes[i];h*=16777619u;}return h;
    }
    bool bounds() const {
        return header[MeshMagic]==0x314d4653 && header[MeshVersion]==1 &&
            header[MeshVertices]>0 && header[MeshVertices]<=kPositions &&
            header[MeshPolygons]>0 && header[MeshPolygons]<=kPolygons &&
            header[MeshCorners]>=header[MeshPolygons]*3 && header[MeshCorners]<=kCorners &&
            header[MeshSources]>0 && header[MeshSources]<=kSources;
    }
    std::uint32_t byte_size() const {
        return static_cast<std::uint32_t>(sizeof(header))+header[MeshVertices]*12+
            header[MeshPolygons]*36+header[MeshCorners]*28+header[MeshSources]*40;
    }
    std::uint32_t checksum() const {
        if(!bounds())return 0;
        auto copy=header;copy[MeshHash]=0;
        auto h=hash_block(2166136261u,copy.data(),sizeof(copy));
        h=hash_block(h,positions.data(),header[MeshVertices]*12);
        h=hash_block(h,polygons.data(),header[MeshPolygons]*36);
        h=hash_block(h,corners.data(),header[MeshCorners]*28);
        return hash_block(h,sources.data(),header[MeshSources]*40);
    }
    bool write(std::ostream& out) const {
        if(!complete || !bounds() || header[MeshBytes]!=byte_size() ||
           byte_size()>kFileLimit || checksum()!=header[MeshHash])return false;
        const auto block=[&](const void* p,std::uint32_t n){out.write(static_cast<const char*>(p),n);};
        block(header.data(),static_cast<std::uint32_t>(sizeof(header)));
        block(positions.data(),header[MeshVertices]*12);
        block(polygons.data(),header[MeshPolygons]*36);
        block(corners.data(),header[MeshCorners]*28);
        block(sources.data(),header[MeshSources]*40);
        return out.good();
    }
};
using MeshPacket=BasicMeshPacket<>;
using LiveMeshPacket=BasicMeshPacket<8192,32768>;
static_assert(sizeof(LiveMeshPacket)<2*1024*1024,"Live mesh storage exceeds 2 MiB");
static_assert(sizeof(MeshPolygon)==36 && sizeof(MeshSourceRecord)==40,"Mesh schema packing");
static_assert(sizeof(MeshPacket)<1024*1024,"Mesh storage exceeds 1 MiB");

// Read and Validate callbacks are guarded/live identity checks in production,
// injectable offline. No native writes, allocations or logging in this function.
template<class Packet,class Read,class Validate>
MeshStatus capture_mesh(Packet& out,const MeshIdentity& id,Read read,Validate valid) {
    out.complete=false;out.header={};
    const auto block=[&](std::uint32_t base,std::uint32_t offset,void* dst,std::uint32_t n){
        std::uint32_t start=0,end=0;
        return n && tint_address(base,offset,start) && tint_address(start,n-1,end) && read(start,dst,n);
    };
    const auto word=[&](std::uint32_t base,std::uint32_t offset,std::uint32_t& dst){return block(base,offset,&dst,4);};
    if(!id.owner || !id.thread || !id.ship || !id.visual || !id.model || !id.manager ||
       !id.source || id.caller!=0x0042E55D || !valid())return MeshStatus::Identity;
    std::array<std::uint32_t,6> model{};
    std::array<std::uint32_t,3> lod{};
    std::uint32_t vt=0,base=0,source=0,child=0,linked_visual=0,linked_source=0;
    if(!block(id.model,0,model.data(),24) || !block(id.visual,0x11c,lod.data(),12) ||
       !word(id.manager,0,vt) || !word(id.manager,0x554,base) || !word(id.manager,0x558,source) ||
       !word(id.ship,0x88,linked_visual) || !word(id.visual,0x158,linked_source))return MeshStatus::Read;
    if(model[0]!=0x007983E8 || vt!=0x007B8D4C || model[3]!=base || source!=id.source ||
       linked_source!=id.source || linked_visual!=id.visual || model[4]!=id.count || model[5]!=id.list)return MeshStatus::Identity;
    if(!model[2] || model[2]>Packet::kPositions || !model[4] || model[4]>Packet::kPolygons ||
       !lod[0] || lod[0]>64)return MeshStatus::Count;
    const auto selected=lod[1]!=0xffffffffu?lod[1]:(lod[0]>1?lod[2]:0);
    if(selected>=lod[0] || !word(id.visual,0x160+selected*4,child) || child!=id.model)return MeshStatus::Identity;
    auto& h=out.header;
    h[MeshMagic]=0x314d4653;h[MeshVersion]=1;h[MeshOwner]=id.owner;h[MeshThread]=id.thread;
    h[MeshFrame]=id.frame;h[MeshElapsed]=id.elapsed;h[MeshShip]=id.ship;h[MeshVisual]=id.visual;
    h[MeshModel]=id.model;h[MeshManager]=id.manager;h[MeshSource]=id.source;h[MeshCaller]=id.caller;
    h[MeshList]=id.list;h[MeshVertexBase]=base;h[MeshVertices]=model[2];h[MeshPolygons]=model[4];
    h[MeshLodCount]=lod[0];h[MeshLodOverride]=lod[1];h[MeshLodSelected]=lod[2];h[MeshActualChild]=selected;
    if(!block(base,0,out.positions.data(),model[2]*12) ||
       !block(id.manager,0x6f4,h.data()+MeshSupplied,68) ||
       !block(id.manager,0x6b0,h.data()+MeshComposed,68) ||
       !read(0x00C69FF0,&h[24],4) || !read(0x00C69FF4,&h[25],4) || !read(0x00C74058,&h[26],4))return MeshStatus::Read;
    std::array<bool,256> seen{};
    for(std::uint32_t p=0;p<model[4];++p) {
        auto& poly=out.polygons[p];
        if(!word(id.list,p*4,poly.native_header) || !block(poly.native_header,0,poly.header.data(),28))return MeshStatus::Read;
        const auto count=poly.header[0],index=poly.header[1];
        if(count<3 || count>8 || index>=256 || count>Packet::kCorners-h[MeshCorners])return MeshStatus::Count;
        poly.native_corners=poly.header[6];poly.header[6]=h[MeshCorners];
        if(!block(poly.native_corners,0,out.corners.data()+h[MeshCorners],count*28))return MeshStatus::Read;
        for(std::uint32_t c=0;c<count;++c) {
            const auto& corner=out.corners[h[MeshCorners]+c];
            const auto vertex=corner[0]&0xffffu;
            if(vertex>=model[2])return MeshStatus::Index;
            for(auto bits:out.positions[vertex])if(!MeshPacket::finite(bits))return MeshStatus::Nonfinite;
            for(std::uint32_t f=1;f<=5;++f)if(!MeshPacket::finite(corner[f]))return MeshStatus::Nonfinite;
        }
        h[MeshCorners]+=count;
        if(!seen[index]) {
            auto& record=out.sources[h[MeshSources]++];record.index=index;
            if(!block(id.source,index*36,record.words.data(),36))return MeshStatus::Read;
            seen[index]=true;
        }
    }
    // Bounded second pass. Detect changed inputs; this is not a global atomicity claim.
    std::array<std::uint32_t,1024> scratch{};
    const auto equal=[&](std::uint32_t address,const void* expected,std::uint32_t bytes){
        const auto* expected_bytes=static_cast<const unsigned char*>(expected);
        for(std::uint32_t offset=0;offset<bytes;) {
            const auto n=(bytes-offset)>sizeof(scratch)?static_cast<std::uint32_t>(sizeof(scratch)):bytes-offset;
            if(!block(address,offset,scratch.data(),n) || std::memcmp(scratch.data(),expected_bytes+offset,n))return false;
            offset+=n;
        }return true;
    };
    if(!equal(base,out.positions.data(),model[2]*12) || !equal(id.model,model.data(),24) ||
       !block(id.visual,0x11c,scratch.data(),12) || std::memcmp(scratch.data(),lod.data(),12) ||
       !equal(id.manager+0x6f4,h.data()+MeshSupplied,68) || !equal(id.manager+0x6b0,h.data()+MeshComposed,68))return MeshStatus::Changed;
    for(std::uint32_t p=0;p<model[4];++p) {
        const auto& poly=out.polygons[p];auto header=poly.header;header[6]=poly.native_corners;
        std::uint32_t pointer=0;
        if(!word(id.list,p*4,pointer) || pointer!=poly.native_header || !equal(pointer,header.data(),28) ||
           !equal(poly.native_corners,out.corners.data()+poly.header[6],poly.header[0]*28))return MeshStatus::Changed;
    }
    for(std::uint32_t s=0;s<h[MeshSources];++s)
        if(!equal(id.source+out.sources[s].index*36,out.sources[s].words.data(),36))return MeshStatus::Changed;
    std::uint32_t final_base=0,final_source=0,final_child=0;
    if(!word(id.manager,0x554,final_base) || !word(id.manager,0x558,final_source) ||
       !word(id.visual,0x160+selected*4,final_child) || final_base!=base || final_source!=source ||
       final_child!=child || !equal(id.ship+0x88,&linked_visual,4) || !equal(id.visual+0x158,&linked_source,4) ||
       !equal(0x00C69FF0,&h[24],4) || !equal(0x00C69FF4,&h[25],4) || !equal(0x00C74058,&h[26],4) ||
       !valid())return MeshStatus::Changed;
    h[MeshBytes]=out.byte_size();h[MeshHash]=out.checksum();out.complete=true;
    return MeshStatus::Complete;
}

struct MeshCaptureBudget {
    MeshIdentity target{};
    std::uint32_t attempts=0,last_frame=0;
    MeshStatus status=MeshStatus::Empty;
    bool retired=false;
    bool admit(const MeshIdentity& id) {
        if(retired || status==MeshStatus::Complete || attempts>=2 || id.elapsed>90000 ||
           !id.count || id.count>512 || (attempts && (!target.same_epoch(id) || id.frame==last_frame)))return false;
        if(!attempts)target=id;
        ++attempts;last_frame=id.frame;return true;
    }
};
} // namespace sfc_m1
