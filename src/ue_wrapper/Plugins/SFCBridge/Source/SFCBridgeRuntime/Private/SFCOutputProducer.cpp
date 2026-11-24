#include "SFCOutputProducer.h"
#include "Engine/TextureRenderTarget2D.h"
#include "RenderingThread.h"
#include "RHICommandList.h"
#include "ID3D12DynamicRHI.h"
#include "Misc/CommandLine.h"
#include <atomic>
#include "Windows/AllowWindowsPlatformTypes.h"
#include <wrl/client.h>
#include "Windows/HideWindowsPlatformTypes.h"
using Microsoft::WRL::ComPtr;
struct FSFCOutputProducer::FState {
    TUniquePtr<sfc_ue_export::Channel> Channel;
    FTextureRHIRef Images[2][2];
    sfc_ue_export::Handle Handles[2][2],ReadyHandle,AckHandle;
    ComPtr<ID3D12Fence> Ready,Ack;
    std::atomic<int32> Initialization{0};
    sfc_ue_export::Packet Description;
    uint64 SlotEpoch[2]{};
    std::atomic<bool> Stopping{false};
    uint64 FailAllocationEpoch=0;
    bool InjectDeviceLoss=false;
    bool Reconfiguring=false;
    sfc_ue_export::Packet Pending;
};
namespace {
bool SameTarget(const sfc_ue_export::Packet& A,const sfc_ue_export::Packet& B){
    return A.width==B.width&&A.height==B.height&&A.target_width==B.target_width&&A.target_height==B.target_height&&
        A.viewport_x==B.viewport_x&&A.viewport_y==B.viewport_y&&A.resource_epoch==B.resource_epoch&&
        A.identity.device==B.identity.device&&A.identity.target==B.identity.target&&A.identity.activation==B.identity.activation;
}
}
FSFCOutputProducer::FSFCOutputProducer():State(MakeShared<FState,ESPMode::ThreadSafe>()){}
FSFCOutputProducer::~FSFCOutputProducer(){Stop();}
bool FSFCOutputProducer::Start(const FString& Consumer,const FString& Output,const std::array<uint64_t,2>& Session,FString& Error,bool DiagnosticReplay,uint32 LastDiagnosticOutput,bool GamePool){
    if(Process.IsValid()||State->Channel||!IsRHID3D12()){Error=TEXT("Invalid UE output startup");return false;}
    try { State->Channel=MakeUnique<sfc_ue_export::Channel>(Session,DiagnosticReplay); }
    catch(const std::exception& E){Error=UTF8_TO_TCHAR(E.what());return false;}
    const auto Luid=GetID3D12DynamicRHI()->RHIGetDevice(0)->GetAdapterLuid();
    FString Args=FString::Printf(TEXT("--stream \"%s\" %u %llu %llu %u %d"),
        State->Channel->name.c_str(),FPlatformProcess::GetCurrentProcessId(),Session[0],Session[1],Luid.LowPart,Luid.HighPart);
    if(DiagnosticReplay)Args+=TEXT(" --replay");
    if(GamePool)Args+=TEXT(" --game-pool");
    FString Fault;
    if(DiagnosticReplay&&FParse::Value(FCommandLine::Get(),TEXT("SFCReceiverFault="),Fault))
        Args+=FString::Printf(TEXT(" --fixture \"%s\""),*Fault);
    if(DiagnosticReplay){
        if(FParse::Param(FCommandLine::Get(),TEXT("SFCExportFailAllocation")))State->FailAllocationEpoch=1;
        FParse::Value(FCommandLine::Get(),TEXT("SFCExportFailAllocationEpoch="),State->FailAllocationEpoch);
        State->InjectDeviceLoss=FParse::Param(FCommandLine::Get(),TEXT("SFCExportDeviceLoss"));
    }
    if(!Output.IsEmpty())Args+=FString::Printf(TEXT(" --diagnostics \"%s\""),*Output);
    if(DiagnosticReplay&&LastDiagnosticOutput)Args+=FString::Printf(TEXT(" --last-output %u"),LastDiagnosticOutput);
    Process=FPlatformProcess::CreateProc(*Consumer,*Args,true,true,true,&ConsumerPid,0,nullptr,nullptr);
    if(!Process.IsValid()){Error=TEXT("UE output receiver did not start");State->Channel.Reset();return false;}
    Diagnostics=DiagnosticReplay;
    return true;
}
bool FSFCOutputProducer::Prepare(const sfc_ue_export::Packet& Description,FString& Error){
    if(!State->Channel||State->Initialization.load()!=0||State->Description.width){Error=TEXT("Output generation already prepared");return false;}
    if(!Description.width||!Description.height||!Description.target_width||!Description.target_height||
       Description.target_width>4096||Description.target_height>4096||
       uint64(Description.viewport_x)+Description.width>Description.target_width||
       uint64(Description.viewport_y)+Description.height>Description.target_height||uint64(Description.target_width)*Description.target_height*
       sfc_ue_output::OutputBytesPerPixel>sfc_ue_output::ResourceBudget){Error=TEXT("UE output generation exceeds budget");return false;}
    State->Description=Description;
    auto Shared=State;
    ENQUEUE_RENDER_COMMAND(SFCPrepareOutput)([Shared](FRHICommandListImmediate& Cmd){
        auto* Native=GetID3D12DynamicRHI();auto* Device=Native->RHIGetDevice(0);
        bool Previous=false;
        for(unsigned Slot=0;Slot<2;++Slot)for(unsigned Plane=0;Plane<2;++Plane){
            Previous|=Shared->Images[Slot][Plane].IsValid();
            Shared->Images[Slot][Plane].SafeRelease();Shared->Handles[Slot][Plane].reset();
        }
        // Once per retired generation, never per frame. GPU reads are already
        // acknowledged and the receiver has released its old imports/outputs.
        if(Previous)Cmd.ImmediateFlush(EImmediateFlushType::FlushRHIThreadFlushResources);
        HRESULT Hr=S_OK;
        if(!Shared->Ready){
            Hr=Device->CreateFence(0,D3D12_FENCE_FLAG_SHARED,IID_PPV_ARGS(&Shared->Ready));
            if(SUCCEEDED(Hr))Hr=Device->CreateFence(0,D3D12_FENCE_FLAG_SHARED,IID_PPV_ARGS(&Shared->Ack));
            if(SUCCEEDED(Hr))Hr=Device->CreateSharedHandle(Shared->Ready.Get(),nullptr,GENERIC_ALL,nullptr,&Shared->ReadyHandle.value);
            if(SUCCEEDED(Hr))Hr=Device->CreateSharedHandle(Shared->Ack.Get(),nullptr,GENERIC_ALL,nullptr,&Shared->AckHandle.value);
        }
        for(unsigned Slot=0;Slot<2&&SUCCEEDED(Hr);++Slot)for(unsigned Plane=0;Plane<2&&SUCCEEDED(Hr);++Plane){
            if(Shared->FailAllocationEpoch==Shared->Description.resource_epoch&&Slot==1&&Plane==0){Hr=E_OUTOFMEMORY;break;}
            D3D12_HEAP_PROPERTIES Heap{};Heap.Type=D3D12_HEAP_TYPE_DEFAULT;Heap.CreationNodeMask=Heap.VisibleNodeMask=1;
            D3D12_RESOURCE_DESC Desc{};Desc.Dimension=D3D12_RESOURCE_DIMENSION_TEXTURE2D;
            Desc.Width=Shared->Description.width;Desc.Height=Shared->Description.height;
            Desc.DepthOrArraySize=Desc.MipLevels=Desc.SampleDesc.Count=1;
            Desc.Format=Plane?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM;
            Desc.Flags=D3D12_RESOURCE_FLAG_ALLOW_RENDER_TARGET|D3D12_RESOURCE_FLAG_ALLOW_SIMULTANEOUS_ACCESS;
            ComPtr<ID3D12Resource> Resource;
            Hr=Device->CreateCommittedResource(&Heap,D3D12_HEAP_FLAG_SHARED,&Desc,D3D12_RESOURCE_STATE_COMMON,nullptr,IID_PPV_ARGS(&Resource));
            if(FAILED(Hr))break;
            auto& Image=Shared->Images[Slot][Plane];
            Image=Native->RHICreateTexture2DFromResource(Plane?PF_R32_FLOAT:PF_B8G8R8A8,
                ETextureCreateFlags::Shared|ETextureCreateFlags::ShaderResource|ETextureCreateFlags::RenderTargetable,
                FClearValueBinding::None,Resource.Get());
            if(!Image.IsValid()){Hr=E_FAIL;break;}
            Hr=Device->CreateSharedHandle(Native->RHIGetResource(Image),nullptr,GENERIC_ALL,nullptr,&Shared->Handles[Slot][Plane].value);
        }
        Shared->Initialization.store(SUCCEEDED(Hr)?1:-1,std::memory_order_release);
    });
    return true;
}
bool FSFCOutputProducer::Reconfigure(const sfc_ue_export::Packet& Description,FString& Error){
    if(!State->Channel||State->Stopping.load()){Error=TEXT("Output generation cannot be reconfigured");return false;}
    if(!State->Reconfiguring&&SameTarget(Description,State->Description))return Ready();
    if(State->Reconfiguring){
        if(!SameTarget(Description,State->Pending)){Error=TEXT("Output target changed during retirement");return false;}
        if(sfc_ue_export::load64(State->Channel->state->retire_completed)!=State->Description.resource_epoch){
            // Native lease drain can finish after the first retirement notice.
            // Reuse the existing handshake event; no renderer or game wait.
            State->Channel->notify();return false;
        }
        State->Initialization.store(0);State->Description={};State->Reconfiguring=false;
        if(!Prepare(Description,Error))return false;
        return false;
    }
    if(Description.identity.device!=State->Description.identity.device){Error=TEXT("Device change requires a fresh renderer generation");return false;}
    if(Description.resource_epoch<=State->Description.resource_epoch||Description.identity.target<=State->Description.identity.target){
        Error=TEXT("Output target generation did not advance");return false;
    }
    if(!Drained())return false;
    if(!State->Channel->request_retirement(State->Description.resource_epoch)){Error=TEXT("Output retirement request rejected");return false;}
    State->Pending=Description;State->Reconfiguring=true;return false;
}
bool FSFCOutputProducer::Ready()const{
    return State->Channel&&State->Initialization.load(std::memory_order_acquire)==1&&
        uint32(sfc_ue_export::load(State->Channel->state->consumer))==ConsumerPid&&!State->Stopping.load()&&!State->Reconfiguring;
}
bool FSFCOutputProducer::Poll(FString& Error){
    if(State->Initialization.load()==-1){Error=TEXT("UE shared output allocation failed");return false;}
    if(!Process.IsValid()||!FPlatformProcess::IsProcRunning(Process)){Error=TEXT("UE output receiver exited");return false;}
    if(sfc_ue_export::load(State->Channel->state->error)){Error=TEXT("UE output receiver rejected the generation");return false;}
    if(State->Initialization.load(std::memory_order_acquire)!=1)return true;
    const uint64 Done=State->InjectDeviceLoss&&Submitted?UINT64_MAX:State->Ack->GetCompletedValue();
    if(Done==UINT64_MAX){Error=TEXT("UE output device removed");return false;}
    if(Done>NextFence){Error=TEXT("UE output acknowledgement exceeds submitted work");return false;}
    for(unsigned Slot=0;Slot<2;++Slot){
        auto& Record=State->Channel->state->slots[Slot];
        if(sfc_ue_export::load(Record.phase)!=sfc_ue_export::Complete)continue;
        const auto Timing=Record.timing;const uint64 Output=Record.packet.identity.output;
        if(State->Channel->reclaim(Slot,Done)){
            ++Completed;
            if(Diagnostics){
                const double Ms=1000.0/State->Channel->state->frequency;
                Timings.Add({Output,(Timing.published-Timing.offered)*Ms,(Timing.acquired-Timing.published)*Ms,
                    (Timing.completed-Timing.acquired)*Ms,(Timing.completed-Timing.offered)*Ms});
            }
        }
    }
    return true;
}
bool FSFCOutputProducer::Submit(sfc_ue_export::Packet Packet,UTextureRenderTarget2D* Colour,UTextureRenderTarget2D* Depth,FString& Error,uint64 Offered){
    if(!Ready())return false;
    const auto& D=State->Description;
    if(Packet.width!=D.width||Packet.height!=D.height||Packet.target_width!=D.target_width||Packet.target_height!=D.target_height||
       Packet.viewport_x!=D.viewport_x||Packet.viewport_y!=D.viewport_y||Packet.resource_epoch!=D.resource_epoch||
       Packet.identity.device!=D.identity.device||Packet.identity.target!=D.identity.target||Packet.identity.activation!=D.identity.activation){
        Error=TEXT("UE output generation changed before retirement");return false;
    }
    unsigned Slot=0;
    for(;Slot<2;++Slot)if(sfc_ue_export::load(State->Channel->state->slots[Slot].phase)==sfc_ue_export::Idle)break;
    if(Slot==2){++Busy;return false;}
    if(!Colour||!Depth){Error=TEXT("Missing paired UE capture");return false;}
    FTextureRHIRef Sources[]{Colour->GameThread_GetRenderTargetResource()->GetRenderTargetTexture(),Depth->GameThread_GetRenderTargetResource()->GetRenderTargetTexture()};
    for(unsigned Plane=0;Plane<2;++Plane)if(!Sources[Plane].IsValid()||Sources[Plane]->GetSizeXYZ().X!=int32(Packet.width)||
        Sources[Plane]->GetSizeXYZ().Y!=int32(Packet.height)||Sources[Plane]->GetFormat()!=(Plane?PF_R32_FLOAT:PF_B8G8R8A8)){
        Error=TEXT("Paired UE capture format/extent mismatch");return false;
    }
    const auto Luid=GetID3D12DynamicRHI()->RHIGetDevice(0)->GetAdapterLuid();
    Packet.adapter_luid=(uint64(uint32(Luid.HighPart))<<32)|Luid.LowPart;
    Packet.producer=FPlatformProcess::GetCurrentProcessId();Packet.consumer=ConsumerPid;Packet.slot=Slot;
    Packet.slot_epoch=++State->SlotEpoch[Slot];Packet.ready_value=Packet.ack_value=++NextFence;
    Packet.ready_fence=reinterpret_cast<UPTRINT>(State->ReadyHandle.value);Packet.ack_fence=reinterpret_cast<UPTRINT>(State->AckHandle.value);
    for(unsigned Plane=0;Plane<2;++Plane)Packet.images[Plane]=reinterpret_cast<UPTRINT>(State->Handles[Slot][Plane].value);
    sfc_ue_export::seal(Packet);
    if(!State->Channel->reserve(Packet,Diagnostics,Offered)){Error=TEXT("UE output transaction rejected");return false;}
    auto Shared=State;
    ENQUEUE_RENDER_COMMAND(SFCExportPair)([Shared,Packet,A=Sources[0],B=Sources[1]](FRHICommandListImmediate& Cmd){
        FTextureRHIRef Input[]{A,B};
        for(unsigned Plane=0;Plane<2;++Plane){
            auto& Target=Shared->Images[Packet.slot][Plane];
            Cmd.Transition(FRHITransitionInfo(Input[Plane],ERHIAccess::Unknown,ERHIAccess::CopySrc));
            Cmd.Transition(FRHITransitionInfo(Target,ERHIAccess::Unknown,ERHIAccess::CopyDest));
            Cmd.CopyTexture(Input[Plane],Target,FRHICopyTextureInfo{});
            Cmd.Transition(FRHITransitionInfo(Input[Plane],ERHIAccess::CopySrc,ERHIAccess::SRVMask));
            Cmd.Transition(FRHITransitionInfo(Target,ERHIAccess::CopyDest,ERHIAccess::SRVMask));
        }
        Cmd.EnqueueLambda([Shared,Packet](FRHICommandListImmediate& Executing){
            GetID3D12DynamicRHI()->RHISignalManualFence(Executing,Shared->Ready.Get(),Packet.ready_value);
            Shared->Channel->publish_reserved(Packet);
        });
    });
    ++Submitted;return true;
}
bool FSFCOutputProducer::Drained()const{
    if(!State->Channel)return true;
    for(auto& Slot:State->Channel->state->slots)if(sfc_ue_export::load(Slot.phase)!=sfc_ue_export::Idle)return false;
    return true;
}
bool FSFCOutputProducer::HasReading()const{
    if(!State->Channel)return false;
    for(auto& Slot:State->Channel->state->slots)if(sfc_ue_export::load(Slot.phase)==sfc_ue_export::Reading)return true;
    return false;
}
void FSFCOutputProducer::Stop(){
    if(State->Stopping.exchange(true))return;
    if(State->Channel)State->Channel->stop();
    // Shutdown-only command drain ensures reserved writes have their signal
    // submitted before waiting for a receiver that may already have acquired one.
    FlushRenderingCommands();
    if(Process.IsValid()){
        const double Until=FPlatformTime::Seconds()+2;
        while(FPlatformProcess::IsProcRunning(Process)&&FPlatformTime::Seconds()<Until)FPlatformProcess::Sleep(.001f);
        if(FPlatformProcess::IsProcRunning(Process)){FPlatformProcess::TerminateProc(Process);FPlatformProcess::WaitForProc(Process);}
        FPlatformProcess::CloseProc(Process);
    }
    if(State->Channel&&State->Initialization.load(std::memory_order_acquire)==1){
        const uint64 Reads=State->Ack->GetCompletedValue(),Writes=State->Ready->GetCompletedValue();
        for(unsigned Slot=0;Slot<2;++Slot){
            if(State->Channel->reclaim(Slot,Reads))++Completed;
            State->Channel->cancel_unread(Slot,Writes);
            State->Channel->cancel_unpublished(Slot,Writes);
        }
    }
}
