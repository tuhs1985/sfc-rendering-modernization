#include "BuildBridgeCommandlet.h"
#if WITH_EDITOR
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Engine/Texture2D.h"
#include "Materials/Material.h"
#include "Materials/MaterialExpressionTextureSampleParameter2D.h"
#include "Materials/MaterialExpressionConstant3Vector.h"
#include "Misc/PackageName.h"
#include "UObject/SavePackage.h"
#endif

int32 UBuildBridgeCommandlet::Main(const FString& Params)
{
#if WITH_EDITOR
    UPackage* MaterialPackage = CreatePackage(TEXT("/Game/Bridge/SourceColour"));
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
    FString MaterialFile = FPackageName::LongPackageNameToFilename(TEXT("/Game/Bridge/SourceColour"), FPackageName::GetAssetPackageExtension());
    if (!UPackage::SavePackage(MaterialPackage, Material, *MaterialFile, SaveArgs))
    {
        UE_LOG(LogTemp, Error, TEXT("Material save failed: %s"), *MaterialFile);
        return 1;
    }
    UPackage* LitPackage = CreatePackage(TEXT("/Game/Bridge/FixtureLit"));
    LitPackage->FullyLoad();
    UMaterial* Lit = NewObject<UMaterial>(LitPackage, TEXT("FixtureLit"), RF_Public | RF_Standalone);
    Lit->SetShadingModel(MSM_DefaultLit);
    Lit->TwoSided = true;
    auto* Grey = NewObject<UMaterialExpressionConstant3Vector>(Lit);
    Grey->Constant = FLinearColor(.5f,.5f,.5f);
    Lit->GetExpressionCollection().AddExpression(Grey);
    Lit->GetEditorOnlyData()->BaseColor.Connect(0,Grey);
    Lit->PostEditChange();
    const FString LitFile = FPackageName::LongPackageNameToFilename(TEXT("/Game/Bridge/FixtureLit"),FPackageName::GetAssetPackageExtension());
    if(!UPackage::SavePackage(LitPackage,Lit,*LitFile,SaveArgs)) return 3;
    UPackage* MapPackage = CreatePackage(TEXT("/Game/BridgeMap"));
    MapPackage->FullyLoad();
    UWorld* World = FindObject<UWorld>(MapPackage, TEXT("BridgeMap"));
    if (!World) World = UWorld::CreateWorld(EWorldType::Editor, false, TEXT("BridgeMap"), MapPackage);
    World->SetFlags(RF_Public | RF_Standalone);
    FString MapFile = FPackageName::LongPackageNameToFilename(TEXT("/Game/BridgeMap"), FPackageName::GetMapPackageExtension());
    const bool Saved = UPackage::SavePackage(MapPackage, World, *MapFile, SaveArgs);
    if (World->IsInitialized()) World->DestroyWorld(false);
    return Saved ? 0 : 2;
#else
    return 1;
#endif
}
