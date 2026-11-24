#include "SFCStreamCheck.h"
#include "SFCWorldSubsystem.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "HAL/PlatformMisc.h"
bool FSFCStreamCheck::Start(const FSFCSceneData& Data,const FString& Output,FString& Error){
    FString Consumer;
    if(!FParse::Value(FCommandLine::Get(),TEXT("SFCGpuConsumer="),Consumer)||Output.IsEmpty()){
        Error=TEXT("Persistent GPU fixture needs a receiver and diagnostic output");return false;
    }
    uint32 W=0,H=0;
    if(!FParse::Value(FCommandLine::Get(),TEXT("SFCNativeWidth="),W)||!FParse::Value(FCommandLine::Get(),TEXT("SFCNativeHeight="),H)){
        Error=TEXT("Supply the explicit native-target fixture extent");return false;
    }
    Source=&Data;OutputDirectory=Output;Started=FPlatformTime::Seconds();
    FParse::Value(FCommandLine::Get(),TEXT("SFCStreamFrames="),FrameCount);
    FParse::Value(FCommandLine::Get(),TEXT("SFCStreamPassiveMs="),PassiveMilliseconds);
    if(FrameCount<4||FrameCount>10000){Error=TEXT("Diagnostic stream frames must be 4..10000");return false;}
    if(PassiveMilliseconds>10000){Error=TEXT("Diagnostic passive interval exceeds ten seconds");return false;}
    const FGuid Session=FGuid::NewGuid();
    Description.identity.session={(uint64(Session.A)<<32)|Session.B,(uint64(Session.C)<<32)|Session.D};
    for(int32 i=0;i<32;++i)Description.identity.asset[i]=uint8(FCString::Strtoi(*Data.Content.Mid(i*2,2),nullptr,16));
    GamePool=FParse::Param(FCommandLine::Get(),TEXT("SFCGamePoolFixture"));
    if(GamePool){
        const FString Prefix=TEXT("Local\\SFCBridge_");
        if(!Data.Session.StartsWith(Prefix)||Data.Session.Len()!=Prefix.Len()+32||Data.SourcePid<=0){
            Error=TEXT("Game-pool fixture requires an explicit native source session");return false;
        }
        uint32 Words[4]{};
        for(int32 I=0;I<4;++I){
            const FString Hex=Data.Session.Mid(Prefix.Len()+I*8,8);
            for(TCHAR C:Hex)if(!FChar::IsHexDigit(C)){Error=TEXT("Invalid native fixture session");return false;}
            Words[I]=uint32(FCString::Strtoui64(*Hex,nullptr,16));
        }
        Description.identity.session={uint64(Words[0])|(uint64(Words[1])<<32),uint64(Words[2])|(uint64(Words[3])<<32)};
        FString EventName;
        if(!FParse::Value(FCommandLine::Get(),TEXT("SFCFixtureReadEvent="),EventName)){
            Error=TEXT("Native-pool fixture needs a read-completion event");return false;
        }
        FixtureReadEvent.value=OpenEventW(SYNCHRONIZE,false,*EventName);
        if(!FixtureReadEvent.value){Error=TEXT("Native fixture read event unavailable");return false;}
    }
    Description.flags=sfc_ue_output::Replay;
    Description.identity.owner_epoch=Data.OwnerEpoch;Description.identity.revision=Data.Revision;
    Description.identity.activation=Description.identity.device=Description.identity.target=1;
    Description.resource_epoch=1;
    const auto& F=Data.Frames[0];
    Description.width=uint32(F.Viewport[2]);Description.height=uint32(F.Viewport[3]);
    Description.viewport_x=uint32(F.Viewport[0]);Description.viewport_y=uint32(F.Viewport[1]);
    Description.target_width=W;Description.target_height=H;
    InitialWidth=W;InitialHeight=H;
    if(uint64(Description.viewport_x)+Description.width>W||uint64(Description.viewport_y)+Description.height>H){
        Error=TEXT("Fixture viewport does not fit its native target");return false;
    }
    IFileManager::Get().MakeDirectory(*Output,true);
    const FString Images=FParse::Param(FCommandLine::Get(),TEXT("SFCStreamNoReadback"))?FString():Output/TEXT("receiver");
    return Producer.Start(Consumer,Images,Description.identity.session,Error,true,FrameCount,GamePool)&&Producer.Prepare(Description,Error);
}
bool FSFCStreamCheck::BeforeCapture(USFCWorldSubsystem* World,FString& Error){
    if(Finished)return true;
    CapturePrepared=false;
    if(!Producer.Poll(Error))return false;
    if((FParse::Param(FCommandLine::Get(),TEXT("SFCStreamCancelBeforeFirst"))&&Producer.Ready())||
       (FParse::Param(FCommandLine::Get(),TEXT("SFCStreamCancelDuringRead"))&&Producer.HasReading()))return Cancel(Error);
    // Diagnostic pacing only: prove every native read before destroying the
    // producer. The production path never waits for this fixture counter.
    if(GamePool&&NativeConsumed()<Producer.Submitted)return true;
    if(Producer.Submitted<FrameCount){
        CurrentFrame=int32(Producer.Submitted%uint64(Source->Frames.Num()));
        const auto& Frame=Source->Frames[CurrentFrame];
        auto Wanted=Description;
        Wanted.width=uint32(Frame.Viewport[2]);Wanted.height=uint32(Frame.Viewport[3]);
        Wanted.viewport_x=uint32(Frame.Viewport[0]);Wanted.viewport_y=uint32(Frame.Viewport[1]);
        Wanted.target_width=InitialWidth;Wanted.target_height=InitialHeight;
        double Extent=0;
        if(Frame.Original->TryGetNumberField(TEXT("target_width"),Extent))Wanted.target_width=uint32(Extent);
        if(Frame.Original->TryGetNumberField(TEXT("target_height"),Extent))Wanted.target_height=uint32(Extent);
        if(Wanted.width!=Description.width||Wanted.height!=Description.height||Wanted.viewport_x!=Description.viewport_x||Wanted.viewport_y!=Description.viewport_y||
           Wanted.target_width!=Description.target_width||Wanted.target_height!=Description.target_height){
            ++Wanted.identity.target;++Wanted.resource_epoch;
            if(!Producer.Reconfigure(Wanted,Error))return Error.IsEmpty();
            Description=Wanted;++GenerationChanges;
        }
        if(!World->EnsureCaptureExtent(CurrentFrame,Error))return Error.IsEmpty();
        if(!World->Apply(CurrentFrame)){Error=TEXT("Persistent source pose rejected");return false;}
        Offered=sfc_ue_export::now();
        CapturePrepared=true;
    }
    return true;
}
bool FSFCStreamCheck::Tick(USFCWorldSubsystem* World,FString& Error){
    if(Finished)return true;
    if(CapturePrepared&&Producer.Submitted<FrameCount&&Producer.Ready()&&1000*(FPlatformTime::Seconds()-Started)>=PassiveMilliseconds){
        auto* Depth=World->CapturePersistentDepth();
        if(!Depth)return true;
        auto Packet=Description;const auto& Frame=Source->Frames[CurrentFrame];
        Packet.identity.output=Producer.Submitted+1;
        // Explicit offline replay: never pretend these are fresh native frames.
        double Native=0;
        if(Frame.Original->TryGetNumberField(TEXT("source_frame"),Native)&&Native>0)Packet.identity.frame=uint64(Native);
        if(Frame.Original->TryGetNumberField(TEXT("source_sequence"),Native)&&Native>0)Packet.identity.sequence=uint64(Native);
        Packet.identity.camera_pose=sfc_ue_output::hash(&Frame.Model,sizeof(Frame.Model));
        for(uint64 Part:{sfc_ue_output::hash(&Frame.View,sizeof(Frame.View)),sfc_ue_output::hash(&Frame.Projection,sizeof(Frame.Projection)),sfc_ue_output::hash(&Frame.Viewport,sizeof(Frame.Viewport))})
            Packet.identity.camera_pose=(Packet.identity.camera_pose^Part)*1099511628211ull;
        Packet.identity.cohort=Packet.identity.camera_pose;
        if(GamePool){
            FString Hash;
            if(!Packet.identity.frame||!Packet.identity.sequence||!Frame.Original->TryGetStringField(TEXT("native_frame_hash"),Hash)||Hash.Len()!=16){
                Error=TEXT("Game-pool fixture needs exact source frame/sequence/seal identity");return false;
            }
            for(TCHAR C:Hash)if(!FChar::IsHexDigit(C)){Error=TEXT("Invalid native fixture seal");return false;}
            Packet.identity.cohort=FCString::Strtoui64(*Hash,nullptr,16);
        }
        Packet.p22=Frame.Projection[2][2];Packet.p23=Frame.Projection[2][3];
        if(Producer.Submitted==1&&FParse::Param(FCommandLine::Get(),TEXT("SFCStreamStaleDevice")))++Packet.identity.device;
        const bool Sent=Producer.Submit(Packet,World->Target(),Depth,Error,Offered);
        if(!Error.IsEmpty())return false;
        if(Sent){
            auto Record=MakeShared<FJsonObject>();Record->SetNumberField(TEXT("output"),Packet.identity.output);
            Record->SetNumberField(TEXT("frame_index"),CurrentFrame);
            if(Producer.Submitted<=4)Record->SetObjectField(TEXT("source"),Frame.Original);
            SubmittedFrames.Add(MakeShared<FJsonValueObject>(Record));
        }
    }
    if(Producer.Submitted==FrameCount&&Producer.Completed==FrameCount&&Producer.Drained()&&(!GamePool||NativeConsumed()==FrameCount)){
        Producer.Stop();Finished=true;
        auto Result=MakeShared<FJsonObject>();Result->SetStringField(TEXT("scope"),TEXT("standalone replay; no SFC insertion"));
        Result->SetNumberField(TEXT("submitted"),Producer.Submitted);Result->SetNumberField(TEXT("completed"),Producer.Completed);
        Result->SetNumberField(TEXT("busy_skips"),Producer.Busy);Result->SetArrayField(TEXT("frames"),SubmittedFrames);
        Result->SetNumberField(TEXT("generation_changes"),GenerationChanges);
        Result->SetNumberField(TEXT("seconds"),FPlatformTime::Seconds()-Started);
        Result->SetStringField(TEXT("source_session"),Source->Session);Result->SetStringField(TEXT("asset"),Source->Content);
        Result->SetStringField(TEXT("replay_session"),FString::Printf(TEXT("%016llx%016llx"),Description.identity.session[0],Description.identity.session[1]));
        TArray<TSharedPtr<FJsonValue>> Timings;
        for(const auto& T:Producer.Timings){
            auto Sample=MakeShared<FJsonObject>();Sample->SetNumberField(TEXT("output"),T.Output);
            Sample->SetNumberField(TEXT("queue_ms"),T.QueueMs);Sample->SetNumberField(TEXT("receiver_ms"),T.ReceiverMs);
            Sample->SetNumberField(TEXT("gpu_and_worker_ms"),T.GpuMs);Sample->SetNumberField(TEXT("total_ms"),T.TotalMs);
            Timings.Add(MakeShared<FJsonValueObject>(Sample));
        }
        Result->SetArrayField(TEXT("timings"),Timings);
        FString Json;FJsonSerializer::Serialize(Result,TJsonWriterFactory<>::Create(&Json));
        if(!FFileHelper::SaveStringToFile(Json,*(OutputDirectory/TEXT("stream.json")))){Error=TEXT("Stream receipt failed");return false;}
        FPlatformMisc::RequestExit(false);
    }
    return true;
}
bool FSFCStreamCheck::Cancel(FString& Error){
    Producer.Stop();Finished=true;
    auto Result=MakeShared<FJsonObject>();Result->SetNumberField(TEXT("submitted"),Producer.Submitted);
    Result->SetNumberField(TEXT("completed"),Producer.Completed);Result->SetBoolField(TEXT("drained"),Producer.Drained());
    FString Json;FJsonSerializer::Serialize(Result,TJsonWriterFactory<>::Create(&Json));
    if(!FFileHelper::SaveStringToFile(Json,*(OutputDirectory/TEXT("cancelled.json")))||!Producer.Drained()){
        Error=TEXT("Cancelled stream did not drain its GPU leases");return false;
    }
    FPlatformMisc::RequestExit(false);return true;
}

uint32 FSFCStreamCheck::NativeConsumed(){
    if(FixtureReadEvent.value&&FixtureConsumed<Producer.Submitted&&WaitForSingleObject(FixtureReadEvent.value,0)==WAIT_OBJECT_0)++FixtureConsumed;
    return FixtureConsumed;
}
void FSFCStreamCheck::Stop(){
    Producer.Stop();FixtureReadEvent.reset();
}
