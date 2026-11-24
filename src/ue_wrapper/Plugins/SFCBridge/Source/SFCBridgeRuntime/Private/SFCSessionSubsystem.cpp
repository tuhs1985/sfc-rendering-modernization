#include "SFCSessionSubsystem.h"
#include "ue_texture_origin.h"
#include "Engine/StaticMesh.h"
#include "Engine/Texture2D.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"
#include "StaticMeshResources.h"
#include "Dom/JsonObject.h"

namespace {
FString TextureIdentity(const FSFCSceneData::FImage& Image){
    // Equal decoded bytes do not imply the same 2D view (e.g. 2x2 vs 1x4).
    return FString::Printf(TEXT("%s:%dx%d:BGRA8"),*Image.DecodedHash,Image.Width,Image.Height);
}
UStaticMesh* BuildGeometry(USFCSessionSubsystem* Outer,const FSFCSceneData& Candidate,const TArray<TObjectPtr<UMaterialInstanceDynamic>>& Materials,bool Diagnostics,bool& ArraysChecked,FString& Error){
    FMeshDescription D; FStaticMeshAttributes A(D); A.Register();
    auto Positions=A.GetVertexPositions(); auto Normals=A.GetVertexInstanceNormals();
    auto Tangents=A.GetVertexInstanceTangents(); auto Signs=A.GetVertexInstanceBinormalSigns();
    auto Colours=A.GetVertexInstanceColors(); auto UV=A.GetVertexInstanceUVs(); UV.SetNumChannels(1);
    TArray<FVertexInstanceID> Corners;
    for(const auto& C:Candidate.Corners) {
        const auto& P=Candidate.Positions[C.Position];
        const FVertexID V=D.CreateVertex(); Positions[V]=FVector3f(-P.Z,P.X,P.Y);
        const auto VI=D.CreateVertexInstance(V); Corners.Add(VI);
        const FVector3f N(-C.Normal.Z,C.Normal.X,C.Normal.Y);
        Normals[VI]=N;
        // No source tangent/normal map is supplied. Deterministic orthogonal basis only.
        Tangents[VI]=FVector3f::CrossProduct(FMath::Abs(N.Z)<.9f?FVector3f(0,0,1):FVector3f(0,1,0),N).GetSafeNormal();
        Signs[VI]=1; Colours[VI]=FVector4f(1,1,1,1); UV.Set(VI,0,C.UV);
    }
    UStaticMesh* Mesh=NewObject<UStaticMesh>(Outer);
    Mesh->bSupportRayTracing=true;
    Mesh->bAllowCPUAccess=Diagnostics;
    for(int32 g=0;g<Candidate.Groups.Num();++g) {
        const auto PG=D.CreatePolygonGroup();
        const FName Slot(*FString::Printf(TEXT("SourceGroup%d"),g));
        A.GetPolygonGroupMaterialSlotNames()[PG]=Slot;
        FStaticMaterial MaterialSlot(Materials[g],Slot);
        // Required by UE's streaming metadata query even for resident transient images.
        // Zero density is deliberate: these images have no streamed mips.
        MaterialSlot.UVChannelData=FMeshUVChannelInfo(0.0f);
        Mesh->GetStaticMaterials().Add(MaterialSlot);
        const auto& G=Candidate.Groups[g];
        for(int32 i=G.First;i<G.First+G.Count;i+=3) {
            TArray<FVertexInstanceID,TInlineAllocator<3>> Tri;
            for(int k=0;k<3;++k) Tri.Add(Corners[Candidate.Indices[i+k]]);
            D.CreateTriangle(PG,Tri);
        }
    }
    UStaticMesh::FBuildMeshDescriptionsParams Params;
    Params.bFastBuild=true; Params.bBuildSimpleCollision=false; Params.bCommitMeshDescription=false;
    Params.bMarkPackageDirty=false; Params.bAllowCpuAccess=Diagnostics;
    UStaticMesh::FBuildMeshDescriptionsLODParams LOD;
    LOD.bUseFullPrecisionUVs=true; LOD.bUseHighPrecisionTangentBasis=true; Params.PerLODOverrides.Add(LOD);
    if(!Mesh->BuildFromMeshDescriptions({&D},Params)||!Mesh->GetRenderData()||Mesh->GetBounds().BoxExtent.ContainsNaN()) {
        Error=TEXT("Runtime StaticMesh build failed"); return nullptr;
    }
    if(Diagnostics) {
        const auto& R=Mesh->GetRenderData()->LODResources[0];
        bool OK=R.Sections.Num()==Candidate.Groups.Num();
        for(int g=0;OK&&g<R.Sections.Num();++g) {
            const auto& Section=R.Sections[g]; const auto& G=Candidate.Groups[g];
            OK=Section.NumTriangles*3==static_cast<uint32>(G.Count)&&Section.MaterialIndex==g;
            for(int i=0;OK&&i<G.Count;++i) {
                const uint32 V=R.IndexBuffer.GetIndex(Section.FirstIndex+i);
                const auto& C=Candidate.Corners[Candidate.Indices[G.First+i]];
                const auto& P=Candidate.Positions[C.Position];
                OK=R.VertexBuffers.PositionVertexBuffer.VertexPosition(V).Equals(FVector3f(-P.Z,P.X,P.Y),1e-5f)&&
                    R.VertexBuffers.StaticMeshVertexBuffer.GetVertexUV(V,0).Equals(C.UV,1e-6f)&&
                    FVector3f(R.VertexBuffers.StaticMeshVertexBuffer.VertexTangentZ(V)).Equals(FVector3f(-C.Normal.Z,C.Normal.X,C.Normal.Y),.001f);
            }
        }
        if(!OK) { Error=TEXT("Constructed StaticMesh differs from original corner/group data"); return nullptr; }
        ArraysChecked=true;
    }
    return Mesh;
}
}

const FSFCSceneData& USFCSessionSubsystem::Data()const{const auto* A=Assets.Find(PrimaryContent);return A?A->Data:EmptyData;}
UStaticMesh* USFCSessionSubsystem::Mesh()const{const auto* A=Assets.Find(PrimaryContent);return A?A->Mesh.Get():nullptr;}
const TArray<TObjectPtr<UMaterialInstanceDynamic>>& USFCSessionSubsystem::Materials()const{
    const auto* A=Assets.Find(PrimaryContent);return A?A->Materials:Pending.Materials;
}
bool USFCSessionSubsystem::Load(const FString& Filename,bool Diagnostics,FString& Error){
    if(!PrimaryContent.IsEmpty()){Error=TEXT("Primary source already admitted");return false;}
    FSFCSceneData Candidate;if(!LoadSFCScene(Filename,Candidate,Error))return false;
    return Admit(MoveTemp(Candidate),Diagnostics,Error);
}
bool USFCSessionSubsystem::Admit(FSFCSceneData Candidate,bool Diagnostics,FString& Error){
    const double Start=FPlatformTime::Seconds();
    if((!Session.IsEmpty()&&Candidate.Session!=Session)||Retired.Contains(Candidate.OwnerEpoch)){
        Error=TEXT("Asset belongs to another or retired source session/owner");return false;
    }
    const FSFCRevisionKey Key{Candidate.OwnerEpoch,Candidate.Revision};
    if(const auto* Existing=Bindings.Find(Key)){
        if(Existing->Content!=Candidate.Content||Existing->Pid!=Candidate.SourcePid||Existing->Model!=Candidate.ModelIdentity||Existing->Source!=Candidate.SourceIdentity){
            Error=TEXT("Immutable source binding changed");return false;
        }
        return true;
    }
    const auto* ExistingAsset=Assets.Find(Candidate.Content);
    uint64 Added=0;
    if(!ExistingAsset){
        Added=Candidate.Positions.GetAllocatedSize()+Candidate.Corners.GetAllocatedSize()+Candidate.Indices.GetAllocatedSize()+Candidate.Groups.GetAllocatedSize();
        for(const auto& Pair:Candidate.Images)if(!Textures.Contains(TextureIdentity(Pair.Value)))Added+=Pair.Value.Pixels.Num();
        if(Added>256ull*1024*1024||RetainedBytes>256ull*1024*1024-Added){Error=TEXT("Retained source asset byte budget");return false;}
        UMaterialInterface* Base=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Bridge/SourceColour.SourceColour"));
        if(!Base){Error=TEXT("Missing cooked source material");return false;}
        TArray<int64> GroupKeys;
        for(int32 Index=0;Index<Candidate.Groups.Num();++Index){
            double Tag=Index;
            if(Candidate.Groups[Index].OriginalAssociation.IsValid())Candidate.Groups[Index].OriginalAssociation->TryGetNumberField(TEXT("group"),Tag);
            if(!FMath::IsFinite(Tag)||Tag<0||Tag>UINT32_MAX||Tag!=FMath::FloorToDouble(Tag)||GroupKeys.Contains(int64(Tag))){Error=TEXT("Invalid original material group identity");return false;}
            GroupKeys.Add(int64(Tag));
        }
        const auto* CachedSlots=GeometryGroups.Find(Candidate.GeometryContent);
        if(CachedSlots){
            if(CachedSlots->Num()!=GroupKeys.Num()){Error=TEXT("Geometry group layout changed without new geometry");return false;}
            for(int64 Tag:GroupKeys)if(!CachedSlots->Contains(Tag)){Error=TEXT("Geometry group identity changed without new geometry");return false;}
        }
        Pending=FSFCRetainedAsset();
        TMap<FString,UTexture2D*> Images,NewTextures;
        for(const auto& Pair:Candidate.Images){
            const auto& I=Pair.Value;UTexture2D* T=nullptr;const FString ImageKey=TextureIdentity(I);
            if(const auto* Cached=Textures.Find(ImageKey))T=Cached->Get();
            else if(auto* New=NewTextures.Find(ImageKey))T=*New;
            else{
                T=UTexture2D::CreateTransient(I.Width,I.Height,PF_B8G8R8A8);
                if(!T||!T->GetPlatformData()){Error=TEXT("Texture allocation failed");Pending=FSFCRetainedAsset();return false;}
                Pending.Images.Add(T);NewTextures.Add(ImageKey,T);
                T->SRGB=false;T->NeverStream=true;T->Filter=TF_Nearest;T->AddressX=TA_Wrap;T->AddressY=TA_Wrap;
                auto& Mip=T->GetPlatformData()->Mips[0];void* Dest=Mip.BulkData.Lock(LOCK_READ_WRITE);
                const bool Uploaded=sfc_ue_texture::upload_rows(I.Pixels.GetData(),I.Pixels.Num(),I.Width,I.Height,
                    Dest,size_t(I.Width)*I.Height*4,size_t(I.Width)*4);
                Mip.BulkData.Unlock();
                if(!Uploaded){Error=TEXT("Invalid UE texture upload extent");Pending=FSFCRetainedAsset();return false;}
                T->UpdateResource();
            }
            Images.Add(Pair.Key,T);
        }
        Pending.Materials.SetNum(Candidate.Groups.Num());
        for(int32 Index=0;Index<Candidate.Groups.Num();++Index){
            const auto& G=Candidate.Groups[Index];
            auto* Material=UMaterialInstanceDynamic::Create(Base,this);
            if(!Material){Error=TEXT("Material allocation failed");Pending=FSFCRetainedAsset();return false;}
            Material->SetTextureParameterValue(TEXT("SourceTexture"),Images.FindChecked(G.Image));
            // A retained mesh keeps its original section slots. Material-only
            // revisions may enumerate groups differently; bind by source ID.
            const int32 Slot=CachedSlots?CachedSlots->Find(GroupKeys[Index]):Index;
            Pending.Materials[Slot]=Material;
        }
        const auto* CachedGeometry=Geometry.Find(Candidate.GeometryContent);
        UStaticMesh* Built=CachedGeometry?CachedGeometry->Get():BuildGeometry(this,Candidate,Pending.Materials,Diagnostics,ArraysChecked,Error);
        if(!Built){Pending=FSFCRetainedAsset();return false;}
        Pending.Mesh=Built;
        if(!CachedGeometry){Geometry.Add(Candidate.GeometryContent,Built);GeometryGroups.Add(Candidate.GeometryContent,MoveTemp(GroupKeys));++AssetBuilds;}
        for(const auto& Pair:NewTextures){Textures.Add(Pair.Key,Pair.Value);++ImageBuilds;}
        for(auto& Pair:Candidate.Images)Pair.Value.Pixels.Empty();
        Pending.Data=Candidate;Assets.Add(Candidate.Content,MoveTemp(Pending));Pending=FSFCRetainedAsset();
        ++MaterialBuilds;RetainedBytes+=Added;
    }
    FSFCAssetBinding Binding;Binding.Content=Candidate.Content;Binding.PacketHash=Candidate.PacketHash;
    Binding.Owner=Candidate.OwnerEpoch;Binding.Revision=Candidate.Revision;Binding.Pid=Candidate.SourcePid;
    Binding.Model=Candidate.ModelIdentity;Binding.Source=Candidate.SourceIdentity;Binding.InitialFrame=Candidate.Frames[0];Binding.Fragment=Candidate.FragmentRelationship;
    Bindings.Add(Key,MoveTemp(Binding));
    if(Session.IsEmpty())Session=Candidate.Session;if(PrimaryContent.IsEmpty())PrimaryContent=Candidate.Content;
    ++AssetAdmissions;PreparationSeconds=FPlatformTime::Seconds()-Start;TotalPreparationSeconds+=PreparationSeconds;return true;
}
const FSFCAssetBinding* USFCSessionSubsystem::Binding(int64 Owner,int64 Revision,int64 Model,int64 Source)const{
    if(Retired.Contains(Owner))return nullptr;
    const auto* Result=Bindings.Find(FSFCRevisionKey{Owner,Revision});
    return Result&&Result->Model==Model&&Result->Source==Source?Result:nullptr;
}
void USFCSessionSubsystem::Retire(int64 Owner){
    Retired.Add(Owner);
    for(auto It=Bindings.CreateIterator();It;++It)if(It.Key().Owner==Owner)It.RemoveCurrent();
}
void USFCSessionSubsystem::Deinitialize(){
    LiveReader.Reset();Bindings.Empty();Retired.Empty();Assets.Empty();Geometry.Empty();GeometryGroups.Empty();Textures.Empty();Pending=FSFCRetainedAsset();
    Session.Empty();PrimaryContent.Empty();RetainedBytes=0;ArraysChecked=false;Super::Deinitialize();
}
