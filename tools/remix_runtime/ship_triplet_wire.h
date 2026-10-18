// Opt-in coherent GPU lease;not the old diagnostic-color frame contract.
#pragma once
#include "return_wire.h"
#include <cstring>
namespace ship_triplet {
constexpr uint32_t Magic=0x33544653,Version=3,Offset=512;
constexpr uint32_t BufferedVersion=4,BufferedMode=2;
enum Lease:LONG {Idle,Rendering,Ready,Reading};
struct alignas(8) Key {
 uint32_t session[4]{},owner=0,revision=0,frame=0,objectId=0;
 uint64_t pose=0,camera=0;
 uint32_t width=0,height=0,viewport[4]{},resourceEpoch=0,depthConvention=0;
 unsigned char asset[32]{};
 uint32_t sourceSession[4]{},sourcePid=0,reserved=0;
 // Explicit diagnostic world translation. Zero mode means an unmodified ship.
 uint32_t diagnosticMode=0;float worldOffset[3]{};
};
static_assert(sizeof(Key)==152);
struct alignas(8) Wire {
 uint32_t magic=Magic,version=Version,bytes=sizeof(Wire),creator=0;
 uint32_t width=0,height=0,formats[3]{87,41,41},resourceEpoch=0;
 uint32_t adapterLow=0,adapterHigh=0;
 uint32_t session[4]{};
 uint64_t handles[3]{},frequency=0,publishedAt=0;
 volatile LONG guard=0,ready=0,lease=Idle,sequence=0,ack=0,stop=0,error=0,consumerPid=0;
 Key requested{},published{};
 uint64_t expected[3]{},consumed[3]{};
 volatile LONG accepted=0,rejected=0;
};
static_assert(sizeof(Wire)==496 && Offset+sizeof(Wire)<4096);
struct Resources {uint32_t width,height,formats[3],epoch,adapterLow,adapterHigh;uint64_t handles[3];};
static_assert(sizeof(Resources)==56);
inline Resources describe(const Wire& s){Resources r{s.width,s.height,{s.formats[0],s.formats[1],s.formats[2]},s.resourceEpoch,s.adapterLow,s.adapterHigh,{s.handles[0],s.handles[1],s.handles[2]}};return r;}
inline LONG load(volatile LONG& v){return return_path::read(v);}
inline void store(volatile LONG& v,LONG n){return_path::write(v,n);}
inline uint64_t hash(const void* raw,size_t size){auto* p=static_cast<const unsigned char*>(raw);uint64_t h=14695981039346656037ull;
 for(size_t i=0;i<size;++i){h^=p[i];h*=1099511628211ull;}return h;}
inline bool same(const Key& a,const Key& b){return std::memcmp(&a,&b,sizeof(Key))==0;}
inline bool dimensions(uint32_t w,uint32_t h){return w&&h&&w<=1920&&h<=1080&&uint64_t(w)*h*4*4<=128*1024*1024;}
inline bool validKey(const Key& k){
 bool session=false,sourceSession=false,asset=false;for(auto x:k.session)session|=x!=0;for(auto x:k.sourceSession)sourceSession|=x!=0;for(auto x:k.asset)asset|=x!=0;
 if(k.diagnosticMode>BufferedMode)return false;
 bool displaced=false;for(auto x:k.worldOffset){if(!std::isfinite(x)||std::abs(x)>1e6f)return false;displaced|=x!=0;}
 if(displaced!=(k.diagnosticMode!=0))return false;
 return session&&sourceSession&&asset&&k.sourcePid&&!k.reserved&&k.owner&&k.revision&&k.frame&&k.objectId&&k.pose&&k.camera&&
  dimensions(k.width,k.height)&&k.resourceEpoch&&k.depthConvention==1&&
  k.viewport[2]&&k.viewport[3]&&k.viewport[0]<=1920&&k.viewport[1]<=1080&&
  uint64_t(k.viewport[0])+k.viewport[2]<=1920&&uint64_t(k.viewport[1])+k.viewport[3]<=1080;
}
inline bool valid(const Wire& s){return s.magic==Magic&&(s.version==Version||s.version==BufferedVersion)&&s.bytes==sizeof(Wire)&&s.creator&&
 dimensions(s.width,s.height)&&s.formats[0]==87&&s.formats[1]==41&&s.formats[2]==41&&s.frequency&&s.resourceEpoch&&
 s.handles[0]&&s.handles[1]&&s.handles[2]&&s.handles[0]<=UINT32_MAX&&s.handles[1]<=UINT32_MAX&&s.handles[2]<=UINT32_MAX&&
 s.handles[0]!=s.handles[1]&&s.handles[1]!=s.handles[2]&&s.handles[0]!=s.handles[2];}
struct Lock {
 Wire& s;bool held;explicit Lock(Wire& w):s(w),held(InterlockedCompareExchange(&w.guard,1,0)==0){}
 ~Lock(){if(held)store(s.guard,0);}
};
inline bool policyMatches(const Wire& s,const Key& k){return (s.version==BufferedVersion)==(k.diagnosticMode==BufferedMode);}
inline bool request(Wire& s,const Key& k){Lock l(s);if(!l.held||!valid(s)||!validKey(k)||load(s.stop)||load(s.error))return false;
 if(!policyMatches(s,k)||k.width!=s.width||k.height!=s.height||k.resourceEpoch!=s.resourceEpoch||std::memcmp(k.session,s.session,16))return false;
 s.requested=k;return true;}
inline bool begin(Wire& s,Key& k){Lock l(s);if(!l.held||!valid(s)||!load(s.ready)||load(s.stop)||load(s.error)||
 load(s.lease)!=Idle||load(s.sequence)!=load(s.ack)||load(s.sequence)<0||load(s.sequence)==LONG_MAX||!validKey(s.requested)||!policyMatches(s,s.requested)||std::memcmp(s.requested.session,s.session,16))return false;
 k=s.requested;store(s.lease,Rendering);return true;}
// Call ONLY after producer GPU EVENT completes all three output copies.
enum class Publication {Busy,Invalid,Cancelled,Published};
inline Publication tryPublish(Wire& s,const Key& k,const uint64_t (&hashes)[3],uint64_t now){Lock l(s);
 if(!l.held)return Publication::Busy;
 if(!valid(s)||load(s.lease)!=Rendering||!policyMatches(s,k))return Publication::Invalid;
 if(load(s.stop)||load(s.error)||!load(s.ready)||!same(k,s.requested)||k.resourceEpoch!=s.resourceEpoch){store(s.lease,Idle);return Publication::Cancelled;}
 s.published=k;std::memcpy(s.expected,hashes,sizeof(hashes));s.publishedAt=now;
 InterlockedIncrement(&s.sequence);store(s.lease,Ready);return Publication::Published;
}
inline bool publish(Wire& s,const Key& k,const uint64_t (&hashes)[3],uint64_t now){return tryPublish(s,k,hashes,now)==Publication::Published;}
// Producer-only completion: a busy metadata guard is NOT a cancelled GPU result.
// Retain both completed surfaces and pending ownership until a terminal outcome.
inline Publication publishCompleted(Wire& s,const Key& k,const uint64_t (&hashes)[3],uint64_t now,bool& pending){
 const auto result=tryPublish(s,k,hashes,now);
 if(result==Publication::Published||result==Publication::Cancelled)pending=false;
 return result;
}
inline bool claim(Wire& s,const Key& current,uint64_t now,const Resources* pinned=nullptr){Lock l(s);if(!l.held||!valid(s)||load(s.lease)!=Ready)return false;
 const auto resources=describe(s);
 if(load(s.stop)||load(s.error)||!load(s.ready)||!validKey(current)||!policyMatches(s,current)||!same(current,s.requested)||!same(current,s.published)||
    std::memcmp(current.session,s.session,16)||current.width!=s.width||current.height!=s.height||
    (pinned&&std::memcmp(pinned,&resources,sizeof(Resources)))||current.resourceEpoch!=s.resourceEpoch||!return_path::fresh(s.publishedAt,now,s.frequency)){
  InterlockedIncrement(&s.rejected);store(s.ack,load(s.sequence));store(s.lease,Idle);return false;}
 store(s.lease,Reading);return true;
}
// Consumer GPU work must be complete before acknowledging. Metadata alone is
// never a GPU fence;this explicit parameter is only exercised by the GPU reader.
inline bool finish(Wire& s,LONG sequence,bool gpuComplete){Lock l(s);
 if(!l.held||!gpuComplete||load(s.lease)!=Reading||sequence!=load(s.sequence)||sequence<=load(s.ack))return false;
 store(s.ack,sequence);store(s.lease,Idle);InterlockedIncrement(&s.accepted);return true;
}
// Explicit delayed-additive policy ONLY. Captured pose/camera/frame remain in
// published key;they are never relabelled as current or used for suppression.
inline bool sameIdentity(Key a,Key b){a.frame=b.frame=1;a.pose=b.pose=1;a.camera=b.camera=1;return same(a,b);}
inline bool sourceRecent(uint64_t observed,uint64_t now,uint64_t frequency){return observed&&frequency>=10&&now>=observed&&now-observed<=frequency/10;}
inline bool claimBuffered(Wire& s,const Key& current,uint64_t now,const Resources* pinned){
 Key completed{};{Lock lock(s);if(!lock.held||s.version!=BufferedVersion||load(s.lease)!=Ready)return false;completed=s.published;}
 if(current.diagnosticMode!=BufferedMode||current.frame<completed.frame||!sameIdentity(current,completed)||!sourceRecent(s.publishedAt,now,s.frequency)){
  // Deliberately invalid key ACKs/discards the completed output,never displays it.
  claim(s,Key{},now,pinned);return false;
 }
 return claim(s,completed,now,pinned);
}
inline uint64_t canonicalHandle(HANDLE h){const uint64_t v=reinterpret_cast<uintptr_t>(h),hi=v>>32;
 if(hi&&hi!=0xffffffffull)throw std::runtime_error("unsupported KMT handle width");return static_cast<uint32_t>(v);}
inline void sessionKey(const std::wstring& name,Key& k){GUID guid{};
 if(FAILED(CLSIDFromString(name.c_str()+wcslen(return_path::Prefix),&guid)))throw std::runtime_error("triplet GUID");std::memcpy(k.session,&guid,16);}
}
