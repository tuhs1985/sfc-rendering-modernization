// Optional evidence of actual successful Remix light-instance submissions.
// No file IO,allocation,wait or effect lifetime policy in this channel.
#pragma once
#include "effect_light_wire.h"
namespace effect_light_trace {
constexpr DWORD Offset=sfc_effect_lights::Offset+64*1024,Magic=0x31544c45,Frames=16;
struct Frame {
 DWORD frame=0,pid=0,generation=0,usable=0;
 ULONGLONG sourceQpc=0,submittedQpc=0;
 sfc_effect_lights::Frame native{};
 int32_t status[62]{};remix_effect_lights::Light lights[62]{};
};
struct alignas(64) Cell {volatile LONG guard=0;DWORD reserved=0;ULONGLONG captured=0;Frame value{};BYTE padding[16]{};};
struct Store {sfc_light_transport::Header header;Cell cells[Frames];};
static_assert(sizeof(Frame)==6944&&sizeof(Cell)==6976&&sizeof(Store)==111680);
static_assert(remix_effect_lights::Offset+sizeof(remix_effect_lights::Store)<=Offset);
static_assert(Offset+sizeof(Store)<=16*1024*1024);
inline bool enabled(Store* store,const DWORD* session,DWORD pid){
 return store&&sfc_light_transport::valid(store->header,Magic,sizeof(Store),session,pid)&&
  InterlockedCompareExchange(reinterpret_cast<volatile LONG*>(&store->header.reserved[0]),0,0)==1;
}
}
