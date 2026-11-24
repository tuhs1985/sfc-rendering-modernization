#include "SFCWorldSubsystem.h"
#include "SFCSessionSubsystem.h"
#include "SFCLiveSource.h"
#include "Engine/World.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "ProceduralMeshComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Materials/Material.h"
#include "RenderUtils.h"
#include "RenderingThread.h"
#include "Dom/JsonObject.h"
namespace {
FMatrix Matrix(const SFCSource::Matrix& M) {
    FMatrix R; for(int i=0;i<4;++i) for(int j=0;j<4;++j) R.M[i][j]=M[i][j]; return R;
}
}
bool USFCWorldSubsystem::InitializeCapture(USFCSessionSubsystem* Session,const FSFCFrame& F,FString& Error){
    if(Camera||!Session){Error=TEXT("Invalid capture activation");return false;}Source=Session;
    Output=NewObject<UTextureRenderTarget2D>(this);
    Output->ClearColor=FLinearColor::Black; Output->TargetGamma=1;
    Output->InitCustomFormat(F.Viewport[2],F.Viewport[3],PF_B8G8R8A8,true); Output->UpdateResourceImmediate(true);
    CameraOwner=GetWorld()->SpawnActor<AActor>();
    Camera=NewObject<USceneCaptureComponent2D>(CameraOwner); CameraOwner->SetRootComponent(Camera); Camera->RegisterComponent();
    Camera->TextureTarget=Output; Camera->CaptureSource=SCS_SceneColorHDR;
    Camera->bCaptureEveryFrame=false; Camera->bCaptureOnMovement=false;
    Camera->bAlwaysPersistRenderingState=true;
    Camera->PrimitiveRenderMode=ESceneCapturePrimitiveRenderMode::PRM_UseShowOnlyList;
    Camera->ShowFlags.SetAntiAliasing(false); Camera->ShowFlags.SetAtmosphere(false);
    Camera->ShowFlags.SetFog(false); Camera->ShowFlags.SetPostProcessing(false);
    Camera->MaxViewDistanceOverride=10000000; Camera->bUseCustomProjectionMatrix=true;
    if(!ApplyCamera(F)){Error=TEXT("Source camera cannot be represented");Stop();return false;}return true;
}
bool USFCWorldSubsystem::StartRegistry(USFCSessionSubsystem* Session,const FSFCFrame& Frame,FString& Error){
    if(!InitializeCapture(Session,Frame,Error))return false;++Session->WorldActivations;return true;
}
bool USFCWorldSubsystem::ApplyCamera(const FSFCFrame& Frame){
    if(!Camera||!CameraOwner||!SFCSource::ValidAffine(Frame.View))return false;
    const FMatrix M=Matrix(SFCSource::ToUERow(SFCSource::InverseAffine(Frame.View)));const FTransform Pose(M);
    if(!Pose.ToMatrixWithScale().Equals(M,1e-4))return false;
    CameraOwner->SetActorTransform(Pose,false,nullptr,ETeleportType::TeleportPhysics);
    Camera->CustomProjectionMatrix=Matrix(SFCSource::ProjectionToUERow(Frame.Projection));return true;
}
bool USFCWorldSubsystem::Start(USFCSessionSubsystem* Session,int32 Frame,bool Procedural,bool SharedOwner,FString& Error) {
    if(!Owners.IsEmpty()||!Session||!Session->Mesh()||!Session->Data().Frames.IsValidIndex(Frame)) { Error=TEXT("Invalid world activation"); return false; }
    const auto& Data=Session->Data();const auto& F=Data.Frames[Frame];
    if(!InitializeCapture(Session,F,Error))return false;
    for(int n=0;n<(SharedOwner?2:1);++n) {
        FSFCOwnerKey Key; Key.Session=Data.Session; Key.Epoch=Data.OwnerEpoch+n;
        if(Data.FragmentRelationship.IsValid()) {
            Key.FragmentIndex=Data.FragmentRelationship->GetIntegerField(TEXT("index"));
            Key.VisualEpoch=Data.FragmentRelationship->GetIntegerField(TEXT("visual_epoch"));
        }
        // n==1 is an explicitly synthetic diagnostic owner, never a captured ship claim.
        if(OwnerSlots.Contains(Key)) { Error=TEXT("Duplicate owner admission"); Stop(); return false; }
        OwnerSlots.Add(Key,Owners.Num());
        AActor* Actor=GetWorld()->SpawnActor<AActor>(); Owners.Add(Actor);
        UMeshComponent* Component=nullptr;
        if(!Procedural) {
            auto* Mesh=NewObject<UStaticMeshComponent>(Actor); Component=Mesh;
            Mesh->SetStaticMesh(Source->Mesh()); BuiltVertices=Data.Corners.Num();
        } else {
            auto* Mesh=NewObject<UProceduralMeshComponent>(Actor); Component=Mesh;
            for(int g=0;g<Data.Groups.Num();++g) {
                const auto& G=Data.Groups[g]; TMap<int32,int32> Remap;
                TArray<FVector> Positions,Normals; TArray<FVector2D> UV; TArray<int32> Indices;
                for(int i=G.First;i<G.First+G.Count;++i) {
                    const int32 SourceCorner=Data.Indices[i]; int32* Found=Remap.Find(SourceCorner);
                    int32 V;
                    if(Found) V=*Found;
                    else {
                        V=Positions.Num(); Remap.Add(SourceCorner,V);
                        const auto& C=Data.Corners[SourceCorner]; const auto& P=Data.Positions[C.Position];
                        Positions.Add(FVector(-P.Z,P.X,P.Y)); Normals.Add(FVector(-C.Normal.Z,C.Normal.X,C.Normal.Y)); UV.Add(FVector2D(C.UV));
                    }
                    Indices.Add(V);
                }
                BuiltVertices+=Positions.Num();
                Mesh->CreateMeshSection_LinearColor(g,Positions,Indices,Normals,UV,TArray<FLinearColor>(),TArray<FProcMeshTangent>(),false);
            }
        }
        Actor->SetRootComponent(Component); Component->SetMobility(EComponentMobility::Movable);
        Component->SetCollisionEnabled(ECollisionEnabled::NoCollision); Component->SetCastShadow(true);
        for(int g=0;g<Data.Groups.Num();++g) Component->SetMaterial(g,Source->Materials()[g]);
        Component->RegisterComponent(); Camera->ShowOnlyComponent(Component);
    }
    SharedGeometry=!Procedural&&Owners.Num()==2&&
        Cast<UStaticMeshComponent>(Owners[0]->GetRootComponent())->GetStaticMesh()==Cast<UStaticMeshComponent>(Owners[1]->GetRootComponent())->GetStaticMesh();
    ++Source->WorldActivations;
    return Apply(Frame);
}
bool USFCWorldSubsystem::Apply(int32 Frame) {
    if(!Source||!Source->Data().Frames.IsValidIndex(Frame)||!Camera) return false;
    return ApplySourceFrame(Source->Data().Frames[Frame]);
}
bool USFCWorldSubsystem::ApplySourceFrame(const FSFCFrame& F) {
    const double Start=FPlatformTime::Seconds();
    if(!Source||!Camera)return false;
    // Matrices are transposed only at the UE boundary; no camera-baked vertices.
    const FMatrix Model=Matrix(SFCSource::ToUERow(F.Model));
    const FMatrix CameraWorld=Matrix(SFCSource::ToUERow(SFCSource::InverseAffine(F.View)));
    const FTransform Pose(Model), CameraPose(CameraWorld);
    if(!Pose.ToMatrixWithScale().Equals(Model,1e-4)||!CameraPose.ToMatrixWithScale().Equals(CameraWorld,1e-4)) return false;
    for(int n=0;n<Owners.Num();++n) {
        FTransform P=Pose;
        if(n) P.AddToTranslation(FVector(0,40,0)); // Explicit diagnostic owner, not another captured ship.
        Owners[n]->SetActorTransform(P,false,nullptr,ETeleportType::TeleportPhysics);
    }
    CameraOwner->SetActorTransform(CameraPose,false,nullptr,ETeleportType::TeleportPhysics);
    Camera->CustomProjectionMatrix=Matrix(SFCSource::ProjectionToUERow(F.Projection));
    ++TransformUpdates; TransformSeconds+=FPlatformTime::Seconds()-Start; return true;
}
void USFCWorldSubsystem::Capture() { if(Camera){++CaptureCalls;Camera->CaptureScene();} }
bool USFCWorldSubsystem::EnsureCaptureExtent(int32 Frame,FString& Error){
    if(!Source||!Source->Data().Frames.IsValidIndex(Frame)||!Output){Error=TEXT("Missing capture extent source");return false;}
    return EnsureSourceExtent(Source->Data().Frames[Frame],Error);
}
bool USFCWorldSubsystem::EnsureSourceExtent(const FSFCFrame& Frame,FString& Error){
    if(!Output){Error=TEXT("Missing capture target");return false;}
    const auto& View=Frame.Viewport;
    if(View[2]!=FMath::FloorToDouble(View[2])||View[3]!=FMath::FloorToDouble(View[3])){Error=TEXT("Fractional capture extent unsupported");return false;}
    const int32 W=int32(View[2]),H=int32(View[3]);
    bool Changed=false;
    if(Output->SizeX!=W||Output->SizeY!=H){Output->ResizeTarget(W,H);Changed=true;}
    if(DiagnosticDepth&&(DiagnosticDepth->SizeX!=W||DiagnosticDepth->SizeY!=H)){DiagnosticDepth->ResizeTarget(W,H);Changed=true;}
    if(Changed)return false;
    for(auto* Target:{Output.Get(),DiagnosticDepth.Get()})if(Target){
        auto* Resource=Target->GameThread_GetRenderTargetResource();
        if(!Resource)return false;
        const auto Image=Resource->GetRenderTargetTexture();
        if(!Image.IsValid()||Image->GetSizeXYZ().X!=W||Image->GetSizeXYZ().Y!=H)return false;
    }
    return true;
}
UTextureRenderTarget2D* USFCWorldSubsystem::CapturePersistentDepth() {
    if(!Camera||!Output)return nullptr;
    if(!DiagnosticDepth){
        DiagnosticDepth=NewObject<UTextureRenderTarget2D>(this);
        DiagnosticDepth->ClearColor=FLinearColor::Black;
        DiagnosticDepth->InitCustomFormat(Output->SizeX,Output->SizeY,PF_R32_FLOAT,true);
        DiagnosticDepth->UpdateResourceImmediate(true);
        return nullptr;
    }
    if(!DiagnosticDepth->GameThread_GetRenderTargetResource()->GetRenderTargetTexture().IsValid())return nullptr;
    Camera->TextureTarget=DiagnosticDepth;Camera->CaptureSource=SCS_SceneDepth;
    Camera->CaptureScene();Camera->TextureTarget=Output;Camera->CaptureSource=SCS_SceneColorHDR;
    return DiagnosticDepth;
}
UTextureRenderTarget2D* USFCWorldSubsystem::CaptureDiagnosticDepth() {
    if(!Camera||!Output) return nullptr;
    DiagnosticDepth=NewObject<UTextureRenderTarget2D>(this);
    DiagnosticDepth->ClearColor=FLinearColor::Black;
    DiagnosticDepth->InitCustomFormat(Output->SizeX,Output->SizeY,PF_R32_FLOAT,true);
    DiagnosticDepth->UpdateResourceImmediate(true);
    FlushRenderingCommands();
    Camera->TextureTarget=DiagnosticDepth;
    Camera->CaptureSource=SCS_SceneDepth;
    Camera->CaptureScene();
    Camera->TextureTarget=Output;
    Camera->CaptureSource=SCS_SceneColorHDR;
    return DiagnosticDepth;
}
bool USFCWorldSubsystem::RenderReady() const {
    auto Ready=[](AActor* Actor) {
        const auto* Mesh=Actor?Cast<UMeshComponent>(Actor->GetRootComponent()):nullptr;
        return !Mesh||(!Mesh->IsPSOPrecaching()&&Mesh->IsRenderStateCreated()&&Mesh->SceneProxy!=nullptr);
    };
    for(int32 i=0;i<Owners.Num();++i) {
        // Pending revisions are intentionally hidden. Their absent scene proxy
        // must not gate unrelated eligible owners or the completed capture.
        if(Instances.IsValidIndex(i)&&!Instances[i].Eligible)continue;
        if(!Ready(Owners[i].Get())) {
        const auto* Mesh=Cast<UMeshComponent>(Owners[i]->GetRootComponent());
        const int32 Code=(i<<3)|(Mesh->IsPSOPrecaching()?1:0)|(Mesh->IsRenderStateCreated()?2:0)|(Mesh->SceneProxy?4:0);
        if(Source&&Source->ArraysChecked&&Code!=LastReadinessDiagnostic) {
            LastReadinessDiagnostic=Code;
            UE_LOG(LogTemp,Display,TEXT("SFC_READY_WAIT owner=%d pso=%d state=%d proxy=%d"),i,Mesh->IsPSOPrecaching(),Mesh->IsRenderStateCreated(),Mesh->SceneProxy!=nullptr);
        }
        return false;
        }
    }
    for(auto Actor:FixtureActors) if(!Ready(Actor.Get())) return false;
    return Instances.IsEmpty()?!Owners.IsEmpty():EligibleCount()>0;
}
bool USFCWorldSubsystem::PrepareShadowFixture() {
    if(!Camera||!IsRayTracingEnabled()||Owners.Num()!=1) return false;
    // Explicit synthetic capability scene, never used as an SFC camera/pose sample.
    Owners[0]->SetActorTransform(FTransform(FRotator::ZeroRotator,FVector(0,0,4)));
    CameraOwner->SetActorLocationAndRotation(FVector(0,0,20),FRotator(-90,0,0));
    Camera->bUseCustomProjectionMatrix=false; Camera->FOVAngle=70;
    Camera->bUseRayTracingIfEnabled=true;
    Output->ResizeTarget(512,512);
    AActor* Floor=GetWorld()->SpawnActor<AActor>(); FixtureActors.Add(Floor);
    auto* Receiver=NewObject<UProceduralMeshComponent>(Floor); Floor->SetRootComponent(Receiver);
    TArray<FVector> V={FVector(-15,-15,0),FVector(15,-15,0),FVector(15,15,0),FVector(-15,15,0)};
    TArray<int32> I={0,1,2,0,2,3,2,1,0,3,2,0};
    TArray<FVector> N; N.Init(FVector(0,0,1),4);
    Receiver->CreateMeshSection_LinearColor(0,V,I,N,TArray<FVector2D>(),TArray<FLinearColor>(),TArray<FProcMeshTangent>(),false);
    auto* Lit=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Bridge/FixtureLit.FixtureLit"));
    if(!Lit) return false;
    Receiver->SetMaterial(0,Lit);
    Receiver->SetCastShadow(false); Receiver->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Receiver->RegisterComponent(); Camera->ShowOnlyComponent(Receiver);
    AActor* Light=GetWorld()->SpawnActor<AActor>(); FixtureActors.Add(Light);
    FixtureLight=NewObject<UDirectionalLightComponent>(Light); Light->SetRootComponent(FixtureLight);
    FixtureLight->SetMobility(EComponentMobility::Movable); FixtureLight->SetIntensity(1);
    FixtureLight->SetCastShadows(true); FixtureLight->SetCastRaytracedShadows(ECastRayTracedShadow::Enabled);
    FixtureLight->RegisterComponent(); Light->SetActorRotation(FRotator(-45,0,0));
    return true;
}
void USFCWorldSubsystem::SetFixtureShadows(bool Enabled) { if(FixtureLight) FixtureLight->SetCastShadows(Enabled); }
void USFCWorldSubsystem::Stop() {
    if(Camera) { Camera->TextureTarget=nullptr; Camera->ClearShowOnlyComponents(); }
    for(auto Owner:Owners) if(IsValid(Owner.Get())) Owner->Destroy(); Owners.Empty();
    OwnerSlots.Empty();Instances.Empty();FreeSlots.Empty();
    for(auto Actor:FixtureActors) if(IsValid(Actor.Get())) Actor->Destroy(); FixtureActors.Empty(); FixtureLight=nullptr;
    if(IsValid(CameraOwner)) CameraOwner->Destroy(); CameraOwner=nullptr; Camera=nullptr; Output=nullptr; DiagnosticDepth=nullptr; Source=nullptr;
}
void USFCWorldSubsystem::Deinitialize() { Stop(); Super::Deinitialize(); }

bool USFCWorldSubsystem::Synchronize(const FSFCSourceSnapshot& Snapshot,FString& Error){
    if(!Source||!Camera){Error=TEXT("Registry world not active");return false;}
    for(uint32 Epoch:Snapshot.Retirements){
        Source->Retire(Epoch);
        for(auto It=OwnerSlots.CreateIterator();It;++It)if(It.Key().Epoch==Epoch){
            const int32 Slot=It.Value();auto* Actor=Owners[Slot].Get();
            if(IsValid(Actor)){
                Camera->RemoveShowOnlyComponent(Cast<UPrimitiveComponent>(Actor->GetRootComponent()));Actor->Destroy();
            }
            Owners[Slot]=nullptr;Instances[Slot]=FInstance();FreeSlots.Add(Slot);It.RemoveCurrent();++RetiredOwners;
        }
    }
    if(!ApplyCamera(Snapshot.Camera)){Error=TEXT("Invalid coherent registry camera");return false;}
    for(const auto& Input:Snapshot.Instances){
        if(Source->IsRetired(Input.Owner))continue;
        FSFCOwnerKey Key;Key.Session=Source->SessionName();Key.Epoch=Input.Owner;
        int32* Existing=OwnerSlots.Find(Key);int32 Slot=INDEX_NONE;
        if(Existing)Slot=*Existing;
        else{
            if(!FreeSlots.IsEmpty())Slot=FreeSlots.Pop(EAllowShrinking::No);
            else{Slot=Owners.Add(nullptr);Instances.AddDefaulted();}
            OwnerSlots.Add(Key,Slot);
        }
        auto& State=Instances[Slot];State.Requested=Input.Revision;
        if(!Input.PoseQualified){State.Eligible=false;if(Owners[Slot])Owners[Slot]->SetActorHiddenInGame(true);continue;}
        const auto* Binding=Source->Binding(Input.Owner,Input.Revision,Input.Model,Input.Source);
        const auto* Asset=Binding?Source->Asset(Binding->Content):nullptr;
        const FMatrix Model=Matrix(SFCSource::ToUERow(Input.Pose));const FTransform Pose(Model);
        if(!Asset||!Pose.ToMatrixWithScale().Equals(Model,1e-4)){
            State.Eligible=false;if(Owners[Slot])Owners[Slot]->SetActorHiddenInGame(true);continue;
        }
        auto* Actor=Owners[Slot].Get();UStaticMeshComponent* Component=nullptr;
        if(!Actor){
            Actor=GetWorld()->SpawnActor<AActor>();Owners[Slot]=Actor;
            Component=NewObject<UStaticMeshComponent>(Actor);Actor->SetRootComponent(Component);
            Component->SetMobility(EComponentMobility::Movable);Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);Component->SetCastShadow(true);
            Component->SetStaticMesh(Asset->Mesh);for(int32 G=0;G<Asset->Materials.Num();++G)Component->SetMaterial(G,Asset->Materials[G]);
            Component->RegisterComponent();Camera->ShowOnlyComponent(Component);
        }else{
            Component=Cast<UStaticMeshComponent>(Actor->GetRootComponent());
            if(Component->GetStaticMesh()!=Asset->Mesh)Component->SetStaticMesh(Asset->Mesh);
            if(State.Content!=Binding->Content)for(int32 G=0;G<Asset->Materials.Num();++G)Component->SetMaterial(G,Asset->Materials[G]);
        }
        Actor->SetActorTransform(Pose,false,nullptr,ETeleportType::TeleportPhysics);Actor->SetActorHiddenInGame(false);
        State.Applied=Input.Revision;State.Content=Binding->Content;State.Eligible=true;
    }
    ++TransformUpdates;return true;
}
int32 USFCWorldSubsystem::EligibleCount()const{int32 Count=0;for(const auto& Pair:OwnerSlots)if(Instances.IsValidIndex(Pair.Value)&&Instances[Pair.Value].Eligible)++Count;return Count;}
int32 USFCWorldSubsystem::ActualMeshCount()const{
    TSet<const UStaticMesh*> Meshes;
    for(const auto& Pair:OwnerSlots){const auto* Actor=Owners[Pair.Value].Get();const auto* Component=Actor?Cast<UStaticMeshComponent>(Actor->GetRootComponent()):nullptr;if(Component)Meshes.Add(Component->GetStaticMesh());}
    return Meshes.Num();
}

bool USFCWorldSubsystem::PrepareDiagnosticOwner(const FSFCSourceInstance& Input,const SFCSource::Point& Offset,FString& Error){
    if(!Camera||!Source||!Input.PoseQualified)return false;
    const FSFCOwnerKey Key{Source->SessionName(),int64(Input.Owner)};
    const int32* Slot=OwnerSlots.Find(Key);
    if(!Slot||!Instances.IsValidIndex(*Slot)||!Instances[*Slot].Eligible||Instances[*Slot].Applied!=Input.Revision)return false;
    auto* Actor=Owners[*Slot].Get();auto* Component=Actor?Cast<UStaticMeshComponent>(Actor->GetRootComponent()):nullptr;
    if(!Component||!Component->IsRenderStateCreated()||!Component->SceneProxy||Component->IsPSOPrecaching())return false;
    SFCSource::Matrix Shifted;
    if(!SFCSource::DiagnosticWorldOffset(Input.Pose,Offset,Shifted)){Error=TEXT("Invalid diagnostic world offset");return false;}
    const FMatrix Model=Matrix(SFCSource::ToUERow(Shifted));const FTransform Pose(Model);
    if(!Pose.ToMatrixWithScale().Equals(Model,1e-4)){Error=TEXT("Diagnostic transform is not representable");return false;}
    Camera->ClearShowOnlyComponents();Camera->ShowOnlyComponent(Component);
    Actor->SetActorTransform(Pose,false,nullptr,ETeleportType::TeleportPhysics);
    return true;
}
