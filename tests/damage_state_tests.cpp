#include "../tools/scene_bridge/damage_state.h"
#include <iostream>
#include <map>
#include <vector>
#include <limits>
using namespace sfc_damage;
int main(){unsigned checks=0;bool failed=false;auto test=[&](bool ok){++checks;if(!ok){failed=true;std::cout<<"FAIL "<<checks<<'\n';}};
 test(severity(bits(0))==-1);test(severity(bits(-.1f))==-1);test(severity(bits(.124f))==-1);test(severity(bits(.125f))==0);
 test(severity(bits(.374f))==0);test(severity(bits(.375f))==1);test(severity(bits(.624f))==1);test(severity(bits(.625f))==2);test(severity(bits(2))==2);
 test(severity(bits(std::numeric_limits<float>::quiet_NaN()))==-2);test(severity(bits(std::numeric_limits<float>::infinity()))==-2);
 // Repair/reversal: classification is absolute state, never a monotonic latch.
 test(severity(bits(.9f))==2&&severity(bits(.5f))==1&&severity(bits(.2f))==0&&severity(bits(0))==-1);
 State a{1,2,bits(.5f),0,1};test(valid(a));a.owner=0;test(!valid(a));a.owner=1;a.revision=0;test(!valid(a));a.revision=2;a.family=3;test(!valid(a));a.family=0;a.qualified=0;test(!valid(a));
 std::map<Word,std::vector<unsigned char>> memory;
 auto put=[&](Word p,const void* v,size_t n){auto* b=static_cast<const unsigned char*>(v);memory[p]={b,b+n};};
 auto word=[&](Word p,Word value){put(p,&value,4);};
 auto read=[&](Word p,void* v,size_t n){auto it=memory.find(p);if(it==memory.end()||it->second.size()!=n)return false;memcpy(v,it->second.data(),n);return true;};
 word(0x1000+0x870,0);word(0x1000+0xAD4,0x2000);word(0x2000,0x3000);word(0x3000+0x88,0x401000);
 std::array<unsigned char,8> code{0x8D,0x81,0x00,0x01,0,0,0xC3,0x90};put(0x401000,code.data(),8);
 std::array<float,3> health{103,120,0};put(0x2118,health.data(),12);Word scalar=0,family=0;
 test(source(0x1000,scalar,family,read));test(scalar==bits(.14166665077209473f)&&family==0);
 word(0x1870,6);test(source(0x1000,scalar,family,read)&&family==1);word(0x1870,14);test(source(0x1000,scalar,family,read)&&family==2);
 word(0x1870,24);test(source(0x1000,scalar,family,read)&&scalar==0);word(0x1870,0);
 code[0]=0x8B;put(0x401000,code.data(),8);word(0x2100,0x2200);put(0x2218,health.data(),12);test(source(0x1000,scalar,family,read));
 code[0]=0xE8;put(0x401000,code.data(),8);test(!source(0x1000,scalar,family,read));
 code[0]=0x8D;put(0x401000,code.data(),8);health[1]=0;put(0x2118,health.data(),12);test(!source(0x1000,scalar,family,read));
 health={103,120,0};put(0x2118,health.data(),12);unsigned reads=0;
 auto changing=[&](Word p,void* v,size_t n){if(!read(p,v,n))return false;if(p==0x2118&&++reads==2)static_cast<float*>(v)[0]=99;return true;};
 test(!source(0x1000,scalar,family,changing));
 // Real pinned default getter has a registration prologue, not a bare LEA.
 word(0x2000,0x0079D530);word(0x0079D530+0x88,0x00448B6E);
 std::array<unsigned char,8> prefix{0xF6,0x05,0x2B,0x19,0xC8,0,1,0x56};
 std::array<unsigned char,8> tail{0x8D,0x86,0xAC,0x08,0,0,0x5E,0xC3};
 put(0x00448B6E,prefix.data(),8);put(0x00448B9B,tail.data(),8);
 health={103,120,0};put(0x2000+0x8AC+0x18,health.data(),12);
 test(source(0x1000,scalar,family,read)&&scalar==bits(.14166665077209473f));
 health={120,120,0};put(0x2000+0x8AC+0x18,health.data(),12);
 test(source(0x1000,scalar,family,read)&&severity(scalar)==-1);
 tail[2]=0xAD;put(0x00448B9B,tail.data(),8);test(!source(0x1000,scalar,family,read));
 std::cout<<"Damage state "<<(failed?"FAIL":"PASS")<<" checks="<<checks<<'\n';return failed?1:0;
}
