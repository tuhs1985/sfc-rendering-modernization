// Explicit standalone native-consumer fixture. Never loaded by normal play.
#include <d3d11_4.h>
#include <dxgi1_6.h>
#include <wrl/client.h>
#include <filesystem>
#include <fstream>
#include <cstdio>
#include <array>
#include <string>
#include <memory>
#include "../tools/d3d9_proof/multi_scene_wire.h"
#include "../tools/d3d9_proof/game_output_wire.h"
#include "../tools/remix_runtime/game_gpu_read_lease.h"
using Microsoft::WRL::ComPtr;
void need(bool v,const char* why){if(!v)throw std::runtime_error(why);}
void hr(HRESULT v,const char* why){need(SUCCEEDED(v),why);}
 #include "ue_native_effects_fixture.h"
int wmain(int argc,wchar_t** argv){try{
    need(argc==6||(argc==7&&std::wstring(argv[6])==L"--native-insertion"),"Consumer fixture arguments");
    const bool insertion=argc==7;
    std::unique_ptr<UENativeEffects> effects;
    const auto source=DWORD(std::stoul(argv[2]));const auto count=std::stoul(argv[4]);need(count>=4&&count<=10000,"Bounded fixture");
    const std::filesystem::path output(argv[3]);std::filesystem::create_directories(output);
    HANDLE completed=OpenEventW(EVENT_MODIFY_STATE,FALSE,argv[5]);need(completed!=nullptr,"Fixture read event");
    HANDLE process=OpenProcess(SYNCHRONIZE,FALSE,source);need(process!=nullptr,"Consumer parent");
    HANDLE mapping=OpenFileMappingW(FILE_MAP_ALL_ACCESS,FALSE,argv[1]);need(mapping!=nullptr,"Consumer mapping");
    auto* base=static_cast<BYTE*>(MapViewOfFile(mapping,FILE_MAP_ALL_ACCESS,0,0,16*1024*1024));need(base!=nullptr,"Consumer view");
    auto* pool=reinterpret_cast<game_output::Pool*>(base+game_output::Offset);
    ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context;ComPtr<ID3D11DeviceContext4> context4;
    std::array<ComPtr<ID3D11Texture2D>,3> images,staging;game_gpu::ReadLease lease;
    uint64_t last=0;unsigned received=0,dumps=0;const auto deadline=GetTickCount64()+120000;
    while(received<count){
        need(GetTickCount64()<deadline&&WaitForSingleObject(process,0)==WAIT_TIMEOUT,"Consumer source/deadline");
        if(!pool->header.ready){Sleep(1);continue;}
        need(game_output::valid(pool->header,reinterpret_cast<DWORD*>(base)+4,source)&&!pool->header.error&&!pool->header.stopped,"Consumer active pool identity");
        unsigned chosen=2;uint64_t next=UINT64_MAX;
        for(unsigned s=0;s<2;++s)if(InterlockedCompareExchange(&pool->slots[s].state,0,0)==output_wire::ready&&pool->slots[s].packet.sequence<next){chosen=s;next=pool->slots[s].packet.sequence;}
        if(chosen==2){Sleep(1);continue;}
        auto& slot=pool->slots[chosen];if(InterlockedCompareExchange(&slot.state,output_wire::acquired,output_wire::ready)!=output_wire::ready)continue;
        const auto packet=slot.packet;const auto meta=game_output::metadata(slot);
        need(packet.checksum==output_wire::checksum(packet)&&packet.sequence>last&&game_output::valid(meta,reinterpret_cast<DWORD*>(base)+4),"Consumer exact packet/session sequence");
        if(!device){
            ComPtr<IDXGIFactory4> factory;ComPtr<IDXGIAdapter> adapter;
            hr(CreateDXGIFactory1(IID_PPV_ARGS(&factory)),"Consumer factory");
            const LUID luid{packet.luid_low,packet.luid_high};hr(factory->EnumAdapterByLuid(luid,IID_PPV_ARGS(&adapter)),"Exact UE GPU");
            hr(D3D11CreateDevice(adapter.Get(),D3D_DRIVER_TYPE_UNKNOWN,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&device,nullptr,&context),"Native consumer device");
            hr(context.As(&context4),"Consumer GPU fence");lease.prepare(device.Get());
        }
        const bool dump=packet.sequence<=2||packet.sequence>=count-1;
        for(unsigned plane=0;plane<3;++plane){
            images[plane].Reset();hr(device->OpenSharedResource(reinterpret_cast<HANDLE>(uintptr_t(packet.handles[plane])),IID_PPV_ARGS(&images[plane])),"Native import");
            if(!staging[plane]){
                D3D11_TEXTURE2D_DESC d{};images[plane]->GetDesc(&d);
                need(d.Width==packet.width&&d.Height==packet.height,"Imported extent");
                d.MiscFlags=d.BindFlags=0;d.Usage=D3D11_USAGE_STAGING;d.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
                hr(device->CreateTexture2D(&d,nullptr,&staging[plane]),"Fixture staging");
            }
            context->CopyResource(staging[plane].Get(),images[plane].Get());
        }
        if(insertion){
            need(game_output::valid_layout(*pool)&&game_output::native_pixels(*pool),"Explicit native-pixel pool required");
            if(!effects){effects=std::make_unique<UENativeEffects>();effects->prepare(device.Get(),context.Get(),packet.width,packet.height);}
            ship_triplet::Key key{};std::memcpy(key.session,pool->header.session,16);std::memcpy(key.sourceSession,meta.source_session,16);std::memcpy(key.asset,pool->asset,32);
            key.owner=key.objectId=packet.owner;key.revision=packet.revision;key.frame=DWORD(packet.source_frame);key.resourceEpoch=DWORD(packet.resource_epoch);
            key.sourcePid=source;key.pose=key.camera=packet.source_state_hash;key.width=packet.width;key.height=packet.height;key.depthConvention=1;
            auto frame=std::make_unique<multi_scene::Frame>();
            need(multi_scene::read(*reinterpret_cast<multi_scene::Store*>(base+multi_scene::Offset),key.frame,meta.source_sequence,*frame)&&frame->checksum==packet.source_state_hash,"Native fixture exact source seal");
            const auto& row=frame->rows[0];float viewport[4]{};std::memcpy(viewport,row.data()+83,16);
            for(unsigned n=0;n<4;++n)key.viewport[n]=uint32_t(viewport[n]);
            ID3D11Texture2D* sourceImages[]{images[0].Get(),images[1].Get(),images[2].Get()};effects->draw(sourceImages,key);
        }
        lease.signal(context4.Get());context->Flush();while(!lease.retire()){need(GetTickCount64()<deadline,"Consumer GPU completion");SwitchToThread();}
        if(effects){
            ID3D11Texture2D* refs[]{staging[0].Get(),staging[1].Get(),staging[2].Get()};effects->verify(refs,packet.owner);
        }
        if(dump){
            need(++dumps<=4,"Bounded diagnostic readback");const auto prefix=output/std::to_wstring(packet.sequence);
            for(unsigned plane=0;plane<3;++plane){
                D3D11_MAPPED_SUBRESOURCE map{};hr(context->Map(staging[plane].Get(),0,D3D11_MAP_READ,0,&map),"Fixture map");
                std::ofstream file(prefix.wstring()+L"-"+std::to_wstring(plane)+L".raw",std::ios::binary);
                for(unsigned y=0;y<packet.height&&file;++y)file.write(static_cast<const char*>(map.pData)+y*map.RowPitch,packet.width*4);
                context->Unmap(staging[plane].Get(),0);need(bool(file),"Fixture write");
            }
            std::ofstream record(prefix.wstring()+L".packet",std::ios::binary);record.write(reinterpret_cast<const char*>(&packet),sizeof(packet));
            std::ofstream identity(prefix.wstring()+L".metadata",std::ios::binary);identity.write(reinterpret_cast<const char*>(&meta),sizeof(meta));
        }
        for(auto& image:images)image.Reset();InterlockedExchange(&slot.state,output_wire::idle);last=packet.sequence;++received;InterlockedIncrement(&pool->stats.drawn);SetEvent(completed);
    }
    std::ofstream summary(output/L"completed.txt");summary<<received;context->ClearState();UnmapViewOfFile(base);CloseHandle(mapping);CloseHandle(process);CloseHandle(completed);
    std::puts("PASS actual x86 native-pool imports, GPU read completion and lease release");return 0;
}catch(const std::exception& e){std::fprintf(stderr,"Native pool fixture: %s\n",e.what());return 1;}}
