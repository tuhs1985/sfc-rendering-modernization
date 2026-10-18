#define WIN32_LEAN_AND_MEAN
#include "../tools/remix_runtime/depth_search_wire.h"
#include <iostream>
#include <stdexcept>
static unsigned checks=0;
static void test(bool good){++checks;if(!good)throw std::runtime_error("search wire check");}
int main(){try{
  using namespace depth_search;
  Data d{};d.magic=Magic;d.version=Version;d.bytes=sizeof(d);d.capacity=Capacity;
  test(valid(d));test(sizeof(d)==2304);test(256+sizeof(d)<=4096);
  Resource r{};r.epoch=1;r.resourceLabel=123;r.viewLabel=456;r.width=800;r.height=600;r.format=44;r.viewFormat=45;r.flags=72;r.samples=1;
  for(unsigned p=0;p<Phases;++p)retain(d,r,p,p+10);
  test(d.resourceCount==1);test(d.resources[0].phaseMask==63);test(d.resources[0].observations==6);
  test(d.resources[0].firstTick==10&&d.resources[0].lastTick==15);
  for(unsigned i=1;i<Capacity;++i){r.resourceLabel=123+i;retain(d,r,0,i+20);}
  test(d.resourceCount==32);r.resourceLabel=999;retain(d,r,0,60);
  test(d.resourceCount==32);test(d.overflow==1);
  r=d.resources[0];r.epoch=2;test(!same(r,d.resources[0]));
  r=d.resources[0];r.viewFormat=0;test(!same(r,d.resources[0]));
  d.version=2;test(!valid(d));
  std::cout<<"Expanded search wire PASS "<<checks<<" checks\n";return 0;
}catch(const std::exception& e){std::cout<<e.what()<<"\n";return 1;}}
