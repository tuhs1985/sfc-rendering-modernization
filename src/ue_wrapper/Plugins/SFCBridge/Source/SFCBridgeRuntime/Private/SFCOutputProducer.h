#pragma once
#include "CoreMinimal.h"
#include "Windows/AllowWindowsPlatformTypes.h"
#include "ue_export_channel.h"
#include "Windows/HideWindowsPlatformTypes.h"
class UTextureRenderTarget2D;
// Backend worker resources only. Never called from SFC's capture callback.
class FSFCOutputProducer {
public:
    FSFCOutputProducer();
    ~FSFCOutputProducer();
    bool Start(const FString& Consumer,const FString& DiagnosticOutput,
               const std::array<uint64_t,2>& Session,FString& Error,bool DiagnosticReplay=false,uint32 LastDiagnosticOutput=0,bool GamePool=false);
    bool Prepare(const sfc_ue_export::Packet& Description,FString& Error);
    bool Reconfigure(const sfc_ue_export::Packet& Description,FString& Error);
    bool Poll(FString& Error);
    bool Ready() const;
    bool Submit(sfc_ue_export::Packet Packet,UTextureRenderTarget2D* Colour,
                UTextureRenderTarget2D* Depth,FString& Error,uint64 Offered=0);
    bool Drained() const;
    bool HasReading() const;
    void Stop();
    uint64 Submitted=0,Busy=0,Completed=0;
    struct FTiming {uint64 Output=0;double QueueMs=0,ReceiverMs=0,GpuMs=0,TotalMs=0;};
    TArray<FTiming> Timings;
private:
    struct FState;
    TSharedPtr<FState,ESPMode::ThreadSafe> State;
    FProcHandle Process;
    uint32 ConsumerPid=0;
    uint64 NextFence=0;
    bool Diagnostics=false;
};
