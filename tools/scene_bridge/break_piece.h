// Native indexed break-mesh layout for the pinned SFC 2.5.6.4 client.
#pragma once
#include <array>
#include <cstdint>
#include "../m1_component/m1_mesh_export.h"
namespace sfc_break {
using Word=std::uint32_t;
struct Layout {
    Word visual=0,model=0,source=0,positions=0,positionCount=0;
    Word polygons=0,polygonCount=0,boundaries=0,pieceCount=0;
    std::array<Word,256> ends{};
    bool operator==(const Layout& b) const {
        return visual==b.visual&&model==b.model&&source==b.source&&positions==b.positions&&
            positionCount==b.positionCount&&polygons==b.polygons&&polygonCount==b.polygonCount&&
            boundaries==b.boundaries&&pieceCount==b.pieceCount&&ends==b.ends;
    }
    bool operator!=(const Layout& b) const {return !(*this==b);}
};
struct Range {Word first=0,count=0,list=0;};
template<class Read>bool layout(Word visual,Layout& out,Read read){
    Layout next{};next.visual=visual;Word vt=0,ready=0;
    const auto word=[&](Word base,Word offset,Word& value){
        return base&&base<=UINT32_MAX-offset-3&&read(base+offset,&value,4);
    };
    if(!word(visual,0,vt)||vt!=0x007985A4||
       !word(visual,0x160,next.model)||!word(visual,0x158,next.source)||!next.source||
       !word(next.model,0,vt)||vt!=0x007983E8||
       !word(next.model,8,next.positionCount)||!word(next.model,12,next.positions)||
       !word(next.model,16,next.polygonCount)||!word(next.model,20,next.polygons)||
       !word(next.model,0x2c,ready)||!(ready&255)||
       !word(next.model,0x30,next.boundaries)||!word(next.model,0x34,next.pieceCount))return false;
    if(!next.positionCount||next.positionCount>65536||!next.polygonCount||
       next.polygonCount>8192||!next.positions||!next.polygons||
       !next.pieceCount||next.pieceCount>next.ends.size()||!next.boundaries||
       next.boundaries>UINT32_MAX-next.pieceCount*4||
       next.positions>UINT32_MAX-next.positionCount*12||
       next.polygons>UINT32_MAX-next.polygonCount*4||
       !read(next.boundaries,next.ends.data(),next.pieceCount*4))return false;
    Word previous=0;
    for(Word i=0;i<next.pieceCount;++i){
        if(next.ends[i]<=previous||next.ends[i]>next.polygonCount)return false;
        previous=next.ends[i];
    }
    if(previous!=next.polygonCount)return false;
    out=next;return true;
}
inline bool range(const Layout& l,Word index,Range& out){
    if(!l.pieceCount||l.pieceCount>l.ends.size()||index>=l.pieceCount)return false;
    const Word first=index?l.ends[index-1]:0,end=l.ends[index];
    if(end<=first||end>l.polygonCount||l.polygons>UINT32_MAX-first*4)return false;
    out={first,end-first,l.polygons+first*4};return true;
}
// Reuses the portable mesh packet; native addresses are provenance only.
// Caller owns preallocated packet storage and supplies a live child check.
template<class Packet,class Read,class Validate>
sfc_m1::MeshStatus capture(Packet& out,const Layout& l,Word piece,
                         Word owner,Word child,Word manager,Read read,Validate valid){
    using namespace sfc_m1;
    out.complete=false;out.header={};Range part{};Layout after{};
    if(!owner||!child||!manager||!valid()||!range(l,piece,part))return MeshStatus::Identity;
    auto& h=out.header;
    h[MeshMagic]=0x314d4653;h[MeshVersion]=1;h[MeshOwner]=owner;
    h[MeshShip]=child;h[MeshVisual]=l.visual;h[MeshModel]=l.model;h[MeshManager]=manager;
    h[MeshSource]=l.source;h[MeshCaller]=0x0042EA92;h[MeshList]=part.list;
    h[MeshVertexBase]=l.positions;h[MeshVertices]=l.positionCount;
    h[MeshPolygons]=part.count;h[MeshLodCount]=1;
    // ActualChild denotes LOD0. Piece membership lives in the separate range.
    if(part.count>Packet::kPolygons||l.positionCount>Packet::kPositions||
       manager>UINT32_MAX-0x738)return MeshStatus::Count;
    if(!read(l.positions,out.positions.data(),l.positionCount*12)||
       !read(manager+0x6f4,h.data()+MeshSupplied,68)||
       !read(manager+0x6b0,h.data()+MeshComposed,68))return MeshStatus::Read;
    for(Word i=0;i<l.positionCount;++i)
        for(Word v:out.positions[i])if(!Packet::finite(v))return MeshStatus::Nonfinite;
    std::array<bool,256> seen{};
    for(Word p=0;p<part.count;++p){
        auto& poly=out.polygons[p];
        if(!read(part.list+p*4,&poly.native_header,4)||!poly.native_header||
           poly.native_header>UINT32_MAX-28||
           !read(poly.native_header,poly.header.data(),28))return MeshStatus::Read;
        const Word count=poly.header[0],group=poly.header[1];
        if(count!=3||group>=256||h[MeshCorners]>Packet::kCorners||
           count>Packet::kCorners-h[MeshCorners])return MeshStatus::Count;
        poly.native_corners=poly.header[6];poly.header[6]=h[MeshCorners];
        if(!poly.native_corners||poly.native_corners>UINT32_MAX-count*28||
           !read(poly.native_corners,out.corners.data()+h[MeshCorners],count*28))return MeshStatus::Read;
        for(Word c=0;c<count;++c){
            const auto& corner=out.corners[h[MeshCorners]+c];
            if((corner[0]&65535)>=l.positionCount)return MeshStatus::Index;
            for(Word f=1;f<=5;++f)if(!Packet::finite(corner[f]))return MeshStatus::Nonfinite;
        }
        h[MeshCorners]+=count;
        if(!seen[group]){
            auto& source=out.sources[h[MeshSources]++];source.index=group;
            if(l.source>UINT32_MAX-group*36-36||
               !read(l.source+group*36,source.words.data(),36))return MeshStatus::Read;
            seen[group]=true;
        }
    }
    if(!layout(l.visual,after,read)||after!=l||!valid())return MeshStatus::Changed;
    h[MeshBytes]=out.byte_size();
    if(h[MeshBytes]>Packet::kFileLimit)return MeshStatus::Count;
    h[MeshHash]=out.checksum();out.complete=true;return MeshStatus::Complete;
}
}
