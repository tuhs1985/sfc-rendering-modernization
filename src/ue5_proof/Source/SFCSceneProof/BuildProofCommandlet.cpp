#include "BuildProofCommandlet.h"
#if WITH_EDITOR
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Engine/Texture2D.h"
#include "Materials/Material.h"
#include "Materials/MaterialExpressionTextureSampleParameter2D.h"
#include "Misc/PackageName.h"
#include "UObject/SavePackage.h"
#endif

int32 UBuildProofCommandlet::Main(const FString& Params)
{
#if WITH_EDITOR
    UPackage* MaterialPackage = CreatePackage(TEXT("/Game/Proof/SourceColour"));
    MaterialPackage->FullyLoad();
    UMaterial* Material = NewObject<UMaterial>(MaterialPackage, TEXT("SourceColour"), RF_Public | RF_Standalone);
    Material->SetShadingModel(MSM_Unlit);
    Material->TwoSided = true;
    UMaterialExpressionTextureSampleParameter2D* Sample = NewObject<UMaterialExpressionTextureSampleParameter2D>(Material);
    Sample->ParameterName = TEXT("SourceTexture");
    Sample->SamplerType = SAMPLERTYPE_LinearColor;
    UTexture2D* White = NewObject<UTexture2D>(MaterialPackage, TEXT("LinearWhite"), RF_Public | RF_Standalone);
    const uint8 Pixel[] = {255, 255, 255, 255};
    White->Source.Init(1, 1, 1, 1, TSF_BGRA8, Pixel);
    White->SRGB = false;
    White->CompressionSettings = TC_VectorDisplacementmap;
    White->PostEditChange();
    Sample->Texture = White;
    Material->GetExpressionCollection().AddExpression(Sample);
    Material->GetEditorOnlyData()->EmissiveColor.Connect(0, Sample);
    Material->PostEditChange();
    FSavePackageArgs SaveArgs;
    SaveArgs.TopLevelFlags = RF_Public | RF_Standalone;
    FString MaterialFile = FPackageName::LongPackageNameToFilename(TEXT("/Game/Proof/SourceColour"), FPackageName::GetAssetPackageExtension());
    if (!UPackage::SavePackage(MaterialPackage, Material, *MaterialFile, SaveArgs))
    {
        UE_LOG(LogTemp, Error, TEXT("Material save failed: %s"), *MaterialFile);
        return 1;
    }
    UPackage* MapPackage = CreatePackage(TEXT("/Game/ProofMap"));
    MapPackage->FullyLoad();
    UWorld* World = FindObject<UWorld>(MapPackage, TEXT("ProofMap"));
    if (!World) World = UWorld::CreateWorld(EWorldType::Editor, false, TEXT("ProofMap"), MapPackage);
    World->SetFlags(RF_Public | RF_Standalone);
    FString MapFile = FPackageName::LongPackageNameToFilename(TEXT("/Game/ProofMap"), FPackageName::GetMapPackageExtension());
    const bool Saved = UPackage::SavePackage(MapPackage, World, *MapFile, SaveArgs);
    if (World->IsInitialized()) World->DestroyWorld(false);
    return Saved ? 0 : 2;
#else
    return 1;
#endif
}
