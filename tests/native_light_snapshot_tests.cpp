#include "../tools/m1_component/native_light_snapshot.h"
#include <iostream>
using namespace sfc_native_lights;
static Snapshot first,second;
static std::array<std::uint8_t,8192> memory{};
int main(){
 unsigned checks=0;auto check=[&](bool good){++checks;if(!good)throw "native light core failure";};
 const Word vtable=0x007B8D4C;std::memcpy(memory.data(),&vtable,4);
 memory[0x1778]=1;memory[0x177a]=1;memory[0x1eb8]=1;
 auto read=[](Word address,void* out,std::size_t bytes){
  if(address<0x10000||address-0x10000>memory.size()||bytes>memory.size()-(address-0x10000))return false;
  std::memcpy(out,memory.data()+address-0x10000,bytes);return true;
 };
 std::array<Word,16> metadata={Magic,Version,sizeof(Snapshot),1,1,2,3,4,2,100,1000,0x10000,0x20000,0x30000,4,0};
 check(capture(first,second,metadata,read,[]{return true;}));
 check(first.enables[0]==1&&first.enables[1]==0&&first.enables[2]==1&&first.gate==1);
 unsigned recordReads=0;
 auto mutating=[&](Word address,void* out,std::size_t bytes){
  const bool ok=read(address,out,bytes);
  if(address==0x10778&&++recordReads==2)static_cast<Word*>(out)[0]=1;
  return ok;
 };
 check(!capture(first,second,metadata,mutating,[]{return true;}));
 check(!capture(first,second,metadata,read,[]{return false;}));
 auto absent=[](Word,void*,std::size_t){return false;};
 check(!capture(first,second,metadata,absent,[]{return true;}));
 auto bad=metadata;bad[11]=0xfffffff0u;check(!capture(first,second,bad,read,[]{return true;}));
 bad=metadata;bad[8]=0;check(!capture(first,second,bad,read,[]{return true;}));
 bad=metadata;bad[15]=1;check(!capture(first,second,bad,read,[]{return true;}));
 memory[0]=0;check(!capture(first,second,metadata,read,[]{return true;}));
 std::cout<<"NATIVE_LIGHT_CORE_PASS checks="<<checks<<" bytes="<<sizeof(Snapshot)<<"\n";
}
