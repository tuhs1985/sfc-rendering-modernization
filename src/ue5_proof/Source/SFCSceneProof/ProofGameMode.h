#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "ProofGameMode.generated.h"

UCLASS()
class AProofGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AProofGameMode();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
private:
    UPROPERTY() TObjectPtr<class UProceduralMeshComponent> Ship;
    UPROPERTY() TObjectPtr<class USceneCaptureComponent2D> Camera;
    UPROPERTY() TObjectPtr<class UTextureRenderTarget2D> Output;
    UPROPERTY() TArray<TObjectPtr<class UTexture2D>> Images;
    TSharedPtr<class FJsonObject> Scene;
    TSharedPtr<struct FSlateBrush> ImageBrush;
    FString OutputDirectory;
    double Started = 0;
    int32 Ticks = 0;
    int32 IndexCount = 0;
    int32 GroupCount = 0;
    int32 CornerCount = 0;
    int32 FrameIndex = 0;
    bool Finished = false;
};
