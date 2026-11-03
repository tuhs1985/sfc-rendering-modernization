// Renderer-neutral,frame-keyed native light bank. Existing scene mapping only.
#pragma once
#include "../m1_component/m1_light_transport.h"
namespace sfc_effect_lights {
constexpr DWORD Offset=15*1024*1024+384*1024,Magic=0x31464c53,Frames=4;
struct Frame {DWORD frame=0,manager=0,thread=0,gate=0;ULONGLONG captured=0;DWORD records[64][16]{};BYTE enables[64]{};};
struct alignas(64) Cell {volatile LONG guard=0;DWORD reserved=0;ULONGLONG captured=0;Frame value{};BYTE padding[24]{};};
struct Store {sfc_light_transport::Header header;Cell frames[Frames];};
constexpr DWORD Bytes=sizeof(Store);
static_assert(sizeof(Frame)==4184&&sizeof(Cell)==4224&&Bytes==16960);
static_assert(Offset+Bytes<16*1024*1024);
inline bool valid(Store& s,const DWORD* session,DWORD pid){return sfc_light_transport::valid(s.header,Magic,Bytes,session,pid);}
template<class Read>bool capture(Store& s,DWORD manager,DWORD frame,Frame& a,Frame& b,Read read){
 if(!frame||!InterlockedCompareExchange(reinterpret_cast<volatile LONG*>(&s.header.reserved[0]),0,0))return false;
 auto bank=[&](Frame& f){f={};f.frame=frame;f.manager=manager;f.thread=GetCurrentThreadId();
  return read(manager+0x778,f.records,sizeof(f.records))&&read(manager+0x1778,f.enables,sizeof(f.enables))&&read(manager+0x1eb8,&f.gate,1);};
 if(!bank(a)||!bank(b)||memcmp(&a,&b,sizeof(a)))return false;
 LARGE_INTEGER q{};if(!QueryPerformanceCounter(&q))return false;a.captured=q.QuadPart;
 sfc_light_transport::publish(s.header,s.frames[frame%Frames],a,a.captured);return true;
}
}
