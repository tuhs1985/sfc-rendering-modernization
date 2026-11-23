#include "../src/rendering/ue/ue_output_contract.h"
#include "../src/rendering/ue/ue_output_leases.h"
#include <windows.h>
#include <process.h>
#include <filesystem>
#include <fstream>
#include <cstdio>
#include <stdexcept>
#include <type_traits>
using namespace sfc_ue_output;
static_assert(std::is_standard_layout_v<Ticket> && std::is_trivially_copyable_v<Ticket>);
void need(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
Ticket read(const std::filesystem::path& path){
    Ticket t{};
    std::ifstream in(path,std::ios::binary);
    need(bool(in.read(reinterpret_cast<char*>(&t),sizeof(t))),"Incomplete ticket");
    need(in.peek()==std::char_traits<char>::eof(),"Trailing ticket bytes");
    return t;
}
void write(const std::filesystem::path& path,const Ticket& t){
    std::ofstream out(path,std::ios::binary);
    need(bool(out.write(reinterpret_cast<const char*>(&t),sizeof(t))),"Ticket write");
}
Ticket fixture(){
    Ticket t{};t.flags=SourceFrame|SourceSequence;
    t.producer=11;t.consumer=12;t.width=1720;t.height=1020;t.adapter_luid=17;
    t.target_width=1920;t.target_height=1080;t.viewport_x=200;t.viewport_y=30;
    auto& i=t.identity;
    i.session={1,2};i.asset[0]=3;i.owner_epoch=4;i.revision=5;
    i.frame=6;i.sequence=7;i.camera_pose=8;i.cohort=9;i.activation=10;
    i.device=11;i.target=12;i.output=13;
    t.resource_epoch=14;t.slot_epoch=15;t.images[0]=0x100000001ull;
    t.images[1]=0x200000002ull;t.images[2]=0x300000003ull;
    t.ready_fence=0x400000004ull;t.ack_fence=0x500000005ull;
    t.ready_value=t.ack_value=16;seal(t);return t;
}
int wmain(int count,wchar_t** args){
    try{
        if(count==4&&std::wcscmp(args[1],L"--check")==0){
            const auto t=read(args[2]),e=read(args[3]);
            return valid(t,e.identity,e.producer,e.consumer,e.adapter_luid)?0:2;
        }
        need(count==2,"Supply a contract fixture directory");
        const std::filesystem::path root=args[1];
        std::filesystem::create_directories(root);
        const auto input=root/"input.ticket",expected=root/"expected.ticket";
        const Ticket base=fixture();write(expected,base);
        wchar_t exe[32768]{};
        need(GetModuleFileNameW(nullptr,exe,UINT(std::size(exe)))>0,"Executable path");
        unsigned checked=0;
        auto test=[&](Ticket t,bool accept){
            seal(t);write(input,t);
            const auto code=_wspawnl(_P_WAIT,exe,L"ue-output-contract-check",L"--check",input.c_str(),expected.c_str(),nullptr);
            need(code==(accept?0:2),"Process-boundary ticket admission");
            ++checked;
        };
        test(base,true);
        auto t=base;t.identity.session[1]++;test(t,false);
        t=base;t.identity.owner_epoch++;test(t,false);
        t=base;t.identity.asset[0]++;test(t,false);
        t=base;t.identity.revision++;test(t,false);
        t=base;t.identity.frame++;test(t,false);
        t=base;t.identity.sequence++;test(t,false);
        t=base;t.identity.camera_pose++;test(t,false);
        t=base;t.identity.cohort++;test(t,false);
        t=base;t.identity.activation++;test(t,false);
        t=base;t.identity.device++;test(t,false);
        t=base;t.identity.target++;test(t,false);
        t=base;t.identity.output++;test(t,false);
        t=base;t.producer++;test(t,false);
        t=base;t.consumer++;test(t,false);
        t=base;t.adapter_luid++;test(t,false);
        t=base;t.width=0;test(t,false);
        t=base;t.viewport_x=201;test(t,false);
        t=base;t.target_height=1020;test(t,false);
        t=base;t.viewport_x=UINT32_MAX;test(t,false);
        t=base;t.width=t.height=4096;test(t,false);
        t=base;t.slot=2;test(t,false);
        t=base;t.images[0]=0;test(t,false);
        t=base;t.ready_fence=0;test(t,false);
        t=base;t.ready_value=0;test(t,false);
        t=base;t.flags=0;test(t,false);
        t=base;t.flags=Replay;test(t,false);
        seal(t);
        need(valid(t,base.identity,base.producer,base.consumer,base.adapter_luid,true),"Explicit replay diagnostic");
        need(matches_lease(base,base),"Current resource lease");
        t=base;t.resource_epoch++;seal(t);need(!matches_lease(t,base),"Retired resource");
        t=base;t.slot_epoch++;seal(t);need(!matches_lease(t,base),"Recycled slot");
        t=base;t.images[0]++;seal(t);need(!matches_lease(t,base),"Changed resource handle");
        t=base;t.viewport_y++;seal(t);need(!matches_lease(t,base),"Changed tactical viewport");
        t=base;t.ack_value++;seal(t);need(!matches_lease(t,base),"Wrong GPU completion value");
        Receipt ack{base.identity,base.resource_epoch,base.slot_epoch,base.ack_value,base.consumer,base.slot};
        LeasePool pool(base);
        need(pool.publish(base),"First slot publication");
        need(!pool.publish(base),"Busy slot must not be overwritten");
        need(!pool.acquire(base,0),"Incomplete producer GPU work");
        auto other=base;other.slot=1;other.identity.output++;seal(other);
        need(!pool.publish(other),"Two slots cannot reuse a shared fence value");
        other.ready_value++;other.ack_value++;seal(other);
        need(pool.publish(other),"Second slot accepts an independent fence value");
        need(pool.cancel_unacquired(1,other,other.ready_value),"Unacquired second slot cancels after completion");
        need(pool.acquire(base,other.ready_value),"Later producer completion also completes the earlier frame");
        need(!pool.release(ack,0),"Incomplete consumer GPU read");
        pool.stop();
        need(!pool.drained()&&!pool.publish(base),"Stopped pool retains active read");
        need(pool.release(ack,base.ack_value+1)&&pool.drained(),"Later completion drains the exact acknowledged read");
        LeasePool unused(base);
        need(unused.publish(base),"Pending publication");
        unused.stop();
        need(!unused.cancel_unacquired(0,base,0),"Pending producer retains resources");
        need(unused.cancel_unacquired(0,base,base.ready_value)&&unused.drained(),"Cancel completed unacquired output");
        LeasePool reuse(base);
        need(reuse.publish(base)&&reuse.acquire(base,base.ready_value)&&reuse.release(ack,base.ack_value),"First use completes");
        need(!reuse.publish(base),"Recycled publication requires new slot epoch");
        t=base;t.slot_epoch++;t.identity.output++;t.ready_value++;t.ack_value++;seal(t);
        need(reuse.publish(t)&&reuse.acquire(t,t.ready_value),"Second use is independent");
        need(!reuse.release(ack,t.ack_value),"Late acknowledgement cannot release second use");
        need(acknowledges(ack,base),"Matching acknowledgement");
        ack.slot_epoch++;need(!acknowledges(ack,base),"Stale acknowledgement");
        ack.slot_epoch--;ack.identity.session[0]++;need(!acknowledges(ack,base),"Cross-session acknowledgement");
        std::printf("PASS %u process-boundary ticket cases, 3 acknowledgement cases; ticket bytes=%zu\n",checked,sizeof(Ticket));
        return 0;
    }catch(const std::exception& e){std::fprintf(stderr,"%s\n",e.what());return 1;}
}
