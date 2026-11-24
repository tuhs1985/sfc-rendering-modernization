#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "SFCSceneData.h"
#include "SFCSessionSubsystem.generated.h"
struct FSFCRevisionKey {
    int64 Owner=0,Revision=0;
    bool operator==(const FSFCRevisionKey& Other)const{return Owner==Other.Owner&&Revision==Other.Revision;}
    friend uint32 GetTypeHash(const FSFCRevisionKey& Key){return HashCombine(GetTypeHash(Key.Owner),GetTypeHash(Key.Revision));}
};
struct FSFCAssetBinding {
    FString Content,PacketHash;
    int64 Owner=0,Revision=0,Pid=0,Model=0,Source=0;
    FSFCFrame InitialFrame;
    TSharedPtr<class FJsonObject> Fragment;
};
USTRUCT()
struct FSFCRetainedAsset {
    GENERATED_BODY()
    FSFCSceneData Data;
    UPROPERTY() TObjectPtr<class UStaticMesh> Mesh;
    UPROPERTY() TArray<TObjectPtr<class UTexture2D>> Images;
    UPROPERTY() TArray<TObjectPtr<class UMaterialInstanceDynamic>> Materials;
};
UCLASS()
class SFCBRIDGERUNTIME_API USFCSessionSubsystem : public UGameInstanceSubsystem {
    GENERATED_BODY()
public:
    bool Load(const FString& Filename,bool Diagnostics,FString& Error);
    bool Admit(FSFCSceneData Candidate,bool Diagnostics,FString& Error);
    const FSFCAssetBinding* Binding(int64 Owner,int64 Revision,int64 Model,int64 Source)const;
    const FSFCRetainedAsset* Asset(const FString& Content)const{return Assets.Find(Content);}
    void Retire(int64 Owner);
    bool IsRetired(int64 Owner)const{return Retired.Contains(Owner);}
    const FString& SessionName()const{return Session;}
    uint64 RetainedSourceBytes()const{return RetainedBytes;}
    int32 BindingCount()const{return Bindings.Num();}
    int32 TextureCount()const{return Textures.Num();}
    virtual void Deinitialize() override;
    const FSFCSceneData& Data()const;
    class UStaticMesh* Mesh()const;
    const TArray<TObjectPtr<class UMaterialInstanceDynamic>>& Materials()const;
    TSharedPtr<class FSFCLiveSource> LiveReader;
    bool ArraysChecked=false;
    double PreparationSeconds=0;
    int32 AssetBuilds=0,MaterialBuilds=0,ImageBuilds=0,AssetAdmissions=0,WorldActivations=0;
    double TotalPreparationSeconds=0;
    int32 RegistryCheckStep=0,RegistryAssetRejected=0,RegistryLateDiscards=0;
private:
    FString Session,PrimaryContent;
    FSFCSceneData EmptyData;
    TMap<FSFCRevisionKey,FSFCAssetBinding> Bindings;
    TSet<int64> Retired;
    TMap<FString,TArray<int64>> GeometryGroups;
    uint64 RetainedBytes=0;
    UPROPERTY() TMap<FString,FSFCRetainedAsset> Assets;
    UPROPERTY() TMap<FString,TObjectPtr<class UStaticMesh>> Geometry;
    UPROPERTY() TMap<FString,TObjectPtr<class UTexture2D>> Textures;
    UPROPERTY() FSFCRetainedAsset Pending;
};
