#pragma once
#include "m1_visual_tint.h"
#include <array>
#include <cstring>

namespace sfc_m1 {
struct PinnedPolygonCopy {
    static constexpr std::uint32_t kCanary=0x53464350;
    std::uint32_t canary_before=kCanary;
    std::array<std::uint32_t,1024> list{};
    std::array<std::array<unsigned char,28>,64> headers{};
    std::array<std::array<unsigned char,8*28>,64> corners{};
    std::uint32_t canary_after=kCanary;
    std::array<std::uint32_t,64> original_headers{};
    std::uint32_t count=0, copied=0, payload_bytes=0, before_hash=0, list_hash=0;
    bool attempted=false, built=false, published=false;
    static std::uint32_t hash_bytes(std::uint32_t hash,const void* data,std::size_t n) {
        const auto* bytes=static_cast<const unsigned char*>(data);
        for(std::size_t i=0;i<n;++i) {hash^=bytes[i];hash*=16777619u;}return hash;
    }
    static std::uint32_t word(const void* p) {std::uint32_t v;std::memcpy(&v,p,4);return v;}
    std::uint32_t payload_hash() const {
        if(copied>64)return 0;
        std::uint32_t hash=2166136261u;
        for(std::uint32_t i=0;i<copied;++i) {
            const auto n=word(headers[i].data());if(n<3 || n>8)return 0;
            hash=hash_bytes(hash,headers[i].data(),24); // relocated corner pointer excluded
            hash=hash_bytes(hash,corners[i].data(),n*28);
        }return hash;
    }
    bool intact() const {
        if(canary_before!=kCanary || canary_after!=kCanary || !built || !count || count>1024 ||
           copied!=(count<64?count:64) || payload_bytes>20224)return false;
        for(std::uint32_t i=0;i<copied;++i) {
            const auto n=word(headers[i].data());
            if(n<3 || n>8 || list[i]!=static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(headers[i].data())) ||
               word(headers[i].data()+24)!=static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(corners[i].data())))return false;
        }
        return hash_bytes(2166136261u,list.data(),count*4)==list_hash && payload_hash()==before_hash;
    }
    template<class Copy>
    bool build(std::uint32_t original_list,std::uint32_t n,std::uint32_t vertices,Copy read) {
        if(attempted || !n || n>1024 || !vertices || vertices>65536)return false;
        attempted=true;count=n;copied=n<64?n:64;
        std::uint32_t end=0;
        if(!tint_address(original_list,n*4-1,end) || !read(original_list,list.data(),n*4))return false;
        before_hash=2166136261u;payload_bytes=n*4;
        for(std::uint32_t i=0;i<copied;++i) {
            original_headers[i]=list[i];
            if(!list[i] || !tint_address(list[i],27,end) || !read(list[i],headers[i].data(),28))return false;
            const auto corner_count=word(headers[i].data());
            const auto pointer=word(headers[i].data()+24);
            if(corner_count<3 || corner_count>8 || word(headers[i].data()+4)>=256 || !pointer ||
               !tint_address(pointer,corner_count*28-1,end) || !read(pointer,corners[i].data(),corner_count*28))return false;
            for(std::uint32_t c=0;c<corner_count;++c) {
                std::uint16_t index;std::memcpy(&index,corners[i].data()+c*28,2);
                if(index>=vertices)return false;
            }
            before_hash=hash_bytes(before_hash,headers[i].data(),24);
            before_hash=hash_bytes(before_hash,corners[i].data(),corner_count*28);
            payload_bytes+=28+corner_count*28;
            const auto relocated=static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(corners[i].data()));
            std::memcpy(headers[i].data()+24,&relocated,4);
            list[i]=static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(headers[i].data()));
        }
        // Re-read originals before publishing: partial/changed inputs never handed off.
        std::array<unsigned char,28> header{};std::array<unsigned char,8*28> corner{};
        for(std::uint32_t i=0;i<n;++i) {
            std::uint32_t value=0;
            if(!read(original_list+i*4,&value,4) || value!=(i<copied?original_headers[i]:list[i]))return false;
            if(i>=copied)continue;
            if(!read(value,header.data(),28) || std::memcmp(header.data(),headers[i].data(),24)!=0)return false;
            const auto size=word(header.data())*28;
            if(size>corner.size() || !read(word(header.data()+24),corner.data(),size) ||
                std::memcmp(corner.data(),corners[i].data(),size)!=0)return false;
        }
        list_hash=hash_bytes(2166136261u,list.data(),count*4);built=true;return intact();
    }
};
} // namespace sfc_m1
