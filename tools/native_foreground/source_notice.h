#pragma once
#include "../d3d9_proof/replacement_transaction.h"

namespace native_foreground::source_notice {
// Optional independent extension inside the existing replacement reservation.
// No changes to the established version2 ledger or renderer output protocol.
constexpr DWORD Offset=replacement::Offset+8192,Magic=0x31464753;
struct Notice {DWORD frame{},generation{},owner{},revision{},ship{},shield{},thread{},reserved{};};
struct alignas(64) Store {
    DWORD magic{},version{},bytes{},pid{},session[4]{};DWORD reserved[8]{};
    replacement::Cell<Notice> frames[replacement::Frames];
};
static_assert(sizeof(Store)==4160&&Offset+sizeof(Store)<replacement::Offset+replacement::Bytes);
inline bool requested() {
    wchar_t flag[2]{};return GetEnvironmentVariableW(L"SFC_D3D9_NATIVE_FOREGROUND",flag,2)==1&&flag[0]==L'1';
}
inline void initialize(Store& s,const DWORD* session,DWORD pid) {
    memset(&s,0,sizeof(s));s.magic=Magic;s.version=1;s.bytes=sizeof(s);s.pid=pid;memcpy(s.session,session,16);
}
inline bool valid(const Store& s,const DWORD* session,DWORD pid) {
    return s.magic==Magic&&s.version==1&&s.bytes==sizeof(s)&&s.pid==pid&&memcmp(s.session,session,16)==0;
}
inline void offer(Store& s,const replacement::Store& ledger,DWORD frame,DWORD ship,DWORD shield,DWORD owner,DWORD thread) {
    replacement::Control c{};if(!owner||!ship||!frame||!replacement::read(ledger.control,c)||c.owner!=owner||!c.revision)return;
    Notice n{frame,c.generation,owner,c.revision,ship,shield,thread,0};replacement::write(s.frames[frame%replacement::Frames],n);
}
inline bool sample(const Store& s,DWORD frame,Notice& n) {
    return replacement::read(s.frames[frame%replacement::Frames],n)&&n.frame==frame&&!n.reserved;
}
} // namespace native_foreground::source_notice
