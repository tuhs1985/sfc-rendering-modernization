#include "../tools/scene_bridge/persistent_scene.h"
#include <iostream>
#include <vector>
static unsigned checks=0;
static void check(bool x){++checks;if(!x)throw std::runtime_error("Persistent scene test failed");}
int main(){try{
 std::vector<unsigned char> memory(0x6000);const unsigned ship=0x10000,visual=0x12000,model=0x13000;
 auto write=[&](unsigned a,const void* p,unsigned n){memcpy(memory.data()+a-ship,p,n);};
 auto word=[&](unsigned a,unsigned v){write(a,&v,4);};
 auto read=[&](unsigned a,void* p,unsigned n){
  if((a>=0xc6a004&&a<0xc72004)&&(n==4)){
   const bool cosine=a>=0xc6c004;const auto index=(a-(cosine?0xc6c004:0xc6a004))/4;
   const float f=float(cosine?cos(double(index)*6.283185307179586/8192):sin(double(index)*6.283185307179586/8192));memcpy(p,&f,4);return true;
  }
  if(a<ship||a+n>ship+memory.size())return false;memcpy(p,memory.data()+a-ship,n);return true;
 };
 word(ship,0x796f0c);word(ship+0x88,visual);word(visual,0x7985a4);word(model,0x7983e8);word(model+0x10,3);word(model+0x14,0x14000);
 std::array<unsigned,3> lod{1,0xffffffffu,0};write(visual+0x11c,lod.data(),12);
 const auto ident=sfc_scene::identity();write(ship+0x980,ident.data(),64);word(ship+0x980+64,0x100);
 float pos[3]{10,20,30};write(ship+0x34,pos,12);sfc_scene::Matrix p{};check(sfc_scene::pose(ship,p,read));
 check(p[3]==10&&p[7]==20&&p[11]==30);check(fabs(p[6]+1)<1e-5&&fabs(p[9]-1)<1e-5);
 sfc_m1::MeshIdentity id{};id.owner=1;id.ship=ship;id.visual=visual;id.model=model;id.count=3;id.list=0x14000;id.frame=1;
 unsigned oracle[16]{};memcpy(oracle,p.data(),64);sfc_scene::Registry r;
 check(r.admit(id,1,lod,oracle,read));check(r.contains(1));const auto generation=r.entries[0].generation;
 pos[0]=50;write(ship+0x34,pos,12);check(r.update(r.entries[0],2,read));check(r.entries[0].world[3]==50);check(r.offscreen==1);
 check(r.entries[0].generation==generation&&r.admitted==1); // no render cache or asset recapture
 id.frame=3;check(r.admit(id,1,lod,oracle,read));check(r.entries[0].lastVisible==3);
 r.destroy(ship);check(!r.contains(1)&&r.destroyed==1);check(!r.update(r.entries[0],4,read));
 id.owner=2;check(sfc_scene::pose(ship,p,read));memcpy(oracle,p.data(),64);check(r.admit(id,1,lod,oracle,read));check(r.entries[0].generation>generation);
 word(ship+0x88,0);check(!r.update(r.entries[0],5,read));check(!r.contains(2));
 std::cout<<"Persistent scene PASS "<<checks<<" checks pointer_bits="<<sizeof(void*)*8<<"\n";return 0;
 }catch(const std::exception& e){std::cerr<<e.what();return 1;}}
