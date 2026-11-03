// Supervisor-owned, one-shot startup cell in the existing protocol4 mapping.
#pragma once
#include <windows.h>
#include <cstdint>
#include <cstring>
#include <cmath>
namespace startup_ticket {
constexpr DWORD Offset=4096,Magic=0x31545353,Version=1;
enum State:LONG {Empty=0,Writing=1,Published=2,Accepted=3,Cancelled=4,Rejected=5};
struct Activation {uint32_t magic,version,bytes,pid,session[4],model,source;uint64_t mask,cookie;BYTE asset[32];float offset;uint32_t reserved;uint64_t checksum;};
struct alignas(64) Store {
 DWORD magic,version,bytes,pid,session[4],producer;
 volatile LONG state;DWORD host;volatile LONG ready;
 uint64_t readyQpc,publishedQpc;Activation ticket;uint64_t acceptedQpc;BYTE padding[80];
};
static_assert(sizeof(Activation)==104&&sizeof(Store)==256&&offsetof(Store,ticket)==64&&offsetof(Store,acceptedQpc)==168);
static_assert(Offset+sizeof(Store)<=65536);
inline LONG load(volatile LONG* p){return InterlockedCompareExchange(p,0,0);}
inline uint64_t hash(const void* data,size_t bytes){uint64_t v=14695981039346656037ull;auto* p=static_cast<const BYTE*>(data);for(size_t i=0;i<bytes;++i){v^=p[i];v*=1099511628211ull;}return v;}
inline bool valid(const Store& s,const void* session,DWORD pid){return s.magic==Magic&&s.version==Version&&s.bytes==sizeof(Store)&&s.pid==pid&&pid&&s.producer&&!memcmp(s.session,session,16);}
inline bool valid(const Activation& a,const Store& s){bool any=false;for(BYTE b:a.asset)any|=b!=0;return a.magic==0x31524157&&a.version==1&&a.bytes==sizeof(a)&&a.pid==s.pid&&!memcmp(a.session,s.session,16)&&a.model&&a.source&&a.mask&&a.cookie&&any&&!a.reserved&&std::isfinite(a.offset)&&a.offset<=0&&a.offset>=-1e6f&&a.checksum==hash(&a,offsetof(Activation,checksum));}
}
