// Reproduces the pinned child draw's pose from simulation fields.
// Must be qualified against paired native setter observations before live use.
#pragma once
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
namespace sfc_break {
using Pose=std::array<float,16>;
struct PoseInputs {
    std::array<std::uint32_t,17> initial{};
    std::array<float,3> position{},pivot{};
    std::array<float,2> angles{};
};
template<class Read>bool pose_inputs(std::uint32_t child,PoseInputs& out,Read read){
    return child&&child<=UINT32_MAX-0x158&&
        read(child+0xa4,out.initial.data(),68)&&read(child+0x34,out.position.data(),12)&&
        read(child+0x144,out.pivot.data(),12)&&read(child+0x150,out.angles.data(),8);
}
inline void translate(Pose& m,const std::array<float,3>& t){
    for(unsigned i=0;i<4;++i){
        double value=m[i*4+3];
        for(unsigned j=0;j<3;++j)value+=double(m[i*4+j])*t[j];
        m[i*4+3]=static_cast<float>(value);
    }
}
template<class Read>bool simulation_pose(std::uint32_t child,Pose& out,Read read){
    PoseInputs a{},b{};
    if(!pose_inputs(child,a,read)||!pose_inputs(child,b,read)||
       a.initial!=b.initial||a.position!=b.position||a.pivot!=b.pivot||a.angles!=b.angles)return false;
    Pose next{};std::memcpy(next.data(),a.initial.data(),64);
    const auto flag=(a.initial[16]>>8)&255;
    if(flag>1)return false;
    if(flag){next[12]=next[13]=next[14]=0;next[15]=1;}
    for(unsigned i=0;i<3;++i)next[i*4+3]=a.position[i];
    for(float x:next)if(!std::isfinite(x))return false;
    for(float x:a.position)if(!std::isfinite(x))return false;
    for(float x:a.pivot)if(!std::isfinite(x))return false;
    translate(next,a.pivot);
    float bias=0;
    if(!read(0x00797278,&bias,4)||!std::isfinite(bias))return false;
    for(unsigned axis=0;axis<2;++axis){
        if(!std::isfinite(a.angles[axis]))return false;
        // Native code adds the bias as float, then masks the resulting word.
        const float biased=bias+a.angles[axis];
        if(!std::isfinite(biased))return false;
        std::uint32_t bits=0;std::memcpy(&bits,&biased,4);
        const auto angle=bits&8191;
        float c=0,s=0;
        if(!read(0x00c6c004+angle*4,&c,4)||!read(0x00c6a004+angle*4,&s,4)||
           !std::isfinite(c)||!std::isfinite(s)||std::fabs(double(c)*c+double(s)*s-1)>1e-4)return false;
        // Postmultiply Rx then Ry, matching 0069C290 and 0069C450.
        for(unsigned row=0;row<4;++row){
            const auto i=row*4+(axis?0:1),j=row*4+2;
            const double u=next[i],v=next[j];
            next[i]=static_cast<float>(axis?u*c-v*s:u*c+v*s);
            next[j]=static_cast<float>(axis?u*s+v*c:-u*s+v*c);
        }
    }
    for(auto& value:a.pivot)value=-value;
    translate(next,a.pivot);
    for(float value:next)if(!std::isfinite(value))return false;
    if(std::fabs(next[12])+std::fabs(next[13])+std::fabs(next[14])+std::fabs(next[15]-1)>1e-5)return false;
    out=next;return true;
}
}
