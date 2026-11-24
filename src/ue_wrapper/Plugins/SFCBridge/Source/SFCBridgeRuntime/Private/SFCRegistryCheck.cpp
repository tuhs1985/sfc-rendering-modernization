#include "SFCRegistryCheck.h"
#include "SFCSessionSubsystem.h"
#include "SFCWorldSubsystem.h"
#include "SFCLiveSource.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
bool FSFCRegistryCheck::Start(const FString& Filename,FString& Error){
    FString Text;TSharedPtr<FJsonObject> Root;const TArray<TSharedPtr<FJsonValue>>* Values=nullptr;FString Schema;
    if(IFileManager::Get().FileSize(*Filename)>32768||!FFileHelper::LoadFileToString(Text,*Filename)||
       !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text),Root)||!Root.IsValid()||
       !Root->TryGetStringField(TEXT("schema"),Schema)||Schema!=TEXT("sfc.ue.registry-check.v1")||
       !Root->TryGetArrayField(TEXT("steps"),Values)||Values->IsEmpty()||Values->Num()>32){Error=TEXT("Invalid standalone registry fixture");return false;}
    Steps=*Values;return true;
}
bool FSFCRegistryCheck::Tick(USFCSessionSubsystem* Session,USFCWorldSubsystem* World,const FSFCSourceSnapshot& Snapshot,
    const FString& Output,bool& Finished,bool& Restart,FString& Error){
    Finished=Restart=false;
    const int32 Index=Session->RegistryCheckStep;
    if(!Steps.IsValidIndex(Index)){Finished=true;return true;}
    const auto Step=Steps[Index]->AsObject();
    if(!Step.IsValid()){Error=TEXT("Invalid registry step");return false;}
    const FString Wait=FString::Printf(TEXT("{\"step\":%d,\"source_stage\":%llu,\"owners\":%d,\"eligible\":%d,\"geometry_builds\":%d,\"materials\":%d,\"render_ready\":%s}"),
        Index,Snapshot.Sequence/1000000,World->IdentityCount(),World->EligibleCount(),Session->AssetBuilds,Session->MaterialBuilds,World->RenderReady()?TEXT("true"):TEXT("false"));
    if(Wait!=LastWait){LastWait=Wait;FFileHelper::SaveStringToFile(Wait,*(Output/TEXT("registry-wait.json")));}
    if(Snapshot.Sequence<static_cast<uint64>(Step->GetNumberField(TEXT("sequence")))||
       World->IdentityCount()!=Step->GetIntegerField(TEXT("owners"))||World->EligibleCount()!=Step->GetIntegerField(TEXT("eligible"))||
       Session->AssetBuilds!=Step->GetIntegerField(TEXT("geometry_builds"))||Session->MaterialBuilds!=Step->GetIntegerField(TEXT("material_builds")))return true;
    double Expected;
    if(Step->TryGetNumberField(TEXT("world_activations"),Expected)&&Session->WorldActivations!=Expected)return true;
    if(Step->TryGetNumberField(TEXT("late_asset_discards"),Expected)&&Session->RegistryLateDiscards!=Expected)return true;
    if(Step->TryGetNumberField(TEXT("asset_rejected"),Expected)&&Session->RegistryAssetRejected!=Expected)return true;
    auto Receipt=MakeShared<FJsonObject>();
    Receipt->SetNumberField(TEXT("sequence"),Snapshot.Sequence);Receipt->SetNumberField(TEXT("frame"),Snapshot.Frame);
    Receipt->SetNumberField(TEXT("owners"),World->IdentityCount());Receipt->SetNumberField(TEXT("eligible"),World->EligibleCount());
    Receipt->SetNumberField(TEXT("geometry_builds"),Session->AssetBuilds);Receipt->SetNumberField(TEXT("material_builds"),Session->MaterialBuilds);
    Receipt->SetNumberField(TEXT("image_builds"),Session->ImageBuilds);Receipt->SetNumberField(TEXT("actual_meshes"),World->ActualMeshCount());
    Receipt->SetNumberField(TEXT("world_activations"),Session->WorldActivations);Receipt->SetNumberField(TEXT("admissions"),Session->AssetAdmissions);
    Receipt->SetNumberField(TEXT("retired"),World->RetiredOwners);Receipt->SetNumberField(TEXT("asset_rejected"),Session->RegistryAssetRejected);
    Receipt->SetNumberField(TEXT("late_asset_discards"),Session->RegistryLateDiscards);
    TArray<FColor> Pixels;FReadSurfaceDataFlags Flags(RCM_UNorm);Flags.SetLinearToGamma(false);
    if(!World->Target()->GameThread_GetRenderTargetResource()->ReadPixels(Pixels,Flags)) {Error=TEXT("Registry readback failed");return false;}
    const FString Prefix=Output/FString::Printf(TEXT("registry-%d"),Index+1);
    if(!FFileHelper::SaveArrayToFile(TArrayView<const uint8>(reinterpret_cast<const uint8*>(Pixels.GetData()),Pixels.Num()*sizeof(FColor)),*(Prefix+TEXT(".bgra")))){Error=TEXT("Registry image write failed");return false;}
    FString Json;FJsonSerializer::Serialize(Receipt,TJsonWriterFactory<>::Create(&Json));
    const FString ReceiptFile=Prefix+TEXT(".json"),PendingFile=ReceiptFile+TEXT(".pending");
    if(!FFileHelper::SaveStringToFile(Json,*PendingFile)||!IFileManager::Get().Move(*ReceiptFile,*PendingFile,true,false,false)){
        Error=TEXT("Registry receipt publication failed");return false;
    }
    ++Session->RegistryCheckStep;Step->TryGetBoolField(TEXT("restart_world"),Restart);Finished=Session->RegistryCheckStep==Steps.Num();return true;
}
