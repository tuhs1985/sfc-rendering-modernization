#include "SFCGameOutput.h"
#include "SFCSessionSubsystem.h"
#include "SFCWorldSubsystem.h"
bool FSFCGameOutput::Start(const FString& Receiver,const FString& SourceMap,const SFCSource::Point& WorldOffset,FString& Error){
    const FString Prefix=TEXT("Local\\SFCBridge_");
    if(Started||Receiver.IsEmpty()||!SourceMap.StartsWith(Prefix)||SourceMap.Len()!=Prefix.Len()+32||WorldOffset[3]!=0){
        Error=TEXT("Incomplete additive output startup");return false;
    }
    for(double Value:WorldOffset)if(!std::isfinite(Value)){Error=TEXT("Invalid world offset");return false;}
    uint32 Words[4]{};
    for(int32 I=0;I<4;++I){
        const FString Hex=SourceMap.Mid(Prefix.Len()+I*8,8);
        for(TCHAR C:Hex)if(!FChar::IsHexDigit(C)){Error=TEXT("Invalid output session");return false;}
        Words[I]=uint32(FCString::Strtoui64(*Hex,nullptr,16));
    }
    Session={uint64(Words[0])|(uint64(Words[1])<<32),uint64(Words[2])|(uint64(Words[3])<<32)};
    // Passive start: no asset, camera or target dependency. The receiver binds
    // only after it independently recovers the first exact native transaction.
    if(!Producer.Start(Receiver,FString(),Session,Error,false,0,true))return false;
    SessionName=SourceMap;Offset=WorldOffset;Started=true;return true;
}
bool FSFCGameOutput::BeforeCapture(USFCWorldSubsystem* World,USFCSessionSubsystem* Retained,const FSFCLiveSource& Source,bool& Capture,FString& Error){
    Capture=false;Prepared=false;
    if(!Started||Source.SessionName()!=SessionName){Error=TEXT("Output source session changed");return false;}
    if(!Producer.Poll(Error))return false;
    sfc_source_view::NativeTarget Target{};
    const auto State=Source.Target(Target);using S=sfc_source_view::Status;
    if(State==S::Empty||State==S::Retry||State==S::Stopped)return true;
    if(State!=S::Ready){Error=TEXT("Native output target identity changed");return false;}
    const auto& Snapshot=Source.Snapshot();
    if(!World||!Retained||!Snapshot.Sequence||Snapshot.Sequence==LastSequence||!Snapshot.FrameHash)return true;
    const FSFCSourceInstance* Selected=Snapshot.Instances.FindByPredicate([&](const FSFCSourceInstance& Item){
        return Item.Owner==Snapshot.Anchor&&Item.Revision==Snapshot.AnchorRevision;
    });
    if(!Selected||!Selected->PoseQualified||Selected->Sequence!=Snapshot.Sequence||!Selected->CameraPoseHash)return true;
    const auto* Binding=Retained->Binding(Selected->Owner,Selected->Revision,Selected->Model,Selected->Source);
    if(!Binding)return true;
    if(BoundOwner&&(BoundOwner!=Selected->Owner||BoundRevision!=Selected->Revision||BoundModel!=Selected->Model||
                    BoundSource!=Selected->Source||BoundContent!=Binding->Content)){
        Error=TEXT("Additive player binding changed; fresh activation required");return false;
    }
    auto Packet=sfc_ue_export::Packet{};
    Packet.flags=sfc_ue_output::SourceFrame|sfc_ue_output::SourceSequence;
    Packet.identity.session=Session;Packet.identity.owner_epoch=Selected->Owner;Packet.identity.revision=Selected->Revision;
    if(Binding->Content.Len()!=64){Error=TEXT("Invalid retained asset identity");return false;}
    for(int32 I=0;I<32;++I)Packet.identity.asset[I]=uint8(FCString::Strtoi(*Binding->Content.Mid(I*2,2),nullptr,16));
    Packet.identity.frame=Snapshot.Frame;Packet.identity.sequence=Snapshot.Sequence;
    Packet.identity.camera_pose=Selected->CameraPoseHash;Packet.identity.cohort=Snapshot.FrameHash;
    Packet.identity.output=Producer.Submitted+1;
    Packet.identity.activation=1;Packet.identity.device=Target.device;Packet.identity.target=Packet.resource_epoch=Target.generation;
    const auto& Camera=Snapshot.Camera;
    Packet.viewport_x=uint32(Camera.Viewport[0]);Packet.viewport_y=uint32(Camera.Viewport[1]);
    Packet.width=uint32(Camera.Viewport[2]);Packet.height=uint32(Camera.Viewport[3]);
    Packet.target_width=Target.width;Packet.target_height=Target.height;
    Packet.p22=Camera.Projection[2][2];Packet.p23=Camera.Projection[2][3];
    if(!BoundOwner){
        if(!Producer.Prepare(Packet,Error))return false;
        BoundOwner=Selected->Owner;BoundRevision=Selected->Revision;BoundModel=Selected->Model;BoundSource=Selected->Source;BoundContent=Binding->Content;
    }else if(!Producer.Reconfigure(Packet,Error))return Error.IsEmpty();
    if(!Producer.Ready())return true;
    if(!World->PrepareDiagnosticOwner(*Selected,Offset,Error))return Error.IsEmpty();
    Pending=Packet;Prepared=true;Capture=true;return true;
}
bool FSFCGameOutput::AfterCapture(USFCWorldSubsystem* World,FString& Error){
    if(!Prepared||!World)return true;
    Prepared=false;
    auto* Depth=World->CapturePersistentDepth();if(!Depth)return true;
    const bool Sent=Producer.Submit(Pending,World->Target(),Depth,Error);
    if(Sent)LastSequence=Pending.identity.sequence;
    return Error.IsEmpty();
}
