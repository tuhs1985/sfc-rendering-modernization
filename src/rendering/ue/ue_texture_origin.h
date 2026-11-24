#pragma once
#include <cstdint>
#include <cstddef>
#include <cstring>
namespace sfc_ue_texture {
inline bool upload_rows(const uint8_t* source,size_t source_bytes,uint32_t width,uint32_t height,
                        void* target,size_t target_bytes,size_t pitch){
    const uint64_t row=uint64_t(width)*4,total=row*height;
    if(!source||!target||source==target||!width||!height||source_bytes!=total||pitch<row||
       uint64_t(pitch)>uint64_t(SIZE_MAX)/height||target_bytes<uint64_t(pitch)*height)return false;
    auto* output=static_cast<uint8_t*>(target);
    // UE upload working copy only. Known SFC V-origin conversion, once:
    // source U/UV arrays and original decoded image bytes stay unchanged.
    for(uint32_t y=0;y<height;++y)std::memcpy(output+size_t(y)*pitch,source+size_t(height-1-y)*size_t(row),size_t(row));
    return true;
}
}
