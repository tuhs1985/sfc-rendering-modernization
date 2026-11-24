#include "../src/rendering/ue/ue_export_channel.h"
#include <process.h>
#include <cstdio>
using namespace sfc_ue_export;
void need(bool ok,const char* why){if(!ok)throw std::runtime_error(why);}
Packet fixture(Channel& c){
    Packet p;p.flags=sfc_ue_output::SourceFrame|sfc_ue_output::SourceSequence;
    p.producer=GetCurrentProcessId();p.consumer=uint32_t(load(c.state->consumer));
    p.width=1720;p.height=1020;p.target_width=1920;p.target_height=1080;p.viewport_x=200;p.viewport_y=30;
    p.identity.session=c.state->session;p.identity.asset[0]=17;p.identity.owner_epoch=7;p.identity.revision=1;
    p.identity.frame=19;p.identity.sequence=31;p.identity.camera_pose=41;p.identity.cohort=47;
    p.identity.activation=p.identity.device=p.identity.target=p.identity.output=1;
    p.resource_epoch=p.slot_epoch=1;p.images[0]=0x100000001ull;p.images[1]=0x200000002ull;
    p.ready_fence=0x300000003ull;p.ack_fence=0x400000004ull;p.ready_value=p.ack_value=1;
    p.adapter_luid=97;p.p22=-1.0000666;p.p23=-2.0000668;seal(p);return p;
}
int wmain(int count,wchar_t** args){try{
    constexpr std::array<uint64_t,2> Session{17,29};
    if(count==4){
        Channel channel(args[1],std::stoul(args[2]),Session);
        if(std::wcscmp(args[3],L"passive")==0){
            need(WaitForSingleObject(channel.stopped(),5000)==WAIT_OBJECT_0,"Passive stop did not wake");return 0;
        }
        for(unsigned frame=1;frame<=5;++frame){
            if(frame==5){
                const ULONGLONG until=GetTickCount64()+5000;
                while(!load64(channel.state->retire_requested)){
                    need(GetTickCount64()<until,"Retirement request deadline");WaitForSingleObject(channel.ready(),10);
                }
                need(channel.complete_retirement(1),"Retirement requires drained slots");
            }
            Packet p;
            const ULONGLONG until=GetTickCount64()+5000;
            while(!channel.acquire(0,p)){
                need(GetTickCount64()<until&&!load(channel.state->stop),"Acquire deadline");
                WaitForSingleObject(channel.ready(),10);
            }
            auto expected=p.identity;expected.output=frame;
            need(valid(p,expected,std::stoul(args[2]),GetCurrentProcessId(),97),"Imported packet mismatch");
            need(p.images[0]>UINT32_MAX&&p.images[1]>UINT32_MAX,"Raw NT handle truncation");
            need(p.resource_epoch==(frame==5?2u:1u),"Resource generation mismatch");
            need(channel.complete(p),"Complete read");
        }
        return 0;
    }
    need(count==1,"Unexpected arguments");
    wchar_t exe[32768]{};need(GetModuleFileNameW(nullptr,exe,UINT(std::size(exe)))>0,"Executable path");
    auto start=[&](Channel& c,const wchar_t* mode){
        std::wstring cmd=L"\""+std::wstring(exe)+L"\" \""+c.name+L"\" "+std::to_wstring(GetCurrentProcessId())+L" "+mode;
        STARTUPINFOW si{};si.cb=sizeof(si);PROCESS_INFORMATION pi{};
        need(CreateProcessW(exe,cmd.data(),nullptr,nullptr,FALSE,CREATE_NO_WINDOW,nullptr,nullptr,&si,&pi),"Start peer");
        CloseHandle(pi.hThread);return pi.hProcess;
    };
    Channel channel(Session);Handle process;process.value=start(channel,L"frames");
    need(WaitForSingleObject(channel.acknowledged(),5000)==WAIT_OBJECT_0&&load(channel.state->consumer)>0,"Peer handshake");
    auto p=fixture(channel);
    auto bad=p;bad.identity.session[0]++;seal(bad);need(!channel.publish(bad),"Cross-session publication");
    bad=p;bad.viewport_x++;seal(bad);need(!channel.publish(bad),"Invalid viewport publication");
    bad=p;bad.flags=sfc_ue_output::Replay;seal(bad);need(!channel.publish(bad),"Replay entered normal mode");
    for(unsigned frame=1;frame<=4;++frame){
        p.identity.output=frame;p.identity.frame=18+frame;p.ready_value=p.ack_value=p.slot_epoch=frame;seal(p);
        need(channel.publish(p),"Publish reused slot");need(!channel.publish(p),"Overwrote occupied slot");
        need(!channel.request_retirement(1),"Retired an outstanding GPU lease");
        const ULONGLONG until=GetTickCount64()+5000;
        while(load(channel.state->slots[0].phase)!=Complete){
            need(GetTickCount64()<until,"Peer read deadline");WaitForSingleObject(channel.acknowledged(),10);
        }
        need(!channel.reclaim(0,frame-1),"Reclaimed before GPU read completion");
        need(!channel.reclaim(0,UINT64_MAX),"Device loss qualified read completion");
        need(channel.reclaim(0,frame),"Exact read completion");
        need(!channel.publish(p),"Reused epoch/timeline");
    }
    need(channel.request_retirement(1),"Drained retirement request");
    const ULONGLONG retirementDeadline=GetTickCount64()+5000;
    while(load64(channel.state->retire_completed)!=1){
        need(GetTickCount64()<retirementDeadline,"Retirement acknowledgement deadline");WaitForSingleObject(channel.acknowledged(),10);
    }
    p.identity.output=p.ready_value=p.ack_value=p.slot_epoch=5;seal(p);
    need(!channel.publish(p),"Republished a retired generation");
    p.resource_epoch=2;p.identity.target=2;p.width=1400;p.height=840;p.target_width=1600;p.target_height=900;seal(p);
    need(channel.publish(p),"New resource generation publication");
    const ULONGLONG finalDeadline=GetTickCount64()+5000;
    while(load(channel.state->slots[0].phase)!=Complete){
        need(GetTickCount64()<finalDeadline,"New generation read deadline");WaitForSingleObject(channel.acknowledged(),10);
    }
    need(channel.reclaim(0,5),"New generation read completion");
    need(WaitForSingleObject(process.value,5000)==WAIT_OBJECT_0,"Peer exit");DWORD code=1;
    need(GetExitCodeProcess(process.value,&code)&&code==0,"Peer rejected input");
    channel.stop();need(!channel.publish(p),"Stopped publication");
    Channel passive(Session);Handle peer;peer.value=start(passive,L"passive");
    need(WaitForSingleObject(passive.acknowledged(),5000)==WAIT_OBJECT_0,"Passive startup");
    passive.stop();need(WaitForSingleObject(peer.value,5000)==WAIT_OBJECT_0,"Passive cancellation");
    need(GetExitCodeProcess(peer.value,&code)&&code==0,"Passive peer exit");
    std::puts("PASS actual child-process raw export channel, 64-bit handles, reuse, retirement, stale generation rejection, passive stop and GPU completion-qualified reclamation");return 0;
}catch(const std::exception& e){std::fprintf(stderr,"%s\n",e.what());return 1;}}
