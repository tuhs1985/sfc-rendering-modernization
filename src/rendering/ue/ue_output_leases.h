#pragma once
#include "ue_output_contract.h"
// Resource owners retain GPU objects until their slot returns to Idle.
// A lost consumer acknowledgement retires the slot for this generation.
namespace sfc_ue_output {
enum class SlotState { Idle, Published, Acquired, Retiring };
class LeasePool {
    struct Slot { SlotState state=SlotState::Idle;Ticket ticket{};bool acquired=false; };
    std::array<Slot,Slots> slots{};
    bool stopped=false;
    Ticket context;
public:
    explicit LeasePool(const Ticket& expected):context(expected){}
    bool publish(const Ticket& ticket){
        if(stopped||ticket.slot>=Slots||slots[ticket.slot].state!=SlotState::Idle||
           !valid(ticket,ticket.identity,ticket.producer,ticket.consumer,ticket.adapter_luid))return false;
        if(ticket.identity.session!=context.identity.session||ticket.identity.activation!=context.identity.activation||
           ticket.identity.device!=context.identity.device||ticket.identity.target!=context.identity.target||
           ticket.producer!=context.producer||ticket.consumer!=context.consumer||
           ticket.adapter_luid!=context.adapter_luid||ticket.resource_epoch!=context.resource_epoch||
           ticket.width!=context.width||ticket.height!=context.height||
           ticket.target_width!=context.target_width||ticket.target_height!=context.target_height||
           ticket.viewport_x!=context.viewport_x||ticket.viewport_y!=context.viewport_y)return false;
        for(const auto& previous:slots){
            if(!previous.ticket.slot_epoch)continue;
            if((ticket.ready_fence==previous.ticket.ready_fence&&ticket.ready_value<=previous.ticket.ready_value)||
               (ticket.ack_fence==previous.ticket.ack_fence&&ticket.ack_value<=previous.ticket.ack_value))return false;
        }
        auto& slot=slots[ticket.slot];
        if(slot.ticket.slot_epoch&&ticket.slot_epoch<=slot.ticket.slot_epoch)return false;
        slot.ticket=ticket;slot.acquired=false;slot.state=SlotState::Published;return true;
    }
    bool acquire(const Ticket& expected,uint64_t completed_ready){
        if(stopped||expected.slot>=Slots)return false;
        auto& slot=slots[expected.slot];
        if(slot.state!=SlotState::Published||!matches_lease(slot.ticket,expected)||
           completed_ready==UINT64_MAX||completed_ready<expected.ready_value)return false;
        slot.state=SlotState::Acquired;slot.acquired=true;return true;
    }
    bool release(const Receipt& ack,uint64_t completed_ack){
        if(ack.slot>=Slots)return false;
        auto& slot=slots[ack.slot];
        if(!slot.acquired||(slot.state!=SlotState::Acquired&&slot.state!=SlotState::Retiring)||
           !acknowledges(ack,slot.ticket)||completed_ack==UINT64_MAX||completed_ack<slot.ticket.ack_value)return false;
        slot.state=SlotState::Idle;return true;
    }
    void stop(){
        stopped=true;
        for(auto& slot:slots)if(slot.state!=SlotState::Idle)slot.state=SlotState::Retiring;
    }
    // No consumer has acquired this slot, so producer completion suffices.
    bool cancel_unacquired(uint32_t index,const Ticket& expected,uint64_t completed_ready){
        if(index>=Slots)return false;
        auto& slot=slots[index];
        if((slot.state!=SlotState::Published&&slot.state!=SlotState::Retiring)||
           slot.acquired||!matches_lease(slot.ticket,expected)||
           completed_ready==UINT64_MAX||completed_ready<slot.ticket.ready_value)return false;
        slot.state=SlotState::Idle;return true;
    }
    SlotState state(uint32_t index)const{return slots.at(index).state;}
    bool drained()const{
        for(const auto& slot:slots)if(slot.state!=SlotState::Idle)return false;
        return true;
    }
};
}
