// Effective native17word arithmetic -> neutral column matrices. No SDK choices.
#pragma once
#include "live_owner_wire.h"
#include <algorithm>
namespace live_owner {
inline bool matches_asset(const Packet& p,DWORD owner,DWORD revision,DWORD model,DWORD source){return p.row[1]==owner&&p.row[7]==revision&&p.row[5]==model&&p.row[6]==source;}
inline bool matrix(const DWORD* words,float* out){
 const auto affine=(words[16]>>8)&255;if(affine>1)return false;memcpy(out,words,64);
 for(unsigned i=0;i<16;++i)if(!std::isfinite(out[i]))return false;
 if(affine){out[12]=out[13]=out[14]=0;out[15]=1;}return true;
}
template<class F>inline bool decode(const Packet& p,F& out){
 const auto& r=p.row;if(!r[1]||!r[2]||r[4]!=1||!r[5]||!r[6]||!r[7]||r[42]||r[43]||r[44]||r[48]!=1)return false;
 out={};out.owner=r[1];out.revision=r[7];out.frame=r[2];out.active=1;
 if(!matrix(r.data()+8,out.model)||!matrix(r.data()+49,out.view)||!matrix(r.data()+66,out.projection))return false;
 float v[6]{};memcpy(v,r.data()+83,sizeof(v));for(float f:v)if(!std::isfinite(f))return false;
 if(v[0]<0||v[1]<0||v[2]<1||v[3]<1||v[2]>4096||v[3]>4096||fabs(v[2]-round(v[2]))>1e-3||fabs(v[3]-round(v[3]))>1e-3||fabs(v[4]-v[2]/2)>1e-3||fabs(v[5]-v[3]/2)>1e-3)return false;
 memcpy(out.viewport,v,sizeof(out.viewport));const auto* view=out.view;const auto* q=out.projection;
 if(view[12]!=0||view[13]!=0||view[14]!=0||view[15]!=1)return false;
 for(unsigned i=0;i<3;++i)for(unsigned j=0;j<3;++j){double value=0;for(unsigned k=0;k<3;++k)value+=double(view[i*4+k])*view[j*4+k];if(fabs(value-(i==j?1.:0.))>1e-3)return false;}
 const double determinant=double(view[0])*(double(view[5])*view[10]-double(view[6])*view[9])-double(view[1])*(double(view[4])*view[10]-double(view[6])*view[8])+double(view[2])*(double(view[4])*view[9]-double(view[5])*view[8]);if(fabs(determinant-1)>1e-3)return false;
 if(fabs(q[12])>1e-5||fabs(q[13])>1e-5||fabs(q[14]+1)>1e-5||fabs(q[15])>1e-5||q[0]<=0||q[5]<=0)return false;
 for(unsigned i:{1u,3u,4u,7u,8u,9u})if(fabs(q[i])>1e-5)return false;
 const double a=q[10],b=q[11];if(fabs(a-1)<1e-9||fabs(a+1)<1e-9)return false;
 const double nearPlane=b/(a-1),farPlane=b/(a+1);if(!(0<nearPlane&&nearPlane<farPlane&&farPlane<=1e9))return false;
 if(fabs((double(q[5])/q[0])/(double(v[2])/v[3])-1)>1e-4)return false;return true;
}
inline void transform(const float* matrix,const double* in,double* out){for(unsigned i=0;i<4;++i){out[i]=0;for(unsigned j=0;j<4;++j)out[i]+=double(matrix[i*4+j])*in[j];}}
template<class F>inline bool projection_matches(const Packet& p,const F& frame,const float* point){
 float composed[16]{};if(!matrix(p.row.data()+25,composed))return false;
 double in[4]{point[0],point[1],point[2],1},world[4]{},view[4]{},clip[4]{},native[4]{};
 transform(frame.model,in,world);transform(frame.view,world,view);transform(frame.projection,view,clip);transform(composed,in,native);
 if(fabs(clip[3])<1e-10||fabs(native[3])<1e-10)return false;
 const auto* v=frame.viewport;const double x=v[0]+v[2]*(clip[0]/clip[3]+1)/2,y=v[1]+v[3]*(1-clip[1]/clip[3])/2;
 return std::isfinite(x)&&std::isfinite(y)&&fabs(x-native[0]/native[3])<=.25&&fabs(y-native[1]/native[3])<=.25;
}
}
