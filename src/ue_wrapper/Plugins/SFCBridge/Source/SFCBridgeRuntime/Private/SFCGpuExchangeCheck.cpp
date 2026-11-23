#include "SFCGpuExchangeCheck.h"
#include "Engine/TextureRenderTarget2D.h"
#include "RenderingThread.h"
#include "RHICommandList.h"
#include "ID3D12DynamicRHI.h"
#include "Misc/CommandLine.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "Windows/AllowWindowsPlatformTypes.h"
#include <d3d11_4.h>
#include <wrl/client.h>
#include "Windows/HideWindowsPlatformTypes.h"

using Microsoft::WRL::ComPtr;
namespace {
struct FCheckResources {
    FTextureRHIRef Shared;
    ComPtr<ID3D12Fence> Ready;
    ComPtr<ID3D12Fence> Acknowledged;
    HANDLE TextureHandle=nullptr;
    HANDLE ReadyHandle=nullptr;
    HANDLE AckHandle=nullptr;
    HANDLE FenceEvent=nullptr;
    HRESULT Result=E_FAIL;
    ~FCheckResources() {
        if(TextureHandle) CloseHandle(TextureHandle);
        if(ReadyHandle) CloseHandle(ReadyHandle);
        if(AckHandle) CloseHandle(AckHandle);
        if(FenceEvent) CloseHandle(FenceEvent);
    }
};
}

bool SFCCheckGpuExchange(UTextureRenderTarget2D* Target,TArray<FColor>& Pixels,FString& Error,const TCHAR* Label,double P22,double P23,uint32 Owner) {
    if(!Target||!IsRHID3D12()) { Error=TEXT("GPU check requires a DX12 target"); return false; }
    auto State=MakeShared<FCheckResources,ESPMode::ThreadSafe>();
    FTextureRHIRef Source=Target->GameThread_GetRenderTargetResource()->GetRenderTargetTexture();
    if(!Source.IsValid()) { Error=TEXT("Missing source texture"); return false; }
    if(Source->GetFormat()!=PF_B8G8R8A8&&Source->GetFormat()!=PF_R32_FLOAT) {
        Error=TEXT("Unsupported diagnostic export format"); return false;
    }
    ENQUEUE_RENDER_COMMAND(SFCExportCheck)(
        [State,Source](FRHICommandListImmediate& Cmd) {
            auto* Native=GetID3D12DynamicRHI();
            const FIntVector Size=Source->GetSizeXYZ();
            ID3D12Device* Device=Native->RHIGetDevice(0);
            D3D12_HEAP_PROPERTIES Heap{};
            Heap.Type=D3D12_HEAP_TYPE_DEFAULT;
            Heap.CreationNodeMask=Heap.VisibleNodeMask=1;
            D3D12_RESOURCE_DESC Desc{};
            Desc.Dimension=D3D12_RESOURCE_DIMENSION_TEXTURE2D;
            Desc.Width=Size.X; Desc.Height=Size.Y;
            Desc.DepthOrArraySize=Desc.MipLevels=1;
            Desc.Format=Source->GetFormat()==PF_R32_FLOAT?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM;
            Desc.SampleDesc.Count=1;
            Desc.Flags=D3D12_RESOURCE_FLAG_ALLOW_RENDER_TARGET|D3D12_RESOURCE_FLAG_ALLOW_SIMULTANEOUS_ACCESS;
            ComPtr<ID3D12Resource> Resource;
            State->Result=Device->CreateCommittedResource(&Heap,D3D12_HEAP_FLAG_SHARED,&Desc,
                D3D12_RESOURCE_STATE_COMMON,nullptr,IID_PPV_ARGS(&Resource));
            if(FAILED(State->Result)) return;
            State->Shared=Native->RHICreateTexture2DFromResource(Source->GetFormat(),
                ETextureCreateFlags::Shared|ETextureCreateFlags::ShaderResource|ETextureCreateFlags::RenderTargetable,
                FClearValueBinding::None,Resource.Get());
            if(!State->Shared.IsValid()) { State->Result=E_FAIL; return; }
            Cmd.Transition(FRHITransitionInfo(Source,ERHIAccess::Unknown,ERHIAccess::CopySrc));
            Cmd.Transition(FRHITransitionInfo(State->Shared,ERHIAccess::Unknown,ERHIAccess::CopyDest));
            Cmd.CopyTexture(Source,State->Shared,FRHICopyTextureInfo{});
            Cmd.Transition(FRHITransitionInfo(Source,ERHIAccess::CopySrc,ERHIAccess::SRVMask));
            Cmd.Transition(FRHITransitionInfo(State->Shared,ERHIAccess::CopyDest,ERHIAccess::SRVMask));
            State->Result=Device->CreateFence(0,D3D12_FENCE_FLAG_SHARED,IID_PPV_ARGS(&State->Ready));
            if(FAILED(State->Result)) return;
            State->Result=Device->CreateFence(0,D3D12_FENCE_FLAG_SHARED,IID_PPV_ARGS(&State->Acknowledged));
            if(FAILED(State->Result)) return;
            State->Result=Device->CreateSharedHandle(State->Ready.Get(),nullptr,GENERIC_ALL,nullptr,&State->ReadyHandle);
            if(FAILED(State->Result)) return;
            State->Result=Device->CreateSharedHandle(State->Acknowledged.Get(),nullptr,GENERIC_ALL,nullptr,&State->AckHandle);
            if(FAILED(State->Result)) return;
            State->Result=Device->CreateSharedHandle(Native->RHIGetResource(State->Shared),nullptr,GENERIC_ALL,nullptr,&State->TextureHandle);
            if(FAILED(State->Result)) return;
            Cmd.EnqueueLambda([State](FRHICommandListImmediate& Executing) {
                GetID3D12DynamicRHI()->RHISignalManualFence(Executing,State->Ready.Get(),1);
            });
            Cmd.ImmediateFlush(EImmediateFlushType::FlushRHIThread);
        });
    // This synchronous path is an explicit standalone diagnostic.
    FlushRenderingCommands();
    if(FAILED(State->Result)) { Error=FString::Printf(TEXT("UE shared export failed 0x%08x"),uint32(State->Result)); return false; }
    LUID Luid=GetID3D12DynamicRHI()->RHIGetDevice(0)->GetAdapterLuid();
    FString Consumer,OutputDirectory;
    if(FParse::Value(FCommandLine::Get(),TEXT("SFCGpuConsumer="),Consumer)) {
        if(!FParse::Value(FCommandLine::Get(),TEXT("SFCOutput="),OutputDirectory)) {
            Error=TEXT("External GPU consumer needs diagnostic output"); return false;
        }
        const FString Raw=OutputDirectory/(FString(Label)+TEXT(".raw"));
        FString Arguments=FString::Printf(TEXT("--ue-consume %u %llu %u %d \"%s\" %llu %llu"),
            FPlatformProcess::GetCurrentProcessId(),uint64(reinterpret_cast<UPTRINT>(State->TextureHandle)),
            Luid.LowPart,Luid.HighPart,*Raw,uint64(reinterpret_cast<UPTRINT>(State->ReadyHandle)),
            uint64(reinterpret_cast<UPTRINT>(State->AckHandle)));
        if(Owner) Arguments+=FString::Printf(TEXT(" %.17g %.17g %u"),P22,P23,Owner);
        FProcHandle Process=FPlatformProcess::CreateProc(*Consumer,*Arguments,true,true,true,nullptr,0,nullptr,nullptr);
        if(!Process.IsValid()) { Error=TEXT("External D3D11 consumer failed to start"); return false; }
        const double Deadline=FPlatformTime::Seconds()+15;
        while(FPlatformProcess::IsProcRunning(Process)&&FPlatformTime::Seconds()<Deadline)
            FPlatformProcess::Sleep(0.001f);
        if(FPlatformProcess::IsProcRunning(Process)) {
            FPlatformProcess::TerminateProc(Process);
            FPlatformProcess::WaitForProc(Process);
        }
        int32 ExitCode=-1;
        const bool Exited=FPlatformProcess::GetProcReturnCode(Process,&ExitCode);
        FPlatformProcess::CloseProc(Process);
        TArray<uint8> Bytes;
        if(!Exited||ExitCode!=0||State->Ready->GetCompletedValue()!=1||
           State->Acknowledged->GetCompletedValue()!=1||!FFileHelper::LoadFileToArray(Bytes,*Raw)||
           Bytes.Num()!=Target->SizeX*Target->SizeY*sizeof(FColor)) {
            Error=TEXT("External D3D11 consumer did not return complete pixels"); return false;
        }
        Pixels.SetNumUninitialized(Target->SizeX*Target->SizeY);
        FMemory::Memcpy(Pixels.GetData(),Bytes.GetData(),Bytes.Num());
        return true;
    }
    State->FenceEvent=CreateEventW(nullptr,false,false,nullptr);
    if(!State->FenceEvent||FAILED(State->Ready->SetEventOnCompletion(1,State->FenceEvent))||
       WaitForSingleObject(State->FenceEvent,5000)!=WAIT_OBJECT_0||
       State->Ready->GetCompletedValue()!=1) { Error=TEXT("UE GPU completion deadline"); return false; }
    ComPtr<IDXGIFactory4> Factory;
    ComPtr<IDXGIAdapter> Adapter;
    ComPtr<ID3D11Device> Base;
    ComPtr<ID3D11DeviceContext> Context;
    ComPtr<ID3D11Device1> Device;
    ComPtr<ID3D11Texture2D> Imported,Staging;
    HRESULT Result=CreateDXGIFactory1(IID_PPV_ARGS(&Factory));
    if(SUCCEEDED(Result)) Result=Factory->EnumAdapterByLuid(Luid,IID_PPV_ARGS(&Adapter));
    if(SUCCEEDED(Result)) Result=D3D11CreateDevice(Adapter.Get(),D3D_DRIVER_TYPE_UNKNOWN,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&Base,nullptr,&Context);
    if(SUCCEEDED(Result)) Result=Base.As(&Device);
    if(SUCCEEDED(Result)) Result=Device->OpenSharedResource1(State->TextureHandle,IID_PPV_ARGS(&Imported));
    if(FAILED(Result)) { Error=FString::Printf(TEXT("D3D11 import failed 0x%08x"),uint32(Result)); return false; }
    D3D11_TEXTURE2D_DESC Desc{};
    Imported->GetDesc(&Desc);
    const DXGI_FORMAT Expected=Source->GetFormat()==PF_R32_FLOAT?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM;
    if(Desc.Format!=Expected||Desc.Width!=uint32(Target->SizeX)||Desc.Height!=uint32(Target->SizeY)) {
        Error=TEXT("Unexpected imported descriptor"); return false;
    }
    Desc.Usage=D3D11_USAGE_STAGING; Desc.BindFlags=Desc.MiscFlags=0; Desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
    Result=Device->CreateTexture2D(&Desc,nullptr,&Staging);
    if(FAILED(Result)) { Error=TEXT("D3D11 diagnostic staging allocation failed"); return false; }
    Context->CopyResource(Staging.Get(),Imported.Get());
    Context->Flush();
    D3D11_MAPPED_SUBRESOURCE Map{};
    const double Deadline=FPlatformTime::Seconds()+5;
    do {
        Result=Context->Map(Staging.Get(),0,D3D11_MAP_READ,D3D11_MAP_FLAG_DO_NOT_WAIT,&Map);
        if(Result!=DXGI_ERROR_WAS_STILL_DRAWING) break;
        FPlatformProcess::Sleep(0.001f);
    } while(FPlatformTime::Seconds()<Deadline);
    if(FAILED(Result)) { Error=TEXT("D3D11 diagnostic copy deadline"); return false; }
    Pixels.SetNumUninitialized(Desc.Width*Desc.Height);
    for(uint32 Y=0;Y<Desc.Height;++Y)
        FMemory::Memcpy(Pixels.GetData()+Y*Desc.Width,static_cast<const uint8*>(Map.pData)+Y*Map.RowPitch,Desc.Width*sizeof(FColor));
    Context->Unmap(Staging.Get(),0);
    return true;
}
