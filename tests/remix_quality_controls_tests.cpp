#include <iostream>
#include <map>
#include "../tools/remix_runtime/remix_quality_controls.h"
int main(){unsigned checks=0;auto require=[&](bool v){++checks;if(!v)throw std::runtime_error("quality test");};try{
 RemixQualityControls q;unsigned char raw[48]{};uint32_t h[8]{0x31544c51,1,1,1,16,3,0,0};float v[2]{-.5f,1};memcpy(raw,h,32);memcpy(raw+32,v,8);auto seal=[&](){auto sum=RemixImageControls::hash(raw,40);memcpy(raw+40,&sum,8);};seal();
 require(q.decode(raw,48));require(!q.decode(raw,48));require(!q.decode(raw,47));
 std::map<std::string,std::string> values;auto set=[&](const char* k,const char* x){values[k]=x;return true;};require(q.apply(set));require(values["rtx.upscalerType"]=="3");require(values["rtx.maxAnisotropySamples"]=="16");require(values["rtx.useDenoiser"]=="False");require(values["rtx.resolutionScale"]=="1.0");
 q.enabled=0;require(q.apply(set));require(values["rtx.upscalerType"]=="0");require(values["rtx.maxAnisotropySamples"]=="8");require(values["rtx.useDenoiser"]=="True");
 v[1]=2;memcpy(raw+32,v,8);seal();require(!q.decode(raw,48));raw[40]^=1;require(!q.decode(raw,48));
 std::cout<<"Quality native PASS "<<checks<<" checks\n";return 0;
 }catch(const std::exception& e){std::cout<<e.what()<<"\n";return 1;}}
