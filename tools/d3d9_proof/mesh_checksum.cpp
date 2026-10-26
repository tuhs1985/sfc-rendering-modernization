// Worker-only acceleration of the EXISTING captured packet FNV-1a32 contract.
// No new hash, pointer identity, parsing, geometry conversion or relaxed check.
#include <cstddef>
#include <cstdint>
#define XXH_INLINE_ALL
#include <xxhash.h>
extern "C" __declspec(dllexport) uint32_t sfc_mesh_checksum(const unsigned char* data,size_t bytes) {
    if(!data||bytes<256||bytes>2*1024*1024)return 0;
    uint32_t value=2166136261u;
    for(size_t i=0;i<bytes;++i){value^=(i>=12&&i<16)?0u:data[i];value*=16777619u;}
    return value;
}

// Existing multi_scene catalog FNV-1a64, over the EXACT bytes being written.
// Consumer still verifies files independently. This removes process startup and
// producer-side file rereads, not the transport's identity contract.
extern "C" __declspec(dllexport) uint64_t sfc_asset_identity(const unsigned char* data,size_t bytes) {
    if(!data||!bytes||bytes>64ull*1024*1024+16)return 0;
    uint64_t value=14695981039346656037ull;
    for(size_t i=0;i<bytes;++i){value^=data[i];value*=1099511628211ull;}
    return value;
}

// Same pinned XXH3 used by texture_hash.exe, over tightly packed BGRA8 pixels.
extern "C" __declspec(dllexport) uint64_t sfc_texture_identity(const unsigned char* data,size_t bytes) {
    if(!data||!bytes||bytes>64ull*1024*1024)return 0;
    return XXH3_64bits(data,bytes);
}
