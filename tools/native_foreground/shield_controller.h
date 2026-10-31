#pragma once
#include "draw_snapshot.h"
#include "masked_assembly.h"
#include "shield_scope_hooks.h"
#include "source_notice.h"
#include "shader_compatibility.h"
#include <thread>
#include <atomic>
#include <memory>
#include <string>

namespace native_foreground {
class ShieldController;
inline ShieldController* shieldController{};
class ShieldController {
    struct Draw {
        // 0 empty,1 setup request,2 worker owns,3 ready,4 unsupported.
        std::atomic<unsigned> state{0};DrawBindings request;
        std::unique_ptr<DrawSnapshot> snapshot;
    };
    struct Frame {
        DWORD number{},generation{};Identity identity{};unsigned count{},spans{};bool complete{},bad{};
        Draw draws[8];
    };
    Frame frames_[3];Frame* recording_{};
    DWORD refused_[replacement::Frames]{};DWORD installedAtFrame_{};
    DWORD invoked_[replacement::Frames]{};
    ComPtr<ID3D11Device> device_;ComPtr<ID3D11DeviceContext> context_,deferred_;
    replacement::Store* ledger_;source_notice::Store* notice_;
    DWORD session_[4]{};DWORD thread_=GetCurrentThreadId();
    DWORD resourceAddress_=0x008F522C;
    bool fixtureMode_{};
    shield_hooks::Verify fixtureVerify_{};
    HANDLE wake_{};
    std::thread worker_;std::atomic<bool> stop_{false},installed_{false},failed_{false};
    std::atomic<bool> unsafeDetach_{false};
    std::atomic<bool> teardownDone_{false};
    std::atomic<uint64_t> allocated_{0};
    std::atomic<DWORD> setupRejected_{0};DWORD goodFrames_{},badFrames_{},captured_{},replayed_{},goodMax_{},badMax_{};
    MaskedAssembly assembly_;
    static constexpr uint64_t cap=32ull*1024*1024;
    static bool readWord(DWORD address,DWORD& out) noexcept {
        __try{out=*reinterpret_cast<const DWORD*>(address);return true;}__except(EXCEPTION_EXECUTE_HANDLER){return false;}
    }
    uint64_t sessionKey() const noexcept {uint64_t key=1469598103934665603ull;for(auto v:session_)key=(key^v)*1099511628211ull;return key?key:1;}
    static bool __cdecl resolve(shield_hooks::Word ship,shield_hooks::Word shield,shield_hooks::Word manager,shield_hooks::Owner* out) noexcept {
        auto* self=shieldController;if(!self||self->stop_||GetCurrentThreadId()!=self->thread_)return false;
        auto& ledger=*self->ledger_;const DWORD frame=static_cast<DWORD>(InterlockedCompareExchange(&ledger.native_frame,0,0));
        if(InterlockedCompareExchange(&ledger.native_stop,0,0)||!InterlockedCompareExchange(&ledger.native_capable,0,0))return false;
        source_notice::Notice n{};replacement::Receipt r{};DWORD vtable{},nativeShield{},resource{};
        if(!source_notice::valid(*self->notice_,self->session_,GetCurrentProcessId())||!source_notice::sample(*self->notice_,frame,n)||
           !replacement::sample(ledger,frame,r)||!n.owner||!n.revision||r.flags&replacement::Invalid||n.generation!=r.generation||n.owner!=r.owner||n.revision!=r.revision||
           n.ship!=ship||n.thread!=self->thread_||!readWord(ship,vtable)||vtable!=0x00796F0C||
           !readWord(ship+0x1BC,nativeShield)||nativeShield!=shield||!readWord(manager,vtable)||vtable!=0x007B8D4C||
           !readWord(self->resourceAddress_,resource))return false;
        DWORD setter{};if(!self->fixtureMode_&&(!readWord(vtable+0xC4,setter)||setter!=0x0069EC60))return false;
        *out={{self->sessionKey(),frame,n.owner,n.revision},ship,shield,manager,resource};return true;
    }
    static void __cdecl notify(bool begin,const shield_hooks::Owner* owner) noexcept {
        auto* self=shieldController;if(!self||self->stop_||GetCurrentThreadId()!=self->thread_)return;
        if(!owner){if(self->recording_)self->recording_->bad=true;return;}
        if(begin)self->begin(*owner);
        else if(self->recording_){if(!shield_hooks::local.producer.balanced())self->recording_->bad=true;
            self->recording_->complete=true;self->recording_=nullptr;}
    }
    static void __cdecl reject(shield_hooks::Word ship,shield_hooks::Word shield,shield_hooks::Word) noexcept {
        auto* self=shieldController;if(!self||self->stop_||GetCurrentThreadId()!=self->thread_)return;
        const DWORD frame=static_cast<DWORD>(InterlockedCompareExchange(&self->ledger_->native_frame,0,0));
        source_notice::Notice n{};
        if(source_notice::valid(*self->notice_,self->session_,GetCurrentProcessId())&&source_notice::sample(*self->notice_,frame,n)) {
            DWORD currentShield{};const bool hasCurrent=readWord(n.ship+0x1BC,currentShield);
            if(n.ship==ship||n.shield==shield||(hasCurrent&&currentShield==shield)){
                self->refused_[frame%replacement::Frames]=frame;if(frame>self->badMax_){self->badMax_=frame;++self->badFrames_;}}
        }
    }
    void begin(const shield_hooks::Owner& owner) noexcept {
        invoked_[owner.identity.frame%replacement::Frames]=static_cast<DWORD>(owner.identity.frame);
        Frame* frame=find(static_cast<DWORD>(owner.identity.frame));
        if(!frame)for(auto& f:frames_)if(!f.number) {
            bool available=true;
            for(auto& d:f.draws)if(d.state.load(std::memory_order_acquire)==3&&d.snapshot) {
                d.snapshot->tryRecycle(context_.Get());available&=d.snapshot->available();
            }
            if(!available)continue;
            frame=&f;break;
        }
        if(!frame){refused_[owner.identity.frame%replacement::Frames]=static_cast<DWORD>(owner.identity.frame);return;}
        if(!frame->number){frame->number=static_cast<DWORD>(owner.identity.frame);frame->identity=owner.identity;
            replacement::Receipt r{};if(!replacement::sample(*ledger_,frame->number,r)){frame->bad=true;return;}frame->generation=r.generation;}
        if(++frame->spans>8||!(frame->identity==owner.identity)||recording_)frame->bad=true;
        frame->complete=false;
        recording_=frame;
    }
    Frame* find(DWORD frame) noexcept {for(auto& f:frames_)if(f.number==frame)return &f;return nullptr;}
    static uint64_t estimate(const DrawBindings& b) {
        uint64_t bytes=0;auto buffer=[&](ID3D11Buffer* p){if(p){D3D11_BUFFER_DESC d{};p->GetDesc(&d);bytes+=d.ByteWidth;}};
        buffer(b.vb.Get());buffer(b.ib.Get());for(const auto& c:b.constants)buffer(c.Get());
        ID3D11Resource* seen[3]{};unsigned count=0;
        for(const auto& v:b.views)if(v){ComPtr<ID3D11Resource> resource;v->GetResource(&resource);
            unsigned i=0;for(;i<count;++i)if(seen[i]==resource.Get())break;if(i<count)continue;
            if(count==3)throw std::runtime_error("shield image cap");seen[count++]=resource.Get();
            ComPtr<ID3D11Texture2D> t;if(FAILED(resource.As(&t)))throw std::runtime_error("shield image type");
            D3D11_TEXTURE2D_DESC d{};t->GetDesc(&d);bytes+=uint64_t(d.Width)*d.Height*4;
        }return bytes;
    }
    void work() noexcept {
        bool attached=false;
        BYTE beforeShield[12]{},beforeDepth[12]{};
        try {
            using Factory=BOOL(__cdecl*)(shield_hooks::FixtureTargets*);
            const auto factory=reinterpret_cast<Factory>(GetProcAddress(GetModuleHandleW(nullptr),"SFCNativeForegroundFixture"));
            if(factory){
                wchar_t path[1024]{};GetModuleFileNameW(nullptr,path,1024);const std::wstring image(path);
                if(image.find(L"\\artifacts\\remix-runtime\\runs\\")==std::wstring::npos||
                   image.substr(image.find_last_of(L"\\/")+1)!=L"d3d11_return_fixture.exe")throw std::runtime_error("shield fixture path gate");
                shield_hooks::FixtureTargets targets{};targets.bytes=sizeof(targets);
                if(!factory(&targets)||targets.bytes!=sizeof(targets)||!targets.shield||!targets.depth||!targets.caller||!targets.resourceAddress)
                    throw std::runtime_error("shield fixture targets");
                shield_hooks::originalShield=targets.shield;shield_hooks::originalDepth=targets.depth;
                fixtureMode_=true;
                shield_hooks::callerReturn=targets.caller;resourceAddress_=targets.resourceAddress;
                fixtureVerify_=targets.verify;
            }else{
            // Full client hash is checked by the runner; retain local byte gates.
            BYTE shield[12]{},depth[12]{};SIZE_T read{};
            if(reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr))!=0x00400000||
               !ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(0x00426563),shield,12,&read)||read!=12||
               !ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(0x0069EC60),depth,12,&read)||read!=12||
               memcmp(shield,"\x55\x8B\xEC\x81\xEC\xB8\0\0\0\x83\x65\xFC",12)||
               memcmp(depth,"\x8A\x44\x24\x04\x56\x84\xC0\x0F\x95\xC0\x88\x44",12))throw std::runtime_error("shield native byte gates");
            shield_hooks::originalShield=reinterpret_cast<void*>(0x00426563);
            shield_hooks::originalDepth=reinterpret_cast<shield_hooks::Depth>(0x0069EC60);
            }
            SIZE_T got{};
            if(!ReadProcessMemory(GetCurrentProcess(),shield_hooks::originalShield,beforeShield,12,&got)||got!=12||
               !ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(shield_hooks::originalDepth),beforeDepth,12,&got)||got!=12)
                throw std::runtime_error("shield original bytes unavailable");
            // The injected add-on already has process lifetime. Pin its code
            // explicitly so a suspended wrapper epilogue can never outlive it.
            // Hook objects/GPU resources are still detached/released normally.
            HMODULE code{};
            if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,
                reinterpret_cast<LPCWSTR>(&resolve),&code))throw std::runtime_error("shield callback code lifetime");
            shield_hooks::resolve=resolve;shield_hooks::notify=notify;shield_hooks::reject=reject;
            if(shield_hooks::transaction(true)!=NO_ERROR)throw std::runtime_error("shield hook install");
            attached=true;installedAtFrame_=static_cast<DWORD>(InterlockedCompareExchange(&ledger_->native_frame,0,0));
            InterlockedExchange(&shield_hooks::enabled,1);installed_=true;
            while(!stop_&&!InterlockedCompareExchange(&ledger_->native_stop,0,0)) {
                for(auto& f:frames_)for(auto& d:f.draws) {
                    unsigned expected=1;if(!d.state.compare_exchange_strong(expected,2))continue;
                    try {const auto bytes=estimate(d.request);
                        if(bytes>RetainedResources::limit||allocated_+bytes>cap)throw std::runtime_error("shield retained memory cap");
                        auto snapshot=std::make_unique<DrawSnapshot>();snapshot->prepare(device_.Get(),d.request);
                        allocated_+=snapshot->bytes();d.snapshot=std::move(snapshot);d.state.store(3,std::memory_order_release);
                    }catch(...){++setupRejected_;d.state.store(4,std::memory_order_release);}
                }
                WaitForSingleObject(wake_,20);
            }
        }catch(...){failed_=true;}
        InterlockedExchange(&shield_hooks::enabled,0);installed_=false;
        bool detached=!attached||shield_hooks::transaction(false)==NO_ERROR;
        if(attached&&detached){BYTE shield[12]{},depth[12]{};SIZE_T got{};
            detached=ReadProcessMemory(GetCurrentProcess(),shield_hooks::originalShield,shield,12,&got)&&got==12&&
                ReadProcessMemory(GetCurrentProcess(),reinterpret_cast<void*>(shield_hooks::originalDepth),depth,12,&got)&&got==12&&
                !memcmp(shield,beforeShield,12)&&!memcmp(depth,beforeDepth,12);}
        const ULONGLONG until=GetTickCount64()+2000;
        while(shield_hooks::active&&GetTickCount64()<until)Sleep(1);
        if(!detached||shield_hooks::active){failed_=true;unsafeDetach_=true;
            // Retain callback code on an abnormal detach; stop() makes the owner
            // retain this controller too. Never unload a still-installed hook.
            HMODULE module{};GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,
                reinterpret_cast<LPCWSTR>(&resolve),&module);
        }
        shield_hooks::resolve=nullptr;shield_hooks::notify=nullptr;shield_hooks::reject=nullptr;
        teardownDone_=true;
        if(source_notice::valid(*notice_,session_,GetCurrentProcessId()))InterlockedExchange(
            reinterpret_cast<volatile LONG*>(&notice_->reserved[7]),unsafeDetach_?2:1);
    }
public:
    ShieldController(ID3D11Device* d,replacement::Store* ledger,source_notice::Store* notice,const DWORD* session):
        device_(d),ledger_(ledger),notice_(notice),assembly_(d) {
        if(shieldController)throw std::runtime_error("only one native shield controller");
        memcpy(session_,session,16);d->GetImmediateContext(&context_);
        // Counters describe the session, not just the latest graphics device.
        // The previous controller stopped/published before a new one can exist.
        if(source_notice::valid(*notice_,session_,GetCurrentProcessId())) {
            goodFrames_=notice_->reserved[1];badFrames_=notice_->reserved[2];
            captured_=notice_->reserved[3];replayed_=notice_->reserved[4];
            setupRejected_=notice_->reserved[6];
        }
        if(FAILED(d->CreateDeferredContext(0,&deferred_)))throw std::runtime_error("shield replay context");
        wake_=CreateEventW(nullptr,FALSE,FALSE,nullptr);if(!wake_)throw std::runtime_error("shield setup event");
        // A restored ACK from an older device must not authorize unloading the
        // current controller's semantic storage before its own worker stops.
        InterlockedExchange(reinterpret_cast<volatile LONG*>(&notice_->reserved[7]),0);
        publish();
        shieldController=this;
        try{worker_=std::thread([this]{work();});}catch(...){shieldController=nullptr;CloseHandle(wake_);wake_=nullptr;throw;}
    }
    ~ShieldController(){stop();if(wake_)CloseHandle(wake_);}
    bool stop() noexcept {
        if(stop_.exchange(true)&&!worker_.joinable())return !shield_hooks::active&&!installed_&&!unsafeDetach_;
        if(wake_)SetEvent(wake_);if(worker_.joinable())worker_.join();
        const bool clean=!shield_hooks::active&&!installed_&&!unsafeDetach_;
        publish();
        if(clean&&shieldController==this)shieldController=nullptr;return clean;
    }
    bool ready() const noexcept {return installed_&&!failed_;}
    void draw(uint64_t native,UINT count,UINT instances,UINT start,INT base,UINT firstInstance) noexcept {
        if(GetCurrentThreadId()!=thread_||stop_||!recording_||recording_->bad)return;
        const auto* owner=shield_hooks::current();if(!owner||
            !shield_hooks::qualified(recording_->identity,owner->resource,true,false,true,true))return;
        if(native!=reinterpret_cast<uintptr_t>(context_.Get())||instances!=1||firstInstance){recording_->bad=true;return;}
        auto& f=*recording_;if(f.count==8){f.bad=true;return;}
        DrawBindings bindings;if(!bindings.read(context_.Get())){f.bad=true;return;}
        D3D11_DEPTH_STENCIL_DESC depth{};D3D11_BLEND_DESC blend{};
        if(!bindings.depth||!bindings.blend){f.bad=true;return;}
        bindings.depth->GetDesc(&depth);bindings.blend->GetDesc(&blend);const auto& b=blend.RenderTarget[0];
        if(!depth.DepthEnable||depth.DepthWriteMask!=D3D11_DEPTH_WRITE_MASK_ZERO||depth.StencilEnable||
           depth.DepthFunc!=D3D11_COMPARISON_LESS_EQUAL||!b.BlendEnable||b.SrcBlend!=D3D11_BLEND_ONE||
           b.DestBlend!=D3D11_BLEND_ONE||b.BlendOp!=D3D11_BLEND_OP_ADD||blend.AlphaToCoverageEnable||
           !shader_compatibility::singleSampleReplay(bindings.ps.Get(),bindings.sampleMask)){f.bad=true;return;}
        auto& d=f.draws[f.count++];const auto state=d.state.load(std::memory_order_acquire);
        if(!state){d.request=bindings;d.state.store(1,std::memory_order_release);SetEvent(wake_);f.bad=true;return;}
        if(state!=3||!d.snapshot||!d.snapshot->capture(context_.Get(),f.identity,count,start,base))f.bad=true;else ++captured_;
    }
    bool frameGood(const replacement::Receipt& r) noexcept {
        source_notice::Notice n{};
        if(!ready()||!source_notice::valid(*notice_,session_,GetCurrentProcessId())||!source_notice::sample(*notice_,r.frame,n)||
           r.frame<=installedAtFrame_||refused_[r.frame%replacement::Frames]==r.frame||
           n.generation!=r.generation||n.owner!=r.owner||n.revision!=r.revision||n.thread!=thread_)return false;
        // No invocation in an entirely observed parent frame is a genuine empty
        // foreground. The entry-time +1BC value is diagnostic, not absence proof.
        auto* f=find(r.frame);bool good=!f&&invoked_[r.frame%replacement::Frames]!=r.frame;
        if(f)good=!f->bad&&f->complete&&f->generation==r.generation&&f->identity.ownerEpoch==r.owner&&f->identity.revision==r.revision;
        if(good&&r.frame>goodMax_){goodMax_=r.frame;++goodFrames_;}return good;
    }
    void unsupportedDraw() noexcept {
        if(GetCurrentThreadId()!=thread_||stop_)return;
        const auto* owner=shield_hooks::current();if(recording_&&owner&&
            shield_hooks::qualified(recording_->identity,owner->resource,true,false,true,true))recording_->bad=true;
    }
    bool assemble(const replacement::Receipt& r,ID3D11RenderTargetView* target,ID3D11DepthStencilView* depth,
                  ID3D11ShaderResourceView*const(&views)[3],UINT owner,const float* origin,const float* scale) {
        if(!frameGood(r)||!assembly_.record(deferred_.Get(),target,depth,views,1920,1080,owner,origin,scale))return false;
        ComPtr<ID3D11CommandList> commands;
        if(FAILED(deferred_->FinishCommandList(FALSE,&commands)))return false;context_->ExecuteCommandList(commands.Get(),TRUE);
        if(auto* f=find(r.frame))for(unsigned i=0;i<f->count;++i) {
            auto& d=f->draws[i];if(!d.snapshot||!d.snapshot->record(deferred_.Get(),target,depth,f->identity,assembly_.foregroundState(),1))return false;
            commands.Reset();if(FAILED(deferred_->FinishCommandList(FALSE,&commands)))return false;context_->ExecuteCommandList(commands.Get(),TRUE);++replayed_;
        }
        if(fixtureVerify_)fixtureVerify_(target,views[0],views[2],r.frame,owner,origin,scale);
        return true;
    }
    void retain(DWORD current,DWORD a,DWORD b) noexcept {
        for(const auto& f:frames_)if(f.bad&&f.number>badMax_){badMax_=f.number;++badFrames_;}
        for(auto& f:frames_)if(f.number&&f.number!=current&&f.number!=a&&f.number!=b) {
            for(auto& d:f.draws)if(d.state.load(std::memory_order_acquire)==3&&d.snapshot)d.snapshot->finish(context_.Get());
            f.number=f.generation=f.count=f.spans=0;f.identity={};f.complete=f.bad=false;
        }
        publish();
    }
    void publish() noexcept {
        if(!source_notice::valid(*notice_,session_,GetCurrentProcessId()))return;
        const bool restored=teardownDone_&&!unsafeDetach_;
        const DWORD values[]{(installed_?1u:0u)|(failed_?2u:0u)|8u|(restored?16u:0u),goodFrames_,badFrames_,captured_,replayed_,
            static_cast<DWORD>(allocated_.load()),setupRejected_.load()};
        memcpy(notice_->reserved,values,sizeof(values));MemoryBarrier();
        if(teardownDone_)InterlockedExchange(reinterpret_cast<volatile LONG*>(&notice_->reserved[7]),unsafeDetach_?2:1);
    }
};
} // namespace native_foreground
