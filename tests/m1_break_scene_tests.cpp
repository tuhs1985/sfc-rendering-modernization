#define main legacy_mesh_tests_main
#include "m1_mesh_export_tests.cpp"
#undef main
#include "../tools/m1_component/m1_live_scene.h"
static LiveScene scene;
static live_owner::Store direct;
static multi_scene::Store cohort;
int wmain(int argc,wchar_t** argv){
    check_mesh(argc==3,"break channel/output required");
    check_mesh(scene.start(argv[1],argv[2]),"actual scene transport start");
    scene.persistent=true;scene.breakEnabled=true;scene.directSource.store=&direct;scene.cohort.store=&cohort;
    Memory x;x.word(0x2000,0x7985a4);x.word(0x302c,1);x.word(0x3030,0x19000);x.word(0x3034,2);
    x.word(0x19000,1);x.word(0x19004,2);x.word(0x2154,0x50000);
    constexpr char modelName[]="Assets/Models/test/test_brk.mod";
    std::memcpy(x.data.data()+0x2014,modelName,sizeof(modelName));
    std::memcpy(x.data.data()+0x50000,"test_a\0\0test_ai",15);
    x.word(0x8000,35);x.word(0x8014,1);x.word(0x8018,0);x.word(0x801c,2);x.word(0x8020,8);
    for(unsigned i=0;i<9;++i)x.word(0x8000+255*36+i*4,*reinterpret_cast<DWORD*>(x.data.data()+0x8000+i*4));
    x.word(0x60000,0x795c54);x.word(0x6000c,0x70000);x.word(0x60020,0x71000);
    std::memcpy(x.data.data()+0x70008,"Assets/Models/test/test_a.bmp",29);
    std::memcpy(x.data.data()+0x71008,"Assets/Models/test/test_ai.bmp",30);
    x.word(0x7f60,0x72000);x.word(0x7f64,0x73000);x.word(0x72004,123);x.word(0x73004,456);
    x.word(x.id.manager+0x1ed0,1);
    auto wordFloat=[&](DWORD address,float value){DWORD bits=0;memcpy(&bits,&value,4);x.word(address,bits);};
    std::array<DWORD,40> camera{};
    auto setFloat=[&](unsigned index,float value){memcpy(camera.data()+index,&value,4);};
    for(unsigned i:{0u,5u,10u,15u})setFloat(i,1);camera[16]=0x100;
    setFloat(17,1);setFloat(22,1920.f/1080.f);setFloat(27,-101.f/99.f);setFloat(28,-200.f/99.f);setFloat(31,-1);
    setFloat(36,1920);setFloat(37,1080);setFloat(38,960);setFloat(39,540);
    memcpy(x.data.data()+x.id.manager+0x628,camera.data(),68);
    memcpy(x.data.data()+x.id.manager+0x55c,camera.data()+17,68);
    memcpy(x.data.data()+x.id.manager+0x75c,camera.data()+34,24);
    for(DWORD child:{0x18000u,0x18400u}){
        x.word(child,0x7972b4);x.word(child+0x24,1);x.word(child+0x9c,0x2000);x.word(child+0xa0,child==0x18000?0:1);
        for(unsigned i:{0u,5u,10u,15u})wordFloat(child+0xa4+i*4,1);
        x.word(child+0xe4,0x100);wordFloat(child+0x3c,-10);
    }
    auto read=[&](std::uint32_t a,void* out,std::size_t n){
        if(a==0x8cc620&&n==4){DWORD value=0x60000;memcpy(out,&value,4);return true;}
        if(n==4&&(a==0x797278||a==0xc6c004||a==0xc6a004)){
            const float value=a==0x797278?12582912.f:(a==0xc6c004?1.f:0.f);memcpy(out,&value,4);return true;}
        return x.read(a,out,static_cast<std::uint32_t>(n));
    };
    scene.breakBorn(0x18000,7,0x2000,0);scene.breakBorn(0x18400,7,0x2000,1);
    check_mesh(scene.owner_count==2&&scene.owners[0].identity.owner!=scene.owners[1].identity.owner,"independent child epochs");
    const auto owner=scene.owners[0].identity.owner;
    direct.header.selected=static_cast<LONG64>(live_owner::selection(owner,1));
    const auto original=x.data;
    scene.observeBreak(0x18000,x.id.manager,1,0x10000,1,1,read);
    scene.observeBreak(0x18400,x.id.manager,1,0x10004,1,1,read);
    check_mesh(scene.revisions==1&&scene.owners[1].revision==0,"one capture per source frame; postponed child remains native");
    scene.updatePersistent(x.id.manager,1,1,read);
    check_mesh(scene.pending[0][4]==1&&scene.pending[0][7]==1,"first ready piece is discoverable without34ms wait");
    scene.observeBreak(0x18400,x.id.manager,1,0x10004,2,2,read);
    scene.updatePersistent(x.id.manager,2,2,read);
    check_mesh(scene.revisions==2&&scene.cohort.pending.count==2,"two pieces in common-camera publication");
    check_mesh(scene.cohort.pending.rows[0][2]==2&&scene.pending[0][2]==1,"functional pose publication is not diagnostic-rate limited");
    DWORD count=0,primary=0,secondary=0;
    auto* submission=scene.breakSubmission(0x18400,scene.owners[1].breakEpoch,x.id.manager,count,primary,secondary,read);
    check_mesh(submission&&count==1&&primary==0x10004&&!secondary,"piece-specific primary slice;empty secondary preserved");
    x.word(0x3018,0x20000);
    check_mesh(scene.breakSubmission(0x18400,scene.owners[1].breakEpoch,x.id.manager,count,primary,secondary,read)&&secondary==0x20004,"secondary uses same qualified partition offset");
    check_mesh(!scene.breakSubmission(0x18400,999,x.id.manager,count,primary,secondary,read),"stale child epoch cannot authorize suppression");
    x.word(0x3018,0);
    check_mesh(x.data==original,"capture/transport leave source bytes unchanged");
    scene.retire(7,3,100);wordFloat(0x18034,4);
    scene.updatePersistent(x.id.manager,3,100,read);
    check_mesh(scene.breaks.entries[0].world[3]==4&&scene.cohort.pending.count==2,"offscreen simulation motion survives parent retirement");
    check_mesh(scene.capture_attempts==2,"offscreen update reuses geometry");
    const auto old=scene.owners[0].breakEpoch;
    scene.breakRetire(0x18000,4,140);scene.updatePersistent(x.id.manager,4,140,read);
    check_mesh(scene.cohort.pending.count==1,"retired child omitted independently");
    scene.breakBorn(0x18000,8,0x2000,0);
    check_mesh(!scene.breaks.retire(0x18000,old)&&scene.owners[0].identity.owner!=owner&&scene.owners[0].revision==0,"pointer reuse cannot revive old epoch or asset");
    Sleep(300);check_mesh(scene.stop(),"worker drain before storage release");
    check_mesh(!scene.worker&&!scene.view&&!scene.mapping,"all source handles closed");
    std::cout<<"Break scene transport/lifetime PASS\n";
}
