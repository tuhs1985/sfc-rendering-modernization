#pragma once
#include <array>
#include <cstdint>
namespace effect_probe {
constexpr unsigned Owners=4096,Nesting=8;
enum Kind:uint32_t {Born=64,Retired,Enter,Leave,Selected,Finalized,Polygon,Resource,Name,Fault,Overflow,Stopped,Statistics};
struct Identity {uint32_t pointer=0,epoch=0;bool alive=false,late=false;};
struct Registry {
 std::array<Identity,Owners> slots{};uint32_t serial=0;
 Identity* find(uint32_t p){if(!p)return nullptr;for(auto& s:slots)if(s.alive&&s.pointer==p)return &s;return nullptr;}
 Identity birth(uint32_t p,bool late=false){
  if(!p||serial==UINT32_MAX)return {};Identity* slot=find(p);
  if(!slot)for(auto& s:slots)if(!s.alive){slot=&s;break;}
  if(!slot)return {};*slot={p,++serial,true,late};return *slot;
 }
 Identity retire(uint32_t p){auto* s=find(p);if(!s)return {};auto result=*s;s->alive=false;return result;}
};
struct Scope {uint32_t owner=0,epoch=0,manager=0;uint64_t token=0;};
struct Scopes {
 std::array<Scope,Nesting> values{};unsigned depth=0,excess=0;
 bool push(Scope s){if(excess||depth==Nesting){++excess;return false;}values[depth++]=s;return true;}
 void pop(){if(excess)--excess;else if(depth)--depth;}
 Scope current()const{return excess||!depth?Scope{}:values[depth-1];}
};
inline bool association(Scope s,uint32_t manager,uint32_t id){return s.epoch&&s.manager==manager&&id&&id<=4096;}
}
