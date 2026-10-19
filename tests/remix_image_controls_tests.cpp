#include <cstdint>
#include <iostream>
#include <map>
#include "../tools/remix_runtime/remix_image_controls.h"
int main(){unsigned checks=0;auto require=[&](bool v){++checks;if(!v)throw std::runtime_error("image controls test");};
 try{RemixImageControls settings;unsigned char raw[48]{};uint32_t h[6]{0x31474d49,1,1,1,0,25};float v[4]{-1,1.5f,2,.5f};
 memcpy(raw,h,24);memcpy(raw+24,v,16);auto seal=[&](){auto s=RemixImageControls::hash(raw,40);memcpy(raw+40,&s,8);};seal();
 require(settings.decode(raw,48));require(!settings.decode(raw,48));require(!settings.decode(raw,47));require(settings.post()[0]==1.5f);
 std::map<std::string,std::string> applied;auto set=[&](const char* k,const char* x){applied[k]=x;return true;};require(settings.apply(set));
 require(applied["rtx.tonemappingMode"]=="1");require(applied["rtx.autoExposure.enabled"]=="False");require(!applied.count("rtx.userBrightness"));
 require(std::abs(std::stof(applied["rtx.localtonemap.exposure"])-.75f*std::exp2(-1.75f))<.00001f);require(applied["rtx.tonemap.colorGradingEnabled"]=="False");
 settings.mode=0;require(settings.apply(set));require(applied["rtx.tonemap.colorGradingEnabled"]=="True");require(settings.post()[0]==1);require(settings.post()[1]==2);
 settings.enabled=0;require(settings.apply(set));require(applied["rtx.tonemappingMode"]=="1");require(applied["rtx.autoExposure.enabled"]=="True");require(std::stof(applied["rtx.tonemap.exposureBias"])==0);require(settings.post()[1]==1);
 raw[24]^=1;require(!settings.decode(raw,48));raw[24]^=1;float bad=0;memcpy(raw+32,&bad,4);seal();require(!settings.decode(raw,48));
 require(!settings.apply([](const char*,const char*){return false;}));
 std::cout<<"Image native PASS "<<checks<<" checks\n";return 0;
 }catch(const std::exception& e){std::cout<<e.what()<<"\n";return 1;}}
