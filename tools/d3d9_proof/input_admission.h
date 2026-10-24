// Avoid spending GPU work on an input already too old to meet its current frame.
#pragma once
#include "live_owner_wire.h"
namespace live_owner {
enum class Admission:unsigned {Accepted,Clock,Frame,BadFrame,Age,Closed,Count};
inline Admission admission(const Packet& p,Header& h,uint64_t now,uint64_t frequency,const volatile LONG* closed=nullptr){
 if(!frequency||now<p.offered)return Admission::Clock;
 const auto current=static_cast<DWORD>(frame_ingress::state(&h.frame));
 if(p.row[2]!=current&&(!closed||p.row[2]==UINT32_MAX||p.row[2]+1!=current))return Admission::Frame;
 if(p.row[2]==static_cast<DWORD>(frame_ingress::state(&h.bad_frame)))return Admission::BadFrame;
 // Buffered mode uses the ACTUAL compositor consumption watermark,not a guessed
 // fixed-Hz deadline.50ms is only the existing history's maximum wall-age guard.
 if(closed&&p.row[2]<=static_cast<DWORD>(frame_ingress::state(const_cast<volatile LONG*>(closed))))return Admission::Closed;
 if(now-p.offered>frequency/(closed?20:500))return Admission::Age;
 return Admission::Accepted;
}
inline bool fresh_input(const Packet& p,Header& h,uint64_t now,uint64_t frequency){
 return admission(p,h,now,frequency)==Admission::Accepted; // Legacy unbuffered policy unchanged.
}
}
