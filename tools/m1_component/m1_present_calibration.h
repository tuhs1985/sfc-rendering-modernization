// Opt-in same-process, nonblocking calibration mailbox. Not replacement sync.
#pragma once
#include <windows.h>
#include <array>
#include <cstring>
namespace sfc_calibration {
constexpr DWORD Offset=32768,Magic=0x314C4143,Version=1,Owners=32,Words=96;
struct Snapshot {
 DWORD magic=Magic,version=Version,bytes=sizeof(Snapshot),frame=0;
 DWORD session[4]{},rows=0,reserved[3]{};
 std::array<std::array<DWORD,Words>,Owners> owner{};
};
struct Mailbox {volatile LONG busy=0,active=0;Snapshot snapshot{};};
static_assert(sizeof(Snapshot)==12336 && Offset+sizeof(Mailbox)<65536);
// A failed try-lock drops evidence, never delays the rendering thread. Readers
// and writers are in the SAME SFC process; no process-shared SRWLOCK is used.
inline bool lock(Mailbox* m){return m&&InterlockedCompareExchange(&m->busy,1,0)==0;}
inline void unlock(Mailbox* m){InterlockedExchange(&m->busy,0);}
inline void begin(Mailbox* m,DWORD frame){
 if(!lock(m))return;
 m->snapshot.frame=frame;m->snapshot.rows=0;m->snapshot.owner={};unlock(m);
}
inline bool offer(Mailbox* m,DWORD index,const std::array<DWORD,Words>& row){
 if(index>=Owners||!lock(m))return false;
 bool ok=m->active&&m->snapshot.frame==row[2]&&row[2]!=0;
 if(ok){auto& old=m->snapshot.owner[index];
  // Different submodels/poses within one owner/frame are explicitly ambiguous,
  // never silently represented by whichever callback happened to run last.
  if(old[1]&&(old[4]!=1||old[1]!=row[1]||old[5]!=row[5]||old[6]!=row[6]||old[7]!=row[7]||
      old[46]!=row[46]||std::memcmp(old.data()+8,row.data()+8,37*sizeof(DWORD))||
      std::memcmp(old.data()+48,row.data()+48,41*sizeof(DWORD))))old[4]=3;
  else {old=row;old[45]=index;}
  m->snapshot.rows=0;for(const auto& r:m->snapshot.owner)if(r[1])++m->snapshot.rows;
 }unlock(m);return ok;
}
inline bool read(Mailbox* m,Snapshot& out){
 if(!lock(m))return false;
 const bool ok=m->active&&m->snapshot.frame&&m->snapshot.rows;
 if(ok)out=m->snapshot;unlock(m);return ok;
}
inline DWORD frame(Mailbox* m){
 if(!lock(m))return 0;const DWORD f=m->active?m->snapshot.frame:0;unlock(m);return f;
}
class Reader {
 HANDLE handle=nullptr;BYTE* view=nullptr;
public:
 Mailbox* mailbox=nullptr;bool requested=false;
 DWORD session[4]{};
 bool prepare(){
  wchar_t name[128]{};const DWORD n=GetEnvironmentVariableW(L"SFC_REMIX_CALIBRATION_SCENE",name,128);
  requested=n!=0;if(!requested)return true;
  constexpr wchar_t prefix[]=L"Local\\SFCBridge_";
  if(n!=wcslen(prefix)+32||wcsncmp(name,prefix,wcslen(prefix)))return false;
  for(DWORD i=static_cast<DWORD>(wcslen(prefix));i<n;++i)
   if(!((name[i]>=L'0'&&name[i]<=L'9')||(name[i]>=L'a'&&name[i]<=L'f')))return false;
  handle=OpenFileMappingW(FILE_MAP_READ|FILE_MAP_WRITE,FALSE,name);if(!handle)return false;
  view=static_cast<BYTE*>(MapViewOfFile(handle,FILE_MAP_READ|FILE_MAP_WRITE,0,0,16*1024*1024));
  if(!view){close();return false;}
  const auto* h=reinterpret_cast<const DWORD*>(view);
  if(h[0]!=0x31424C53||h[1]!=3||h[2]!=16*1024*1024){close();return false;}
  for(unsigned i=0;i<4;++i){wchar_t hex[9]{};std::memcpy(hex,name+wcslen(prefix)+i*8,8*sizeof(wchar_t));
   if(h[4+i]!=wcstoul(hex,nullptr,16)){close();return false;}session[i]=h[4+i];}
  mailbox=reinterpret_cast<Mailbox*>(view+Offset);return true;
 }
 void close(){mailbox=nullptr;if(view){UnmapViewOfFile(view);view=nullptr;}if(handle){CloseHandle(handle);handle=nullptr;}}
};
}
