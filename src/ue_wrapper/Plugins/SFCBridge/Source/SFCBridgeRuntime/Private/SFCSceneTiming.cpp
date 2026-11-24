#include "SFCSceneTiming.h"
#include "SFCSessionSubsystem.h"
#include "SFCWorldSubsystem.h"
#include "RenderingThread.h"
#include "RHICommandList.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Engine/TextureRenderTarget2D.h"
#include "HAL/PlatformMemory.h"
#include "DynamicRHI.h"
#include "RHIStats.h"
#include <atomic>
struct FSFCSceneTiming::FState {
    struct FSlot {FGPUFenceRHIRef Fence;std::atomic<bool> Armed{false};bool Used=false;uint64 Start=0,Offered=0;double Process=0,Capture=0;};
    FSlot Slots[2];
};
FSFCSceneTiming::FSFCSceneTiming():State(MakeShared<FState,ESPMode::ThreadSafe>()){}
bool FSFCSceneTiming::Start(int32 Frames,int32 Owners,const FString& Output,FString& Error){
    if(Frames<10||Frames>10000||Owners<1||Owners>256){Error=TEXT("Invalid bounded timing fixture");return false;}
    Wanted=Frames;ExpectedOwners=Owners;Samples.Reserve(Frames);
    for(auto& Slot:State->Slots){Slot.Fence=RHICreateGPUFence(TEXT("SFC standalone capture completion"));if(!Slot.Fence){Error=TEXT("GPU timing fence unavailable");return false;}}
    return FFileHelper::SaveStringToFile(TEXT("{\"timing_only\":true,\"image_readback\":false}"),*(Output/TEXT("timing-started.json")));
}
void FSFCSceneTiming::Poll(){
    for(auto& Slot:State->Slots)if(Slot.Used&&Slot.Armed.load(std::memory_order_acquire)&&Slot.Fence->Poll()){
        const uint64 Now=FPlatformTime::Cycles64();
        if(Samples.Num()<Wanted)Samples.Add({Slot.Process,Slot.Capture,FPlatformTime::ToMilliseconds64(Now-Slot.Start),
            Slot.Offered&&Now>=Slot.Offered?FPlatformTime::ToMilliseconds64(Now-Slot.Offered):0});
        Slot.Used=false;Slot.Armed.store(false,std::memory_order_release);
    }
}
int32 FSFCSceneTiming::BeforeCapture(uint64 Sequence,uint64 Offered,double ProcessMs,int32 Eligible){
    if(Eligible!=ExpectedOwners||!Sequence||Sequence<=LastSequence||Finished())return INDEX_NONE;
    for(int32 I=0;I<2;++I){auto& Slot=State->Slots[I];if(Slot.Used)continue;
        Slot.Fence->Clear();Slot.Used=true;Slot.Start=FPlatformTime::Cycles64();Slot.Offered=Offered;Slot.Process=ProcessMs;
        Slot.Armed.store(false,std::memory_order_release);LastSequence=Sequence;return I;
    }
    ++Busy;return INDEX_NONE;
}
void FSFCSceneTiming::AfterCapture(int32 Index,double CaptureMs){
    if(Index==INDEX_NONE)return;State->Slots[Index].Capture=CaptureMs;const auto Shared=State;
    ENQUEUE_RENDER_COMMAND(SFCRecordCaptureCompletion)([Shared,Index](FRHICommandListImmediate& Commands){
        Commands.WriteGPUFence(Shared->Slots[Index].Fence);Shared->Slots[Index].Armed.store(true,std::memory_order_release);
    });
}
bool FSFCSceneTiming::Finished()const{return Wanted&&Samples.Num()>=Wanted;}
bool FSFCSceneTiming::Write(USFCSessionSubsystem* Session,USFCWorldSubsystem* World,const FString& Output,FString& Error){
    auto Report=MakeShared<FJsonObject>();Report->SetNumberField(TEXT("samples"),Samples.Num());
    Report->SetNumberField(TEXT("owners"),World->IdentityCount());Report->SetNumberField(TEXT("eligible"),World->EligibleCount());
    Report->SetNumberField(TEXT("geometry_builds"),Session->AssetBuilds);Report->SetNumberField(TEXT("actual_meshes"),World->ActualMeshCount());
    Report->SetNumberField(TEXT("busy_samples_skipped"),Busy);Report->SetNumberField(TEXT("capture_calls"),World->CaptureCalls);
    Report->SetNumberField(TEXT("preparation_seconds"),Session->TotalPreparationSeconds);Report->SetBoolField(TEXT("image_readback"),false);
    Report->SetNumberField(TEXT("retained_source_bytes"),double(Session->RetainedSourceBytes()));
    Report->SetNumberField(TEXT("bindings"),Session->BindingCount());Report->SetNumberField(TEXT("textures"),Session->TextureCount());
    const auto Memory=FPlatformMemory::GetStats();
    Report->SetNumberField(TEXT("process_physical_bytes"),double(Memory.UsedPhysical));
    Report->SetNumberField(TEXT("process_virtual_bytes"),double(Memory.UsedVirtual));
    FTextureMemoryStats TextureStats;RHIGetTextureMemoryStats(TextureStats);
    Report->SetNumberField(TEXT("rhi_streaming_texture_bytes"),double(TextureStats.StreamingMemorySize));
    Report->SetNumberField(TEXT("rhi_nonstreaming_texture_bytes"),double(TextureStats.NonStreamingMemorySize));
    Report->SetNumberField(TEXT("colour_target_bytes"),double(World->Target()->SizeX)*World->Target()->SizeY*4);
    // Retain bounded raw samples, including admission/warm-up tails. Completion
    // is observed through a later nonblocking poll, not a GPU timestamp query.
    TArray<TSharedPtr<FJsonValue>> Rows;
    for(const auto& Sample:Samples){
        TArray<TSharedPtr<FJsonValue>> Row;
        for(double Value:{Sample.ProcessMs,Sample.CaptureMs,Sample.CompletionMs,Sample.SourceMs})Row.Add(MakeShared<FJsonValueNumber>(Value));
        Rows.Add(MakeShared<FJsonValueArray>(Row));
    }
    Report->SetArrayField(TEXT("samples_ms"),Rows);
    auto Stats=[&](const TCHAR* Name,auto Select){
        TArray<double> Values;for(const auto& Sample:Samples)Values.Add(Select(Sample));Values.Sort();
        auto Object=MakeShared<FJsonObject>();
        Object->SetNumberField(TEXT("median"),Values[Values.Num()/2]);Object->SetNumberField(TEXT("p95"),Values[FMath::Min(Values.Num()-1,int32(Values.Num()*.95))]);
        Object->SetNumberField(TEXT("p99"),Values[FMath::Min(Values.Num()-1,int32(Values.Num()*.99))]);Object->SetNumberField(TEXT("maximum"),Values.Last());
        Report->SetObjectField(Name,Object);
    };
    Stats(TEXT("source_and_transform_cpu_ms"),[](const FSample& S){return S.ProcessMs;});
    Stats(TEXT("capture_submission_cpu_ms"),[](const FSample& S){return S.CaptureMs;});
    Stats(TEXT("capture_to_observed_gpu_ms"),[](const FSample& S){return S.CompletionMs;});
    Stats(TEXT("source_to_observed_gpu_ms"),[](const FSample& S){return S.SourceMs;});
    FString Json;FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Json));
    if(!FFileHelper::SaveStringToFile(Json,*(Output/TEXT("registry-timing.json")))){Error=TEXT("Timing receipt write failed");return false;}return true;
}
