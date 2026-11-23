#include "SFCWorldSubsystem.h"
#include "SFCSessionSubsystem.h"
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
bool USFCWorldSubsystem::Start(USFCSessionSubsystem* Session,int32 Frame,bool Procedural,bool SharedOwner,FString& Error) {
    if(!Owners.IsEmpty()||!Session||!Session->Mesh()||!Session->Data().Frames.IsValidIndex(Frame)) { Error=TEXT("Invalid world activation"); return false; }
    Source=Session;
    const auto& Data=Source->Data(); const auto& F=Data.Frames[Frame];
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
    const double Start=FPlatformTime::Seconds();
    if(!Source||!Source->Data().Frames.IsValidIndex(Frame)||!Camera) return false;
    const auto& F=Source->Data().Frames[Frame];
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
void USFCWorldSubsystem::Capture() { if(Camera) Camera->CaptureScene(); }
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
    for(int32 i=0;i<Owners.Num();++i) if(!Ready(Owners[i].Get())) {
        const auto* Mesh=Cast<UMeshComponent>(Owners[i]->GetRootComponent());
        const int32 Code=(i<<3)|(Mesh->IsPSOPrecaching()?1:0)|(Mesh->IsRenderStateCreated()?2:0)|(Mesh->SceneProxy?4:0);
        if(Source&&Source->ArraysChecked&&Code!=LastReadinessDiagnostic) {
            LastReadinessDiagnostic=Code;
            UE_LOG(LogTemp,Display,TEXT("SFC_READY_WAIT owner=%d pso=%d state=%d proxy=%d"),i,Mesh->IsPSOPrecaching(),Mesh->IsRenderStateCreated(),Mesh->SceneProxy!=nullptr);
        }
        return false;
    }
    for(auto Actor:FixtureActors) if(!Ready(Actor.Get())) return false;
    return !Owners.IsEmpty();
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
    OwnerSlots.Empty();
    for(auto Actor:FixtureActors) if(IsValid(Actor.Get())) Actor->Destroy(); FixtureActors.Empty(); FixtureLight=nullptr;
    if(IsValid(CameraOwner)) CameraOwner->Destroy(); CameraOwner=nullptr; Camera=nullptr; Output=nullptr; DiagnosticDepth=nullptr; Source=nullptr;
}
void USFCWorldSubsystem::Deinitialize() { Stop(); Super::Deinitialize(); }
