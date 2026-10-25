// Scalar native metadata only. No mesh/image arrays, callbacks never wait or allocate.
#pragma once
#include <detours.h>
#include <tlhelp32.h>
#include <intrin.h>
#include "survey_native_contract.h"
namespace survey_native {
inline Targets targets;
inline std::atomic<unsigned> active{0},faults{0},busy{0},overflow{0};
inline std::atomic<bool> enabled{false};
inline std::atomic<uint64_t> tokens{0};
inline SRWLOCK listLock=SRWLOCK_INIT;
inline std::array<Word,8192> visited{};
inline std::array<Word,8> banks{};
inline bool read(Word address,void* out,size_t size){
 if(!address||size>256||size>UINT32_MAX-address)return false;
 __try{std::memcpy(out,reinterpret_cast<void*>(address),size);return true;}
 __except(EXCEPTION_EXECUTE_HANDLER){return false;}
}
inline Word word(Word address){Word value=0;if(!read(address,&value,4))++faults;return value;}
struct Active {Active(){++active;}~Active(){--active;}};
struct Error {DWORD entry=GetLastError(),result=entry;void before(){SetLastError(entry);}void after(){result=GetLastError();}~Error(){SetLastError(result);}};
inline void emit(Word kind,Word object,Word caller,const std::array<uint64_t,11>& args){survey_events::trace.emit(kind,object,caller,args,true);}
inline void light(Word manager,Word slot,Word caller,Word kind){
 if(slot>=64){emit(LightControl,manager,caller,{++tokens,slot,0,0,kind,0});return;}
 std::array<Word,16> a{},b{};BYTE on=0,gate=0;
 const auto token=++tokens;
 const bool ok=word(manager)==0x007B8D4C&&read(manager+0x778+slot*64,a.data(),64)&&
  read(manager+0x778+slot*64,b.data(),64)&&a==b&&read(manager+0x1778+slot,&on,1)&&read(manager+0x1EB8,&gate,1);
 emit(LightControl,manager,caller,{token,slot,on,gate,kind,ok});
 if(!ok){++faults;return;}
 for(unsigned offset=0;offset<16;offset+=8){std::array<uint64_t,11> v{token,slot,offset};for(unsigned i=0;i<8;++i)v[3+i]=a[offset+i];emit(LightPart,manager,caller,v);}
}
inline Word __fastcall onSet(void* object,void*,Word slot,Word data){
 Error last;Active hold;last.before();const auto result=targets.set(object,slot,data);last.after();
 if(enabled)light(reinterpret_cast<Word>(object),slot,reinterpret_cast<Word>(_ReturnAddress()),1);return result;
}
inline Word __fastcall onEnable(void* object,void*,Word slot,Word value){
 Error last;Active hold;last.before();const auto result=targets.enable(object,slot,value);last.after();
 if(enabled)light(reinterpret_cast<Word>(object),slot,reinterpret_cast<Word>(_ReturnAddress()),2);return result;
}
inline Word __fastcall onGate(void* object,void*,Word value){
 Error last;Active hold;last.before();const auto result=targets.gate(object,value);last.after();
 if(enabled){BYTE gate=0;const auto p=reinterpret_cast<Word>(object);const bool ok=word(p)==0x007B8D4C&&read(p+0x1EB8,&gate,1);emit(LightControl,p,reinterpret_cast<Word>(_ReturnAddress()),{++tokens,UINT32_MAX,0,gate,3,ok});if(!ok)++faults;}return result;
}
inline void census(Word manager,Word caller){
 if(!TryAcquireSRWLockExclusive(&listLock)){++busy;return;}
 struct Unlock {~Unlock(){ReleaseSRWLockExclusive(&listLock);}} unlock;
 if(word(manager)==0x007B8D4C){
  bool seen=false;unsigned empty=8;for(unsigned i=0;i<8;++i){if(banks[i]==manager)seen=true;if(!banks[i]&&empty==8)empty=i;}
  if(!seen){if(empty==8)++overflow;else{banks[empty]=manager;for(Word slot=0;slot<64;++slot)light(manager,slot,caller,4);}}
 }
 const auto token=++tokens;Word node=word(targets.head);unsigned count=0;visited.fill(0);
 while(node){
  if(count==4096){++overflow;break;}
  unsigned bucket=((node>>4)*2654435761u)&8191u;
  while(visited[bucket]&&visited[bucket]!=node)bucket=(bucket+1)&8191u;
  if(visited[bucket]==node){++overflow;break;}visited[bucket]=node;++count;
  std::array<Word,4> fields{};if(!read(node,fields.data(),16)){++faults;break;}
  const auto draw=word(fields[0]+4);
  // List membership before dispatch, NOT proof the visibility test called draw.
  emit(EffectCensus,node,caller,{token,manager,fields[0],draw,fields[1],fields[3],count});node=fields[1];
 }
 emit(NativeStatus,manager,caller,{token,count,faults.load(),busy.load(),overflow.load(),0});
}
inline Word __cdecl onDispatch(Word manager){
 Error last;Active hold;if(enabled)census(manager,reinterpret_cast<Word>(_ReturnAddress()));
 last.before();const auto result=targets.dispatch(manager);last.after();return result;
}
inline LONG transaction(bool attach){
 LONG error=DetourTransactionBegin();if(error!=NO_ERROR)return error;
 std::array<HANDLE,256> handles{};unsigned used=0;
 auto snapshot=CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD,0);THREADENTRY32 t{};t.dwSize=sizeof(t);
 if(snapshot==INVALID_HANDLE_VALUE){DetourTransactionAbort();return ERROR_INVALID_HANDLE;}
 bool more=Thread32First(snapshot,&t)!=FALSE;if(!more)error=GetLastError();
 while(more&&error==NO_ERROR){
  if(t.th32OwnerProcessID==GetCurrentProcessId()&&t.th32ThreadID!=GetCurrentThreadId()){
   if(used==handles.size()){error=ERROR_BUFFER_OVERFLOW;break;}
   auto h=OpenThread(THREAD_SUSPEND_RESUME|THREAD_GET_CONTEXT|THREAD_SET_CONTEXT|THREAD_QUERY_INFORMATION,FALSE,t.th32ThreadID);
   if(!h){error=GetLastError();break;}handles[used++]=h;error=DetourUpdateThread(h);
  }
  more=Thread32Next(snapshot,&t)!=FALSE;if(!more&&GetLastError()!=ERROR_NO_MORE_FILES)error=GetLastError();
 }
 CloseHandle(snapshot);if(error==NO_ERROR)error=DetourUpdateThread(GetCurrentThread());
#define SURVEY_CHANGE(field,callback) if(error==NO_ERROR)error=attach?DetourAttach(reinterpret_cast<PVOID*>(&targets.field),reinterpret_cast<PVOID>(callback)):DetourDetach(reinterpret_cast<PVOID*>(&targets.field),reinterpret_cast<PVOID>(callback))
 SURVEY_CHANGE(set,onSet);SURVEY_CHANGE(enable,onEnable);SURVEY_CHANGE(gate,onGate);SURVEY_CHANGE(dispatch,onDispatch);
#undef SURVEY_CHANGE
 if(error==NO_ERROR)error=DetourTransactionCommit();else DetourTransactionAbort();
 for(unsigned i=0;i<used;++i)CloseHandle(handles[i]);return error;
}
inline bool configure(){
 const auto module=GetModuleHandleW(nullptr);
 using Factory=BOOL(__cdecl*)(Targets*);
 const auto factory=reinterpret_cast<Factory>(GetProcAddress(module,"SurveyNativeFixture"));
 if(factory){wchar_t path[1024]{};if(!GetModuleFileNameW(nullptr,path,1024))return false;const std::wstring image(path);
  if(image.find(L"\\artifacts\\remix-runtime\\runs\\")==std::wstring::npos||image.substr(image.find_last_of(L"\\/")+1)!=L"d3d11_return_fixture.exe")return false;
  return factory(&targets)&&targets.set&&targets.enable&&targets.gate&&targets.dispatch&&targets.head;}
 if(reinterpret_cast<uintptr_t>(module)!=0x400000)return false;
 struct Check {Word address;const char* bytes;unsigned size;};
 const Check checks[]={{0x006A9AB0,"\x56\x8B\x74\x24\x08\x83\xFE\x40",8},
 {0x006A9C40,"\x8B\x44\x24\x04\x83\xF8\x40",7},{0x006A9C20,"\x8A\x54\x24\x04\x8A\x81\xB8\x1E\x00\x00",10},
 {0x004ECFB3,"\x55\x8B\x6C\x24\x08\x56\x57\x8B\x45\x00",10}};
 for(const auto& c:checks){std::array<char,16> data{};if(!read(c.address,data.data(),c.size)||memcmp(data.data(),c.bytes,c.size))return false;}
 targets={reinterpret_cast<Set>(0x006A9AB0),reinterpret_cast<Set>(0x006A9C40),reinterpret_cast<Gate>(0x006A9C20),reinterpret_cast<Dispatch>(0x004ECFB3),0x0092F470};return true;
}
}
