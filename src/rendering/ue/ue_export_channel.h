#pragma once
// Private UE -> receiver transport. Original source/D3D9/Remix wires unchanged.
// Two raw planes precede native normalization; this is not an insertion ticket.
#include "ue_output_contract.h"
#include <windows.h>
#include <sddl.h>
#include <objbase.h>
#include <cmath>
#include <atomic>
#include <intrin.h>
#include <string>
#include <stdexcept>

namespace sfc_ue_export {
using sfc_ue_output::Identity;
constexpr uint32_t Magic=0x31584555,Version=1;
enum Phase:LONG {Idle=0,Writing=1,Published=2,Reading=3,Complete=4,Retired=5};
inline uint64_t now(){LARGE_INTEGER n{};QueryPerformanceCounter(&n);return uint64_t(n.QuadPart);}
struct alignas(8) Packet {
    uint32_t magic=Magic,version=Version,bytes=sizeof(Packet),flags{};
    uint32_t producer{},consumer{},width{},height{};
    uint32_t target_width{},target_height{},viewport_x{},viewport_y{};
    uint64_t adapter_luid{};
    Identity identity{};
    uint64_t resource_epoch{},slot_epoch{},images[2]{};
    uint64_t ready_fence{},ack_fence{},ready_value{},ack_value{};
    double p22{},p23{};
    uint32_t slot{},reserved{};
    uint64_t checksum{};
};
static_assert(sizeof(Packet)==280&&offsetof(Packet,checksum)==272);
inline void seal(Packet& p){p.checksum=sfc_ue_output::hash(&p,offsetof(Packet,checksum));}
inline bool valid(const Packet& p,const Identity& expected,uint32_t producer,uint32_t consumer,uint64_t luid,bool diagnostic=false){
    using namespace sfc_ue_output;
    const auto& i=p.identity;
    bool asset=false;for(auto b:i.asset)asset|=b!=0;
    return p.magic==Magic&&p.version==Version&&p.bytes==sizeof(Packet)&&!p.reserved&&
        !(p.flags&~(Replay|SourceFrame|SourceSequence))&&(!(p.flags&Replay)||diagnostic)&&
        ((p.flags&Replay)||(p.flags&(SourceFrame|SourceSequence))==(SourceFrame|SourceSequence))&&
        (!(p.flags&SourceFrame)||i.frame)&&(!(p.flags&SourceSequence)||i.sequence)&&
        same(i,expected)&&(i.session[0]||i.session[1])&&asset&&i.owner_epoch&&i.owner_epoch<=UINT32_MAX&&
        i.revision&&i.camera_pose&&i.cohort&&i.activation&&i.device&&i.target&&i.output&&
        producer&&consumer&&p.producer==producer&&p.consumer==consumer&&p.adapter_luid==luid&&
        p.width&&p.height&&p.target_width&&p.target_height&&p.target_width<=4096&&p.target_height<=4096&&
        uint64_t(p.viewport_x)+p.width<=p.target_width&&uint64_t(p.viewport_y)+p.height<=p.target_height&&
        uint64_t(p.target_width)*p.target_height*OutputBytesPerPixel<=ResourceBudget&&
        p.resource_epoch&&p.slot_epoch&&p.slot<Slots&&p.images[0]&&p.images[1]&&
        p.ready_fence&&p.ack_fence&&p.ready_value&&p.ack_value&&
        std::isfinite(p.p22)&&std::isfinite(p.p23)&&p.p23!=0&&
        p.checksum==hash(&p,offsetof(Packet,checksum));
}
struct alignas(64) Slot {
    volatile LONG phase=Idle;
    LONG reserved=0;
    Packet packet{};
    sfc_ue_output::Receipt receipt{};
    struct Timing {uint64_t offered=0,published=0,acquired=0,completed=0;} timing;
    uint64_t padding[4]{};
};
struct alignas(64) State {
    uint32_t magic{},version{},bytes{},producer{};
    std::array<uint64_t,2> session{};
    volatile LONG consumer=0,stop=0,error=0,processed=0;
    uint64_t frequency=0;
    uint32_t diagnostics=0,reserved=0;
    alignas(8) volatile LONG64 retire_requested=0,retire_completed=0;
    uint64_t padding[6]{};
    Slot slots[2];
};
static_assert(sizeof(State)<=4096);
inline LONG load(volatile LONG& v){return _InterlockedCompareExchange(&v,0,0);}
inline void store(volatile LONG& v,LONG n){_InterlockedExchange(&v,n);}
inline uint64_t load64(volatile LONG64& v){return uint64_t(_InterlockedCompareExchange64(&v,0,0));}
inline void store64(volatile LONG64& v,uint64_t n){
    // MSVC x86 has compare/exchange64 but no exchange64 intrinsic.
    LONG64 observed=LONG64(load64(v));
    for(;;){const LONG64 old=_InterlockedCompareExchange64(&v,LONG64(n),observed);if(old==observed)return;observed=old;}
}
struct Handle {
    HANDLE value=nullptr;
    Handle()=default;Handle(const Handle&)=delete;Handle& operator=(const Handle&)=delete;
    ~Handle(){if(value&&value!=INVALID_HANDLE_VALUE)CloseHandle(value);}
    void reset(){if(value&&value!=INVALID_HANDLE_VALUE)CloseHandle(value);value=nullptr;}
};
// Same current-user-only security pattern as the existing session mappings.
struct Security {
    PSECURITY_DESCRIPTOR descriptor=nullptr;
    SECURITY_ATTRIBUTES attributes{sizeof(SECURITY_ATTRIBUTES),nullptr,FALSE};
    Security(){
        Handle token;
        if(!OpenProcessToken(GetCurrentProcess(),TOKEN_QUERY,&token.value))throw std::runtime_error("Export user token");
        alignas(TOKEN_USER) BYTE user[1024]{};DWORD size=0;
        if(!GetTokenInformation(token.value,TokenUser,user,sizeof(user),&size))throw std::runtime_error("Export token user");
        LPWSTR sid=nullptr;
        if(!ConvertSidToStringSidW(reinterpret_cast<TOKEN_USER*>(user)->User.Sid,&sid))throw std::runtime_error("Export SID");
        const std::wstring acl=std::wstring(L"D:P(A;;GA;;;")+sid+L")";LocalFree(sid);
        if(!ConvertStringSecurityDescriptorToSecurityDescriptorW(acl.c_str(),SDDL_REVISION_1,&descriptor,nullptr))throw std::runtime_error("Export DACL");
        attributes.lpSecurityDescriptor=descriptor;
    }
    Security(const Security&)=delete;Security& operator=(const Security&)=delete;
    ~Security(){if(descriptor)LocalFree(descriptor);}
};
class Channel {
    Handle mapping,readyEvent,stopEvent,ackEvent;
public:
    State* state=nullptr;
    std::wstring name;
    Channel(const Channel&)=delete;Channel& operator=(const Channel&)=delete;
    explicit Channel(const std::array<uint64_t,2>& session,bool diagnostics=false){
        if(!(session[0]||session[1]))throw std::runtime_error("Empty export session");
        GUID guid{};wchar_t text[40]{};
        if(FAILED(CoCreateGuid(&guid))||!StringFromGUID2(guid,text,40))throw std::runtime_error("Export channel GUID");
        name=std::wstring(L"Local\\SFCUEExport-")+text;
        Security security;
        mapping.value=CreateFileMappingW(INVALID_HANDLE_VALUE,&security.attributes,PAGE_READWRITE,0,4096,name.c_str());
        const auto error=GetLastError();
        if(!mapping.value||error==ERROR_ALREADY_EXISTS)throw std::runtime_error("Unique export mapping");
        auto create=[&](Handle& h,const wchar_t* suffix,bool manual){
            h.value=CreateEventW(&security.attributes,manual,FALSE,(name+suffix).c_str());
            const auto result=GetLastError();
            if(!h.value||result==ERROR_ALREADY_EXISTS)throw std::runtime_error("Unique export event");
        };
        create(readyEvent,L"-Ready",false);create(stopEvent,L"-Stop",true);create(ackEvent,L"-Ack",false);
        auto* view=static_cast<State*>(MapViewOfFile(mapping.value,FILE_MAP_ALL_ACCESS,0,0,4096));
        if(!view)throw std::runtime_error("Map export state");
        // No throwing operations after the view is acquired.
        state=view;*state=State{};state->version=Version;state->bytes=sizeof(State);
        state->producer=GetCurrentProcessId();state->session=session;
        LARGE_INTEGER frequency{};QueryPerformanceFrequency(&frequency);state->frequency=uint64_t(frequency.QuadPart);
        state->diagnostics=diagnostics?1u:0u;
        std::atomic_thread_fence(std::memory_order_release);state->magic=Magic;
    }
    Channel(const wchar_t* existing,uint32_t producer,const std::array<uint64_t,2>& session){
        if(!existing)throw std::runtime_error("Missing export name");name=existing;
        const std::wstring prefix=L"Local\\SFCUEExport-";GUID guid{};
        if(name.size()!=prefix.size()+38||name.compare(0,prefix.size(),prefix)||
           FAILED(CLSIDFromString(name.c_str()+prefix.size(),&guid)))throw std::runtime_error("Export name invalid");
        mapping.value=OpenFileMappingW(FILE_MAP_ALL_ACCESS,FALSE,name.c_str());
        auto open=[&](Handle& h,const wchar_t* suffix){h.value=OpenEventW(SYNCHRONIZE|EVENT_MODIFY_STATE,FALSE,(name+suffix).c_str());return h.value!=nullptr;};
        if(!mapping.value||!open(readyEvent,L"-Ready")||!open(stopEvent,L"-Stop")||!open(ackEvent,L"-Ack"))throw std::runtime_error("Open export channel");
        auto* view=static_cast<State*>(MapViewOfFile(mapping.value,FILE_MAP_ALL_ACCESS,0,0,4096));
        if(!view)throw std::runtime_error("Map export peer");
        if(view->magic!=Magic||view->version!=Version||view->bytes!=sizeof(State)||
           !producer||view->producer!=producer||view->session!=session||!view->frequency||view->diagnostics>1||view->reserved||load(view->stop)||
           _InterlockedCompareExchange(&view->consumer,LONG(GetCurrentProcessId()),0)!=0){
            UnmapViewOfFile(view);throw std::runtime_error("Export peer/session identity");
        }
        state=view;SetEvent(ackEvent.value);
    }
    ~Channel(){if(state)UnmapViewOfFile(state);}
    HANDLE ready()const{return readyEvent.value;}
    HANDLE stopped()const{return stopEvent.value;}
    HANDLE acknowledged()const{return ackEvent.value;}
    void stop(){store(state->stop,1);SetEvent(stopEvent.value);}
    void notify(){SetEvent(readyEvent.value);}
    bool reserve(const Packet& p,bool diagnostic=false,uint64_t offered=0){
        if(load(state->stop)||load(state->error)||p.slot>=2||p.identity.session!=state->session||
           GetCurrentProcessId()!=state->producer||p.resource_epoch<=load64(state->retire_completed)||
           !valid(p,p.identity,state->producer,uint32_t(load(state->consumer)),p.adapter_luid,diagnostic))return false;
        for(const auto& previous:state->slots){
            const auto& old=previous.packet;
            if(!old.slot_epoch)continue;
            if((p.ready_fence==old.ready_fence&&p.ready_value<=old.ready_value)||
               (p.ack_fence==old.ack_fence&&p.ack_value<=old.ack_value))return false;
        }
        auto& s=state->slots[p.slot];
        if(s.packet.slot_epoch&&p.slot_epoch<=s.packet.slot_epoch)return false;
        if(_InterlockedCompareExchange(&s.phase,Writing,Idle)!=Idle)return false;
        s.packet=p;s.receipt={};s.timing={};if(state->diagnostics)s.timing.offered=offered?offered:now();return true;
    }
    // Called after the matching RHI copy and ready-fence signal are queued.
    // Published is an available descriptor, not proof of GPU completion.
    bool publish_reserved(const Packet& p){
        if(GetCurrentProcessId()!=state->producer||p.slot>=2)return false;
        auto& s=state->slots[p.slot];
        if(s.packet.checksum!=p.checksum||load(state->stop)||load(state->error))return false;
        if(state->diagnostics)s.timing.published=now();
        if(_InterlockedCompareExchange(&s.phase,Published,Writing)!=Writing)return false;
        notify();return true;
    }
    bool publish(const Packet& p,bool diagnostic=false){
        return reserve(p,diagnostic)&&publish_reserved(p);
    }
    bool acquire(unsigned slot,Packet& p){
        if(slot>=2||load(state->stop)||load(state->error)||
           uint32_t(load(state->consumer))!=GetCurrentProcessId())return false;
        auto& s=state->slots[slot];
        if(_InterlockedCompareExchange(&s.phase,Reading,Published)!=Published)return false;
        if(state->diagnostics)s.timing.acquired=now();p=s.packet;return true;
    }
    bool complete(const Packet& p){
        if(p.slot>=2||uint32_t(load(state->consumer))!=GetCurrentProcessId())return false;
        auto& s=state->slots[p.slot];
        if(load(s.phase)!=Reading||s.packet.checksum!=p.checksum)return false;
        s.receipt={p.identity,p.resource_epoch,p.slot_epoch,p.ack_value,p.consumer,p.slot};
        if(state->diagnostics)s.timing.completed=now();
        store(s.phase,Complete);_InterlockedIncrement(&state->processed);SetEvent(ackEvent.value);return true;
    }
    bool reclaim(unsigned slot,uint64_t completed){
        if(slot>=2||GetCurrentProcessId()!=state->producer||completed==UINT64_MAX)return false;
        auto& s=state->slots[slot];
        if(load(s.phase)!=Complete||completed<s.packet.ack_value)return false;
        const auto& r=s.receipt;const auto& p=s.packet;
        if(!sfc_ue_output::same(r.identity,p.identity)||r.resource_epoch!=p.resource_epoch||
           r.slot_epoch!=p.slot_epoch||r.ack_value!=p.ack_value||r.consumer!=p.consumer||r.slot!=p.slot)return false;
        return _InterlockedCompareExchange(&s.phase,Idle,Complete)==Complete;
    }
    bool cancel_unread(unsigned slot,uint64_t completed){
        if(slot>=2||GetCurrentProcessId()!=state->producer||completed==UINT64_MAX)return false;
        auto& s=state->slots[slot];
        if(completed<s.packet.ready_value||_InterlockedCompareExchange(&s.phase,Retired,Published)!=Published)return false;
        store(s.phase,Idle);return true;
    }
    bool cancel_unpublished(unsigned slot,uint64_t completed){
        if(slot>=2||GetCurrentProcessId()!=state->producer||completed==UINT64_MAX||!load(state->stop))return false;
        auto& s=state->slots[slot];
        if(completed<s.packet.ready_value||_InterlockedCompareExchange(&s.phase,Retired,Writing)!=Writing)return false;
        store(s.phase,Idle);return true;
    }
    bool request_retirement(uint64_t epoch){
        if(!epoch||GetCurrentProcessId()!=state->producer||load(state->stop)||load(state->error)||
           epoch<=load64(state->retire_completed))return false;
        for(auto& slot:state->slots)if(load(slot.phase)!=Idle)return false;
        const uint64_t old=load64(state->retire_requested);
        if(old>load64(state->retire_completed)&&old!=epoch)return false;
        store64(state->retire_requested,epoch);notify();return true;
    }
    bool complete_retirement(uint64_t epoch){
        if(uint32_t(load(state->consumer))!=GetCurrentProcessId()||!epoch||
           epoch!=load64(state->retire_requested)||epoch<=load64(state->retire_completed))return false;
        for(auto& slot:state->slots)if(load(slot.phase)!=Idle)return false;
        store64(state->retire_completed,epoch);SetEvent(ackEvent.value);return true;
    }
};
}
