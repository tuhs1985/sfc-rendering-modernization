#include "SFCInspectionMode.h"
#include "SFCGameOutput.h"
#include "SFCGpuExchangeCheck.h"
#include "SFCStreamCheck.h"
#include "SFCLiveSource.h"
#include "SFCRegistryCheck.h"
#include "SFCSceneTiming.h"
#include "SFCSessionSubsystem.h"
#include "SFCWorldSubsystem.h"
#include "Modules/ModuleManager.h"
#include "Engine/GameInstance.h"
#include "Engine/GameViewportClient.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Engine/StaticMesh.h"
#include "StaticMeshResources.h"
#include "Engine/Engine.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "InputCoreTypes.h"
#include "Misc/CommandLine.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "Serialization/JsonSerializer.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/Layout/SConstraintCanvas.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Text/STextBlock.h"
#include "Styling/SlateBrush.h"
#include "Framework/Application/SlateApplication.h"
#include "SFCInspectionView.h"
IMPLEMENT_MODULE(FDefaultModuleImpl,SFCBridgeRuntime);
ASFCInspectionMode::ASFCInspectionMode() { PrimaryActorTick.bCanEverTick=true; DefaultPawnClass=nullptr; }
void ASFCInspectionMode::Fail(const FString& Why) {
    UE_LOG(LogTemp,Error,TEXT("SFC_BRIDGE_REJECTED %s"),*Why);
    // Explicit test receipt in Shipping too: logs/assertions are not admission logic.
    if(Diagnostics&&!OutputDirectory.IsEmpty()) {
        IFileManager::Get().MakeDirectory(*OutputDirectory,true);
        FFileHelper::SaveStringToFile(Why,*(OutputDirectory/TEXT("rejected.txt")));
    }
    FPlatformMisc::RequestExitWithStatus(false,2);
}
void ASFCInspectionMode::BeginPlay() {
    Super::BeginPlay(); Started=FPlatformTime::Seconds(); FString Input,Error;
    Diagnostics=FParse::Param(FCommandLine::Get(),TEXT("SFCDiagnostics"));
    FParse::Value(FCommandLine::Get(),TEXT("SFCOutput="),OutputDirectory);
    FParse::Value(FCommandLine::Get(),TEXT("SFCFrame="),Frame);
    if(Diagnostics&&OutputDirectory.IsEmpty()) { Fail(TEXT("Diagnostics requires a separate output directory")); return; }
    FParse::Value(FCommandLine::Get(),TEXT("SFCDefinitionDirectory="),DefinitionDirectory);
    if(!FParse::Value(FCommandLine::Get(),TEXT("SFCScene="),Input)&&DefinitionDirectory.IsEmpty()) { Fail(TEXT("Supply a captured SFC scene")); return; }
    if(FParse::Value(FCommandLine::Get(),TEXT("SFCSourceMap="),SourceMap)){
        uint32 ParentPid=0;
        if(FParse::Value(FCommandLine::Get(),TEXT("SFCParentPID="),ParentPid)){
            if(!ParentPid||(SourceParent=FPlatformProcess::OpenProcess(ParentPid),!SourceParent.IsValid())){Fail(TEXT("Source supervisor unavailable"));return;}
        }
        uint32 Pid=0,Model=0,Source=0;
        FParse::Value(FCommandLine::Get(),TEXT("SFCSourcePID="),Pid);
        FParse::Value(FCommandLine::Get(),TEXT("SFCOwner="),SourceOwner);
        FParse::Value(FCommandLine::Get(),TEXT("SFCRevision="),SourceRevision);
        FParse::Value(FCommandLine::Get(),TEXT("SFCModelIdentity="),Model);
        FParse::Value(FCommandLine::Get(),TEXT("SFCSourceIdentity="),Source);
        if(FParse::Param(FCommandLine::Get(),TEXT("SFCSourceReplay"))){
            FParse::Value(FCommandLine::Get(),TEXT("SFCSourceReplayUpdates="),SourceReplayUpdates);
            if(!Diagnostics||SourceReplayUpdates<1){Fail(TEXT("Source replay requires bounded explicit diagnostics"));return;}
        }
        LiveSource=MakeShared<FSFCLiveSource>();
        if(!DefinitionDirectory.IsEmpty()){
            auto* Session=GetGameInstance()->GetSubsystem<USFCSessionSubsystem>();
            if(Session->LiveReader){
                LiveSource=Session->LiveReader;
                if(LiveSource->SessionName()!=SourceMap||LiveSource->Pid()!=Pid){Fail(TEXT("Cannot reuse another source session"));return;}
            }else if(!LiveSource->StartScene(SourceMap,Pid,Error)){Fail(Error);return;}
            Session->LiveReader=LiveSource;
            FString Check;
            if(FParse::Value(FCommandLine::Get(),TEXT("SFCRegistryCheck="),Check)){
                if(!Diagnostics){Fail(TEXT("Registry fixture requires explicit diagnostics"));return;}
                RegistryCheck=MakeShared<FSFCRegistryCheck>();if(!RegistryCheck->Start(Check,Error)){Fail(Error);return;}
            }
            int32 TimingFrames=0,TimingOwners=0;
            if(FParse::Value(FCommandLine::Get(),TEXT("SFCRegistryTiming="),TimingFrames)){
                FParse::Value(FCommandLine::Get(),TEXT("SFCRegistryTimingOwners="),TimingOwners);
                if(!Diagnostics||RegistryCheck){Fail(TEXT("Standalone timing requires its own explicit diagnostic mode"));return;}
                RegistryTiming=MakeShared<FSFCSceneTiming>();
                if(!RegistryTiming->Start(TimingFrames,TimingOwners,OutputDirectory,Error)){Fail(Error);return;}
            }
            if(FParse::Param(FCommandLine::Get(),TEXT("SFCNativeAdditive"))){
                FString Receiver;SFCSource::Point Offset{};
                if(RegistryCheck||RegistryTiming||SourceReplayUpdates||
                   !FParse::Value(FCommandLine::Get(),TEXT("SFCGpuConsumer="),Receiver)||
                   !FParse::Value(FCommandLine::Get(),TEXT("SFCWorldOffsetX="),Offset[0])||
                   !FParse::Value(FCommandLine::Get(),TEXT("SFCWorldOffsetY="),Offset[1])||
                   !FParse::Value(FCommandLine::Get(),TEXT("SFCWorldOffsetZ="),Offset[2])){
                    Fail(TEXT("Additive output requires its receiver and three explicit world offsets"));return;
                }
                GameOutput=MakeShared<FSFCGameOutput>();
                if(!GameOutput->Start(Receiver,SourceMap,Offset,Error)){Fail(Error);return;}
            }
        }else if(!LiveSource->Start(SourceMap,Pid,SourceOwner,SourceRevision,Model,Source,Error)){Fail(Error);return;}
        SourceInput=Input;
        Overlay=SNew(SConstraintCanvas)
            +SConstraintCanvas::Slot().Offset(FMargin(12,8,260,34))[
                SNew(SButton).OnClicked_Lambda([] { FPlatformMisc::RequestExit(false);return FReply::Handled(); })[
                    SNew(STextBlock).Text(FText::FromString(TEXT("Waiting for SFC - Exit (Escape)")))]];
        if(GEngine&&GEngine->GameViewport)GEngine->GameViewport->AddViewportWidgetContent(Overlay.ToSharedRef());
        if(auto* PC=GetWorld()->GetFirstPlayerController()){PC->bShowMouseCursor=true;PC->SetInputMode(FInputModeGameAndUI());}
        if(Diagnostics){
            IFileManager::Get().MakeDirectory(*OutputDirectory,true);
            FFileHelper::SaveStringToFile(TEXT("{\"attached_read_only\":true}"),*(OutputDirectory/TEXT("source-attached.json")));
        }
        return; // Passive lifetime has no asset deadline. Escape still closes it.
    }
    ActivateScene(Input);
}
void ASFCInspectionMode::ActivateScene(const FString& Input){
    FString Error;
    auto* Session=GetGameInstance()->GetSubsystem<USFCSessionSubsystem>();
    // The input definition is immutable for this offline session. World recreation
    // reuses the admitted definition; it is not a request to reload changed files.
    if(!Session->Mesh()&&!Session->Load(Input,Diagnostics,Error)) { Fail(Error); return; }
    if(LiveSource&&(Session->Data().Session!=SourceMap||Session->Data().OwnerEpoch!=SourceOwner||Session->Data().Revision!=SourceRevision||!LiveSource->MatchesBinding(Session->Data()))){
        Fail(TEXT("Late source asset belongs to another session/owner/revision/model/source"));return;
    }
    SceneWorld=GetWorld()->GetSubsystem<USFCWorldSubsystem>();
    const bool Procedural=FParse::Param(FCommandLine::Get(),TEXT("SFCProcedural"));
    if(!SceneWorld->Start(Session,Frame,Procedural,FParse::Param(FCommandLine::Get(),TEXT("SFCSharedOwner")),Error)) { Fail(Error.IsEmpty()?TEXT("Source pose cannot be represented without changing geometry"):Error); return; }
    if(Diagnostics&&FParse::Param(FCommandLine::Get(),TEXT("SFCGpuStream"))){
        if(SceneWorld->IdentityCount()!=1){Fail(TEXT("Paired depth fixture requires one source owner"));return;}
        StreamCheck=MakeShared<FSFCStreamCheck>();
        if(!StreamCheck->Start(Session->Data(),OutputDirectory,Error)){Fail(Error);return;}
    }
    ShadowCheck=Diagnostics&&FParse::Param(FCommandLine::Get(),TEXT("SFCShadowCheck"));
    if(ShadowCheck&&!SceneWorld->PrepareShadowFixture()) { Fail(TEXT("Hardware ray-traced shadow fixture unavailable")); return; }
    const auto& View=Session->Data().Frames[Frame].Viewport;
    if(GEngine&&GEngine->GameViewport&&Overlay.IsValid())GEngine->GameViewport->RemoveViewportWidgetContent(Overlay.ToSharedRef());
    Brush=MakeShared<FSlateBrush>(); Brush->SetResourceObject(SceneWorld->Target()); Brush->ImageSize=FVector2D(View[2],View[3]);
    Overlay=SFCInspectionView(Brush.Get());
    if(GEngine&&GEngine->GameViewport) GEngine->GameViewport->AddViewportWidgetContent(Overlay.ToSharedRef());
    if(auto* PC=GetWorld()->GetFirstPlayerController()) { PC->bShowMouseCursor=true; PC->SetInputMode(FInputModeGameAndUI()); }
    UE_LOG(LogTemp,Display,TEXT("SFC_BRIDGE_READY %s preparation=%.6f"),*Session->Data().ModelName,Session->PreparationSeconds);
}
void ASFCInspectionMode::Tick(float DeltaSeconds) {
    Super::Tick(DeltaSeconds);
    if(SourceParent.IsValid()&&!FPlatformProcess::IsProcRunning(SourceParent)){FPlatformMisc::RequestExit(false);return;}
    if(auto* PC=GetWorld()->GetFirstPlayerController()) if(PC->WasInputKeyJustPressed(EKeys::Escape)) { FPlatformMisc::RequestExit(false); return; }
    if(LiveSource){TickSource();return;}
    if(!SceneWorld||!SceneWorld->Target()) return;
    if(StreamCheck){FString Error;if(!StreamCheck->BeforeCapture(SceneWorld,Error)){Fail(Error);return;}}
    // Continue rendering while UE prepares proxies/PSOs. Readiness gates receipt,
    // not the work required to become ready.
    SceneWorld->Capture();
    // Public UE readiness, not a guessed warm-up duration or assertion side effect.
    if(!SceneWorld->RenderReady()) { Ticks=0; return; }
    if(StreamCheck){FString Error;if(!StreamCheck->Tick(SceneWorld,Error))Fail(Error);return;}
    if(!ReadySeconds) ReadySeconds=FPlatformTime::Seconds()-Started;
    ++Ticks;
    if(Finished||!Diagnostics||Ticks<30) return;
    Finished=true;
    TArray<FColor> Pixels,SharedPixels; FReadSurfaceDataFlags Flags(RCM_UNorm); Flags.SetLinearToGamma(false);
    auto* Target=SceneWorld->Target();
    IFileManager::Get().MakeDirectory(*OutputDirectory,true);
    const bool GpuExchange=FParse::Param(FCommandLine::Get(),TEXT("SFCGpuExchange"));
    if(GpuExchange) {
        FString ExchangeError;
        if(!SFCCheckGpuExchange(Target,SharedPixels,ExchangeError)) { Fail(ExchangeError); return; }
        if(FParse::Param(FCommandLine::Get(),TEXT("SFCGpuDepth"))) {
            if(SceneWorld->IdentityCount()!=1) { Fail(TEXT("Depth-derived owner fixture requires one owner")); return; }
            auto* Depth=SceneWorld->CaptureDiagnosticDepth();
            TArray<FColor> DepthBits;
            const auto& SourceFrame=GetGameInstance()->GetSubsystem<USFCSessionSubsystem>()->Data().Frames[Frame];
            if(!SFCCheckGpuExchange(Depth,DepthBits,ExchangeError,TEXT("depth"),
                SourceFrame.Projection[2][2],SourceFrame.Projection[2][3],SourceFrame.Original->GetIntegerField(TEXT("owner")))) { Fail(ExchangeError); return; }
        }
    }
    // Export completes through its own GPU fence before the reference readback.
    if(!Target->GameThread_GetRenderTargetResource()->ReadPixels(Pixels,Flags)) { Fail(TEXT("Diagnostic readback failed")); return; }
    if(FParse::Param(FCommandLine::Get(),TEXT("SFCInspectionCheck"))){
        TArray<FColor> WindowPixels;FIntVector Size;
        if(!Overlay.IsValid()||!FSlateApplication::Get().TakeScreenshot(Overlay.ToSharedRef(),WindowPixels,Size)||
           !FFileHelper::CreateBitmap(*(OutputDirectory/TEXT("inspection.bmp")),Size.X,Size.Y,WindowPixels.GetData())){
            Fail(TEXT("Inspection widget pixel check failed"));return;
        }
    }
    if(GpuExchange) {
        if(SharedPixels!=Pixels) { Fail(TEXT("D3D11 pixels differ from UE target")); return; }
        if(!FFileHelper::CreateBitmap(*(OutputDirectory/TEXT("d3d11.bmp")),Target->SizeX,Target->SizeY,SharedPixels.GetData())) {
            Fail(TEXT("Shared image write failed")); return;
        }
    }
    if(ShadowCheck&&!ShadowSecondPass) {
        if(!FFileHelper::CreateBitmap(*(OutputDirectory/TEXT("shadow-on.bmp")),Target->SizeX,Target->SizeY,Pixels.GetData())) { Fail(TEXT("Shadow fixture image failed")); return; }
        ShadowPixels=MoveTemp(Pixels); ShadowSecondPass=true; Finished=false; Ticks=0;
        SceneWorld->SetFixtureShadows(false); return;
    }
    auto* Session=GetGameInstance()->GetSubsystem<USFCSessionSubsystem>(); const auto& D=Session->Data();
    const bool RestartWorld=FParse::Param(FCommandLine::Get(),TEXT("SFCWorldRestart"))&&Session->WorldActivations==1;
    const FString ImageFile=RestartWorld?TEXT("ship-before-world-restart.bmp"):TEXT("ship.bmp");
    if(!FFileHelper::CreateBitmap(*(OutputDirectory/ImageFile),Target->SizeX,Target->SizeY,Pixels.GetData())) { Fail(TEXT("Diagnostic image write failed")); return; }
    auto Receipt=MakeShared<FJsonObject>();
    Receipt->SetStringField(TEXT("session"),D.Session); Receipt->SetStringField(TEXT("model"),D.ModelName);
    Receipt->SetStringField(TEXT("source_packet_sha256"),D.PacketHash);
    Receipt->SetObjectField(TEXT("source_frame"),D.Frames[Frame].Original);
    Receipt->SetNumberField(TEXT("frame_index"),Frame);
    Receipt->SetNumberField(TEXT("corners"),D.Corners.Num()); Receipt->SetNumberField(TEXT("groups"),D.Groups.Num());
    Receipt->SetNumberField(TEXT("indices"),D.Indices.Num()); Receipt->SetNumberField(TEXT("textures"),D.Images.Num());
    Receipt->SetNumberField(TEXT("width"),Target->SizeX); Receipt->SetNumberField(TEXT("height"),Target->SizeY);
    Receipt->SetNumberField(TEXT("preparation_seconds"),Session->PreparationSeconds);
    Receipt->SetNumberField(TEXT("renderer_ready_seconds"),ReadySeconds);
    Receipt->SetBoolField(TEXT("constructed_arrays_checked"),Session->ArraysChecked);
    Receipt->SetBoolField(TEXT("diagnostic_readback"),true);
    Receipt->SetBoolField(TEXT("synthetic_shadow_fixture"),ShadowCheck);
    if(ShadowCheck) {
        int32 Changed=0;
        for(int32 i=0;i<Pixels.Num();++i) {
            const auto& A=ShadowPixels[i]; const auto& B=Pixels[i];
            if(static_cast<int32>(B.R)-A.R>15||static_cast<int32>(B.G)-A.G>15||static_cast<int32>(B.B)-A.B>15) ++Changed;
        }
        Receipt->SetNumberField(TEXT("shadow_darkened_pixels"),Changed);
        if(Changed<20) { Fail(TEXT("No qualified ray-traced shadow difference")); return; }
    }
    Receipt->SetNumberField(TEXT("built_vertices"),SceneWorld->BuiltVertices);
    Receipt->SetBoolField(TEXT("shared_geometry"),SceneWorld->SharedGeometry);
    Receipt->SetNumberField(TEXT("owner_identities"),SceneWorld->IdentityCount());
    Receipt->SetNumberField(TEXT("asset_builds"),Session->AssetBuilds);
    Receipt->SetNumberField(TEXT("world_activations"),Session->WorldActivations);
    Receipt->SetStringField(TEXT("engine"),FEngineVersion::Current().ToString());
    // Exercise transform-only updates against an already-built shared mesh.
    for(int i=0;i<100;++i) if(!SceneWorld->Apply(i==99?Frame:i%D.Frames.Num())) { Fail(TEXT("Transform replay failed")); return; }
    Receipt->SetNumberField(TEXT("transform_updates"),SceneWorld->TransformUpdates);
    Receipt->SetNumberField(TEXT("transform_seconds"),SceneWorld->TransformSeconds);
    const auto* Proxy=Session->Mesh()->GetRenderData()->RayTracingProxy;
    Receipt->SetBoolField(TEXT("ray_tracing_representation"),Proxy&&Proxy->LODs.Num()>0&&Proxy->LODs[0].RayTracingGeometry!=nullptr);
    Receipt->SetNumberField(TEXT("render_vertices"),Session->Mesh()->GetRenderData()->LODResources[0].VertexBuffers.PositionVertexBuffer.GetNumVertices());
    FString Json; FJsonSerializer::Serialize(Receipt,TJsonWriterFactory<>::Create(&Json));
    const FString ReceiptFile=RestartWorld?TEXT("before-world-restart.json"):TEXT("result.json");
    if(!FFileHelper::SaveStringToFile(Json,*(OutputDirectory/ReceiptFile))) { Fail(TEXT("Diagnostic receipt write failed")); return; }
    if(RestartWorld) { UGameplayStatics::OpenLevel(this,FName(TEXT("/Game/BridgeMap"))); return; }
    if(FParse::Param(FCommandLine::Get(),TEXT("SFCExit"))) FPlatformMisc::RequestExit(false);
}
bool ASFCInspectionMode::TickSource(){
    if(!DefinitionDirectory.IsEmpty())return TickRegistry();
    FString Error;bool Changed=false,Stopped=false;
    if(!LiveSource->Poll(Changed,Stopped,Error)){Fail(Error);return false;}
    if(Stopped){FPlatformMisc::RequestExit(false);return true;}
    if(!SceneWorld&&LiveSource->Sequence()&&IFileManager::Get().FileExists(*SourceInput))ActivateScene(SourceInput);
    if(!SceneWorld||!SceneWorld->Target())return true;
    if(Changed||!ReadySeconds){
        if(!SceneWorld->EnsureSourceExtent(LiveSource->Frame(),Error)||!SceneWorld->ApplySourceFrame(LiveSource->Frame())){
            Fail(Error.IsEmpty()?TEXT("Live source transform rejected"):Error);return false;
        }
    }
    SceneWorld->Capture();
    if(!SceneWorld->RenderReady())return true;
    if(!ReadySeconds)ReadySeconds=FPlatformTime::Seconds()-Started;
    if(!Diagnostics||!SourceReplayUpdates||LiveSource->Updates<uint64(SourceReplayUpdates)||Finished)return true;
    Finished=true;
    auto* Session=GetGameInstance()->GetSubsystem<USFCSessionSubsystem>();
    auto Receipt=MakeShared<FJsonObject>();
    Receipt->SetStringField(TEXT("session"),Session->Data().Session);
    Receipt->SetNumberField(TEXT("updates"),LiveSource->Updates);
    Receipt->SetNumberField(TEXT("sequence"),LiveSource->Sequence());
    Receipt->SetNumberField(TEXT("frame"),LiveSource->SourceFrame());
    Receipt->SetNumberField(TEXT("asset_builds"),Session->AssetBuilds);
    Receipt->SetNumberField(TEXT("transform_updates"),SceneWorld->TransformUpdates);
    Receipt->SetNumberField(TEXT("preparation_seconds"),Session->PreparationSeconds);
    auto MatrixValue=[](const SFCSource::Matrix& M){
        TArray<TSharedPtr<FJsonValue>> Rows;
        for(const auto& Row:M){TArray<TSharedPtr<FJsonValue>> Values;for(double V:Row)Values.Add(MakeShared<FJsonValueNumber>(V));Rows.Add(MakeShared<FJsonValueArray>(Values));}
        return Rows;
    };
    const auto& F=LiveSource->Frame();
    Receipt->SetArrayField(TEXT("model"),MatrixValue(F.Model));Receipt->SetArrayField(TEXT("view"),MatrixValue(F.View));
    Receipt->SetArrayField(TEXT("projection"),MatrixValue(F.Projection));
    TArray<TSharedPtr<FJsonValue>> View;for(double V:F.Viewport)View.Add(MakeShared<FJsonValueNumber>(V));Receipt->SetArrayField(TEXT("viewport"),View);
    // Explicit fixture readback only; no live or diagnostics-off image transfer.
    TArray<FColor> Pixels;FReadSurfaceDataFlags Flags(RCM_UNorm);Flags.SetLinearToGamma(false);
    auto* Target=SceneWorld->Target();
    if(!Target->GameThread_GetRenderTargetResource()->ReadPixels(Pixels,Flags)||
       !FFileHelper::SaveArrayToFile(TArrayView<const uint8>(reinterpret_cast<const uint8*>(Pixels.GetData()),Pixels.Num()*sizeof(FColor)),*(OutputDirectory/TEXT("source-colour.bgra")))){
        Fail(TEXT("Source replay diagnostic readback failed"));return false;
    }
    FString Json;FJsonSerializer::Serialize(Receipt,TJsonWriterFactory<>::Create(&Json));
    if(!FFileHelper::SaveStringToFile(Json,*(OutputDirectory/TEXT("source-result.json")))){Fail(TEXT("Source replay receipt failed"));return false;}
    FPlatformMisc::RequestExit(false);return true;
}
void ASFCInspectionMode::EndPlay(const EEndPlayReason::Type Reason) {
    if(SourceParent.IsValid())FPlatformProcess::CloseProc(SourceParent);
    if(GameOutput){GameOutput->Stop();GameOutput.Reset();}
    if(StreamCheck){StreamCheck->Stop();StreamCheck.Reset();}
    LiveSource.Reset();
    RegistryTiming.Reset();
    if(GEngine&&GEngine->GameViewport&&Overlay.IsValid()) GEngine->GameViewport->RemoveViewportWidgetContent(Overlay.ToSharedRef());
    Overlay.Reset(); Brush.Reset();
    if(SceneWorld) SceneWorld->Stop(); SceneWorld=nullptr;
    Super::EndPlay(Reason);
}
