// Fixed game-facing simulation registry. No renderer/API resources or callbacks.
#pragma once
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include "../m1_component/m1_mesh_export.h"
namespace sfc_scene {
using Word=std::uint32_t;using Matrix=std::array<float,16>;
inline Matrix identity(){Matrix m{};for(unsigned n=0;n<4;++n)m[n*5]=1;return m;}
inline Matrix multiply(const Matrix& a,const Matrix& b){Matrix o{};
 for(unsigned i=0;i<4;++i)for(unsigned j=0;j<4;++j){double x=0;for(unsigned k=0;k<4;++k)x+=double(a[i*4+k])*b[k*4+j];o[i*4+j]=float(x);}return o;}
struct Inputs {std::array<float,3> base{},offset{};std::array<std::uint16_t,3> angles{},shipAngles{};std::array<Word,17> extra{};};
template<class Read>bool inputs(Word ship,Inputs& p,Read read){return read(ship+0x34,p.base.data(),12)&&read(ship+0xe6,p.offset.data(),12)&&
 read(ship+0x90,p.angles.data(),6)&&read(ship+0x92a,p.shipAngles.data(),6)&&read(ship+0x980,p.extra.data(),68);}
template<class Read>bool pose(Word ship,Matrix& out,Read read){
 Inputs a{},b{};if(!inputs(ship,a,read)||!inputs(ship,b,read)||memcmp(&a,&b,sizeof(a)))return false;
 Matrix m=identity();for(unsigned n=0;n<3;++n)m[n*4+3]=a.base[n];
 const unsigned axes[]{0,1,2,0,2,0};const unsigned angles[]{2048,a.angles[0],a.angles[2],a.angles[1],a.shipAngles[2],a.shipAngles[0]};
 for(unsigned n=0;n<6;++n){float c=0,s=0;const auto index=(angles[n]&8191)*4;
  if(!read(0x00c6c004+index,&c,4)||!read(0x00c6a004+index,&s,4)||!std::isfinite(c)||!std::isfinite(s)||fabs(double(c)*c+double(s)*s-1)>1e-4)return false;
  auto r=identity();if(axes[n]==0){r[5]=r[10]=c;r[6]=-s;r[9]=s;}else if(axes[n]==1){r[0]=r[10]=c;r[2]=s;r[8]=-s;}else{r[0]=r[5]=c;r[1]=-s;r[4]=s;}m=multiply(m,r);
 }
 Matrix extra{};memcpy(extra.data(),a.extra.data(),64);
 if(((a.extra[16]>>8)&255)==1){extra[12]=extra[13]=extra[14]=0;extra[15]=1;}
 else if(((a.extra[16]>>8)&255)!=0)return false;
 m=multiply(m,extra);for(unsigned n=0;n<3;++n)m[n*4+3]+=a.offset[n];
 for(float x:m)if(!std::isfinite(x))return false;
 if(fabs(m[12])+fabs(m[13])+fabs(m[14])+fabs(m[15]-1)>1e-5)return false;
 out=m;return true;
}
struct Entry {sfc_m1::MeshIdentity id{};std::array<Word,3> lod{};Word revision=0,generation=0,lastVisible=0,lastUpdated=0;bool live=false,qualified=false;Matrix world{};};
struct Registry {
 std::array<Entry,32> entries{};Word generations=0,admitted=0,destroyed=0,rejected=0,updated=0,offscreen=0;
 Entry* find(Word owner){for(auto& e:entries)if(e.live&&e.id.owner==owner)return &e;return nullptr;}
 bool contains(Word owner){return find(owner)!=nullptr;}
 template<class Read>bool valid(const Entry& e,Read read){Word ship=0,visual=0,model=0,link=0,count=0,list=0;std::array<Word,3> lod{};
  return read(e.id.ship,&ship,4)&&ship==0x00796f0c&&read(e.id.ship+0x88,&link,4)&&link==e.id.visual&&read(link,&visual,4)&&visual==0x007985a4&&
   read(e.id.model,&model,4)&&model==0x007983e8&&read(e.id.model+0x10,&count,4)&&count==e.id.count&&read(e.id.model+0x14,&list,4)&&list==e.id.list&&
   read(e.id.visual+0x11c,lod.data(),12)&&lod==e.lod;
 }
 template<class Read>bool admit(const sfc_m1::MeshIdentity& id,Word revision,const std::array<Word,3>& lod,const void* observed,Read read){
  if(auto* e=find(id.owner)){e->lastVisible=id.frame;return e->id.same_epoch(id)&&e->revision==revision;}
  Matrix m{};if(!revision||!pose(id.ship,m,read)){++rejected;return false;}
  float oracle[16]{};memcpy(oracle,observed,64);for(unsigned i=0;i<16;++i)if(!std::isfinite(oracle[i])||fabs(double(m[i])-oracle[i])>1e-5*(std::fmax)(1.,fabs(double(oracle[i])))){++rejected;return false;}
  for(auto& e:entries)if(!e.live){e={};e.id=id;e.lod=lod;e.revision=revision;e.generation=++generations;e.lastVisible=id.frame;e.world=m;e.live=e.qualified=true;++admitted;return true;}
  ++rejected;return false;
 }
 void destroy(Word ship){for(auto& e:entries)if(e.live&&e.id.ship==ship){e.live=false;e.qualified=false;++destroyed;}}
 template<class Read>bool update(Entry& e,Word frame,Read read){
  if(!e.live)return false;if(!valid(e,read)){e.live=e.qualified=false;++rejected;return false;}
  Matrix next{};if(!pose(e.id.ship,next,read)||!valid(e,read)){e.qualified=false;++rejected;return false;}
  e.world=next;e.lastUpdated=frame;e.qualified=true;++updated;if(e.lastVisible!=frame)++offscreen;return true;
 }
};
}
