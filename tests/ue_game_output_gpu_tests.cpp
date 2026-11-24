// Standalone GPU fixture. Synthetic upload/readback is not runtime pixel transport.
#include "../src/rendering/ue/ue_output_normalizer.h"
#include <d3d11_4.h>
#include <dxgi1_6.h>
#include <cstdio>
#include <vector>
#include <memory>
void check(bool ok,const char* why){if(!ok)throw std::runtime_error(why);}
void hr(HRESULT value,const char* why){check(SUCCEEDED(value),why);}
#include "../src/rendering/ue/ue_game_output_writer.h"
#include "../tools/remix_runtime/game_gpu_read_lease.h"
using Microsoft::WRL::ComPtr;

int consume(const wchar_t* mappingName,unsigned step,DWORD sourcePid){
    sfc_ue_export::Handle mapping;mapping.value=OpenFileMappingW(FILE_MAP_ALL_ACCESS,FALSE,mappingName);
    check(mapping.value!=nullptr,"Cross-process pool mapping");
    auto* base=static_cast<BYTE*>(MapViewOfFile(mapping.value,FILE_MAP_ALL_ACCESS,0,0,16*1024*1024));check(base!=nullptr,"Consumer pool view");
    auto* pool=reinterpret_cast<game_output::Pool*>(base+game_output::Offset);
    check(game_output::valid(pool->header,reinterpret_cast<DWORD*>(base)+4,sourcePid),"Consumer source/session");
    unsigned slot=2;for(unsigned n=0;n<2;++n)if(pool->slots[n].packet.source_frame==step&&pool->slots[n].state==output_wire::ready)slot=n;
    check(slot<2,"Consumer matching READY source frame");
    auto& out=pool->slots[slot];check(InterlockedCompareExchange(&out.state,output_wire::acquired,output_wire::ready)==output_wire::ready,"Cross-process lease acquire");
    ComPtr<IDXGIFactory4> factory;ComPtr<IDXGIAdapter> adapter;hr(CreateDXGIFactory1(IID_PPV_ARGS(&factory)),"Consumer DXGI");
    const LUID luid{out.packet.luid_low,out.packet.luid_high};hr(factory->EnumAdapterByLuid(luid,IID_PPV_ARGS(&adapter)),"Consumer exact GPU");
    ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context;
    hr(D3D11CreateDevice(adapter.Get(),D3D_DRIVER_TYPE_UNKNOWN,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&device,nullptr,&context),"Cross-process native GPU");
    ComPtr<ID3D11DeviceContext4> write4;hr(context.As(&write4),"Consumer fence context");
    game_gpu::ReadLease lease;lease.prepare(device.Get());const auto until=GetTickCount64()+5000;
    D3D11_TEXTURE2D_DESC d{};unsigned checked=0;
        for(unsigned plane=0;plane<3;++plane){
            ComPtr<ID3D11Texture2D> shared,staging;
            hr(device->OpenSharedResource(reinterpret_cast<HANDLE>(uintptr_t(out.packet.handles[plane])),IID_PPV_ARGS(&shared)),"Independent legacy GPU import");
            shared->GetDesc(&d);d.MiscFlags=d.BindFlags=0;d.Usage=D3D11_USAGE_STAGING;d.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
            hr(device->CreateTexture2D(&d,nullptr,&staging),"Consumer fixture readback");
            context->CopyResource(staging.Get(),shared.Get());lease.signal(write4.Get());context->Flush();while(!lease.retire()){check(GetTickCount64()<until,"Consumer GPU deadline");SwitchToThread();};
            D3D11_MAPPED_SUBRESOURCE map{};hr(context->Map(staging.Get(),0,D3D11_MAP_READ,0,&map),"Consumer completed read");
            bool good=true;
            for(unsigned y=0;y<out.packet.height;++y)for(unsigned x=0;x<out.packet.width;++x){
                const bool inside=x>=3&&x<14&&y>=2&&y<9;const unsigned index=inside?(y-2)*11+x-3:0;
                const auto bits=reinterpret_cast<const uint32_t*>(static_cast<BYTE*>(map.pData)+y*map.RowPitch)[x];
                if(!plane)good&=bits==(inside?(index?0xff000000u|(step*37u<<8):0xff000000u):0);else if(plane==2)good&=bits==(inside?3u:0u);
                else{float value;std::memcpy(&value,&bits,4);good&=std::abs(value-(inside?1.f-2.f/(120.f+step):-1234.f))<1e-6f;}++checked;
            }
            context->Unmap(staging.Get(),0);check(good,"Colour/depth/owner pixels mismatched current source");
        }

    // Deliberately keep ACQUIRED: parent verifies two occupied leases cannot be overwritten.
    check(checked==out.packet.width*out.packet.height*3,"Consumer pixel count");UnmapViewOfFile(base);return 0;
}
int wmain(int argc,wchar_t** argv){try{
    if(argc==5&&std::wstring(argv[1])==L"--consumer")return consume(argv[2],unsigned(std::stoul(argv[3])),DWORD(std::stoul(argv[4])));

    const DWORD pid=GetCurrentProcessId();const std::array<DWORD,4> session{1,2,3,4};
    const wchar_t* name=L"Local\\SFCBridge_00000001000000020000000300000004";
    sfc_ue_export::Handle mapping;
    mapping.value=CreateFileMappingW(INVALID_HANDLE_VALUE,nullptr,PAGE_READWRITE,0,16*1024*1024,name);
    check(mapping.value&&GetLastError()!=ERROR_ALREADY_EXISTS,"Unique fixture source mapping");
    auto* base=static_cast<BYTE*>(MapViewOfFile(mapping.value,FILE_MAP_ALL_ACCESS,0,0,16*1024*1024));
    check(base!=nullptr,"Fixture source view");
    auto* common=reinterpret_cast<DWORD*>(base);common[0]=0x31424c53;common[1]=scene_capacity::Version;common[2]=16*1024*1024;common[3]=1;
    std::memcpy(common+4,session.data(),16);
    auto* scene=new(base+multi_scene::Offset)multi_scene::Store();scene->header.pid=pid;scene->header.bytes=sizeof(*scene);std::memcpy(scene->header.session,session.data(),16);
    auto* live=new(base+live_owner::Offset)live_owner::Store();live->header.pid=pid;live->header.bytes=sizeof(*live);std::memcpy(live->header.session,session.data(),16);
    SetEnvironmentVariableW(L"SFC_REMIX_CALIBRATION_SCENE",name);SetEnvironmentVariableW(L"SFC_D3D9_GAME_OUTPUT",L"1");
    SetEnvironmentVariableW(L"SFC_D3D9_SYNC_BUFFER",L"1");SetEnvironmentVariableW(L"SFC_D3D9_MULTISCENE",L"1");
    SetEnvironmentVariableW(L"SFC_NATIVE_RESOLUTION",L"1");
    // Fresh subprocess invocation has no replacement/gate environment.
    check(!replacement::requested()&&!native_gate::requested(),"Fixture cannot enable native suppression");
    sfc_ue_game::Writer writer(false);
    output_wire::Packet legacy{};game_output::Metadata metadata{};
    sfc_ue_export::Packet p{};check(!writer.admit(p,legacy,metadata),"Passive output admitted without source assets");
    auto& asset=scene->assets[4];asset.guard=2;auto& a=asset.packet;
    a.id=a.path_id=a.revision=5;a.owner=3;a.model=53;a.source=59;a.geometry_bytes=16;a.content[0]=7;a.replay_hash=a.textures_hash=1;a.checksum=multi_scene::checksum(a);
    live->header.selected=live_owner::selection(3,5);
    output_target::Notice notice{};notice.pid=pid;std::memcpy(notice.session,session.data(),16);
    notice.width=19;notice.height=13;notice.device=notice.generation=1;notice.observed=1;
    auto& target=*reinterpret_cast<output_target::Store*>(base+output_target::Offset);output_target::publish(target,notice);
    ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context;
    hr(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&device,nullptr,&context),"Fixture GPU");
    ComPtr<IDXGIDevice> dxgi;ComPtr<IDXGIAdapter> adapter;DXGI_ADAPTER_DESC ad{};
    hr(device.As(&dxgi),"Fixture DXGI");hr(dxgi->GetAdapter(&adapter),"Fixture adapter");hr(adapter->GetDesc(&ad),"Fixture adapter identity");
    ComPtr<ID3D11DeviceContext4> write4;hr(context.As(&write4),"Writer fence context");
    game_gpu::ReadLease writeLease;writeLease.prepare(device.Get());
    auto wait=[](game_gpu::ReadLease& lease){const auto until=GetTickCount64()+5000;while(!lease.retire()){check(GetTickCount64()<until,"Fixture GPU deadline");SwitchToThread();}};
    sfc_ue_output::Normalizer normalizer(device.Get());
    auto* pool=reinterpret_cast<game_output::Pool*>(base+game_output::Offset);
    int held[2]{-1,-1};unsigned checked=0;
    for(unsigned step=1;step<=8;++step){
        if(step==7){
            check(!writer.retire(),"Target generation retired before native drain");
            context->ClearState();InterlockedExchange(&pool->header.stopped,1);check(writer.retire(),"Native generation drain");
            notice.width=23;notice.height=17;notice.generation=2;output_target::publish(target,notice);
        }
        auto frame=std::make_unique<multi_scene::Frame>();frame->sequence=step;frame->offered=1;frame->frame=step;frame->anchor=3;frame->revision=5;frame->count=1;
        auto& row=frame->rows[0];row[1]=3;row[2]=step;row[4]=1;row[5]=53;row[6]=59;row[7]=5;row[48]=1;row[94]=step;
        for(unsigned o:{8u,49u}){row[o]=row[o+5]=row[o+10]=row[o+15]=0x3f800000;row[o+16]=0x100;}
        const float proj[16]{2,0,0,0,0,3,0,0,0,0,-1,-2,0,0,-1,0};std::memcpy(row.data()+66,proj,64);
        const float viewport[6]{3,2,11,7,5.5,3.5};std::memcpy(row.data()+83,viewport,24);frame->checksum=multi_scene::checksum(*frame);
        scene->frames[step%8].packet=*frame;scene->frames[step%8].guard=2;
        sfc_source_view::Row source{};std::memcpy(source.data(),row.data(),sizeof(source));
        p={};p.flags=sfc_ue_output::SourceFrame|sfc_ue_output::SourceSequence;p.producer=p.consumer=pid;
        p.adapter_luid=(uint64_t(uint32_t(ad.AdapterLuid.HighPart))<<32)|ad.AdapterLuid.LowPart;
        p.width=11;p.height=7;p.viewport_x=3;p.viewport_y=2;p.target_width=notice.width;p.target_height=notice.height;p.p22=-1;p.p23=-2;
        p.identity.session=sfc_ue_game::session64(session);p.identity.asset[0]=7;p.identity.owner_epoch=3;p.identity.revision=5;
        p.identity.frame=p.identity.sequence=p.identity.output=step;p.identity.camera_pose=sfc_ue_game::camera_hash(source);p.identity.cohort=frame->checksum;
        p.resource_epoch=p.identity.target=notice.generation;p.identity.device=p.identity.activation=1;
        auto wrong=p;wrong.identity.camera_pose++;check(!writer.admit(wrong,legacy,metadata),"Wrong pose entered game pool");
        check(writer.admit(p,legacy,metadata),"Independent native source admission");
        const int slot=writer.reserve(device.Get(),legacy,metadata,normalizer);
        if(step==3){check(slot<0&&pool->header.published==2&&pool->header.overwritten==0,"Held native outputs overwritten");
            InterlockedExchange(&pool->slots[held[0]].state,output_wire::idle);InterlockedExchange(&pool->slots[held[1]].state,output_wire::idle);continue;}
        check(slot>=0&&pool->slots[slot].state==game_output::Writing,"Pool reservation premature readiness");
        std::vector<uint32_t> colours(77,0xff000000u|(step*37u<<8));std::vector<float> depths(77,120.f+step);
        colours[0]=0xff000000u;
        ComPtr<ID3D11Texture2D> colour,depth;
        D3D11_TEXTURE2D_DESC d{};d.Width=11;d.Height=7;d.MipLevels=d.ArraySize=d.SampleDesc.Count=1;d.Format=DXGI_FORMAT_B8G8R8A8_UNORM;d.BindFlags=D3D11_BIND_SHADER_RESOURCE;
        D3D11_SUBRESOURCE_DATA bytes{colours.data(),44,0};hr(device->CreateTexture2D(&d,&bytes,&colour),"Fixture colour");
        d.Format=DXGI_FORMAT_R32_FLOAT;bytes.pSysMem=depths.data();hr(device->CreateTexture2D(&d,&bytes,&depth),"Fixture depth");
        const auto inputs=normalizer.bind_inputs(colour.Get(),depth.Get());normalizer.draw(context.Get(),inputs,writer.target(unsigned(slot)),3,2,-1,-2,3);
        writeLease.signal(write4.Get());context->Flush();wait(writeLease);
        check(pool->slots[slot].state==game_output::Writing,"Pool READY before explicit GPU completion publication");
        writer.publish(slot,legacy,metadata);auto& out=pool->slots[slot];check(out.state==output_wire::ready,"Completed output not READY");
        check(out.packet.source_frame==step&&game_output::metadata(out).source_sequence==step&&out.packet.source_state_hash==p.identity.cohort,"Published source provenance lost");
        check(argc==2,"Supply the x86 native consumer executable");
        std::wstring command=L"\""+std::wstring(argv[1])+L"\" --consumer \""+name+L"\" "+std::to_wstring(step)+L" "+std::to_wstring(pid);
        STARTUPINFOW startup{sizeof(startup)};PROCESS_INFORMATION process{};
        check(CreateProcessW(argv[1],command.data(),nullptr,nullptr,FALSE,CREATE_NO_WINDOW,nullptr,nullptr,&startup,&process),"Start x86 native consumer");
        CloseHandle(process.hThread);const auto result=WaitForSingleObject(process.hProcess,10000);
        if(result!=WAIT_OBJECT_0){TerminateProcess(process.hProcess,9);WaitForSingleObject(process.hProcess,1000);}
        DWORD code=1;GetExitCodeProcess(process.hProcess,&code);CloseHandle(process.hProcess);
        if(result!=WAIT_OBJECT_0||code||out.state!=output_wire::acquired)std::fprintf(stderr,"Native consumer step %u, exit %lu, state %ld\n",step,code,out.state);
        check(result==WAIT_OBJECT_0&&code==0&&out.state==output_wire::acquired,"Cross-process GPU read/held lease");checked+=p.target_width*p.target_height*3;
        if(step<=2)held[step-1]=slot;else InterlockedExchange(&out.state,output_wire::idle);
    }
    check(writer.published==7&&writer.busy==1,"Publication/busy accounting");
    check(!writer.retire(),"Resources retired before native consumer drain");
    context->ClearState();InterlockedExchange(&pool->header.stopped,1);check(writer.retire(),"Drained generation not retired");
    writer.retire();UnmapViewOfFile(base);
    std::printf("PASS %u independent GPU pixel checks, passive/late identity, exact source, GPU-complete READY, held leases/busy skip and generation drain\n",checked);return 0;
}catch(const std::exception& e){std::fprintf(stderr,"%s\n",e.what());return 1;}}
