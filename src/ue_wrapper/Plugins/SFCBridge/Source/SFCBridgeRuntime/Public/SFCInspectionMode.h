#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "HAL/PlatformProcess.h"
#include "SFCInspectionMode.generated.h"
UCLASS()
class SFCBRIDGERUNTIME_API ASFCInspectionMode : public AGameModeBase {
    GENERATED_BODY()
public:
    ASFCInspectionMode();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    void Fail(const FString& Why);
    void ActivateScene(const FString& Input);
    bool TickSource();
    bool TickRegistry();
    UPROPERTY() TObjectPtr<class USFCWorldSubsystem> SceneWorld;
    TSharedPtr<class SWidget> Overlay;
    TSharedPtr<struct FSlateBrush> Brush;
    TSharedPtr<class FSFCStreamCheck> StreamCheck;
    TSharedPtr<class FSFCGameOutput> GameOutput;
    TSharedPtr<class FSFCLiveSource> LiveSource;
    FString SourceInput,SourceMap;
    FProcHandle SourceParent;
    uint32 SourceOwner=0,SourceRevision=0;
    int32 SourceReplayUpdates=0;
    FString DefinitionDirectory;
    TSharedPtr<class FSFCRegistryCheck> RegistryCheck;
    uint32 RegistryDiagnosticCounter=MAX_uint32;
    TSharedPtr<class FSFCSceneTiming> RegistryTiming;
    bool RegistryDirty=true,RegistryReadyCapture=false;
    FString OutputDirectory;
    int32 Frame=0, Ticks=0;
    bool Diagnostics=false, Finished=false;
    bool ShadowCheck=false, ShadowSecondPass=false;
    TArray<FColor> ShadowPixels;
    double Started=0, ReadySeconds=0;
};
