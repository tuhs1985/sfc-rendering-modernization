#include "../tools/d3d9_proof/output_extent.h"
#include <iostream>
#include <stdexcept>
int main(){unsigned count=0;auto test=[&](bool value){if(!value)throw std::runtime_error("extent contract");++count;};
 using namespace output_extent;
 test(bytes(1920,1080)==132710400ull);test(bytes(2560,1440)==235929600ull);test(bytes(3840,2160)==530841600ull);
 test(bytes(1280,360)==29491200ull);test(bytes(1031,517)==34113728ull);
 test(!bytes(0,1080));test(!bytes(1920,0));test(!bytes(3841,2160));test(!bytes(3840,2161));test(!bytes(UINT32_MAX,UINT32_MAX));
 Target a{1920,1080,1,1};test(same(a,a));test(!same(a,{1920,1080,1,2}));test(!same(a,{1920,1080,2,1}));
 test(!same(a,{2560,1440,1,1}));test(!same(a,{1920,1080,0,1}));
 std::cout<<"Alpha extent PASS "<<count<<" checks;4K controlled output="<<MaxBytes<<" bytes;slots=2\n";
}
