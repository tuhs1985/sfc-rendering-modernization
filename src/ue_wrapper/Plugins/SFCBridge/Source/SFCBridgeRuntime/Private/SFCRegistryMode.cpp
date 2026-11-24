#include "SFCInspectionMode.h"
#include "SFCGameOutput.h"
#include "SFCLiveSource.h"
#include "SFCRegistryCheck.h"
#include "SFCSceneTiming.h"
#include "SFCInspectionView.h"
#include "SFCSessionSubsystem.h"
#include "SFCWorldSubsystem.h"
#include "Engine/GameInstance.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "Kismet/GameplayStatics.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/Layout/SConstraintCanvas.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Text/STextBlock.h"
#include "Styling/SlateBrush.h"

bool ASFCInspectionMode::TickRegistry(){
    const uint64 TickStarted=FPlatformTime::Cycles64();
    FString Error;bool Changed=false,Stopped=false;
    if(RegistryTiming){
        RegistryTiming->Poll();
        if(RegistryTiming->Finished()){
            if(!RegistryTiming->Write(GetGameInstance()->GetSubsystem<USFCSessionSubsystem>(),SceneWorld,OutputDirectory,Error)){Fail(Error);return false;}
            FPlatformMisc::RequestExit(false);return true;
        }
    }
    if(!LiveSource->PollScene(Changed,Stopped,Error)){Fail(Error);return false;}
    if(Stopped){FPlatformMisc::RequestExit(false);return true;}
    auto* Session=GetGameInstance()->GetSubsystem<USFCSessionSubsystem>();
    const auto& Snapshot=LiveSource->Snapshot();
    for(uint32 Epoch:Snapshot.Retirements)Session->Retire(Epoch);
    bool Admitted=false;
    for(const auto& Descriptor:LiveSource->NewAssets()){
        if(Session->IsRetired(Descriptor.owner)){++Session->RegistryLateDiscards;continue;}
        FString Content;for(uint8 Byte:Descriptor.content)Content+=FString::Printf(TEXT("%02x"),Byte);
        const FString Path=DefinitionDirectory/FString::Printf(TEXT("%s-%u-%u.json"),*Content,Descriptor.owner,Descriptor.revision);
        FSFCSceneData Candidate;
        if(!LoadSFCScene(Path,Candidate,Error,Session->Asset(Content)!=nullptr)||Candidate.Session!=SourceMap||Candidate.SourcePid!=LiveSource->Pid()||
           Candidate.OwnerEpoch!=Descriptor.owner||Candidate.Revision!=Descriptor.revision||Candidate.Content!=Content||
           Candidate.ModelIdentity!=Descriptor.model||Candidate.SourceIdentity!=Descriptor.source){
            ++Session->RegistryAssetRejected;
            if(Diagnostics)FFileHelper::SaveStringToFile(Error.IsEmpty()?TEXT("Source definition/catalog identity mismatch"):Error,*(OutputDirectory/TEXT("registry-admission-error.txt")));
            Error.Empty();continue;
        }
        if(!Session->Admit(MoveTemp(Candidate),Diagnostics,Error)){
            ++Session->RegistryAssetRejected;
            if(Diagnostics)FFileHelper::SaveStringToFile(Error,*(OutputDirectory/TEXT("registry-admission-error.txt")));
            Error.Empty();continue;
        }
        Admitted=true;
    }
    if(Diagnostics&&RegistryDiagnosticCounter!=LiveSource->CatalogPublications()){
        RegistryDiagnosticCounter=LiveSource->CatalogPublications();
        const FString State=FString::Printf(TEXT("{\"catalog\":%u,\"received\":%d,\"admissions\":%d,\"rejected\":%d,\"geometry_builds\":%d,\"materials\":%d}"),
            RegistryDiagnosticCounter,LiveSource->NewAssets().Num(),Session->AssetAdmissions,Session->RegistryAssetRejected,Session->AssetBuilds,Session->MaterialBuilds);
        FFileHelper::SaveStringToFile(State,*(OutputDirectory/TEXT("registry-admission.json")));
    }
    if(!SceneWorld&&Session->Mesh()&&Snapshot.Sequence){
        SceneWorld=GetWorld()->GetSubsystem<USFCWorldSubsystem>();
        if(!SceneWorld->StartRegistry(Session,Snapshot.Camera,Error)){Fail(Error);return false;}
        if(GEngine&&GEngine->GameViewport&&Overlay.IsValid())GEngine->GameViewport->RemoveViewportWidgetContent(Overlay.ToSharedRef());
        const auto& View=Snapshot.Camera.Viewport;
        Brush=MakeShared<FSlateBrush>();Brush->SetResourceObject(SceneWorld->Target());Brush->ImageSize=FVector2D(View[2],View[3]);
        Overlay=SFCInspectionView(Brush.Get());
        if(GEngine&&GEngine->GameViewport)GEngine->GameViewport->AddViewportWidgetContent(Overlay.ToSharedRef());
        Changed=true;
    }
    if(!SceneWorld||!Snapshot.Sequence)return true;
    if((Changed||Admitted)&&!SceneWorld->Synchronize(Snapshot,Error)){Fail(Error);return false;}
    RegistryDirty|=Changed||Admitted;
    if(!SceneWorld->EnsureSourceExtent(Snapshot.Camera,Error)){
        if(!Error.IsEmpty()){Fail(Error);return false;}return true;
    }
    if(GameOutput){
        bool Capture=false;
        if(!GameOutput->BeforeCapture(SceneWorld,Session,*LiveSource,Capture,Error)){Fail(Error);return false;}
        if(Capture){
            SceneWorld->Capture();
            if(!GameOutput->AfterCapture(SceneWorld,Error)){Fail(Error);return false;}
        }
        return true;
    }
    if(RegistryDirty||!RegistryReadyCapture){
        const int32 TimingSlot=RegistryTiming&&SceneWorld->RenderReady()?RegistryTiming->BeforeCapture(Snapshot.Sequence,Snapshot.Offered,
            FPlatformTime::ToMilliseconds64(FPlatformTime::Cycles64()-TickStarted),SceneWorld->EligibleCount()):INDEX_NONE;
        const uint64 CaptureStarted=FPlatformTime::Cycles64();SceneWorld->Capture();
        if(RegistryTiming)RegistryTiming->AfterCapture(TimingSlot,FPlatformTime::ToMilliseconds64(FPlatformTime::Cycles64()-CaptureStarted));
        RegistryReadyCapture=SceneWorld->RenderReady();RegistryDirty=false;
    }
    if(!SceneWorld->RenderReady())return true;
    if(RegistryCheck){
        bool Done=false,Restart=false;
        if(!RegistryCheck->Tick(Session,SceneWorld,Snapshot,OutputDirectory,Done,Restart,Error)){Fail(Error);return false;}
        if(Restart){UGameplayStatics::OpenLevel(this,FName(TEXT("/Game/BridgeMap")));return true;}
        if(Done)FPlatformMisc::RequestExit(false);
    }
    return true;
}
