#pragma once
#include "CoreMinimal.h"
#include "SFCOutputProducer.h"
#include "SFCLiveSource.h"
class USFCSessionSubsystem;
class USFCWorldSubsystem;
// Default-off additive backend component. Source ownership/identity stays with
// the retained scene; capture changes only the diagnostic actor's world pose.
// Caller must supply the existing parent's uniquely selected player anchor.
class FSFCGameOutput {
public:
    bool Start(const FString& Receiver,const FString& SourceMap,const SFCSource::Point& WorldOffset,FString& Error);
    bool BeforeCapture(USFCWorldSubsystem* World,USFCSessionSubsystem* Session,const FSFCLiveSource& Source,bool& Capture,FString& Error);
    bool AfterCapture(USFCWorldSubsystem* World,FString& Error);
    void Stop(){Producer.Stop();Prepared=false;}
    ~FSFCGameOutput(){Stop();}
private:
    FSFCOutputProducer Producer;
    FString SessionName,BoundContent;
    std::array<uint64_t,2> Session{};
    SFCSource::Point Offset{};
    sfc_ue_export::Packet Pending;
    uint64 LastSequence=0;
    uint32 BoundOwner=0,BoundRevision=0,BoundModel=0,BoundSource=0;
    bool Started=false,Prepared=false;
};
