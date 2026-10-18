#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "../tools/remix_runtime/ship_triplet_wire.h"
#include <iostream>
#include <limits>
using namespace ship_triplet;
static unsigned count=0;
static void check(bool v){++count;if(!v){std::cerr<<"triplet check "<<count<<" failed\n";std::exit(1);}}
static Key key(){Key k{};k.session[0]=1;k.owner=2;k.revision=2;k.frame=120;k.objectId=29;k.pose=3;k.camera=4;
 k.width=k.height=256;k.viewport[0]=200;k.viewport[1]=30;k.viewport[2]=1720;k.viewport[3]=1020;k.resourceEpoch=1;k.depthConvention=1;k.asset[0]=8;k.sourceSession[0]=9;k.sourcePid=38852;return k;}
static Wire wire(){Wire s{};s.creator=1;s.width=s.height=256;s.handles[0]=1;s.handles[1]=2;s.handles[2]=3;s.frequency=100;s.resourceEpoch=1;s.session[0]=1;s.ready=1;return s;}
int main(){
 auto s=wire();auto k=key();Key acquired{};uint64_t hashes[]={11,12,13};
 check(sizeof(Wire)==496&&sizeof(Key)==152);check(valid(s)&&validKey(k));check(request(s,k));check(begin(s,acquired));check(same(k,acquired));
 check(!begin(s,acquired));check(!finish(s,1,true));check(publish(s,k,hashes,100));check(!begin(s,acquired));
 check(claim(s,k,101));check(!claim(s,k,101));check(!finish(s,1,false));check(!finish(s,2,true));check(finish(s,1,true));check(s.ack==1&&s.lease==Idle);
 check(request(s,k)&&begin(s,acquired)&&publish(s,k,hashes,200)&&claim(s,k,200)&&finish(s,2,true));
 for(unsigned field=0;field<12;++field){s=wire();k=key();check(request(s,k)&&begin(s,acquired)&&publish(s,k,hashes,100));Key wrong=k;
  switch(field){case 0:++wrong.owner;break;case 1:++wrong.revision;break;case 2:++wrong.frame;break;case 3:++wrong.pose;break;case 4:++wrong.camera;break;
   case 5:++wrong.session[0];break;case 6:++wrong.asset[0];break;case 7:++wrong.resourceEpoch;break;case 8:++wrong.objectId;break;case 9:++wrong.viewport[0];break;
   case 10:++wrong.sourceSession[0];break;case 11:++wrong.sourcePid;break;}
  check(!claim(s,wrong,101)&&s.lease==Idle&&s.rejected==1&&s.ack==1);}
 s=wire();k=key();check(request(s,k)&&begin(s,acquired));auto changed=k;++changed.frame;check(request(s,changed));check(!publish(s,k,hashes,100)&&s.lease==Idle);
 s=wire();check(request(s,k)&&begin(s,acquired)&&publish(s,k,hashes,100));check(!claim(s,k,201)&&s.lease==Idle);
 s=wire();s.stop=1;check(!request(s,k)&&!begin(s,acquired));s=wire();s.version=BufferedVersion+1;check(!valid(s)&&!request(s,k));
 s=wire();s.handles[1]=s.handles[0];check(!valid(s));s=wire();s.handles[0]=uint64_t(UINT32_MAX)+1;check(!valid(s));
 check(!dimensions(1921,1080)&&!dimensions(0,256)&&dimensions(1920,1080));
 k=key();k.asset[0]=0;check(!validKey(k));k=key();k.depthConvention=2;check(!validKey(k));
 s=wire();s.guard=1;check(!request(s,key())&&!begin(s,acquired));
 s=wire();s.sequence=s.ack=LONG_MAX;check(request(s,key())&&!begin(s,acquired));
 s=wire();k=key();const auto pinned=describe(s);check(request(s,k)&&begin(s,acquired)&&publish(s,k,hashes,100));
 s.handles[0]=4;check(!claim(s,k,100,&pinned)&&s.lease==Idle);
 k=key();k.diagnosticMode=1;k.worldOffset[0]=12;check(validKey(k));
 s=wire();check(request(s,k)&&begin(s,acquired)&&publish(s,k,hashes,100));
 auto wrong=k;wrong.worldOffset[0]=13;check(!claim(s,wrong,100));
 k=key();k.diagnosticMode=1;check(!validKey(k));k.worldOffset[1]=1;check(validKey(k));
 k.diagnosticMode=0;check(!validKey(k));k.diagnosticMode=BufferedMode;check(validKey(k));check(!request(s,k));k.diagnosticMode=BufferedMode+1;check(!validKey(k));
 k.diagnosticMode=1;k.worldOffset[1]=std::numeric_limits<float>::infinity();check(!validKey(k));
 k.worldOffset[1]=1000001;check(!validKey(k));
 std::cout<<"SHIP_TRIPLET_WIRE_PASS checks="<<count<<" wire="<<sizeof(Wire)<<" key="<<sizeof(Key)<<"\n";
}
