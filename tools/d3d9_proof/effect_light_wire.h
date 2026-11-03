// Remix-only conversion policy;native range is not an intensity multiplier.
#pragma once
#include "../scene_bridge/effect_lights.h"
#include <cmath>
namespace remix_effect_lights {
constexpr DWORD Offset=sfc_effect_lights::Offset+32*1024,Magic=0x31434c45,Count=62;
struct Row {DWORD enabled=0;float gain[3]{},radius=1;DWORD reserved=0;};
struct Config {DWORD magic=Magic,version=1,bytes=sizeof(Config),generation=1;Row rows[Count]{};uint64_t checksum=0;};
struct alignas(64) ConfigCell {volatile LONG guard=0;DWORD reserved=0;ULONGLONG captured=0;Config value{};BYTE padding[8]{};};
struct Store {sfc_light_transport::Header header;ConfigCell cell;};
static_assert(sizeof(Row)==24&&sizeof(Config)==1512&&sizeof(Store)==1600);
static_assert(Offset+sizeof(Store)<16*1024*1024);
inline uint64_t checksum(const Config& c){uint64_t h=14695981039346656037ull;auto* p=reinterpret_cast<const BYTE*>(&c);
 for(unsigned i=0;i<sizeof(c)-8;++i)h=(h^p[i])*1099511628211ull;return h;}
inline bool valid(const Config& c){if(c.magic!=Magic||c.version!=1||c.bytes!=sizeof(c)||!c.generation||c.checksum!=checksum(c))return false;
 for(const auto& r:c.rows){if(r.enabled>1||r.reserved||!std::isfinite(r.radius)||r.radius<1e-5f||r.radius>1e5f)return false;
  for(float f:r.gain)if(!std::isfinite(f)||f<0||f>1e6f)return false;}return true;}
struct Light {DWORD slot=0,type=0;float position[3]{},radiance[3]{},range=0,radius=1;};
// Status1=active,0=disabled/unsupported,-1=invalid used data. Ignore unused
// type5 direction/tail fields,which can contain uninitialized bit patterns.
inline int convert(const sfc_effect_lights::Frame& f,const Config& c,unsigned slot,Light& out){
 if(slot<2||slot>=64||!f.gate||!c.rows[slot-2].enabled)return 0;
 for(unsigned i=0;i<=slot;++i)if(!f.enables[i])return 0;
 const auto& v=f.records[slot];if(v[0]!=1&&v[0]!=5)return 0;
 float p[3]{},rgb[3]{},range=0;memcpy(p,v+4,12);memcpy(rgb,v+7,12);memcpy(&range,v+10,4);
 if(!std::isfinite(range)||range<=0||range>1e9f)return -1;
 out={};out.slot=slot;out.type=v[0];out.radius=c.rows[slot-2].radius;out.range=range;
 for(unsigned i=0;i<3;++i){if(!std::isfinite(p[i])||std::abs(p[i])>1e9f||!std::isfinite(rgb[i])||rgb[i]<0)return -1;
  out.position[i]=p[i];out.radiance[i]=rgb[i]*c.rows[slot-2].gain[i];
  if(!std::isfinite(out.radiance[i])||out.radiance[i]>1e6f)return -1;}return 1;
}
}
