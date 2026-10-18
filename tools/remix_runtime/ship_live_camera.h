// Native 17-word arithmetic qualified by Run19/20. Not a generic matrix cast.
#pragma once
#include "ship_live_request.h"
namespace ship_live {
struct Camera {float model[12]{},position[3]{},right[3]{},up[3]{},forward[3]{},fov=0,aspect=0,nearZ=0,farZ=0;};
inline bool matrix(const uint32_t* words,float (&m)[4][4]){
 const auto flag=(words[16]>>8)&255;if(flag>1)return false;memcpy(m,words,64);
 for(auto& r:m)for(float x:r)if(!std::isfinite(x))return false;
 if(flag){m[3][0]=m[3][1]=m[3][2]=0;m[3][3]=1;}return true;
}
inline bool camera(const std::array<uint32_t,96>& r,Camera& out){
 float m[4][4]{},v[4][4]{},p[4][4]{};
 if(r[42]||r[43]||r[44]||!matrix(r.data()+8,m)||!matrix(r.data()+49,v)||!matrix(r.data()+66,p))return false;
 for(unsigned i=0;i<4;++i)if(std::abs(v[3][i]-(i==3?1.f:0.f))>1e-6f||std::abs(m[3][i]-(i==3?1.f:0.f))>1e-6f||std::abs(p[3][i]-(i==2?-1.f:0.f))>1e-5f)return false;
 for(unsigned i=0;i<3;++i)for(unsigned j=0;j<3;++j){float dot=0;for(unsigned k=0;k<3;++k)dot+=v[i][k]*v[j][k];if(std::abs(dot-(i==j?1.f:0.f))>.001f)return false;}
 const float det=v[0][0]*(v[1][1]*v[2][2]-v[1][2]*v[2][1])-v[0][1]*(v[1][0]*v[2][2]-v[1][2]*v[2][0])+v[0][2]*(v[1][0]*v[2][1]-v[1][1]*v[2][0]);
 if(std::abs(det-1)>.001f||p[0][0]<=0||p[1][1]<=0||std::abs(p[2][2])<1e-9f||std::abs(p[2][2]+1)<1e-9f)return false;
 for(auto pair:{std::pair{0,1},std::pair{0,2},std::pair{0,3},std::pair{1,0},std::pair{1,2},std::pair{1,3},std::pair{2,0},std::pair{2,1}})if(std::abs(p[pair.first][pair.second])>1e-5f)return false;
 for(unsigned i=0;i<3;++i){out.right[i]=v[0][i];out.up[i]=v[1][i];out.forward[i]=-v[2][i];out.position[i]=0;
  for(unsigned j=0;j<3;++j)out.position[i]-=v[j][i]*v[j][3];for(unsigned j=0;j<4;++j)out.model[i*4+j]=m[i][j];}
 out.fov=2*std::atan(1.f/p[1][1])*180.f/3.14159265358979323846f;out.aspect=p[1][1]/p[0][0];out.nearZ=p[2][3]/p[2][2];out.farZ=p[2][3]/(p[2][2]+1);
 float viewport[6]{};memcpy(viewport,r.data()+83,24);
 return out.nearZ>0&&out.farZ>out.nearZ&&out.farZ<=1e9&&out.fov>0&&out.fov<180&&viewport[2]>0&&viewport[3]>0&&
  std::abs(out.aspect/(viewport[2]/viewport[3])-1)<1e-4f&&std::abs(viewport[4]-viewport[2]*.5f)<.001f&&std::abs(viewport[5]-viewport[3]*.5f)<.001f;
}
}
