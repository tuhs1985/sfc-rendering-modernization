#include "SFCSessionSubsystem.h"
#include "Engine/StaticMesh.h"
#include "Engine/Texture2D.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"
#include "StaticMeshResources.h"

bool USFCSessionSubsystem::Load(const FString& Filename,bool Diagnostics,FString& Error) {
    const double Start=FPlatformTime::Seconds();
    if(RetainedMesh) { Error=TEXT("Session already admitted; stop before replacing its source"); return false; }
    FSFCSceneData Candidate;
    if(!LoadSFCScene(Filename,Candidate,Error)) return false;
    UMaterialInterface* Base=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Bridge/SourceColour.SourceColour"));
    if(!Base) { Error=TEXT("Missing cooked source material"); return false; }
    TMap<FString,UTexture2D*> Images;
    for(const auto& Pair:Candidate.Images) {
        const auto& I=Pair.Value;
        UTexture2D* T=UTexture2D::CreateTransient(I.Width,I.Height,PF_B8G8R8A8);
        if(!T||!T->GetPlatformData()) { Error=TEXT("Texture allocation failed"); Deinitialize(); return false; }
        T->SRGB=false; T->NeverStream=true; T->Filter=TF_Nearest; T->AddressX=TA_Wrap; T->AddressY=TA_Wrap;
        auto& Mip=T->GetPlatformData()->Mips[0];
        void* Dest=Mip.BulkData.Lock(LOCK_READ_WRITE); FMemory::Memcpy(Dest,I.Pixels.GetData(),I.Pixels.Num()); Mip.BulkData.Unlock();
        T->UpdateResource(); RetainedImages.Add(T); Images.Add(Pair.Key,T);
    }
    for(const auto& G:Candidate.Groups) {
        auto* Material=UMaterialInstanceDynamic::Create(Base,this);
        Material->SetTextureParameterValue(TEXT("SourceTexture"),Images.FindChecked(G.Image));
        RetainedMaterials.Add(Material);
    }
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
    UStaticMesh* Mesh=NewObject<UStaticMesh>(this);
    Mesh->bSupportRayTracing=true;
    Mesh->bAllowCPUAccess=Diagnostics;
    for(int32 g=0;g<Candidate.Groups.Num();++g) {
        const auto PG=D.CreatePolygonGroup();
        const FName Slot(*FString::Printf(TEXT("SourceGroup%d"),g));
        A.GetPolygonGroupMaterialSlotNames()[PG]=Slot;
        FStaticMaterial MaterialSlot(RetainedMaterials[g],Slot);
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
        Error=TEXT("Runtime StaticMesh build failed"); Deinitialize(); return false;
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
        if(!OK) { Error=TEXT("Constructed StaticMesh differs from original corner/group data"); Deinitialize(); return false; }
        ArraysChecked=true;
    }
    RetainedMesh=Mesh; Source=MoveTemp(Candidate);
    ++AssetBuilds;
    // Decoded pixels have been copied into owned textures; do not retain another image dump.
    for(auto& Pair:Source.Images) Pair.Value.Pixels.Empty();
    PreparationSeconds=FPlatformTime::Seconds()-Start; return true;
}
void USFCSessionSubsystem::Deinitialize() {
    RetainedMesh=nullptr; RetainedImages.Empty(); RetainedMaterials.Empty(); Source=FSFCSceneData();
    ArraysChecked=false; Super::Deinitialize();
}
