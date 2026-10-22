// Avoid spending GPU work on an input already too old to meet its current frame.
#pragma once
#include "live_owner_wire.h"
namespace live_owner {
inline bool fresh_input(const Packet& p,Header& h,uint64_t now,uint64_t frequency){
 if(!frequency||now<p.offered||p.row[2]!=static_cast<DWORD>(frame_ingress::state(&h.frame))||
    p.row[2]==static_cast<DWORD>(frame_ingress::state(&h.bad_frame)))return false;
 return now-p.offered<=frequency/500; //2ms admission window,NOT a new display deadline
}
}
