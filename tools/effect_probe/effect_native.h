#pragma once
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <tlhelp32.h>
#include <detours.h>
#include <d3d.h>
#include <atomic>
#include <cstring>
#include <intrin.h>
#include "effect_core.h"
#include "retained_frame_join.h"
namespace effect_probe {
using Word=uint32_t;
using Zero=Word(__thiscall*)(void*);
using One=Word(__thiscall*)(void*,Word);
using Three=Word(__thiscall*)(void*,Word,Word,Word);
using Four=Word(__thiscall*)(void*,Word,Word,Word,Word);
using Flush=void(__thiscall*)(void*);
struct Targets {Zero born=nullptr,retire=nullptr;One draw=nullptr,select=nullptr,finalize=nullptr;Three polygon=nullptr;Four append=nullptr;Flush flush=nullptr;Zero present=nullptr,sceneBegin=nullptr;};
using Sink=void(*)(Kind,Word,Word,const std::array<uint64_t,11>&);
inline Targets native;inline Sink sink=nullptr;inline Registry registry;
inline SRWLOCK identityLock=SRWLOCK_INIT;
inline std::atomic<unsigned> active{0},faults{0},busy{0},unscoped{0};
inline std::atomic<bool> observing{false};inline std::atomic<uint64_t> tokens{0};
inline std::atomic<bool> identityUncertain{false};
inline bool quadObservation=false;
inline bool batchObservation=false;
inline bool batchFixture=false;
inline BYTE* joinView=nullptr;
inline DWORD joinSession[4]{};
inline volatile LONG* armedFlag=nullptr;
inline std::atomic<unsigned> quadAttempts{0};
inline std::atomic<bool> batchFinished{false};
constexpr unsigned QuadLimit=16;
inline Word quadReturnSite=0x006ACE8F;
inline thread_local uint64_t lastQuadScope=0;
inline thread_local Scopes scopes;
struct BatchMarker {
 Scope scope{};
 Word sample=0,resource=0,first=0,count=0;
 uint64_t scene=0;
};
inline thread_local FrameStamp joinAtSubmit,joinAtFlush;
inline FrameStamp joinPublished,joinFlushed,joinPresented;
inline std::atomic<bool> joinReady{false};
inline bool current_join(Word manager,FrameStamp& stamp){
 if(!joinView)return false;
 auto& owner=reinterpret_cast<live_owner::Store*>(joinView+live_owner::Offset)->header;
 auto& slot=*reinterpret_cast<StampSlot*>(joinView+StampOffset);
 return live_owner::header_valid(owner,joinSession)&&!frame_ingress::state(&owner.stopped)&&
    read_stamp(slot,stamp)&&stamp.pid==GetCurrentProcessId()&&stamp.manager==manager&&stamp.thread==GetCurrentThreadId()&&
    live_owner::same_session(stamp.session,joinSession)&&stamp.frame==static_cast<DWORD>(frame_ingress::state(&owner.frame));
}
inline bool stamp_now(FrameStamp& stamp){
 LARGE_INTEGER now{};
 if(!QueryPerformanceCounter(&now))return false;
 stamp.observed=now.QuadPart;
 return true;
}
inline thread_local BatchMarker inPolygon,pendingBatch;
inline thread_local BatchMarker awaitingPresent;
inline thread_local uint64_t awaitingOrder=0,presentOrder=0;
inline thread_local uint64_t sceneOrdinal=0;
inline thread_local Word sceneManager=0;
inline thread_local bool inAppend=false,appendFlushed=false;
inline std::atomic<uint64_t> flushOrder{0};
constexpr Word BatchOffset=0x1F4C,TriangleCountOffset=0x3C00,VertexCountOffset=0x3BFC;
inline Word concreteVtable=0x007AA050,registryAddress=0x008CC620;
inline bool read(Word address,void* target,size_t n){
 if(!address||n>4096||n>UINT32_MAX-address)return false;
 __try{std::memcpy(target,reinterpret_cast<void*>(address),n);return true;}
 __except(EXCEPTION_EXECUTE_HANDLER){return false;}
}
inline Word word(Word address){Word value=0;if(!read(address,&value,4))++faults;return value;}
inline void emit(Kind kind,Word object,Word manager,const std::array<uint64_t,11>& args={}){if(sink)sink(kind,object,manager,args);}
struct Active {Active(){++active;}~Active(){--active;}};
struct NativeError {
 DWORD entry=GetLastError(),result=entry;
 void before(){SetLastError(entry);}void after(){result=GetLastError();}~NativeError(){SetLastError(result);}
};
struct ScopeExit {
 Scope value;bool normal=false;
 ~ScopeExit(){if(!normal)emit(Fault,value.owner,value.manager,{value.epoch,value.token,2});scopes.pop();}
};
inline Identity identity(Word object,bool born=false){
 if(identityUncertain)return {};
 if(!TryAcquireSRWLockExclusive(&identityLock)){++busy;if(born)identityUncertain=true;return {};}
 auto* found=registry.find(object);Identity result=born?registry.birth(object):found?*found:registry.birth(object,true);
 ReleaseSRWLockExclusive(&identityLock);if(born&&!result.epoch)identityUncertain=true;return result;
}
inline Word __fastcall onBorn(void* object,void*){
 NativeError last;Active hold;last.before();const auto result=native.born(object);last.after();
 if(observing){const auto p=reinterpret_cast<Word>(object);const auto id=identity(p,true);emit(Born,p,0,{id.epoch,id.late});}
 return result;
}
inline Word __fastcall onRetire(void* object,void*){
 NativeError last;Active hold;const auto p=reinterpret_cast<Word>(object);
 if(observing){
  if(TryAcquireSRWLockExclusive(&identityLock)){const auto id=registry.retire(p);ReleaseSRWLockExclusive(&identityLock);emit(Retired,p,0,{id.epoch});}
  else{++busy;identityUncertain=true;}
 }
 last.before();const auto result=native.retire(object);last.after();return result;
}
inline Word __fastcall onDraw(void* object,void*,Word manager){
 NativeError last;Active hold;const auto p=reinterpret_cast<Word>(object);
 if(!observing||word(p)!=concreteVtable){last.before();const auto result=native.draw(object,manager);last.after();return result;}
 const auto id=identity(p);const auto token=++tokens;const bool pushed=scopes.push({p,id.epoch,manager,token});
 if(!pushed)emit(Overflow,p,manager,{token});
 ScopeExit exit{{p,id.epoch,manager,token}};
 std::array<Word,10> fields{};const bool valid=read(p+0x20,fields.data(),40);
 emit(Enter,p,manager,{id.epoch,token,id.late,valid,fields[0],fields[1],fields[2],fields[3],fields[4],fields[5],word(p+0x44)});
 emit(Selected,p,manager,{id.epoch,token,0,0,word(p+0x350),fields[7],fields[6],reinterpret_cast<Word>(_ReturnAddress()),concreteVtable}); // entry flags/model/caller,not an image selection
 last.before();const auto result=native.draw(object,manager);last.after();
 emit(Leave,p,manager,{id.epoch,token,result});exit.normal=true;return result;
}
inline Word __fastcall onSelect(void* object,void*,Word resource){
 NativeError last;Active hold;const auto s=scopes.current();const auto manager=reinterpret_cast<Word>(object);
 last.before();const auto result=native.select(object,resource);last.after();
 if(observing&&s.token)emit(Selected,s.owner,manager,{s.epoch,s.token,1,resource,word(manager+0x1F24),s.manager==manager});
 return result;
}
inline void resourceRequest(Word manager,Word id,Scope s){
 if(!association(s,manager,id))return;
 const Word reg=word(registryAddress),object=reg?word(reg+12+(id-1)*20):0;
 const Word entry=word(manager+0x3F60+(id-1)*4),surface=entry?word(entry+4):0;
 emit(Resource,s.owner,manager,{s.epoch,s.token,id,reg,object,entry,surface});
}
inline Word __fastcall onFinalize(void* object,void*,Word end){
 NativeError last;Active hold;const auto s=scopes.current();const auto manager=reinterpret_cast<Word>(object);
 if(observing){
  if(s.token){const auto id=word(manager+0x1F24);emit(Finalized,s.owner,manager,{s.epoch,s.token,id,word(manager+0x1EEC),word(manager+0x1EF0),end,association(s,manager,id)});resourceRequest(manager,id,s);}
  else ++unscoped;
 }
 last.before();const auto result=native.finalize(object,end);last.after();return result;
}
inline Word __fastcall onPolygon(void* object,void*,Word flags,Word id,Word count){
 NativeError last;Active hold;const auto s=scopes.current();const auto manager=reinterpret_cast<Word>(object);
 unsigned sample=0;
 FrameStamp candidate{};
 if(observing&&s.token){
  const bool qualified=association(s,manager,id)&&id==word(manager+0x1F24);
  const auto limit=batchObservation?1u:QuadLimit;
  const bool sceneMatched=!batchObservation||(joinView?current_join(manager,candidate):sceneManager==manager);
  const bool selected=quadObservation&&qualified&&count==4&&s.token!=lastQuadScope&&
      sceneMatched&&
      (!armedFlag||InterlockedCompareExchange(armedFlag,0,0))&&
      (!quadReturnSite||reinterpret_cast<Word>(_ReturnAddress())==quadReturnSite)&&quadAttempts.load()<limit;
  if(!quadObservation||selected)emit(Polygon,s.owner,manager,{s.epoch,s.token,id,count,flags,qualified});
  if(selected){
   {
    Word base=0,used=0;std::array<uint16_t,4> indices{};
    std::array<std::array<uint64_t,11>,4> rows{};
    bool good=read(manager+4,&base,4)&&read(manager+0x1EF0,&used,4)&&used>=4&&used<=336&&
              read(manager+0x14,indices.data(),sizeof(indices));
    for(unsigned i=0;good&&i<rows.size();++i){
     rows[i][1]=s.token;rows[i][2]=i;
     const auto offset=Word(indices[i])*64;
     good=indices[i]<used&&base&&base<=UINT32_MAX-offset&&read(base+offset,rows[i].data()+3,64);
    }
    if(good){
     // The pinned main variant uses the rightmost atlas column. The trail
     // samples use a different strip. Compare raw positive float encodings.
     for(const auto& row:rows){
      Word u=0;std::memcpy(&u,reinterpret_cast<const BYTE*>(row.data()+3)+0x2C,4);
      if(batchObservation&&u!=0x3F400000&&u!=0x3F7F0000){good=false;break;}
     }
     if(good){
      auto seen=quadAttempts.load();
      if(seen<limit&&quadAttempts.compare_exchange_strong(seen,seen+1)){
       sample=seen+1;lastQuadScope=s.token;
       if(joinView)joinAtSubmit=candidate;
       for(auto& row:rows){row[0]=sample;emit(QuadCorner,s.owner,manager,row);}
      }
     }
    }
   }
  }
 }
 struct Restore {BatchMarker saved;~Restore(){inPolygon=saved;}} restore{inPolygon};
 inPolygon=sample&&batchObservation?BatchMarker{s,sample,id,0,0,joinView?joinAtSubmit.frame:sceneOrdinal}:BatchMarker{};
 last.before();const auto result=native.polygon(object,flags,id,count);last.after();
 if(sample)emit(QuadResult,s.owner,manager,{sample,s.token,s.epoch,id,flags,result});
 return result;
}
inline Word __fastcall onAppend(void* object,void*,Word corners,Word second,Word id,Word flip){
 NativeError last;Active hold;
 const auto manager=reinterpret_cast<Word>(object);
 const auto sample=inPolygon;
 if(!observing||!sample.sample||sample.scope.manager!=manager||sample.resource!=id||corners<3||corners>16||inAppend){
  last.before();const auto result=native.append(object,corners,second,id,flip);last.after();return result;
 }
 const auto before=word(manager+TriangleCountOffset);
 struct Reset {~Reset(){inAppend=false;appendFlushed=false;}} reset;
 inAppend=true;appendFlushed=false;
 last.before();const auto result=native.append(object,corners,second,id,flip);last.after();
 const auto after=word(manager+TriangleCountOffset),added=corners-2;
 const auto first=appendFlushed?0:before;
 if(static_cast<BYTE>(result)&&after<=72&&after==first+added&&!pendingBatch.sample){
  pendingBatch={sample.scope,sample.sample,id,first*3,added*3,sample.scene};
  emit(BatchSpan,sample.scope.owner,manager,{sample.sample,sample.scope.token,sample.scope.epoch,id,first*3,added*3,corners});
 }
 return result;
}
inline void captureBatchState(BatchMarker sample, Word manager, uint64_t order, Word device){
 if(batchFixture)return;
 auto* nativeDevice=reinterpret_cast<IDirect3DDevice3*>(device);
 constexpr D3DRENDERSTATETYPE states[]{
  D3DRENDERSTATE_ALPHABLENDENABLE,D3DRENDERSTATE_SRCBLEND,D3DRENDERSTATE_DESTBLEND,
  D3DRENDERSTATE_ZENABLE,D3DRENDERSTATE_ZWRITEENABLE,D3DRENDERSTATE_ZFUNC,D3DRENDERSTATE_CULLMODE,
  D3DRENDERSTATE_ALPHATESTENABLE,D3DRENDERSTATE_ALPHAREF,D3DRENDERSTATE_ALPHAFUNC,
  D3DRENDERSTATE_COLORKEYENABLE
 };
 for(auto state:states){
  DWORD value=0;
  const auto hr=nativeDevice->GetRenderState(state,&value);
  emit(BatchState,sample.scope.owner,manager,{sample.sample,sample.scope.token,order,0,static_cast<Word>(state),value,static_cast<Word>(hr)});
 }
 constexpr D3DTEXTURESTAGESTATETYPE stageStates[]{
  D3DTSS_COLOROP,D3DTSS_COLORARG1,D3DTSS_COLORARG2,D3DTSS_ALPHAOP,D3DTSS_ALPHAARG1,D3DTSS_ALPHAARG2,
  D3DTSS_ADDRESSU,D3DTSS_ADDRESSV,D3DTSS_MAGFILTER,D3DTSS_MINFILTER,D3DTSS_MIPFILTER
 };
 for(auto state:stageStates){
  DWORD value=0;
  const auto hr=nativeDevice->GetTextureStageState(0,state,&value);
  emit(BatchState,sample.scope.owner,manager,{sample.sample,sample.scope.token,order,1,static_cast<Word>(state),value,static_cast<Word>(hr)});
 }
 IDirect3DTexture2* texture=nullptr;
 IDirectDrawSurface4* target=nullptr;
 const auto texResult=nativeDevice->GetTexture(0,&texture);
 const auto targetResult=nativeDevice->GetRenderTarget(&target);
 emit(BatchState,sample.scope.owner,manager,{sample.sample,sample.scope.token,order,2,0,
  reinterpret_cast<Word>(texture),static_cast<Word>(texResult),reinterpret_cast<Word>(target),static_cast<Word>(targetResult),
  word(manager+0x3F5C)});
 if(texture)texture->Release();
 if(target)target->Release();
}
inline void __fastcall onFlush(void* object,void*){
 NativeError last;Active hold;
 const auto base=reinterpret_cast<Word>(object),manager=base-BatchOffset;
 const auto order=++flushOrder;
 if(inAppend&&inPolygon.scope.manager==manager)appendFlushed=true;
 if(observing&&pendingBatch.sample&&pendingBatch.scope.manager==manager){
  const auto sample=pendingBatch;pendingBatch={};
  const auto vertices=word(manager+VertexCountOffset),triangles=word(manager+TriangleCountOffset);
  const auto topology=word(manager+0x3C08),device=word(manager+0x3C0C);
  const bool sameScene=joinView?(current_join(manager,joinAtFlush)&&same_frame(joinAtSubmit,joinAtFlush)&&stamp_now(joinAtFlush)):
      sample.scene==sceneOrdinal&&sceneManager==manager;
  std::array<uint16_t,42> indices{};
  std::array<std::array<uint64_t,4>,42> rows{};
  bool good=sample.scene&&sameScene&&topology==4&&device&&triangles<=72&&sample.first+sample.count<=triangles*3&&
      read(manager+0x3A4C+sample.first*2,indices.data(),sample.count*2);
  for(Word i=0;good&&i<sample.count;++i){
   good=indices[i]<vertices&&indices[i]<216&&read(base+indices[i]*32,rows[i].data(),32);
  }
  if(good){
   for(Word i=0;i<sample.count;++i){
    emit(BatchIndices,sample.scope.owner,manager,{sample.sample,sample.scope.token,order,i,indices[i]});
    emit(BatchVertex,sample.scope.owner,manager,{sample.sample,sample.scope.token,order,i,rows[i][0],rows[i][1],rows[i][2],rows[i][3]});
   }
   emit(BatchFlush,sample.scope.owner,manager,{sample.sample,sample.scope.token,order,device,vertices,triangles,topology,sample.scene});
   captureBatchState(sample,manager,order,device);
   awaitingPresent=sample;awaitingOrder=order;
  }
 }
 last.before();native.flush(object);last.after();
}
inline Word __fastcall onSceneBegin(void* object,void*){
 NativeError last;Active hold;
 if(observing){++sceneOrdinal;sceneManager=0;pendingBatch={};awaitingPresent={};}
 const auto ordinal=sceneOrdinal;
 last.before();const auto result=native.sceneBegin(object);last.after();
 if(observing&&sceneOrdinal==ordinal&&static_cast<BYTE>(result)==1)
  sceneManager=reinterpret_cast<Word>(object);
 return result;
}
inline Word __fastcall onPresent(void* object,void*){
 NativeError last;Active hold;
 const auto manager=reinterpret_cast<Word>(object);
 const auto sequence=++presentOrder;
 last.before();const auto result=native.present(object);last.after();
 FrameStamp current{};
 const bool sameScene=joinView?(awaitingPresent.sample&&current_join(manager,current)&&same_frame(joinAtFlush,current)):
     awaitingPresent.scene==sceneOrdinal&&sceneManager==manager;
 if(observing&&awaitingPresent.sample&&awaitingPresent.scope.manager==manager&&
    sameScene){
  const auto sample=awaitingPresent;awaitingPresent={};
  emit(BatchPresent,sample.scope.owner,manager,{sample.sample,sample.scope.token,awaitingOrder,sequence,static_cast<BYTE>(result),sample.scene});
  if(joinView&&static_cast<BYTE>(result)==1&&stamp_now(current)){
   joinPublished=joinAtSubmit;joinFlushed=joinAtFlush;joinPresented=current;
   joinReady.store(true,std::memory_order_release);
  }
  if(!batchFixture)batchFinished=true;
 }
 if(sceneManager==manager)sceneManager=0;
 return result;
}
// Detours enrolls/suspends other threads and relocates their IPs at transaction
// commit. Do not hand-copy relative instructions or patch active code piecemeal.
inline LONG transaction(bool attach){
 LONG error=DetourTransactionBegin();if(error!=NO_ERROR)return error;
 std::array<HANDLE,256> handles{};unsigned used=0;
 auto snapshot=CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD,0);THREADENTRY32 t{};t.dwSize=sizeof(t);
 if(snapshot==INVALID_HANDLE_VALUE){DetourTransactionAbort();return ERROR_INVALID_HANDLE;}
 bool more=Thread32First(snapshot,&t)!=FALSE;
 if(!more)error=GetLastError();
 while(more&&error==NO_ERROR){
  if(t.th32OwnerProcessID==GetCurrentProcessId()&&t.th32ThreadID!=GetCurrentThreadId()){
   if(used==handles.size()){error=ERROR_BUFFER_OVERFLOW;break;}
   auto h=OpenThread(THREAD_SUSPEND_RESUME|THREAD_GET_CONTEXT|THREAD_SET_CONTEXT|THREAD_QUERY_INFORMATION,FALSE,t.th32ThreadID);
   if(!h){error=GetLastError();break;}handles[used++]=h;error=DetourUpdateThread(h);
  }
  more=Thread32Next(snapshot,&t)!=FALSE;
  if(!more&&GetLastError()!=ERROR_NO_MORE_FILES)error=GetLastError();
 }
 CloseHandle(snapshot);
 if(error==NO_ERROR)error=DetourUpdateThread(GetCurrentThread());
#define EFFECT_CHANGE(field,callback) if(error==NO_ERROR)error=attach?DetourAttach(reinterpret_cast<PVOID*>(&native.field),reinterpret_cast<PVOID>(callback)):DetourDetach(reinterpret_cast<PVOID*>(&native.field),reinterpret_cast<PVOID>(callback))
 EFFECT_CHANGE(born,onBorn);EFFECT_CHANGE(retire,onRetire);EFFECT_CHANGE(draw,onDraw);
 EFFECT_CHANGE(select,onSelect);EFFECT_CHANGE(finalize,onFinalize);EFFECT_CHANGE(polygon,onPolygon);
 if(native.append){EFFECT_CHANGE(append,onAppend);}
 if(native.flush){EFFECT_CHANGE(flush,onFlush);}
 if(native.present){EFFECT_CHANGE(present,onPresent);}
 if(native.sceneBegin){EFFECT_CHANGE(sceneBegin,onSceneBegin);}
#undef EFFECT_CHANGE
 if(error==NO_ERROR)error=DetourTransactionCommit();else DetourTransactionAbort();
 for(unsigned i=0;i<used;++i)CloseHandle(handles[i]);return error;
}
}
