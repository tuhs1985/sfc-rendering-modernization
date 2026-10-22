// Remix returns full-frustum pixels;restore the actual SFC tactical viewport.
// This is output composition,not model scale,world position or camera repair.
#pragma once
#include <cstdint>
namespace native_viewport {
struct Mapping {float origin[2],scale[2];};
inline bool mapping(uint32_t width,uint32_t height,const uint32_t* viewport,Mapping& out){
 if(!width||!height||!viewport||!viewport[2]||!viewport[3]||
    uint64_t(viewport[0])+viewport[2]>width||uint64_t(viewport[1])+viewport[3]>height)return false;
 out.origin[0]=static_cast<float>(viewport[0]);out.origin[1]=static_cast<float>(viewport[1]);
 out.scale[0]=static_cast<float>(width)/viewport[2];out.scale[1]=static_cast<float>(height)/viewport[3];return true;
}
}
