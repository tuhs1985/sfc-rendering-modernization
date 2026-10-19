// Remix-specific adapter. Packet is worker-written; never read inside SFC.
#pragma once
#include <array>
#include <cmath>
#include <fstream>
#include <cstring>
#include <string>
struct RemixImageControls {
 uint32_t enabled=0,mode=1,automatic=1,brightness=50;
 std::array<float,4> values{0,1,1,1};uint64_t revision=0;
 static uint64_t hash(const void* bytes,size_t size){auto p=static_cast<const unsigned char*>(bytes);uint64_t h=14695981039346656037ull;for(size_t i=0;i<size;++i)h=(h^p[i])*1099511628211ull;return h;}
 bool decode(const unsigned char* raw,size_t size){
  if(size!=48)return false;uint32_t h[6]{};std::array<float,4> v{};uint64_t sum=0;
  memcpy(h,raw,24);memcpy(v.data(),raw+24,16);memcpy(&sum,raw+40,8);
  if(h[0]!=0x31474d49||h[1]!=1||h[2]>1||h[3]>1||h[4]>1||h[5]>100||hash(raw,40)!=sum)return false;
  const float low[4]{-4,0,.25f,0},high[4]{4,2,4,2};
  for(unsigned i=0;i<4;++i)if(!std::isfinite(v[i])||v[i]<low[i]||v[i]>high[i])return false;
  if(sum==revision)return false;enabled=h[2];mode=h[3];automatic=h[4];brightness=h[5];values=v;revision=sum;return true;
 }
 bool read(){std::ifstream f("image-controls.bin",std::ios::binary);std::array<unsigned char,48> raw{};if(!f)return false;f.read(reinterpret_cast<char*>(raw.data()),raw.size());return f&&f.peek()==EOF&&decode(raw.data(),raw.size());}
 // Native controls are applied as a complete set, including restoration of the
 // inactive mapper. Global grade has no local-path effect: local fallback below.
 template<class Set> bool apply(Set set)const{
  const bool on=enabled!=0;const auto m=on?mode:1u;const auto& v=values;
  // This pinned DLL rejects rtx.userBrightness (API error1). Reuse its public
  // source slider's EV formula through the working per-mapper exposure options.
  const float ev=on?v[0]+(static_cast<float>(brightness)-50.f)*.03f:0.f;
  const auto value=[&](const char* key,float x){return set(key,std::to_string(x).c_str());};
  return set("rtx.tonemappingMode",m?"1":"0")&&
   set("rtx.autoExposure.enabled",(!on||automatic)?"True":"False")&&
   value("rtx.tonemap.exposureBias",ev)&&
   value("rtx.localtonemap.exposure",.75f*std::exp2(ev))&&
   set("rtx.tonemap.colorGradingEnabled",on&&!m&&(v[1]!=1||v[3]!=1)?"True":"False")&&
   value("rtx.tonemap.contrast",on&&!m?v[1]:1.f)&&
   value("rtx.tonemap.saturation",on&&!m?v[3]:1.f);
 }
 std::array<float,4> post()const{return enabled?std::array<float,4>{mode?values[1]:1.f,values[2],mode?values[3]:1.f,0}:std::array<float,4>{1,1,1,0};}
};
