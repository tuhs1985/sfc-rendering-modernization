// Replacement admission is deliberately separate from delayed additive display.
// No hook consumes this contract yet. All runtime qualifications default FALSE.
#pragma once
#include "ship_triplet_wire.h"
namespace ship_replacement {
using ship_triplet::Key;
enum class Refusal {None,Invalid,Diagnostic,Identity,State,Frame,Stale,NotReady,
 Coverage,Visibility,Ordering,Target,AlreadyConsumed};
struct Evidence {
 bool gpuReady=false,coverage=false,visibility=false,preUi=false,target=false;
 uint64_t completedAt=0,frequency=0;
 uint32_t sequence=0;
};
// These raw words supplement (not replace) existing identity/hash validation.
// supplied[17],composed[17],view/projection/viewport[40] from the qualified row.
struct Observation {Key key{};uint32_t state[74]{};};
inline Observation observe(const Key& key,const std::array<uint32_t,96>& row){
 Observation o{};o.key=key;std::memcpy(o.state,row.data()+8,34*4);
 std::memcpy(o.state+34,row.data()+49,40*4);return o;
}
inline bool validObservation(const Observation& o){
 if(!ship_triplet::validKey(o.key)||o.key.pose!=ship_triplet::hash(o.state,17*4)||
    o.key.camera!=ship_triplet::hash(o.state+34,40*4))return false;
 for(unsigned i=0;i<74;++i){
  // Native word17 is flags,not a floating-point matrix element.
  if(i==16||i==33||i==50||i==67)continue;
  float value=0;std::memcpy(&value,o.state+i,4);if(!std::isfinite(value))return false;
 }
 return true;
}
inline Refusal adjudicate(const Observation& current,const Observation& returned,
                          const Evidence& e,uint64_t now){
 if(!validObservation(current)||!validObservation(returned)||!e.sequence)return Refusal::Invalid;
 if(current.key.diagnosticMode||returned.key.diagnosticMode)return Refusal::Diagnostic;
 if(!ship_triplet::sameIdentity(current.key,returned.key))return Refusal::Identity;
 if(current.key.pose!=returned.key.pose||current.key.camera!=returned.key.camera||
    std::memcmp(current.state,returned.state,sizeof(current.state)))return Refusal::State;
 // No stationary/frame-age waiver. If necessary,qualify that separately first.
 if(current.key.frame!=returned.key.frame)return Refusal::Frame;
 if(!ship_triplet::sourceRecent(e.completedAt,now,e.frequency))return Refusal::Stale;
 if(!e.gpuReady)return Refusal::NotReady;
 if(!e.coverage)return Refusal::Coverage;
 if(!e.visibility)return Refusal::Visibility;
 if(!e.preUi)return Refusal::Ordering;
 if(!e.target)return Refusal::Target;
 return Refusal::None;
}
class Admission {
 uint32_t consumed=0;
public:
 // Call once at the actual original-draw decision,not at Present. A refusal
 // never authorizes suppression. This alone does NOT prove any Evidence flag.
 Refusal inspect(const Observation& current,const Observation& returned,
                 const Evidence& e,uint64_t now)const{
  if(e.sequence&&e.sequence<=consumed)return Refusal::AlreadyConsumed;
  return adjudicate(current,returned,e,now);
 }
 bool commit(const Observation& current,const Observation& returned,
             const Evidence& e,uint64_t now,bool compositionSubmitted){
  if(!compositionSubmitted||inspect(current,returned,e,now)!=Refusal::None)return false;
  consumed=e.sequence;return true;
 }
};
}
