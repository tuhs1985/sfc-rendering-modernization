// Worker-only acceleration of the EXISTING captured packet FNV-1a32 contract.
// No new hash, pointer identity, parsing, geometry conversion or relaxed check.
#include <cstddef>
#include <cstdint>
extern "C" __declspec(dllexport) uint32_t sfc_mesh_checksum(const unsigned char* data,size_t bytes) {
    if(!data||bytes<256||bytes>2*1024*1024)return 0;
    uint32_t value=2166136261u;
    for(size_t i=0;i<bytes;++i){value^=(i>=12&&i<16)?0u:data[i];value*=16777619u;}
    return value;
}
