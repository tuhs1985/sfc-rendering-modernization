#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "../tools/d3d9_proof/frame_ingress.h"
#include <iostream>
#include <limits>
#include <thread>
#include <atomic>
using namespace frame_ingress;
static Packet sample(uint64_t sequence){
 Packet p{};p.key={9,sequence,100+sequence,0,44,2,3};p.offered_qpc=100;p.deadline_qpc=200;
 p.model[0]=p.model[5]=p.model[10]=p.model[15]=1;
 memcpy(p.view,p.model,sizeof(p.view));memcpy(p.projection,p.model,sizeof(p.projection));
 p.model[12]=static_cast<float>(sequence);p.viewport[2]=1720;p.viewport[3]=1020;
 p.key.state_hash=state_hash(p);p.checksum=checksum(p);return p;
}
int main(){
 unsigned checks=0;auto test=[&](bool b){++checks;if(!b){std::cerr<<"Ingress FAIL "<<checks<<'\n';ExitProcess(1);}};
 Channel c{};c.session=9;Producer producer;Consumer consumer;TakeStats stats{};Packet out{},p=sample(1);
 test(channel_valid(c,9));test(!channel_valid(c,8));test(valid(p,9));test(!valid(p,8));
 test(producer.publish(c,p));test(!producer.publish(c,p));test(consumer.take(c,9,150,out,stats));test(same(out.key,p.key));
 test(usable(out,p.key,150,true));test(!usable(out,p.key,150,false));test(!usable(out,p.key,200,true));test(!usable(out,p.key,99,true));
 auto key=p.key;++key.source_frame;test(!usable(out,key,150,true));key=p.key;++key.owner_epoch;test(!usable(out,key,150,true));
 key=p.key;++key.revision;test(!usable(out,key,150,true));key=p.key;++key.asset_hash;test(!usable(out,key,150,true));
 key=p.key;++key.state_hash;test(!usable(out,key,150,true));key=p.key;++key.sequence;test(!usable(out,key,150,true));
 auto bad=p;bad.model[3]=std::numeric_limits<float>::quiet_NaN();bad.checksum=checksum(bad);test(!valid(bad,9));
 bad=p;bad.viewport[2]=0;bad.checksum=checksum(bad);test(!valid(bad,9));bad=p;++bad.key.sequence;test(!valid(bad,9));
 bad=p;++bad.model[12];bad.checksum=checksum(bad);test(!valid(bad,9)); // hash must bind converted state
 for(uint64_t i=2;i<=100;++i)test(producer.publish(c,sample(i)));
 test(consumer.take(c,9,150,out,stats));test(out.key.sequence==100);test(stats.obsolete==3);
 test(!consumer.take(c,9,150,out,stats));test(producer.publish(c,sample(101)));test(!consumer.take(c,9,200,out,stats));test(stats.expired==1);
 // Claimed resources are immutable even when source keeps producing.
 for(auto& s:c.slots){s.packet=sample(777);InterlockedExchange(&s.state,Reading);}
 test(!producer.publish(c,sample(102)));test(c.slots[0].packet.key.sequence==777);
 for(auto& s:c.slots)InterlockedExchange(&s.state,Free);
 c.slots[0].packet=sample(103);c.slots[0].packet.checksum^=1;InterlockedExchange(&c.slots[0].state,Ready);
 test(!consumer.take(c,9,150,out,stats));test(stats.invalid==1);
 InterlockedExchange(&c.stopped,1);test(!producer.publish(c,sample(104)));test(!consumer.take(c,9,150,out,stats));
 Channel late{};late.session=9;Producer lp;Consumer lc;TakeStats ls{};
 test(lp.publish(late,sample(1)));test(lc.take(late,9,150,out,ls));
 auto expected=sample(2);test(!usable(out,expected.key,151,true));test(!usable(out,out.key,201,true));
 test(lp.publish(late,expected));test(lc.take(late,9,150,out,ls));test(usable(out,expected.key,151,true));
 // Same actual slot ownership under concurrent overload. No timing/rate claim.
 Channel stress{};stress.session=9;std::atomic<bool> done=false,failed=false;
 std::thread writer([&]{Producer w;for(uint64_t i=1;i<=100000;++i){auto q=sample(i);while(!w.publish(stress,q))std::this_thread::yield();}done=true;});
 Consumer reader;TakeStats counts{};uint64_t last=0;unsigned received=0;
 while(!done||last<100000){Packet q{};if(reader.take(stress,9,150,q,counts)){
   if(q.key.sequence<=last||q.key.source_frame!=100+q.key.sequence||q.model[12]!=static_cast<float>(q.key.sequence))failed=true;
   last=q.key.sequence;++received;
  }else std::this_thread::yield();}
 writer.join();test(!failed&&last==100000&&received>0&&counts.invalid==0);
 std::cout<<"Frame ingress PASS "<<checks<<" checks pointer_bits="<<sizeof(void*)*8<<" packet="<<sizeof(Packet)
          <<" channel="<<sizeof(Channel)<<" stress_received="<<received<<" obsolete="<<counts.obsolete<<'\n';
}
