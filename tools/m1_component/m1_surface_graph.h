#pragma once
#include "m1_private_copy.h"

namespace sfc_m1 {

// Timing begins at actual marker activation, not at launch/menu entry.
inline unsigned surface_test_phase(std::uint64_t elapsed_ms) {
    return elapsed_ms<20000?0:elapsed_ms<25000?1:elapsed_ms<40000?2:3;
}

// Complete small primary mesh, unlike the historical 64-polygon prefix.
// Never move/copy this object after build: its internal pointers refer to itself.
struct SurfaceGraph {
    static constexpr std::uint32_t kCapacity=512;
    std::array<PinnedPolygonCopy,8> chunks{};
    std::array<std::uint32_t,kCapacity> list{};
    std::uint32_t original_list=0,count=0,vertices=0,list_hash=0;
    bool built=false;

    template<class Read>
    bool build(std::uint32_t input,std::uint32_t n,std::uint32_t vertex_count,Read read) {
        if(built || !n || n>kCapacity)return false;
        original_list=input;count=n;vertices=vertex_count;
        for(std::uint32_t offset=0;offset<n;offset+=64) {
            std::uint32_t address=0;const auto remaining=n-offset;
            const auto size=remaining<64?remaining:64;
            if(!tint_address(input,offset*4,address) ||
               !chunks[offset/64].build(address,size,vertex_count,read))return false;
            for(std::uint32_t j=0;j<size;++j)list[offset+j]=chunks[offset/64].list[j];
        }
        list_hash=PinnedPolygonCopy::hash_bytes(2166136261u,list.data(),count*4);
        built=true;return intact();
    }
    bool intact() const {
        if(!built || !count || count>kCapacity ||
           PinnedPolygonCopy::hash_bytes(2166136261u,list.data(),count*4)!=list_hash)return false;
        for(std::uint32_t i=0;i<count;++i) {
            if(i%64==0 && !chunks[i/64].intact())return false;
            if(list[i]!=chunks[i/64].list[i%64])return false;
        }
        return true;
    }
    template<class Read>
    bool matches_original(std::uint32_t input,std::uint32_t n,std::uint32_t vertex_count,Read read) const {
        if(!intact() || input!=original_list || n!=count || vertex_count!=vertices)return false;
        std::array<unsigned char,28> header{};
        std::array<unsigned char,8*28> corner{};
        for(std::uint32_t i=0;i<count;++i) {
            const auto& chunk=chunks[i/64];const auto index=i%64;
            std::uint32_t pointer=0,address=0,end=0;
            if(!tint_address(input,i*4,address) || !read(address,&pointer,4) ||
               pointer!=chunk.original_headers[index] || !tint_address(pointer,27,end) ||
               !read(pointer,header.data(),28) ||
               std::memcmp(header.data(),chunk.headers[index].data(),24)!=0)return false;
            const auto size=PinnedPolygonCopy::word(header.data())*28;
            const auto source=PinnedPolygonCopy::word(header.data()+24);
            if(size>corner.size() || !size || !tint_address(source,size-1,end) ||
               !read(source,corner.data(),size) ||
               std::memcmp(corner.data(),chunk.corners[index].data(),size)!=0)return false;
        }
        return true;
    }
};

struct SurfaceGraphPair {
    SurfaceGraph neutral,altered;
    bool attempted=false,built=false;
    std::uint32_t changed_vectors=0;
    SurfaceGraphPair()=default;
    SurfaceGraphPair(const SurfaceGraphPair&)=delete;
    SurfaceGraphPair& operator=(const SurfaceGraphPair&)=delete;

    template<class Read>
    bool build(std::uint32_t input,std::uint32_t n,std::uint32_t vertices,Read read) {
        if(attempted)return false;
        attempted=true;
        if(!neutral.build(input,n,vertices,read) || !altered.build(input,n,vertices,read))return false;
        for(std::uint32_t i=0;i<n;++i) {
            const auto& original=neutral.chunks[i/64];auto& copy=altered.chunks[i/64];
            const auto index=i%64;
            if(std::memcmp(original.headers[index].data(),copy.headers[index].data(),24)!=0 ||
               original.before_hash!=copy.before_hash)return false;
            const auto corner_count=PinnedPolygonCopy::word(copy.headers[index].data());
            for(std::uint32_t c=0;c<corner_count;++c) {
                bool nonzero=false;
                for(std::uint32_t axis=0;axis<3;++axis) {
                    auto* field=copy.corners[index].data()+c*28+4+axis*4;
                    auto bits=PinnedPolygonCopy::word(field);
                    if((bits&0x7f800000u)==0x7f800000u)return false; // no NaN/Inf
                    nonzero|=(bits&0x7fffffffu)!=0;
                    bits^=0x80000000u;std::memcpy(field,&bits,4);
                }
                if(nonzero)++changed_vectors;
            }
            // Finalize fingerprints only after the whole chunk has been altered.
            if(index==63 || i+1==n)copy.before_hash=copy.payload_hash();
        }
        built=changed_vectors && neutral.matches_original(input,n,vertices,read) && intact();
        return built;
    }
    bool intact() const {
        if(!neutral.intact() || !altered.intact() || neutral.count!=altered.count)return false;
        for(std::uint32_t i=0;i<neutral.count;++i) {
            const auto& before=neutral.chunks[i/64];const auto& after=altered.chunks[i/64];
            const auto index=i%64;
            if(std::memcmp(before.headers[index].data(),after.headers[index].data(),24)!=0)return false;
            const auto count=PinnedPolygonCopy::word(before.headers[index].data());
            for(std::uint32_t c=0;c<count;++c)for(std::uint32_t byte=0;byte<28;++byte) {
                // Little-endian float sign bit: byte7/11/15 only.
                const unsigned char mask=(byte==7 || byte==11 || byte==15)?0x80:0;
                if((before.corners[index][c*28+byte]^after.corners[index][c*28+byte])!=mask)return false;
            }
        }
        return true;
    }
};
static_assert(sizeof(SurfaceGraphPair)<1024u*1024u,"Surface graph pair exceeds1MiB");
} // namespace sfc_m1
