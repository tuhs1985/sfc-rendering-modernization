#define main legacy_mesh_tests_main
#include "m1_mesh_export_tests.cpp"
#undef main
#include "../tools/m1_component/m1_live_scene.h"
static LiveScene scene;
static LiveMeshPacket large_packet;
static LiveScene journal;
int wmain(int argc,wchar_t** argv){
    std::array<DWORD,96> event{};event[1]=1;event[7]=1;event[4]=1;
    journal.offer(0,event);check_mesh(journal.lifecycleWrite==0,"default-off lifecycle journal");
    journal.lifecycleCapture=true;
    for(DWORD n=0;n<300;++n){event[4]=n%2?1:2;journal.offer(0,event);}
    check_mesh(journal.lifecycleWrite==256 && journal.lifecycleDropped==44,"fixed lifecycle queue never overwrites unread transition");
    check_mesh(journal.lifecycle[0][4]==2 && journal.lifecycle[255][4]==1,"transition ordering preserved through saturation");
    check_mesh(argc==3,"scene channel and output required");
    check_mesh(scene.start(argv[1],argv[2]),"scene worker start/current-user mapping");
    Memory x;x.id.frame=1;x.id.elapsed=34;
    x.word(0x2154,0x50000);x.word(0x8000,0x21);x.word(0x8014,1);x.word(0x8018,0);x.word(0x801c,2);x.word(0x8020,8);
    std::memcpy(x.data.data()+0x2014,"Assets/Models/test/test.mod",27);
    std::memcpy(x.data.data()+0x50000,"test_a\0\0test_ai",15);
    x.word(0x60000,0x00795C54);x.word(0x6000c,0x70000);x.word(0x60020,0x71000);
    std::memcpy(x.data.data()+0x70008,"Assets/Models/test/test_a.bmp",29);
    std::memcpy(x.data.data()+0x71008,"Assets/Models/test/test_ai.bmp",30);
    x.word(0x7f60,0x72000);x.word(0x7f64,0x73000);x.word(0x72004,123);x.word(0x73004,456);
    x.word(x.id.manager+0x1ed0,1);
    auto read=[&](auto a,auto* dst,auto n){
        if(a==0x008CC620 && n==4){DWORD registry=0x60000;std::memcpy(dst,&registry,4);return true;}
        return x.read(a,dst,n);
    };
    auto id=x.id;scene.observe(id,read,[]{return true;});
    check_mesh(scene.capture_attempts==1 && scene.capture_failures==0,"fresh non-Klingon capture");
    id.owner=2;scene.observe(id,read,[]{return true;});
    check_mesh(scene.capture_attempts==1,"one asset attempt per rendered frame");
    ++id.frame;id.elapsed=68;scene.observe(id,read,[]{return true;});
    check_mesh(scene.capture_attempts==2 && scene.owners[1].revision==2,"two distinct owners qualify independently");
    const auto seq=scene.owners[1].sequence;scene.observe(id,read,[]{return true;});
    check_mesh(scene.owners[1].sequence==seq,"per-owner 30Hz throttle");
    AcquireSRWLockExclusive(&scene.mailbox);std::array<DWORD,96> r{};scene.offer(1,r);ReleaseSRWLockExclusive(&scene.mailbox);
    check_mesh(scene.dropped==1,"nonwaiting mailbox");
    // Four transfer slots without acknowledgements: later assets remain bounded.
    for(DWORD owner=3;owner<=6;++owner){id.owner=owner;++id.frame;id.elapsed+=34;scene.observe(id,read,[]{return true;});Sleep(30);}
    check_mesh(scene.capture_failures==0 && scene.revisions==6,"bounded queued asset captures");
    x.word(0x2124,100);++id.frame;id.elapsed+=34;scene.observe(id,read,[]{return true;});
    check_mesh(scene.revisions==7,"LOD metadata change creates a fresh revision even with same pointers");
    Sleep(300);scene.retire(1,20,700);Sleep(100);
    check_mesh(scene.owners[0].retired,"owner retirement");
    const auto previous_sequence=scene.owners[0].sequence;
    for(DWORD i=scene.owner_count;i<32;++i){scene.owners[i].identity.owner=100+i;scene.owners[i].retired=true;}
    scene.owner_count=32;id.owner=999;++id.frame;id.elapsed=800;scene.observe(id,read,[]{return true;});
    check_mesh(scene.owners[0].identity.owner==999 && scene.owners[0].sequence>previous_sequence,
        "retired owner slot reused with new epoch and monotonic sequence");
    // Maximum triangular packet stays below 2MiB; reject count overflow before reads.
    auto& h=large_packet.header;h[MeshMagic]=0x314d4653;h[MeshVersion]=1;h[MeshVertices]=65536;
    h[MeshPolygons]=8192;h[MeshCorners]=32768;h[MeshSources]=256;
    check_mesh(large_packet.bounds() && large_packet.byte_size()<2*1024*1024,"expanded packet byte/storage ceiling");
    h[MeshCorners]=32769;check_mesh(!large_packet.bounds(),"expanded corner bound");
    // Exact-frame calibration observes BEFORE the independent 30Hz stream throttle.
    static sfc_calibration::Mailbox calibration;calibration.active=1;scene.calibration=&calibration;
    ++id.frame;++id.elapsed;sfc_calibration::begin(&calibration,id.frame);
    scene.observe(id,read,[]{return true;});sfc_calibration::Snapshot snap;
    check_mesh(sfc_calibration::read(&calibration,snap)&&snap.frame==id.frame&&snap.owner[0][1]==999,
        "current-frame observation bypasses 30Hz throttle");
    check_mesh(snap.owner[0][47]==GetCurrentThreadId(),"calibration render-thread provenance");
    scene.sourceTiming=true;++id.frame;sfc_calibration::begin(&calibration,id.frame);
    scene.observe(id,read,[]{return true;});
    check_mesh(sfc_calibration::read(&calibration,snap)&&snap.owner[0][93]==sfc_calibration::TimingMagic&&
        (snap.owner[0][89]||snap.owner[0][90])&&snap.owner[0][89]==snap.owner[0][91]&&snap.owner[0][90]==snap.owner[0][92],
        "opt-in source QPC annotation before independent stream throttle");
    static live_owner::Store directStore;directStore.header.bytes=sizeof(directStore);
    directStore.header.selected=static_cast<LONG64>(live_owner::selection(id.owner,scene.owners[0].revision));
    scene.directSource.store=&directStore;++id.frame;sfc_calibration::begin(&calibration,id.frame);scene.directSource.begin(id.frame);
    scene.observe(id,read,[]{return true;});live_owner::Packet raw;uint64_t latest=0;DWORD malformed=0;
    check_mesh(sfc_calibration::read(&calibration,snap)&&live_owner::sequence(snap.owner[0])==1&&
        live_owner::take(directStore.input,directStore.header,raw,latest,malformed)&&raw.row==snap.owner[0]&&!malformed,
        "live raw publication precedes30Hz throttle and binds exact calibration row");
    if(scene.lightTuning){id.owner=2;id.elapsed=100000;++id.frame;
        const auto old=scene.owners[1].sequence;
        scene.observe(id,read,[]{return true;});
        check_mesh(scene.owners[1].sequence>old,"tuning stream survives90seconds");}
    if(scene.lifecycleCapture){
        // More than the old100records, then coalesced retirement/reappearance.
        // No executable death flag is invented: these are observation epochs.
        std::array<DWORD,96> later{};later[1]=2;later[4]=1;later[7]=2;
        for(DWORD n=0;n<140;++n){later[2]=500+n;later[3]=100100+n*50;scene.offer(1,later);Sleep(15);}
        scene.retire(2,640,107100);
        later[1]=1001;later[2]=641;later[3]=107150;later[7]=8;scene.offer(1,later);
    }
    Sleep(100);check_mesh(scene.stop(),"worker drains and joins before unmap");
    check_mesh(!calibration.active,"calibration deactivated before producer storage removed");
    check_mesh(directStore.header.stopped==1,"live raw storage stopped before source view removal");
    check_mesh(!scene.worker&&!scene.mapping&&!scene.view,"native scene handles closed");
    std::cout<<"Fresh scene native capture/multi-owner/bounds/worker tests passed\n";
}
