#pragma once
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <tlhelp32.h>
#include <detours.h>
#include <atomic>
#include <cstring>
#include <intrin.h>
#include "effect_core.h"
namespace effect_probe {
using Word=uint32_t;
using Zero=Word(__thiscall*)(void*);
using One=Word(__thiscall*)(void*,Word);
using Three=Word(__thiscall*)(void*,Word,Word,Word);
struct Targets {Zero born=nullptr,retire=nullptr;One draw=nullptr,select=nullptr,finalize=nullptr;Three polygon=nullptr;};
using Sink=void(*)(Kind,Word,Word,const std::array<uint64_t,11>&);
inline Targets native;inline Sink sink=nullptr;inline Registry registry;
inline SRWLOCK identityLock=SRWLOCK_INIT;
inline std::atomic<unsigned> active{0},faults{0},busy{0},unscoped{0};
inline std::atomic<bool> observing{false};inline std::atomic<uint64_t> tokens{0};
inline std::atomic<bool> identityUncertain{false};
inline thread_local Scopes scopes;
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
 if(observing&&s.token)emit(Polygon,s.owner,manager,{s.epoch,s.token,id,count,flags,association(s,manager,id)&&id==word(manager+0x1F24)});
 last.before();const auto result=native.polygon(object,flags,id,count);last.after();return result;
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
#undef EFFECT_CHANGE
 if(error==NO_ERROR)error=DetourTransactionCommit();else DetourTransactionAbort();
 for(unsigned i=0;i<used;++i)CloseHandle(handles[i]);return error;
}
}
