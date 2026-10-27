// Remix-specific adapter. Packet is worker-written; never read inside SFC.
#pragma once
#include <array>
#include <cmath>
#include <fstream>
#include <cstring>
#include <string>
#include <charconv>
#include <limits>
struct RemixImageControls {
 uint32_t enabled=0,mode=1,automatic=1,brightness=50;
 std::array<float,4> values{0,1,1,1};uint64_t revision=0;
 bool nativeConfigured=false;uint32_t bloomEnable=1,bloomSteps=5;
 std::array<float,2> nativeValues{1,.25f}; // Exact native bloom intensity and threshold.
 static uint64_t hash(const void* bytes,size_t size){auto p=static_cast<const unsigned char*>(bytes);uint64_t h=14695981039346656037ull;for(size_t i=0;i<size;++i)h=(h^p[i])*1099511628211ull;return h;}
 bool decode(const unsigned char* raw,size_t size){
  if(size!=48&&size!=64)return false;uint32_t h[6]{};std::array<float,4> v{};uint64_t sum=0;
  memcpy(h,raw,24);memcpy(v.data(),raw+24,16);memcpy(&sum,raw+size-8,8);
  if(h[0]!=0x31474d49||h[1]!=(size==64?2u:1u)||h[2]>1||h[3]>1||h[4]>1||h[5]>100||hash(raw,size-8)!=sum)return false;
  const float low[4]{-4,0,.25f,0},high[4]{4,2,4,2};
  for(unsigned i=0;i<4;++i)if(!std::isfinite(v[i])||v[i]<low[i]||v[i]>high[i])return false;
  uint32_t bloom[2]{1,5};std::array<float,2> nv{1,.25f};
  if(size==64){memcpy(bloom,raw+40,8);memcpy(nv.data(),raw+48,8);
   if(bloom[0]>1||bloom[1]<1||bloom[1]>8)return false;
   for(float x:nv)if(!std::isfinite(x)||x<0)return false;
  }
  if(sum==revision)return false;enabled=h[2];mode=h[3];automatic=h[4];brightness=h[5];values=v;revision=sum;
  nativeConfigured=nativeConfigured||size==64;bloomEnable=bloom[0];bloomSteps=bloom[1];nativeValues=nv;return true;
 }
 bool read(){std::ifstream f("image-controls.bin",std::ios::binary);std::array<unsigned char,65> raw{};if(!f)return false;f.read(reinterpret_cast<char*>(raw.data()),raw.size());const auto size=static_cast<size_t>(f.gcount());return f.eof()&&decode(raw.data(),size);}
 template<class Set> bool applyNative(Set set)const{
  if(!nativeConfigured)return true;
  const auto value=[&](const char* key,float x){char text[64]{};auto result=std::to_chars(text,text+63,x,std::chars_format::general,std::numeric_limits<float>::max_digits10);return result.ec==std::errc{}&&set(key,text);};
  return set("rtx.bloom.enable",bloomEnable?"True":"False")&&
   set("rtx.bloom.steps",std::to_string(bloomSteps).c_str())&&
   value("rtx.bloom.burnIntensity",nativeValues[0])&&
   value("rtx.bloom.luminanceThreshold",nativeValues[1]);
 }
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
   value("rtx.tonemap.saturation",on&&!m?v[3]:1.f)&&applyNative(set);
 }
 std::array<float,4> post()const{return enabled?std::array<float,4>{mode?values[1]:1.f,values[2],mode?values[3]:1.f,0}:std::array<float,4>{1,1,1,0};}
};
