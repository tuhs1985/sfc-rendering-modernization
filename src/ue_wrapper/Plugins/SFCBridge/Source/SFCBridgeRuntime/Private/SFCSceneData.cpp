#include "SFCSceneData.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
namespace {
using Values=TArray<TSharedPtr<FJsonValue>>;
bool Numbers(const TSharedPtr<FJsonValue>& V, int32 Count, TArray<double>& Out) {
    const Values* A=nullptr; Out.Reset();
    if(!V.IsValid() || !V->TryGetArray(A) || A->Num()!=Count) return false;
    for(const auto& E:*A) { double N; if(!E->TryGetNumber(N)||!FMath::IsFinite(N)) return false; Out.Add(N); }
    return true;
}
bool Matrix(const TSharedPtr<FJsonObject>& O,const TCHAR* Key,SFCSource::Matrix& M,bool Affine) {
    const Values* A=nullptr; if(!O->TryGetArrayField(Key,A)||A->Num()!=4) return false;
    for(int r=0;r<4;++r) { TArray<double> V; if(!Numbers((*A)[r],4,V)) return false; for(int c=0;c<4;++c) M[r][c]=V[c]; }
    return !Affine||SFCSource::ValidAffine(M);
}
bool Integer(const TSharedPtr<FJsonObject>& O,const TCHAR* Key,int64& N) {
    double V; if(!O->TryGetNumberField(Key,V)||!FMath::IsFinite(V)||V<0||V>9007199254740991.0||V!=FMath::FloorToDouble(V)) return false;
    N=static_cast<int64>(V); return true;
}
bool Index(double N,int32 Limit) { return N>=0&&N<Limit&&N==FMath::FloorToDouble(N); }
}
bool LoadSFCScene(const FString& Filename,FSFCSceneData& Out,FString& Error) {
    // Fresh temporary means a failed admission never mutates a retained asset.
    FSFCSceneData S;
    auto Fail=[&](const TCHAR* Why) { Error=Why; return false; };
    const int64 Size=IFileManager::Get().FileSize(*Filename);
    if(Size<=0||Size>16*1024*1024) return Fail(TEXT("Missing or oversized source scene"));
    FString Text; TSharedPtr<FJsonObject> O;
    if(!FFileHelper::LoadFileToString(Text,*Filename)||!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text),O)||!O.IsValid()) return Fail(TEXT("Invalid source JSON"));
    FString Schema; const TSharedPtr<FJsonObject>* Asset=nullptr;
    if(!O->TryGetStringField(TEXT("proof_schema"),Schema)||Schema!=TEXT("sfc.ue5.offline-proof.v1")||
       !O->TryGetStringField(TEXT("session"),S.Session)||S.Session.IsEmpty()||
       !O->TryGetStringField(TEXT("source_packet_sha256"),S.PacketHash)||S.PacketHash.Len()!=64||
       !Integer(O,TEXT("owner_epoch"),S.OwnerEpoch)||!S.OwnerEpoch||!O->TryGetObjectField(TEXT("asset"),Asset)||
       !(*Asset)->TryGetStringField(TEXT("content"),S.Content)||S.Content.Len()!=64||
       !(*Asset)->TryGetStringField(TEXT("model"),S.ModelName)||!Integer(*Asset,TEXT("revision"),S.Revision)||!S.Revision) return Fail(TEXT("Incomplete source identity"));
    const Values *Points=nullptr,*Corners=nullptr,*Indices=nullptr,*Groups=nullptr,*Frames=nullptr;
    if(!O->TryGetArrayField(TEXT("positions"),Points)||Points->IsEmpty()||Points->Num()>65536||
       !O->TryGetArrayField(TEXT("corners"),Corners)||Corners->IsEmpty()||Corners->Num()>32768||
       !O->TryGetArrayField(TEXT("indices"),Indices)||Indices->IsEmpty()||Indices->Num()>8192*3||Indices->Num()%3||
       !O->TryGetArrayField(TEXT("groups"),Groups)||Groups->IsEmpty()||Groups->Num()>256||
       !O->TryGetArrayField(TEXT("frames"),Frames)||Frames->IsEmpty()) return Fail(TEXT("Unsupported source counts"));
    const TSharedPtr<FJsonObject>* Fragment=nullptr;
    if(O->TryGetObjectField(TEXT("fragment"),Fragment)) S.FragmentRelationship=*Fragment;
    for(const auto& P:*Points) {
        TArray<double> V; if(!Numbers(P,3,V)) return Fail(TEXT("Invalid position"));
        const FVector3f Position(V[0],V[1],V[2]);
        if(Position.ContainsNaN()) return Fail(TEXT("Position cannot be represented"));
        S.Positions.Add(Position);
    }
    for(const auto& C:*Corners) {
        const Values* A=nullptr; double P; TArray<double> N,UV;
        if(!C->TryGetArray(A)||A->Num()!=3||!(*A)[0]->TryGetNumber(P)||!Index(P,S.Positions.Num())||!Numbers((*A)[1],3,N)||!Numbers((*A)[2],2,UV)) return Fail(TEXT("Invalid corner"));
        S.Corners.Add({static_cast<int32>(P),FVector3f(N[0],N[1],N[2]),FVector2f(UV[0],UV[1])});
    }
    for(const auto& I:*Indices) { double N; if(!I->TryGetNumber(N)||!Index(N,S.Corners.Num())) return Fail(TEXT("Invalid index")); S.Indices.Add(static_cast<int32>(N)); }
    int64 Next=0;
    for(const auto& G:*Groups) {
        const auto P=G->AsObject(); int64 First,Count; const TSharedPtr<FJsonObject>* Image=nullptr; FString Name;
        if(!P.IsValid()||!Integer(P,TEXT("first_index"),First)||!Integer(P,TEXT("index_count"),Count)||First!=Next||Count<=0||Count%3||Count>S.Indices.Num()-First||
           !P->TryGetObjectField(TEXT("primary"),Image)||!(*Image)->TryGetStringField(TEXT("filename"),Name)||Name.IsEmpty()) return Fail(TEXT("Invalid group association"));
        S.Groups.Add({static_cast<int32>(First),static_cast<int32>(Count),Name,P}); Next+=Count;
    }
    if(Next!=S.Indices.Num()) return Fail(TEXT("Incomplete group coverage"));
    for(const auto& F:*Frames) {
        FSFCFrame Frame; Frame.Original=F->AsObject(); const Values* V=nullptr;
        int64 Owner,Revision;
        if(!Frame.Original.IsValid()||!Integer(Frame.Original,TEXT("owner"),Owner)||Owner!=S.OwnerEpoch||
           !Integer(Frame.Original,TEXT("revision"),Revision)||Revision!=S.Revision) return Fail(TEXT("Frame owner/revision does not match its asset"));
        if(!Frame.Original.IsValid()||!Matrix(Frame.Original,TEXT("model"),Frame.Model,true)||!Matrix(Frame.Original,TEXT("view"),Frame.View,true)||!Matrix(Frame.Original,TEXT("projection"),Frame.Projection,false)||
           !Frame.Original->TryGetArrayField(TEXT("viewport"),V)||V->Num()!=4) return Fail(TEXT("Invalid frame transform"));
        for(int i=0;i<4;++i) if(!(*V)[i]->TryGetNumber(Frame.Viewport[i])||!FMath::IsFinite(Frame.Viewport[i])) return Fail(TEXT("Invalid viewport"));
        if(Frame.Viewport[0]<0||Frame.Viewport[1]<0||Frame.Viewport[2]<=0||Frame.Viewport[3]<=0||Frame.Viewport[0]+Frame.Viewport[2]>4096||Frame.Viewport[1]+Frame.Viewport[3]>4096) return Fail(TEXT("Unsupported viewport"));
        S.Frames.Add(MoveTemp(Frame));
    }
    const TSharedPtr<FJsonObject>* Images=nullptr; int64 Bytes=0;
    if(!O->TryGetObjectField(TEXT("images"),Images)) return Fail(TEXT("Missing images"));
    for(const auto& G:S.Groups) {
        if(S.Images.Contains(G.Image)) continue;
        const TSharedPtr<FJsonObject>* R=nullptr; int64 W,H; FString File;
        if(!(*Images)->TryGetObjectField(G.Image,R)||!Integer(*R,TEXT("width"),W)||!Integer(*R,TEXT("height"),H)||W<=0||W>4096||H<=0||H>4096||!(*R)->TryGetStringField(TEXT("file"),File)||File.IsEmpty()||File!=FPaths::GetCleanFilename(File)||File==TEXT("..")) return Fail(TEXT("Invalid image descriptor"));
        Bytes+=W*H*4; if(Bytes>128*1024*1024) return Fail(TEXT("Image budget exceeded"));
        FSFCSceneData::FImage Image; Image.Width=W; Image.Height=H;
        if(!(*R)->TryGetStringField(TEXT("original_sha256"),Image.OriginalHash)||Image.OriginalHash.Len()!=64||
           !(*R)->TryGetStringField(TEXT("sha256"),Image.DecodedHash)||Image.DecodedHash.Len()!=64) return Fail(TEXT("Missing original image identity"));
        const FString ImagePath=FPaths::GetPath(Filename)/File;
        if(IFileManager::Get().FileSize(*ImagePath)!=W*H*4||!FFileHelper::LoadFileToArray(Image.Pixels,*ImagePath)||Image.Pixels.Num()!=W*H*4) return Fail(TEXT("Missing or invalid original image"));
        S.Images.Add(G.Image,MoveTemp(Image));
    }
    Out=MoveTemp(S); return true;
}
