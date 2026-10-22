// Worker-only acknowledged rebind. Existing packet/frame/resource checks unchanged.
#pragma once
#include "live_owner_wire.h"
namespace owner_rebind {
constexpr DWORD Offset=11*1024*1024+112*1024,Magic=0x3142524f;
struct Target {DWORD generation=0,owner=0,revision=0,model=0,source=0,reserved=0;uint64_t cookie=0,checksum=0;};
struct alignas(64) Control {
 DWORD magic=Magic,version=1,bytes=128,session[4]{},pid=0;
 volatile LONG guard=0;DWORD reserved[7]{};
 Target request{};volatile LONG acknowledged=0;DWORD rejected=0;BYTE padding[16]{};
};
static_assert(sizeof(Target)==40&&sizeof(Control)==128);
static_assert(live_owner::Offset+sizeof(live_owner::Store)<=Offset);
static_assert(Offset+sizeof(Control)<=11*1024*1024+128*1024);
inline bool read(Control& c,const live_owner::Header& h,Target& out){
 if(c.magic!=Magic||c.version!=1||c.bytes!=sizeof(Control)||c.pid!=h.pid||!live_owner::same_session(c.session,h.session))return false;
 const auto before=InterlockedCompareExchange(&c.guard,0,0);if(!before||(before&1))return false;
 out=c.request;MemoryBarrier();return before==InterlockedCompareExchange(&c.guard,0,0);
}
inline bool valid(const Target& t,uint64_t cookie,DWORD previous){
 return t.generation==previous+1&&t.generation<=64&&t.owner&&t.revision&&t.model&&t.source&&!t.reserved&&
  t.cookie==cookie&&cookie&&t.checksum==live_owner::checksum(t);
}
inline bool apply(Control& c,live_owner::Store& store,const Target& t,uint64_t cookie,DWORD& generation){
 if(!valid(t,cookie,generation)){++c.rejected;return false;}
 // No callback waits. An in-flight old publication is still checked against the
 // new owner/revision/model/source by the worker and compositor, never displayed.
 InterlockedExchange64(&store.header.selected,static_cast<LONG64>(live_owner::selection(t.owner,t.revision)));
 generation=t.generation;MemoryBarrier();InterlockedExchange(&c.acknowledged,static_cast<LONG>(generation));return true;
}
}
