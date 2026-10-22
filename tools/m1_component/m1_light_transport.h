// Fixed worker-published raw light observations. No backend types or callback IO.
#pragma once
#include <windows.h>
#include "native_light_snapshot.h"
namespace sfc_light_transport {
constexpr DWORD RawOffset=15*1024*1024,EncodedOffset=RawOffset+256*1024;
constexpr DWORD RawMagic=0x31524c53,EncodedMagic=0x31454c53,Owners=32;
struct alignas(64) Header {
 DWORD magic=0,version=1,bytes=0,session[4]{},pid=0;
 volatile LONG stopped=0,published=0;DWORD reserved[6]{};
};
template<class T>struct alignas(64) Cell {volatile LONG guard=0;DWORD reserved=0;ULONGLONG captured=0;T value{};};
struct alignas(64) RawCell {volatile LONG guard=0;DWORD reserved=0;ULONGLONG captured=0;sfc_native_lights::Snapshot value{};BYTE padding[36]{};};
struct Raw {Header header;RawCell cells[Owners];};
struct EncodedPayload {BYTE packet[200]{},shapes[808]{};};
struct Encoded {Header header;Cell<EncodedPayload> cell;};
static_assert(sizeof(Header)==64&&sizeof(RawCell)==6208);
static_assert(sizeof(Raw)==198720&&sizeof(Encoded)==1088);
static_assert(RawOffset+sizeof(Raw)<=EncodedOffset&&EncodedOffset+sizeof(Encoded)<16*1024*1024);
inline bool valid(const Header& h,DWORD magic,DWORD bytes,const DWORD* session,DWORD pid){
 return h.magic==magic&&h.version==1&&h.bytes==bytes&&!InterlockedCompareExchange(const_cast<LONG*>(&h.stopped),0,0)&&
  !memcmp(h.session,session,16)&&(!pid||h.pid==pid);
}
template<class C,class T>inline bool read(C& cell,T& value,ULONGLONG& captured){
 const auto before=InterlockedCompareExchange(&cell.guard,0,0);if(!before||(before&1))return false;
 value=cell.value;captured=cell.captured;MemoryBarrier();return captured&&before==InterlockedCompareExchange(&cell.guard,0,0);
}
template<class C,class T>inline void publish(Header& h,C& cell,const T& value,ULONGLONG captured){
 InterlockedIncrement(&cell.guard);cell.value=value;cell.captured=captured;MemoryBarrier();InterlockedIncrement(&cell.guard);InterlockedIncrement(&h.published);
}
}
