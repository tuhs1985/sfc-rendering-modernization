// Diagnostic placement only. World->camera is a qualified orthonormal rotation.
#pragma once
#include <cmath>
namespace diagnostic_offset {
inline bool camera_left(const float* view,float distance,float* out){
 if(!std::isfinite(distance)||distance<=0||distance>1e6f)return false;
 double norm=0;for(unsigned i=0;i<3;++i){if(!std::isfinite(view[i]))return false;norm+=double(view[i])*view[i];}
 if(std::abs(norm-1)>1e-3)return false;
 // Inverse rotation column0 == view row0. No forward/depth displacement.
 for(unsigned i=0;i<3;++i)out[i]=-distance*view[i];return true;
}
}
