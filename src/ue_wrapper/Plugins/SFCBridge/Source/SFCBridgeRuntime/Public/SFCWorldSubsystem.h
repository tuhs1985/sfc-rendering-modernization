#pragma once
#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "SFCSceneData.h"
#include "SFCWorldSubsystem.generated.h"
UCLASS()
class SFCBRIDGERUNTIME_API USFCWorldSubsystem : public UWorldSubsystem {
    GENERATED_BODY()
public:
    bool Start(class USFCSessionSubsystem* Session,int32 Frame,bool Procedural,bool SharedOwner,FString& Error);
    bool Apply(int32 Frame);
    bool ApplySourceFrame(const FSFCFrame& Frame);
    bool StartRegistry(class USFCSessionSubsystem* Session,const FSFCFrame& Camera,FString& Error);
    bool Synchronize(const struct FSFCSourceSnapshot& Snapshot,FString& Error);
    bool PrepareDiagnosticOwner(const struct FSFCSourceInstance& Instance,const SFCSource::Point& Offset,FString& Error);
    int32 EligibleCount()const;
    int32 ActualMeshCount()const;
    int32 RetiredOwners=0;
    int32 CaptureCalls=0;
    void Capture();
    class UTextureRenderTarget2D* CaptureDiagnosticDepth();
    class UTextureRenderTarget2D* CapturePersistentDepth();
    bool EnsureCaptureExtent(int32 Frame,FString& Error);
    bool EnsureSourceExtent(const FSFCFrame& Frame,FString& Error);
    bool RenderReady() const;
    void Stop();
    bool PrepareShadowFixture();
    void SetFixtureShadows(bool Enabled);
    virtual void Deinitialize() override;
    class UTextureRenderTarget2D* Target() const { return Output; }
    int32 TransformUpdates=0, BuiltVertices=0;
    double TransformSeconds=0;
    bool SharedGeometry=false;
    int32 IdentityCount() const { return OwnerSlots.Num(); }
private:
    bool InitializeCapture(class USFCSessionSubsystem* Session,const FSFCFrame& Camera,FString& Error);
    bool ApplyCamera(const FSFCFrame& Frame);
    struct FInstance {uint32 Requested=0,Applied=0;FString Content;bool Eligible=false;};
    TArray<FInstance> Instances;
    TArray<int32> FreeSlots;
    TMap<FSFCOwnerKey,int32> OwnerSlots;
    mutable int32 LastReadinessDiagnostic=INDEX_NONE;
    UPROPERTY() TObjectPtr<class USFCSessionSubsystem> Source;
    UPROPERTY() TArray<TObjectPtr<AActor>> Owners;
    UPROPERTY() TObjectPtr<AActor> CameraOwner;
    UPROPERTY() TObjectPtr<class USceneCaptureComponent2D> Camera;
    UPROPERTY() TObjectPtr<class UTextureRenderTarget2D> Output;
    UPROPERTY() TObjectPtr<class UTextureRenderTarget2D> DiagnosticDepth;
    UPROPERTY() TArray<TObjectPtr<AActor>> FixtureActors;
    UPROPERTY() TObjectPtr<class UDirectionalLightComponent> FixtureLight;
};
