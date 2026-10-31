#pragma once
#include "../d3d9_proof/replacement_transaction.h"

namespace native_insertion {
// Metadata only, within the existing current-user/session mapping reservation.
constexpr DWORD Offset=replacement::Offset+16384,Magic=0x3142494e,Capacity=256;
enum Kind:DWORD {FrameBegin=1,ModelBegin,ModelEnd,SourcePublished,NativeDraw,Present,OutputDiscarded};
enum Phase:DWORD {BeforeSelected=0,InsideSelected=1,AfterSelected=2,OtherModel=3};
struct alignas(64) Header {
    DWORD magic{},version{},bytes{},pid{},session[4]{};
    volatile LONG written{},read{},dropped{},wrongThread{},stopped{},error{},thread{},phase{};
    DWORD frame{},owner{},revision{},model{},source{},manager{},sourceFrame{},draws{};
    uint64_t sourceQpc{},frequency{};DWORD outputSamples{},reserved[3]{};
};
struct alignas(8) Event {
    DWORD kind{},frame{},owner{},revision{},phase{},model{},source{},manager{};
    uint64_t qpc{},target{},depth{},outputQpc{},sourceQpc{};
    DWORD width{},height{},targetFormat{},depthFormat{},viewFormat{},samples{};
    DWORD depthEnabled{},depthWrite{},depthFunc{},outputFrame{},outputSequence{},flags{};
    DWORD caller{};volatile LONG committed{};
};
struct Store {Header header{};Event events[Capacity]{};};
static_assert(sizeof(Header)==128&&sizeof(Event)==128&&sizeof(Store)==32896);
static_assert(Offset+sizeof(Store)<replacement::Offset+replacement::Bytes);
inline bool requested(){wchar_t flag[2]{};return GetEnvironmentVariableW(L"SFC_NATIVE_INSERTION_OBSERVE",flag,2)==1&&flag[0]==L'1';}
// Native capture and private output publication still require this handshake,
// even though observation must never construct the replacement presenter.
inline bool preparePassiveLedger(BYTE* base,const DWORD* session,DWORD pid){
    auto* ledger=reinterpret_cast<replacement::Store*>(base+replacement::Offset);
    if(!ledger->magic)replacement::initialize(*ledger,session,pid);
    replacement::Control c{};
    return replacement::valid(ledger,session,pid)&&replacement::read(ledger->control,c)&&
        c.mode==replacement::Priming&&!ledger->suppressed&&!ledger->committed;
}
inline bool valid(const Header& h,const DWORD* session,DWORD pid){return h.magic==Magic&&h.version==1&&h.bytes==sizeof(Store)&&h.pid==pid&&
    !memcmp(h.session,session,16)&&h.frequency;}
inline void initialize(Store& s,const DWORD* session,DWORD pid){
    memset(&s,0,sizeof(s));s.header.version=1;s.header.bytes=sizeof(s);s.header.pid=pid;
    memcpy(s.header.session,session,16);LARGE_INTEGER f{};QueryPerformanceFrequency(&f);s.header.frequency=f.QuadPart;
    MemoryBarrier();InterlockedExchange(reinterpret_cast<volatile LONG*>(&s.header.magic),Magic);
}
inline bool thread(Header& h){const LONG id=static_cast<LONG>(GetCurrentThreadId());
    const auto old=InterlockedCompareExchange(&h.thread,id,0);if(old&&old!=id){InterlockedIncrement(&h.wrongThread);return false;}return true;}
inline Event context(const Header& h,DWORD kind){Event e{};e.kind=kind;e.frame=h.frame;e.owner=h.owner;e.revision=h.revision;
    e.phase=static_cast<DWORD>(h.phase);e.model=h.model;e.source=h.source;e.manager=h.manager;e.sourceQpc=h.sourceQpc;return e;}
inline bool publish(Store& s,const Event& e){auto& h=s.header;
    if(h.stopped||!thread(h)||!e.frame||!e.owner||!e.revision)return false;
    const auto write=static_cast<DWORD>(h.written),read=static_cast<DWORD>(InterlockedCompareExchange(&h.read,0,0));
    if(write-read>=Capacity){InterlockedIncrement(&h.dropped);return false;}
    LARGE_INTEGER now{};if(!QueryPerformanceCounter(&now)){InterlockedIncrement(&h.error);return false;}
    auto& slot=s.events[write%Capacity];memcpy(&slot,&e,offsetof(Event,committed));slot.qpc=now.QuadPart;
    InterlockedExchange(&slot.committed,static_cast<LONG>(write+1));InterlockedExchange(&h.written,static_cast<LONG>(write+1));return true;
}
inline void phase(Header& h,Phase p){if(static_cast<DWORD>(h.phase)!=p){h.phase=p;h.draws=0;}}
inline void begin(Store& s,DWORD frame,uint64_t selected){auto& h=s.header;if(!thread(h)||h.stopped)return;
    h.frame=frame;h.owner=static_cast<DWORD>(selected);h.revision=static_cast<DWORD>(selected>>32);
    h.model=h.source=h.manager=h.sourceFrame=0;h.sourceQpc=0;h.phase=BeforeSelected;h.draws=0;
    publish(s,context(h,FrameBegin));
}
inline void model(Store& s,bool entering,DWORD owner,DWORD model,DWORD source,DWORD manager){auto& h=s.header;
    if(!thread(h)||h.stopped)return;
    if(owner!=h.owner){if(entering)phase(h,OtherModel);return;}
    h.model=model;h.source=source;h.manager=manager;phase(h,entering?InsideSelected:AfterSelected);
    publish(s,context(h,entering?ModelBegin:ModelEnd));
}
inline void offered(Store& s,DWORD frame,uint64_t qpc){auto& h=s.header;if(!thread(h)||h.stopped||h.frame!=frame||h.sourceFrame==frame)return;
    h.sourceFrame=frame;h.sourceQpc=qpc;publish(s,context(h,SourcePublished));}
} // namespace native_insertion
