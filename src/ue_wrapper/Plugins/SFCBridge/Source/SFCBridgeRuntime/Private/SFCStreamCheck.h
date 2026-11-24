#pragma once
#include "CoreMinimal.h"
#include "SFCOutputProducer.h"
#include "SFCSceneData.h"
class USFCWorldSubsystem;
// Explicit standalone orchestration. Not enabled by normal inspection/gameplay.
class FSFCStreamCheck {
public:
    bool Start(const FSFCSceneData& Data,const FString& Output,FString& Error);
    bool BeforeCapture(USFCWorldSubsystem* World,FString& Error);
    bool Tick(USFCWorldSubsystem* World,FString& Error);
    void Stop();
    ~FSFCStreamCheck(){Stop();}
private:
    FSFCOutputProducer Producer;
    const FSFCSceneData* Source=nullptr;
    sfc_ue_export::Packet Description;
    FString OutputDirectory;
    TArray<TSharedPtr<class FJsonValue>> SubmittedFrames;
    double Started=0;
    int32 CurrentFrame=0;
    uint32 FrameCount=12;
    uint64 Offered=0;
    bool Finished=false,GamePool=false;
    bool CapturePrepared=false;
    uint32 InitialWidth=0,InitialHeight=0,GenerationChanges=0;
    uint32 PassiveMilliseconds=0;
    bool Cancel(FString& Error);
    sfc_ue_export::Handle FixtureReadEvent;
    uint32 FixtureConsumed=0;
    uint32 NativeConsumed();
};
