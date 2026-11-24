#pragma once
#include "CoreMinimal.h"
// Explicit standalone timing only. No texture readback or source-thread work.
class FSFCSceneTiming {
public:
    FSFCSceneTiming();
    bool Start(int32 Frames,int32 Owners,const FString& Output,FString& Error);
    void Poll();
    int32 BeforeCapture(uint64 Sequence,uint64 Offered,double ProcessMs,int32 Eligible);
    void AfterCapture(int32 Slot,double CaptureMs);
    bool Finished()const;
    bool Write(class USFCSessionSubsystem* Session,class USFCWorldSubsystem* World,const FString& Output,FString& Error);
private:
    struct FState;
    TSharedPtr<FState,ESPMode::ThreadSafe> State;
    struct FSample {double ProcessMs,CaptureMs,CompletionMs,SourceMs;};
    TArray<FSample> Samples;
    int32 Wanted=0,ExpectedOwners=0,Busy=0;
    uint64 LastSequence=0;
};
