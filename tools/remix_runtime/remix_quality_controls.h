// Native Remix-only quality adapter;not an SFC sampler or requirements change.
#pragma once
#include <cstdint>
#include "remix_image_controls.h"
struct RemixQualityControls {
 uint32_t enabled=0,anisotropic=1,samples=8,aa=0,denoising=1;float bias=0;uint64_t revision=0;
 bool decode(const unsigned char* raw,size_t size){
  if(size!=48)return false;uint32_t h[8]{};float v[2]{};uint64_t sum=0;memcpy(h,raw,32);memcpy(v,raw+32,8);memcpy(&sum,raw+40,8);
  if(h[0]!=0x31544c51||h[1]!=1||h[2]>1||h[3]>1||!(h[4]==1||h[4]==2||h[4]==4||h[4]==8||h[4]==16)||(h[5]!=0&&h[5]!=3)||h[6]>1||h[7]||!std::isfinite(v[0])||v[0]<-1||v[0]>1||v[1]!=1||RemixImageControls::hash(raw,40)!=sum||revision==sum)return false;
  enabled=h[2];anisotropic=h[3];samples=h[4];aa=h[5];denoising=h[6];bias=v[0];revision=sum;return true;
 }
 bool read(){std::ifstream f("quality-controls.bin",std::ios::binary);unsigned char raw[48]{};if(!f)return false;f.read(reinterpret_cast<char*>(raw),48);return f&&f.peek()==EOF&&decode(raw,48);}
 template<class Set>bool apply(Set set)const{
  return set("rtx.useAnisotropicFiltering",!enabled||anisotropic?"True":"False")&&
   set("rtx.maxAnisotropySamples",std::to_string(enabled?samples:8).c_str())&&
   set("rtx.nativeMipBias",std::to_string(enabled?bias:0.f).c_str())&&
   set("rtx.upscalerType",enabled&&aa==3?"3":"0")&&
   set("rtx.resolutionScale","1.0")&&set("rtx.enableRayReconstruction","False")&&
   set("rtx.useDenoiser",!enabled||denoising?"True":"False")&&
   set("rtx.useDenoiserReferenceMode","False");
 }
};
