// Checked resolution-dependent output accounting. Queue/slot counts unchanged.
#pragma once
#include <cstdint>
namespace output_extent {
constexpr bool alpha_supported(uint32_t w,uint32_t h){
 return (w==1024&&h==768)||(w==1280&&h==720)||(w==1366&&h==768)||
        (w==1440&&h==900)||(w==1600&&h==900)||(w==1920&&h==1080);
}
constexpr uint32_t MaxWidth=3840,MaxHeight=2160;
// Existing controlled replacement output: three producer planes, six game-pool
// planes, grading/history/coverage resources, and physical hull DSV. Imported
// aliases do not allocate another image. Retain the conservative 16-plane bound.
constexpr uint64_t BytesPerPixel=4,Planes=16;
constexpr uint64_t MaxBytes=uint64_t(MaxWidth)*MaxHeight*BytesPerPixel*Planes;
constexpr bool valid(uint32_t width,uint32_t height){
 return width&&height&&width<=MaxWidth&&height<=MaxHeight;
}
constexpr uint64_t bytes(uint32_t width,uint32_t height){
 return valid(width,height)?uint64_t(width)*height*BytesPerPixel*Planes:0;
}
// Read-only generation comparison. A changed device/target is never authorized
// by equal dimensions alone; old GPU leases must retire before resource reuse.
struct Target {uint32_t width=0,height=0,device=0,generation=0;};
constexpr bool valid(const Target& t){return valid(t.width,t.height)&&t.device&&t.generation;}
constexpr bool same(const Target& a,const Target& b){
 return valid(a)&&valid(b)&&a.width==b.width&&a.height==b.height&&a.device==b.device&&a.generation==b.generation;
}
}
