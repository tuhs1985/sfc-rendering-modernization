// Independent debris instances. Parent retirement is not child retirement.
#pragma once
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
#include "scene_capacity.h"
namespace sfc_break {
struct Instance {
    std::uint64_t epoch=0;
    std::uint32_t pointer=0,parent=0,visual=0,piece=0,revision=0,frame=0;
    bool live=false,posed=false;
    std::array<float,16> world{};
};
struct Registry {
    std::array<Instance,scene_capacity::Owners> entries{};
    std::uint64_t serial=0;
    Instance* find(std::uint32_t pointer,std::uint64_t epoch){
        for(auto& entry:entries)
            if(entry.live&&entry.pointer==pointer&&entry.epoch==epoch)return &entry;
        return nullptr;
    }
    std::uint64_t born(std::uint32_t pointer,std::uint32_t parent,
                       std::uint32_t visual,std::uint32_t piece){
        if(!pointer||!parent||!visual||serial==(std::numeric_limits<std::uint64_t>::max)())return 0;
        Instance* available=nullptr;
        for(auto& entry:entries){
            if(entry.live&&entry.pointer==pointer){available=&entry;break;}
            if(!entry.live&&!available)available=&entry;
        }
        if(!available)return 0;
        *available={};available->epoch=++serial;available->pointer=pointer;
        available->parent=parent;available->visual=visual;available->piece=piece;
        available->live=true;return available->epoch;
    }
    bool asset(std::uint32_t pointer,std::uint64_t epoch,std::uint32_t visual,
               std::uint32_t piece,std::uint32_t revision){
        auto* entry=find(pointer,epoch);
        if(!entry||entry->visual!=visual||entry->piece!=piece||!revision||
           (entry->revision&&entry->revision!=revision))return false;
        entry->revision=revision;return true;
    }
    bool pose(std::uint32_t pointer,std::uint64_t epoch,std::uint32_t frame,
              const std::array<float,16>& world){
        auto* entry=find(pointer,epoch);
        if(!entry||!frame||(entry->posed&&frame<=entry->frame))return false;
        for(float value:world)if(!std::isfinite(value))return false;
        if(std::fabs(world[12])+std::fabs(world[13])+std::fabs(world[14])+
           std::fabs(world[15]-1)>1e-5)return false;
        entry->world=world;entry->frame=frame;entry->posed=true;return true;
    }
    bool retire(std::uint32_t pointer,std::uint64_t epoch){
        auto* entry=find(pointer,epoch);if(!entry)return false;
        entry->live=false;entry->posed=false;return true;
    }
};
}
