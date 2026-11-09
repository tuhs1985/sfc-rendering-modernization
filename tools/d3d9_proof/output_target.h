// Versioned preallocated target notice, independent of ship readiness/identity.
// Reserved first-64KiB semantic IPC: startup 4096..4351; target 4352..4479;
// environment begins 8192. No GPU handles or process pointers are transported.
#pragma once
#include <windows.h>
#include <cstdint>
#include <cstddef>
#include <cstring>
#include "output_extent.h"
namespace output_target {
constexpr DWORD Offset=4352,Magic=0x31544754,Version=1;
inline bool requested(){static const bool value=[](){wchar_t f[2]{};return GetEnvironmentVariableW(L"SFC_NATIVE_RESOLUTION",f,2)==1&&f[0]==L'1';}();return value;}
struct alignas(8) Notice {
 DWORD magic=Magic,version=Version,bytes=sizeof(Notice),pid=0,session[4]{};
 uint64_t observed=0;DWORD width=0,height=0,device=0,generation=0;uint64_t checksum=0;
};
struct alignas(64) Store {volatile LONG sequence=0;BYTE reserved[60]{};Notice notice{};};
static_assert(sizeof(Notice)==64&&sizeof(Store)==128&&offsetof(Notice,checksum)==56);
static_assert(Offset>=4096+256&&Offset+sizeof(Store)<=8192);
inline uint64_t hash(const void* data,size_t size){
 uint64_t h=14695981039346656037ull;auto* bytes=static_cast<const BYTE*>(data);
 for(size_t i=0;i<size;++i){h^=bytes[i];h*=1099511628211ull;}return h;
}
inline void seal(Notice& n){n.checksum=hash(&n,offsetof(Notice,checksum));}
inline bool valid(const Notice& n,const DWORD* session,DWORD pid){
 return n.magic==Magic&&n.version==Version&&n.bytes==sizeof(Notice)&&n.pid==pid&&pid&&
  session&&!memcmp(n.session,session,16)&&n.observed&&
  output_extent::valid(output_extent::Target{n.width,n.height,n.device,n.generation})&&
  n.checksum==hash(&n,offsetof(Notice,checksum));
}
// Single native game-thread writer. One bounded reader attempt; a torn or busy
// notice is not permission to reuse pixels from an older target generation.
inline void publish(Store& store,Notice value){
 seal(value);InterlockedIncrement(&store.sequence);MemoryBarrier();
 memcpy(&store.notice,&value,sizeof(value));MemoryBarrier();InterlockedIncrement(&store.sequence);
}
inline bool read(const Store& store,Notice& out){
 const LONG before=InterlockedCompareExchange(const_cast<volatile LONG*>(&store.sequence),0,0);
 if(!before||(before&1))return false;
 memcpy(&out,&store.notice,sizeof(out));MemoryBarrier();
 return before==InterlockedCompareExchange(const_cast<volatile LONG*>(&store.sequence),0,0);
}
}
