#pragma once
#include <array>
#include <cstdint>
#include <ostream>

namespace sfc_m1 {
// Caller holds the existing recorder lock. Fixed storage;no IO/allocation/game
// reads. Retains first-seen/changed associations beyond the120-frame detail cap.
struct IdentityCensus {
    static constexpr std::uint32_t Capacity=256,TableSize=512,OutputCap=128*1024;
    enum Field:std::size_t {Kind,Caller,Ship,Visual,Model,Source,ChosenOwner,
        ContextShip,ContextVisual,ContextOwner,ShipOwner,ContextShipOwner,
        VisualFirstOwner,VisualOwnerCount,Reason,ShipVtable,VisualVtable,ModelVtable,Thread,Fields};
    using Key=std::array<std::uint32_t,Fields>;
    struct Entry {Key key{};std::uint32_t first_frame=0,last_frame=0,first_ms=0,last_ms=0;std::uint64_t observations=0;};
    std::array<Entry,Capacity> entries{};
    std::array<std::uint16_t,TableSize> table{};
    std::uint32_t count=0;
    std::uint64_t observations=0,omitted=0;
    bool enabled=false;
    void record(const Key& key,std::uint32_t frame,std::uint32_t elapsed){
        enabled=true;++observations;
        std::uint32_t hash=2166136261u;for(auto word:key)hash=(hash^word)*16777619u;
        for(std::uint32_t probe=0;probe<TableSize;++probe){auto& cell=table[(hash+probe)%TableSize];
            if(cell){auto& e=entries[cell-1];if(e.key!=key)continue;
                e.last_frame=frame;e.last_ms=elapsed;++e.observations;return;}
            if(count==Capacity){++omitted;return;}
            auto& e=entries[count];e.key=key;e.first_frame=e.last_frame=frame;
            e.first_ms=e.last_ms=elapsed;e.observations=1;cell=static_cast<std::uint16_t>(++count);return;
        }++omitted;
    }
    void write(std::ostream& out)const{
        out<<"{\"schema\":\"m1.identity-census.v1\",\"enabled\":"<<(enabled?"true":"false")
            <<",\"capacity\":"<<Capacity<<",\"storage_bytes\":"<<sizeof(*this)
            <<",\"observations\":"<<observations<<",\"omitted_observations\":"<<omitted
            <<",\"columns\":[\"kind\",\"caller\",\"ship\",\"visual\",\"model\",\"source\",\"chosen_owner\","
              "\"context_ship\",\"context_visual\",\"context_owner\",\"ship_owner\",\"context_ship_owner\","
              "\"visual_first_owner\",\"visual_owner_count\",\"reason\",\"ship_vtable\",\"visual_vtable\",\"model_vtable\",\"thread\"],\"entries\":[";
        for(std::uint32_t i=0;i<count;++i){const auto& e=entries[i];out<<(i?",{":"{")<<"\"key\":[";
            for(std::size_t k=0;k<Fields;++k)out<<(k?",":"")<<e.key[k];
            out<<"],\"first_frame\":"<<e.first_frame<<",\"last_frame\":"<<e.last_frame
                <<",\"first_ms\":"<<e.first_ms<<",\"last_ms\":"<<e.last_ms<<",\"observations\":"<<e.observations<<'}';}
        out<<"]}";
    }
};
static_assert(sizeof(IdentityCensus)<32*1024,"identity census must stay small/fixed");
}
