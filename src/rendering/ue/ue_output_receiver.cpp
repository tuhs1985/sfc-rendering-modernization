// UE backend receiver worker. No SFC hooks or CPU pixel transport.
// Optional bounded staging files belong only to standalone qualification.
#include "ue_export_channel.h"
#include "ue_output_normalizer.h"
#include <d3d11_4.h>
#include <dxgi1_6.h>
#include <filesystem>
#include <fstream>
#include <cstdio>
#include <vector>
using Microsoft::WRL::ComPtr;
namespace wire=sfc_ue_export;
void need(bool ok,const char* why){if(!ok)throw std::runtime_error(why);}
void hr(HRESULT result,const char* why){if(FAILED(result)){std::fprintf(stderr,"%s: %08lx\n",why,static_cast<unsigned long>(result));throw std::runtime_error(why);}}
void check(bool ok,const char* why){need(ok,why);}
#include "ue_game_output_writer.h"
struct Receiver {
    ComPtr<ID3D11Device5> device;ComPtr<ID3D11DeviceContext4> context;
    ComPtr<ID3D11Fence> ready,ack;
    wire::Handle parent,event;
    std::unique_ptr<sfc_ue_output::Normalizer> normalizer;
    std::unique_ptr<sfc_ue_game::Writer> gameOutput;
    // One worker consumes sequentially. A single diagnostic staging triplet is
    // enough; duplicating it per slot would exceed the 1080p output budget.
    std::array<ComPtr<ID3D11Texture2D>,3> staging;
    struct Slot {
        bool initialized=false;
        wire::Packet admitted;
        std::array<ComPtr<ID3D11Texture2D>,2> sources;
        std::array<ComPtr<ID3D11Texture2D>,3> outputs;
        sfc_ue_output::Normalizer::Inputs input;
        sfc_ue_output::Normalizer::Targets target;
    } slots[2];
    uint64_t readyHandle=0,ackHandle=0,luid=0,lastFence=0;
    unsigned diagnosticsWritten=0;
    std::filesystem::path diagnosticFolder;
    bool replay=false;
    std::wstring fixture;
    uint64_t lastOutput=4;
    explicit Receiver(DWORD pid,LUID expected,const std::filesystem::path& output,bool allowReplay,const std::wstring& fault,uint64_t last,bool gamePool):diagnosticFolder(output),replay(allowReplay),fixture(fault),lastOutput(last){
        parent.value=OpenProcess(PROCESS_DUP_HANDLE|SYNCHRONIZE,FALSE,pid);need(parent.value!=nullptr,"Open UE parent");
        event.value=CreateEventW(nullptr,FALSE,FALSE,nullptr);need(event.value!=nullptr,"Receiver GPU event");
        ComPtr<IDXGIFactory4> factory;ComPtr<IDXGIAdapter> adapter;
        ComPtr<ID3D11Device> base;ComPtr<ID3D11DeviceContext> immediate;
        hr(CreateDXGIFactory1(IID_PPV_ARGS(&factory)),"DXGI factory");
        hr(factory->EnumAdapterByLuid(expected,IID_PPV_ARGS(&adapter)),"Exact UE GPU");
        hr(D3D11CreateDevice(adapter.Get(),D3D_DRIVER_TYPE_UNKNOWN,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&base,nullptr,&immediate),"D3D11 receiver");
        hr(base.As(&device),"Shared fence device");hr(immediate.As(&context),"Shared fence context");
        luid=(uint64_t(uint32_t(expected.HighPart))<<32)|expected.LowPart;
        normalizer=std::make_unique<sfc_ue_output::Normalizer>(device.Get());
        if(gamePool)gameOutput=std::make_unique<sfc_ue_game::Writer>(allowReplay);
        if(!output.empty())std::filesystem::create_directories(output);
    }
    void duplicate(uint64_t handle,wire::Handle& local){
        need(DuplicateHandle(parent.value,reinterpret_cast<HANDLE>(uintptr_t(handle)),GetCurrentProcess(),&local.value,0,FALSE,DUPLICATE_SAME_ACCESS),"Duplicate UE handle");
    }
    void retire(wire::Channel& channel){
        const auto requested=wire::load64(channel.state->retire_requested);
        if(requested==wire::load64(channel.state->retire_completed))return;
        for(auto& slot:channel.state->slots)need(wire::load(slot.phase)==wire::Idle,"Generation retired while GPU lease active");
        if(gameOutput&&!gameOutput->retire())return;
        context->ClearState();
        for(auto& slot:slots)slot=Slot{};
        for(auto& image:staging)image.Reset();
        need(channel.complete_retirement(requested),"Retired generation acknowledgement rejected");
    }
    void admit(const wire::Packet& p){
        if(!ready){
            wire::Handle r,a;duplicate(p.ready_fence,r);duplicate(p.ack_fence,a);
            hr(device->OpenSharedFence(r.value,IID_PPV_ARGS(&ready)),"Open UE ready fence");
            hr(device->OpenSharedFence(a.value,IID_PPV_ARGS(&ack)),"Open UE acknowledgement fence");
            readyHandle=p.ready_fence;ackHandle=p.ack_fence;
        }
        need(p.ready_fence==readyHandle&&p.ack_fence==ackHandle,"Shared fence generation changed");
        auto& slot=slots[p.slot];
        if(slot.initialized){
            const auto& old=slot.admitted;
            need(p.resource_epoch==old.resource_epoch&&p.identity.device==old.identity.device&&p.identity.target==old.identity.target&&
                 p.width==old.width&&p.height==old.height&&p.target_width==old.target_width&&p.target_height==old.target_height&&
                 p.viewport_x==old.viewport_x&&p.viewport_y==old.viewport_y&&p.images[0]==old.images[0]&&p.images[1]==old.images[1],"Output resources changed without retirement");
            return;
        }
        for(unsigned plane=0;plane<2;++plane){
            wire::Handle handle;duplicate(p.images[plane],handle);
            hr(device->OpenSharedResource1(handle.value,IID_PPV_ARGS(&slot.sources[plane])),"Import UE raw plane");
        }
        slot.input=normalizer->bind_inputs(slot.sources[0].Get(),slot.sources[1].Get());
        need(slot.input.width==p.width&&slot.input.height==p.height,"Imported raw extent differs");
        ID3D11Texture2D* images[3]{};
        for(unsigned plane=0;plane<3;++plane){
            D3D11_TEXTURE2D_DESC d{};d.Width=p.target_width;d.Height=p.target_height;
            d.MipLevels=d.ArraySize=d.SampleDesc.Count=1;
            d.Format=plane?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM;
            d.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;
            if(!gameOutput){hr(device->CreateTexture2D(&d,nullptr,&slot.outputs[plane]),"Receiver output allocation");images[plane]=slot.outputs[plane].Get();}
            if(!diagnosticFolder.empty()&&!staging[plane]){
                d.BindFlags=0;d.Usage=D3D11_USAGE_STAGING;d.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
                hr(device->CreateTexture2D(&d,nullptr,&staging[plane]),"Diagnostic staging allocation");
            }
        }
        if(!gameOutput)slot.target=normalizer->bind_targets(images);
        slot.admitted=p;slot.initialized=true;
    }
    bool read(wire::Channel& channel,const wire::Packet& p){
        need(wire::valid(p,p.identity,channel.state->producer,GetCurrentProcessId(),luid,replay)&&
             p.identity.session==channel.state->session&&p.ready_value>lastFence&&
             p.resource_epoch>wire::load64(channel.state->retire_completed),"Export identity/timeline invalid");
        if(fixture==L"slow-read")Sleep(50); // Explicit test worker only.
        if(fixture==L"crash-after-acquire")ExitProcess(7);
        admit(p);auto& slot=slots[p.slot];
        hr(context->Wait(ready.Get(),p.ready_value),"GPU wait for paired UE capture");
        output_wire::Packet gamePacket{};game_output::Metadata gameMeta{};int gameSlot=-1;
        if(gameOutput&&gameOutput->admit(p,gamePacket,gameMeta))gameSlot=gameOutput->reserve(device.Get(),gamePacket,gameMeta,*normalizer);
        const bool rendered=!gameOutput||gameSlot>=0;
        if(rendered)normalizer->draw(context.Get(),slot.input,gameOutput?gameOutput->target(unsigned(gameSlot)):slot.target,p.viewport_x,p.viewport_y,float(p.p22),float(p.p23),uint32_t(p.identity.owner_epoch));
        if(fixture==L"hold-before-ack")Sleep(200);
        const bool selected=p.identity.output<=2||p.identity.output==lastOutput-1||p.identity.output==lastOutput;
        const bool dump=rendered&&!diagnosticFolder.empty()&&diagnosticsWritten<4&&selected;
        if(dump)for(unsigned plane=0;plane<3;++plane)context->CopyResource(staging[plane].Get(),gameOutput?gameOutput->image(unsigned(gameSlot),plane):slot.outputs[plane].Get());
        hr(context->Signal(ack.Get(),fixture==L"wrong-ack"?p.ack_value+100:p.ack_value),"GPU acknowledgement after normalization");context->Flush();
        hr(ack->SetEventOnCompletion(p.ack_value,event.value),"Arm receiver completion");
        HANDLE waits[]{event.value,parent.value};
        const DWORD completed=WaitForMultipleObjects(2,waits,FALSE,INFINITE);
        if(completed==WAIT_OBJECT_0+1)return false;
        need(completed==WAIT_OBJECT_0&&ack->GetCompletedValue()!=UINT64_MAX&&ack->GetCompletedValue()>=p.ack_value,"Receiver GPU completion invalid");
        if(gameSlot>=0)gameOutput->publish(gameSlot,gamePacket,gameMeta);
        lastFence=p.ready_value;
        auto receipt=p;
        if(fixture==L"wrong-receipt"){receipt.identity.camera_pose++;wire::seal(receipt);}
        need(channel.complete(receipt),"Completed export receipt rejected");
        if(dump){
            ++diagnosticsWritten;
            const auto prefix=diagnosticFolder/std::to_wstring(p.identity.output);
            for(unsigned plane=0;plane<3;++plane){
                D3D11_MAPPED_SUBRESOURCE map{};hr(context->Map(staging[plane].Get(),0,D3D11_MAP_READ,0,&map),"Diagnostic output read");
                std::ofstream file(prefix.wstring()+L"-"+std::to_wstring(plane)+L".raw",std::ios::binary);
                for(unsigned y=0;y<p.target_height&&file;++y)file.write(static_cast<const char*>(map.pData)+y*map.RowPitch,p.target_width*4);
                context->Unmap(staging[plane].Get(),0);need(bool(file),"Diagnostic output write");
            }
            std::ofstream packet(prefix.wstring()+L".packet",std::ios::binary);packet.write(reinterpret_cast<const char*>(&p),sizeof(p));
            need(bool(packet),"Diagnostic packet write");
        }
        return true;
    }
};
int wmain(int count,wchar_t** args){
    std::unique_ptr<wire::Channel> channel;
    try{
        need(count>=8&&std::wcscmp(args[1],L"--stream")==0,"Receiver arguments");
        bool replay=false,gamePool=false;std::filesystem::path output;std::wstring fixture;uint64_t lastOutput=4;
        for(int n=8;n<count;++n){
            if(std::wcscmp(args[n],L"--replay")==0){need(!replay,"Duplicate replay option");replay=true;}
            else if(std::wcscmp(args[n],L"--game-pool")==0){need(!gamePool,"Duplicate game-pool option");gamePool=true;}
            else if(std::wcscmp(args[n],L"--diagnostics")==0&&n+1<count){need(output.empty(),"Duplicate diagnostic option");output=args[++n];}
            else if(std::wcscmp(args[n],L"--fixture")==0&&n+1<count){need(fixture.empty(),"Duplicate fixture option");fixture=args[++n];}
            else if(std::wcscmp(args[n],L"--last-output")==0&&n+1<count){lastOutput=std::stoull(args[++n]);need(lastOutput>=4&&lastOutput<=10000,"Diagnostic sample bounds");}
            else throw std::runtime_error("Unknown receiver option");
        }
        need(fixture.empty()||replay,"Receiver fault fixtures require explicit replay mode");
        need(fixture.empty()||fixture==L"slow-read"||fixture==L"crash-after-acquire"||fixture==L"passive-exit"||
             fixture==L"wrong-ack"||fixture==L"wrong-receipt"||fixture==L"hold-before-ack","Unknown receiver fixture");
        const auto parent=std::stoul(args[3]);const std::array<uint64_t,2> session{std::stoull(args[4]),std::stoull(args[5])};
        const LUID luid{DWORD(std::stoul(args[6])),std::stol(args[7])};
        Receiver receiver(parent,luid,output,replay,fixture,lastOutput,gamePool);
        channel=std::make_unique<wire::Channel>(args[2],parent,session);
        if(fixture==L"passive-exit")return 7;
        for(;;){
            if(wire::load(channel->state->stop)||WaitForSingleObject(receiver.parent.value,0)!=WAIT_TIMEOUT)return 0;
            receiver.retire(*channel);
            unsigned chosen=2;uint64_t first=UINT64_MAX;
            // A shared fence timeline must be consumed in producer order.
            for(unsigned slot=0;slot<2;++slot)if(wire::load(channel->state->slots[slot].phase)==wire::Published){
                const auto value=channel->state->slots[slot].packet.ready_value;
                if(value<first){first=value;chosen=slot;}
            }
            if(chosen<2){wire::Packet p;if(channel->acquire(chosen,p)&&!receiver.read(*channel,p))return 0;continue;}
            HANDLE waits[]{channel->ready(),channel->stopped(),receiver.parent.value};
            const DWORD result=WaitForMultipleObjects(3,waits,FALSE,INFINITE);
            if(result==WAIT_OBJECT_0+1||result==WAIT_OBJECT_0+2)return 0;
            need(result==WAIT_OBJECT_0,"Receiver event wait");
        }
    }catch(const std::exception& e){
        if(channel){wire::store(channel->state->error,1);SetEvent(channel->acknowledged());}
        std::fprintf(stderr,"UE receiver: %s\n",e.what());return 1;
    }
}
