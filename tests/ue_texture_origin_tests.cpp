#include "../src/rendering/ue/ue_texture_origin.h"
#include <array>
#include <cstdio>
#include <stdexcept>
void need(bool value,const char* why){if(!value)throw std::runtime_error(why);}
int main(){try{
    const std::array<unsigned char,16> original{1,2,3,255,4,5,6,255,7,8,9,255,10,11,12,255};
    const auto saved=original;std::array<unsigned char,24> output{};output.fill(99);
    need(sfc_ue_texture::upload_rows(original.data(),original.size(),2,2,output.data(),output.size(),12),"Valid padded upload rejected");
    for(unsigned x=0;x<8;++x){need(output[x]==original[x+8],"Bottom row not at UE V=0");need(output[12+x]==original[x],"Top row not at UE V=1");}
    need(output[8]==99&&output[20]==99,"Row padding changed");need(original==saved,"Original source image changed");
    need(!sfc_ue_texture::upload_rows(original.data(),15,2,2,output.data(),24,12),"Truncated source accepted");
    need(!sfc_ue_texture::upload_rows(original.data(),16,2,2,output.data(),15,8),"Truncated target accepted");
    need(!sfc_ue_texture::upload_rows(original.data(),16,2,2,output.data(),24,4),"Short pitch accepted");
    need(!sfc_ue_texture::upload_rows(original.data(),16,0,2,output.data(),24,12),"Zero extent accepted");
    std::puts("PASS UE-only vertical origin conversion, unchanged source/U/channel bytes and padded rows");return 0;
}catch(const std::exception& e){std::fprintf(stderr,"%s\n",e.what());return 1;}}
