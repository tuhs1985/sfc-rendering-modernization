#pragma once
#include "CoreMinimal.h"
#include "SFCSourceMath.h"
struct FSFCOwnerKey {
    FString Session;
    int64 Epoch=0, VisualEpoch=0;
    int32 FragmentIndex=INDEX_NONE;
    bool operator==(const FSFCOwnerKey& Other) const {
        return Session==Other.Session&&Epoch==Other.Epoch&&VisualEpoch==Other.VisualEpoch&&FragmentIndex==Other.FragmentIndex;
    }
    friend uint32 GetTypeHash(const FSFCOwnerKey& K) {
        return HashCombine(HashCombine(GetTypeHash(K.Session),GetTypeHash(K.Epoch)),HashCombine(GetTypeHash(K.VisualEpoch),GetTypeHash(K.FragmentIndex)));
    }
};
struct FSFCCorner { int32 Position; FVector3f Normal; FVector2f UV; };
struct FSFCGroup {
    int32 First, Count;
    FString Image;
    TSharedPtr<class FJsonObject> OriginalAssociation;
};
struct FSFCFrame {
    SFCSource::Matrix Model, View, Projection;
    SFCSource::Point Viewport;
    TSharedPtr<class FJsonObject> Original;
};
struct FSFCSceneData {
    FString Session, Content, PacketHash, ModelName;
    TSharedPtr<class FJsonObject> FragmentRelationship;
    int64 OwnerEpoch=0, Revision=0;
    TArray<FVector3f> Positions;
    TArray<FSFCCorner> Corners;
    TArray<int32> Indices;
    TArray<FSFCGroup> Groups;
    TArray<FSFCFrame> Frames;
    struct FImage {
        int32 Width, Height;
        FString OriginalHash, DecodedHash;
        TArray<uint8> Pixels;
    };
    TMap<FString,FImage> Images;
};
// Offline proof input facade, not a new source wire. No UObject work here.
bool LoadSFCScene(const FString& Filename, FSFCSceneData& Out, FString& Error);
