#include "SFCLiveSource.h"
#include "ue_source_identity.h"
bool FSFCLiveSource::Start(const FString& Map,uint32 Pid,uint32 InOwner,uint32 InRevision,uint32 InModel,uint32 InSource,FString& Error){
    if(!InOwner||!InRevision||!InModel||!InSource){Error=TEXT("Incomplete source owner identity");return false;}
    if(!StartSession(Map,Pid,Error))return false;
    Owner=InOwner;Revision=InRevision;Model=InModel;Source=InSource;return true;
}
bool FSFCLiveSource::StartScene(const FString& Map,uint32 Pid,FString& Error){return StartSession(Map,Pid,Error);}
bool FSFCLiveSource::StartSession(const FString& Map,uint32 Pid,FString& Error){
    const FString Hex=Map.Right(32);std::array<uint32_t,4> Session{};
    if(Map.Len()<32||!Pid){Error=TEXT("Incomplete source identity");return false;}
    for(TCHAR C:Hex)if(!FChar::IsHexDigit(C)){Error=TEXT("Invalid source session");return false;}
    for(int32 I=0;I<4;++I)Session[I]=FCString::Strtoui64(*Hex.Mid(I*8,8),nullptr,16);
    if(!Reader.open(std::wstring(*Map),Session,Pid)){Error=TEXT("Could not attach read-only source session");return false;}
    MapName=Map;SourcePid=Pid;
    Packet=MakeUnique<sfc_source_view::Frame>();return true;
}
bool FSFCLiveSource::Poll(bool& Changed,bool& Stopped,FString& Error){
    Changed=Stopped=false;if(!Packet){Error=TEXT("Source reader not started");return false;}
    const auto Status=Reader.poll(*Packet);
    using S=sfc_source_view::Status;
    if(Status==S::Stopped){Stopped=true;return true;}
    if(Status==S::Empty||Status==S::Retry||Status==S::Unchanged)return true;
    if(Status!=S::Ready){Error=TEXT("Source session or sealed frame changed unexpectedly");return false;}
    const auto* Row=sfc_source_view::find(*Packet,Owner,Revision,Model,Source);
    // Missing/offscreen rows do not retire retained geometry or change identity.
    if(!Row)return true;
    sfc_source_view::Pose Pose;if(!sfc_source_view::pose(*Row,Pose))return true;
    auto Copy=[](const std::array<double,16>& From,SFCSource::Matrix& To){
        for(int32 R=0;R<4;++R)for(int32 C=0;C<4;++C)To[R][C]=From[R*4+C];
    };
    FSFCFrame Candidate;Copy(Pose.model,Candidate.Model);Copy(Pose.view,Candidate.View);Copy(Pose.projection,Candidate.Projection);
    if(!SFCSource::ValidAffine(Candidate.Model)||!SFCSource::ValidAffine(Candidate.View)){
        Error=TEXT("Invalid source affine transform");return false;
    }
    for(int32 I=0;I<4;++I)Candidate.Viewport[I]=Pose.viewport[I];
    Current=MoveTemp(Candidate);LastSequence=Packet->sequence;LastFrame=Packet->frame;++Updates;Changed=true;return true;
}

bool FSFCLiveSource::PollScene(bool& Changed,bool& Stopped,FString& Error){
    Changed=Stopped=false;Catalog.Reset();Scene.Retirements.Reset();
    if(!Packet){Error=TEXT("Source reader not started");return false;}
    const auto Status=Reader.poll(*Packet);using S=sfc_source_view::Status;
    if(Status==S::Stopped){Stopped=true;return true;}
    if(Status==S::InvalidHeader||Status==S::InvalidFrame){Error=TEXT("Source session or sealed frame changed unexpectedly");return false;}
    auto Copy=[](const std::array<double,16>& From,SFCSource::Matrix& To){
        for(int32 R=0;R<4;++R)for(int32 C=0;C<4;++C)To[R][C]=From[R*4+C];
    };
    if(Status==S::Ready){
        sfc_source_view::Pose Common;
        if(!sfc_source_view::camera(Packet->rows[0],Common)){Error=TEXT("Invalid coherent source camera");return false;}
        Copy(Common.view,Scene.Camera.View);Copy(Common.projection,Scene.Camera.Projection);
        if(!SFCSource::ValidAffine(Scene.Camera.View)){Error=TEXT("Invalid source camera affine transform");return false;}
        for(int32 I=0;I<4;++I)Scene.Camera.Viewport[I]=Common.viewport[I];
        Scene.Frame=Packet->frame;Scene.Sequence=Packet->sequence;Scene.Offered=Packet->offered;
        Scene.FrameHash=Packet->checksum;Scene.Anchor=Packet->anchor;Scene.AnchorRevision=Packet->revision;Scene.Instances.Reset(Packet->count);
        for(uint32 I=0;I<Packet->count;++I){
            const auto& Row=Packet->rows[I];if(Retired.Contains(Row[1]))continue;
            FSFCSourceInstance Instance;Instance.Owner=Row[1];Instance.Revision=Row[7];Instance.Model=Row[5];Instance.Source=Row[6];
            Instance.Sequence=sfc_source_view::sequence(Row);Instance.CameraPoseHash=sfc_ue_game::camera_hash(Row);
            sfc_source_view::Pose SourcePose;
            if(sfc_source_view::pose(Row,SourcePose)){
                Copy(SourcePose.model,Instance.Pose);Instance.PoseQualified=SFCSource::ValidAffine(Instance.Pose);
            }
            Scene.Instances.Add(MoveTemp(Instance));
        }
        ++Updates;Changed=true;
    }
    const uint32 Count=Reader.owner_count();
    if(Count>sfc_source_view::Owners){Error=TEXT("Source owner table exceeds its declared byte budget");return false;}
    auto RetireEpoch=[&](uint32 Epoch){
        if(!Epoch||Retired.Contains(Epoch))return;
        Retired.Add(Epoch);Scene.Retirements.Add(Epoch);
        Scene.Instances.RemoveAll([&](const FSFCSourceInstance& Instance){return Instance.Owner==Epoch;});Changed=true;
    };
    for(uint32 I=0;I<Count;++I){
        sfc_source_view::Row Row{};
        if(Reader.owner_state(I,Row)==S::Ready){
            // The pinned producer recycles only retired slots. Epoch change is
            // authoritative even if its intermediate state=2 was coalesced away.
            if(SlotEpochs[I]&&SlotEpochs[I]!=Row[1])RetireEpoch(SlotEpochs[I]);
            SlotEpochs[I]=Row[1];if(Row[4]==2)RetireEpoch(Row[1]);
        }
    }
    // asset_ready is a downstream admission receipt, not a producer notice.
    // Waiting for it would bootstrap the consumer from its own acknowledgement.
    // Scan only guards for unseen immutable slots; validate each payload once.
    for(uint32 I=0;I<sfc_source_view::Assets;++I){
        if(SeenCatalog.Contains(I))continue;
        sfc_source_view::Asset Asset{};const auto State=Reader.catalog(I,Asset);
        if(State==S::Ready){Catalog.Add(Asset);SeenCatalog.Add(I);}
    }
    CatalogCounter=SeenCatalog.Num();
    return true;
}
