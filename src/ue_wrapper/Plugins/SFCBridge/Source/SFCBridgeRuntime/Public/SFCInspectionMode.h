#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
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
    UPROPERTY() TObjectPtr<class USFCWorldSubsystem> SceneWorld;
    TSharedPtr<class SWidget> Overlay;
    TSharedPtr<struct FSlateBrush> Brush;
    FString OutputDirectory;
    int32 Frame=0, Ticks=0;
    bool Diagnostics=false, Finished=false;
    bool ShadowCheck=false, ShadowSecondPass=false;
    TArray<FColor> ShadowPixels;
    double Started=0, ReadySeconds=0;
};
