#pragma once
#include "CoreMinimal.h"
#include "SFCSceneData.h"
#include "Windows/AllowWindowsPlatformTypes.h"
#include "source_scene_channel.h"
#include "Windows/HideWindowsPlatformTypes.h"

// CPU-only source receipt; all UObject work remains with the world/game thread.
// A selected owner is supplied by the existing parent selector, never guessed.
struct FSFCSourceInstance {
    uint32 Owner=0,Revision=0,Model=0,Source=0;
    uint64 Sequence=0,CameraPoseHash=0;
    SFCSource::Matrix Pose{};
    bool PoseQualified=false;
};
struct FSFCSourceSnapshot {
    FSFCFrame Camera{};
    uint32 Frame=0,Anchor=0,AnchorRevision=0;
    uint64 Sequence=0;
    uint64 Offered=0,FrameHash=0;
    TArray<FSFCSourceInstance> Instances;
    TArray<uint32> Retirements;
};
class FSFCLiveSource {
public:
    bool Start(const FString& Map,uint32 Pid,uint32 Owner,uint32 Revision,uint32 Model,uint32 Source,FString& Error);
    bool Poll(bool& Changed,bool& Stopped,FString& Error);
    bool StartScene(const FString& Map,uint32 Pid,FString& Error);
    bool PollScene(bool& Changed,bool& Stopped,FString& Error);
    const FSFCSourceSnapshot& Snapshot()const{return Scene;}
    const TArray<sfc_source_view::Asset>& NewAssets()const{return Catalog;}
    const FString& SessionName()const{return MapName;}
    uint32 Pid()const{return SourcePid;}
    sfc_source_view::Status Target(sfc_source_view::NativeTarget& Value)const{return Reader.target(Value);}
    uint32 CatalogPublications()const{return CatalogCounter;}
    const FSFCFrame& Frame()const{return Current;}
    uint64 Sequence()const{return LastSequence;}
    uint32 SourceFrame()const{return LastFrame;}
    bool MatchesBinding(const FSFCSceneData& Data)const{return Data.SourcePid==SourcePid&&Data.ModelIdentity==Model&&Data.SourceIdentity==Source;}
    uint64 Updates=0;
private:
    bool StartSession(const FString& Map,uint32 Pid,FString& Error);
    sfc_source_view::Reader Reader;
    TUniquePtr<sfc_source_view::Frame> Packet;
    FSFCFrame Current{};
    uint32 Owner=0,Revision=0,Model=0,Source=0,SourcePid=0,LastFrame=0;
    uint64 LastSequence=0;
    FString MapName;
    FSFCSourceSnapshot Scene;
    TArray<sfc_source_view::Asset> Catalog;
    TSet<uint32> SeenCatalog,Retired;
    uint32 CatalogCounter=0;
    std::array<uint32_t,sfc_source_view::Owners> SlotEpochs{};
};
