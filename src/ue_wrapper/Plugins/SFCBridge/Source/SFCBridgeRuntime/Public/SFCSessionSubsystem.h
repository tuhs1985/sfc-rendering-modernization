#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "SFCSceneData.h"
#include "SFCSessionSubsystem.generated.h"
UCLASS()
class SFCBRIDGERUNTIME_API USFCSessionSubsystem : public UGameInstanceSubsystem {
    GENERATED_BODY()
public:
    bool Load(const FString& Filename,bool Diagnostics,FString& Error);
    virtual void Deinitialize() override;
    const FSFCSceneData& Data() const { return Source; }
    UStaticMesh* Mesh() const { return RetainedMesh; }
    const TArray<TObjectPtr<UMaterialInstanceDynamic>>& Materials() const { return RetainedMaterials; }
    bool ArraysChecked=false;
    double PreparationSeconds=0;
    int32 AssetBuilds=0, WorldActivations=0;
private:
    FSFCSceneData Source;
    UPROPERTY() TObjectPtr<class UStaticMesh> RetainedMesh;
    UPROPERTY() TArray<TObjectPtr<class UTexture2D>> RetainedImages;
    UPROPERTY() TArray<TObjectPtr<class UMaterialInstanceDynamic>> RetainedMaterials;
};
