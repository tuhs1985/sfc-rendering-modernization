#include "../tools/m1_component/m1_live_bridge.h"
#include <iostream>
#include <cstdlib>
static sfc_m1::LiveBridge bridge;
void check_live(bool ok,const char* what){if(!ok){std::cerr<<what<<'\n';std::exit(1);}}
int wmain(int argc,wchar_t** argv){
    check_live(argc==3,"channel and generated output required");
    const std::wstring name=argv[1];
    check_live(sfc_m1::LiveBridge::name_ok(name),"name schema");
    check_live(!sfc_m1::LiveBridge::name_ok(L"Global\\anything"),"reject global namespace");
    check_live(bridge.start(name,argv[2]),"open creator session/start worker");
    sfc_m1::MeshIdentity id{};id.owner=7;id.thread=1;id.ship=2;id.visual=3;id.model=4;
    id.manager=0x10000;id.source=5;id.list=6;id.count=452;id.caller=0x0042E55D;id.elapsed=34;
    bridge.epochs=1;bridge.retired=false;bridge.assets[0].identity=id;
    bool bad=false,camera_changed=false;DWORD camera_reads=0;
    auto read=[&](DWORD address,void* output,DWORD bytes){
        std::memset(output,0,bytes);
        if(bytes==68 && (address==id.manager+0x6f4 || address==id.manager+0x6b0)) {
            auto* words=static_cast<DWORD*>(output);words[0]=words[5]=words[10]=words[15]=0x3f800000;
            if(bad)words[0]=0x7fc00000;
        }
        if(address==id.manager+0x628 && camera_changed && ++camera_reads==2)
            static_cast<DWORD*>(output)[3]=0x3f800000;
        return true;
    };
    bridge.observe(id,read,[]{return true;});check_live(bridge.sequence==1,"qualified transform published");
    bridge.observe(id,read,[]{return true;});check_live(bridge.sequence==1,"30Hz throttle");
    id.elapsed=68;bad=true;bridge.observe(id,read,[]{return true;});
    check_live(bridge.invalid==1 && bridge.sequence==1,"nonfinite update rejected without publication");
    bad=false;camera_changed=true;
    bridge.observe(id,read,[]{return true;});
    check_live(bridge.invalid==2 && bridge.sequence==1,"changed camera read-recheck rejects torn observation");
    bridge.epochs=0;bridge.retired=true;
    AcquireSRWLockExclusive(&bridge.mailbox);
    std::array<DWORD,sfc_m1::kLiveRecordWords> r{};r[1]=1;r[4]=1;
    bridge.offer(r); // Must drop, never wait for a receiver/worker.
    ReleaseSRWLockExclusive(&bridge.mailbox);
    check_live(bridge.dropped==1,"nonwaiting busy mailbox");
    for(DWORD i=0;i<12;++i){r[2]=i;r[3]=i*34;bridge.offer(r);Sleep(15);}
    bridge.epochs=1;bridge.active_slot=0;bridge.retired=false;bridge.assets[0].identity.owner=1;
    bridge.retire(2,12,408);check_live(!bridge.retired,"other owner cannot retire target");
    bridge.retire(1,12,408);check_live(bridge.retired,"selected epoch retirement");
    Sleep(30);check_live(bridge.stop(),"worker joined before unmap");
    check_live(!bridge.worker&&!bridge.mapping&&!bridge.view,"all native resources closed");
    std::cout<<"Live transport/worker/nonwaiting/retirement tests passed\n";
}
