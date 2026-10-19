#include "../tools/m1_component/native_light_observer.h"
#include <iostream>
using namespace sfc_native_lights;
static Observer observer;static std::array<std::uint8_t,8192> memory{};
struct Identity{Word owner=1,frame=1,elapsed=0,manager=0x10000,model=2,source=3,thread=4;};
int wmain(int argc,wchar_t** argv){
 if(argc!=2)return 2;
 unsigned checks=0;auto check=[&](bool ok){++checks;if(!ok)throw "observer regression";};
 const Word vt=0x007B8D4C;std::memcpy(memory.data(),&vt,4);
 auto read=[](Word address,void* out,std::size_t bytes){if(address<0x10000||address-0x10000>memory.size()||bytes>memory.size()-(address-0x10000))return false;std::memcpy(out,memory.data()+address-0x10000,bytes);return true;};
 const Word session[4]={1,2,3,4};observer.start(session);Identity id;
 observer.observe(id,read,[]{return true;});observer.observe(id,read,[]{return true;});
 check(observer.sequence==1);id.owner=2;observer.observe(id,read,[]{return true;});check(observer.sequence==2);
 id.owner=3;observer.observe(id,read,[]{return true;});check(observer.sequence==2);
 id.owner=1;
 for(unsigned i=1;i<8;++i){id.elapsed=i*200;observer.observe(id,read,[]{return true;});}
 check(observer.queued==8&&observer.dropped==1);
 std::ofstream file(argv[1],std::ios::binary|std::ios::trunc);observer.drain(file);file.close();
 check(observer.written==8&&observer.queued==0&&!observer.ioFailed);
 observer.sequence=899;id.elapsed+=200;observer.observe(id,read,[]{return true;});id.elapsed+=200;observer.observe(id,read,[]{return true;});check(observer.sequence==900);
 InterlockedExchange(&observer.active,0);id.elapsed+=200;observer.observe(id,read,[]{return true;});check(observer.sequence==900);
 observer.start(session);id.elapsed=90001;observer.observe(id,read,[]{return true;});check(!observer.sequence);
 id.elapsed=100;observer.busy=1;observer.observe(id,read,[]{return true;});observer.busy=0;check(!observer.sequence);
 observer.observe(id,read,[]{return false;});check(observer.rejected==1);
 observer.start(session);observer.tuning=true;id.elapsed=100000;
 observer.observe(id,read,[]{return true;});check(observer.sequence==1);
 id.elapsed=1800001;observer.observe(id,read,[]{return true;});check(observer.sequence==1);
 observer.sequence=18000;id.elapsed=200000;observer.observe(id,read,[]{return true;});check(observer.sequence==18000);
 std::cout<<"NATIVE_LIGHT_OBSERVER_PASS checks="<<checks<<"\n";
}
