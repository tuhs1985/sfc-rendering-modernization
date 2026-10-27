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
 unsigned char extended[64]{};h[1]=2;h[2]=0;v[2]=1;memcpy(extended,h,24);memcpy(extended+24,v,16);
 uint32_t bloom[2]{0,8};float nv[2]{2.f,.01f};memcpy(extended+40,bloom,8);memcpy(extended+48,nv,8);
 auto sealExtended=[&](){auto sum=RemixImageControls::hash(extended,56);memcpy(extended+56,&sum,8);};sealExtended();
 require(settings.decode(extended,64));require(settings.nativeConfigured);require(settings.apply(set));
 require(applied["rtx.bloom.enable"]=="False");require(applied["rtx.bloom.steps"]=="8");
 require(!applied.count("rtx.emissiveIntensity"));require(std::stof(applied["rtx.bloom.burnIntensity"])==2.f);
 require(std::abs(std::stof(applied["rtx.bloom.luminanceThreshold"])-.01f)<1e-6f);
 require(settings.post()==std::array<float,4>{1,1,1,0}); // Native controls do not grade diffuse.
 const auto accepted=settings.revision;extended[40]=2;sealExtended();require(!settings.decode(extended,64));require(settings.revision==accepted);
 extended[40]=0;extended[44]=9;sealExtended();require(!settings.decode(extended,64));
 extended[44]=8;nv[0]=-1;memcpy(extended+48,nv,8);sealExtended();require(!settings.decode(extended,64));
 // Removing [remix] via the original restore example restores stock values.
 h[1]=1;h[2]=0;memcpy(raw,h,24);memcpy(raw+24,v,16);seal();require(settings.decode(raw,48));require(settings.apply(set));
 require(applied["rtx.bloom.enable"]=="True");require(applied["rtx.bloom.steps"]=="5");require(!applied.count("rtx.emissiveIntensity"));
 std::cout<<"Image native PASS "<<checks<<" checks\n";return 0;
 }catch(const std::exception& e){std::cout<<e.what()<<"\n";return 1;}}
