// Optional indexed-piece evidence carried beside the unchanged mesh packet.
#pragma once
#include <cstdint>
#include <ostream>
namespace sfc_break {
struct Metadata {
    std::uint32_t owner=0,parent=0,piece=0,pieces=0,first=0,count=0,total=0,list=0;
    bool valid() const {
        return (owner&0x80000000u)&&parent&&!(parent&0x80000000u)&&
            pieces&&pieces<=256&&piece<pieces&&count&&total<=8192&&
            first<total&&count<=total-first&&list&&list<=UINT32_MAX-first*4;
    }
    bool write(std::ostream& out) const {
        if(!valid())return false;
        out<<"{\"schema\":\"sfc.break.piece.v1\",\"owner_epoch\":"<<owner
           <<",\"parent_owner_epoch\":"<<parent<<",\"index\":"<<piece
           <<",\"piece_count\":"<<pieces<<",\"first\":"<<first
           <<",\"count\":"<<count<<",\"total\":"<<total<<",\"primary_base\":"<<list<<'}';
        return out.good();
    }
};
}
