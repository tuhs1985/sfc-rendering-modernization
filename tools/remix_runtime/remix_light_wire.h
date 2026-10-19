// Backend-specific fixed200B relay contract;not shared SFC light semantics.
#pragma once
#include <cstdint>
#include <cmath>
#include <cstring>
struct LiveLightRow {uint32_t slot,enabled,reserved[2];float values[12];};
struct LiveLightPacket {uint32_t h[12];uint64_t observed,revision;LiveLightRow rows[2];uint64_t checksum;};
static_assert(sizeof(LiveLightRow)==64&&sizeof(LiveLightPacket)==200);
inline uint64_t lightChecksum(const LiveLightPacket& packet){
 const auto* bytes=reinterpret_cast<const unsigned char*>(&packet);uint64_t value=14695981039346656037ull;
 for(unsigned i=0;i<sizeof(packet)-8;++i)value=(value^bytes[i])*1099511628211ull;
 return value;
}
inline bool validLightPacket(const LiveLightPacket& p,const uint32_t* session,uint32_t owner,uint32_t model,uint32_t source,uint32_t frame,uint64_t frequency,uint64_t now){
 if(!frequency||!owner||!model||!source||p.h[0]!=0x3154474c||p.h[1]!=1||p.h[2]!=sizeof(p)||!p.h[3]||
    memcmp(p.h+4,session,16)||p.h[8]!=owner||p.h[9]!=model||p.h[10]!=source||
    p.h[11]>frame||frame-p.h[11]>30||!p.observed||p.observed>now||now-p.observed>frequency/2||
    p.checksum!=lightChecksum(p))return false;
 for(unsigned i=0;i<2;++i){const auto& r=p.rows[i];
  if(r.slot!=i||r.enabled>1||r.reserved[0]||r.reserved[1])return false;
  for(float f:r.values)if(!std::isfinite(f))return false;
  const float length=r.values[0]*r.values[0]+r.values[1]*r.values[1]+r.values[2]*r.values[2];
  if(std::abs(length-1)>.001f)return false;
  for(unsigned j=3;j<6;++j)if(r.values[j]<0||r.values[j]>1e6f)return false;
  if(r.values[6]<0||r.values[6]>180||r.values[7]<0||r.values[7]>16||(r.values[10]!=0&&r.values[10]!=1)||r.values[11])return false;
 }
 return true;
}
