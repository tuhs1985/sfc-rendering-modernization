// Offline only: no SFC, hooks, runtime phase activation or original asset writes.
#include "../tools/m1_component/m1_surface_graph.h"
#include <cstdlib>
#include <iostream>
#include <limits>

namespace {
std::array<std::uint32_t,452> list;
std::array<std::array<std::uint32_t,7>,452> headers;
std::array<std::array<std::uint32_t,21>,452> corners;
sfc_m1::SurfaceGraphPair pair,invalid;
void require(bool ok,const char* message) {if(!ok){std::cerr<<message<<'\n';std::exit(1);}}
bool read(std::uint32_t address,void* out,std::size_t length) {
    const auto contains=[&](const void* base,std::size_t size) {
        const auto start=reinterpret_cast<std::uintptr_t>(base);
        return address>=start && length<=size && address-start<=size-length;
    };
    if(!contains(list.data(),sizeof(list)) && !contains(headers.data(),sizeof(headers)) &&
       !contains(corners.data(),sizeof(corners)))return false;
    std::memcpy(out,reinterpret_cast<const void*>(address),length);return true;
}
}
int main() {
    for(unsigned i=0;i<452;++i) {
        list[i]=static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(headers[i].data()));
        headers[i]={3,i%5,0x3f800000,0,0,0x5a5a5a5a,
            static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(corners[i].data()))};
        for(unsigned c=0;c<3;++c) {
            corners[i][c*7]=c;corners[i][c*7+1]=0x3f800000;
            corners[i][c*7+2]=0x80000000;corners[i][c*7+3]=0x3f000000;
            corners[i][c*7+4]=i;corners[i][c*7+5]=c;corners[i][c*7+6]=0xa5a5a5a5;
        }
    }
    const auto input=static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(list.data()));
    const auto original_headers=headers;const auto original_corners=corners;const auto original_list=list;
    require(pair.build(input,452,3,read),"complete452-polygon pair builds");
    require(pair.built && pair.changed_vectors==1356 && pair.intact(),"all corners reversed, no other payload change");
    require(pair.neutral.matches_original(input,452,3,read),"current input exactly matches baseline");
    for(unsigned i=0;i<1200;++i)require(pair.neutral.matches_original(input,452,3,read) && pair.intact(),
                                     "immutable pair supports repeated checked access without rewriting");
    require(headers==original_headers && corners==original_corners && list==original_list,"original bytes untouched");
    corners[400][1]^=1;
    require(!pair.neutral.matches_original(input,452,3,read),"changed input beyond old64 prefix rejected");
    corners=original_corners;list[400]=0;
    require(!pair.neutral.matches_original(input,452,3,read),"changed pointer beyond prefix rejected");
    list=original_list;
    require(!pair.neutral.matches_original(input,452,2,read) && !pair.neutral.matches_original(input,451,3,read),
            "vertex/count identity change rejected");
    require(!pair.build(input,452,3,read),"no rebuilding or overwriting used pair");
    corners[0][1]=0x7f800000;
    require(!invalid.build(input,452,3,read) && !invalid.built,"nonfinite vector never qualifies");
    require(sfc_m1::surface_test_phase(0)==0 && sfc_m1::surface_test_phase(19999)==0 &&
        sfc_m1::surface_test_phase(20000)==1 && sfc_m1::surface_test_phase(24999)==1 &&
        sfc_m1::surface_test_phase(25000)==2 && sfc_m1::surface_test_phase(39999)==2 &&
        sfc_m1::surface_test_phase(40000)==3,"20s marker,5s baseline,15s intervention,restored");
    std::cout<<"Surface graph/schedule offline tests passed; bytes="<<sizeof(pair)<<"\n";
}
