#include "ProofGameMode.h"
#include "Modules/ModuleManager.h"
#include "ProceduralMeshComponent.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Engine/Texture2D.h"
#include "Engine/GameViewportClient.h"
#include "Engine/Engine.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/Layout/SConstraintCanvas.h"
#include "Styling/SlateBrush.h"

IMPLEMENT_PRIMARY_GAME_MODULE(FDefaultGameModuleImpl, SFCSceneProof, "SFCSceneProof");

namespace
{
    FVector4 ApplyMatrix(const TArray<TSharedPtr<FJsonValue>>& Rows, const FVector4& Position)
    {
        check(Rows.Num() == 4);
        FVector4 Result(0, 0, 0, 0);
        for (int32 Row = 0; Row < 4; ++Row)
        {
            const auto& Values = Rows[Row]->AsArray();
            check(Values.Num() == 4);
            for (int32 Column = 0; Column < 4; ++Column)
                Result[Row] += Values[Column]->AsNumber() * Position[Column];
        }
        return Result;
    }

    double ProjectionValue(const TArray<TSharedPtr<FJsonValue>>& Rows, int32 Row, int32 Column)
    {
        return Rows[Row]->AsArray()[Column]->AsNumber();
    }
}

AProofGameMode::AProofGameMode()
{
    PrimaryActorTick.bCanEverTick = true;
    DefaultPawnClass = nullptr;
    Started = FPlatformTime::Seconds();
}

void AProofGameMode::BeginPlay()
{
    Super::BeginPlay();
    // AGameModeBase inherits AInfo's hidden default. This proof owns visible geometry.
    SetActorHiddenInGame(false);
    FString InputFile;
    if (!FParse::Value(FCommandLine::Get(), TEXT("SFCScene="), InputFile) ||
        !FParse::Value(FCommandLine::Get(), TEXT("SFCOutput="), OutputDirectory))
    {
        UE_LOG(LogTemp, Error, TEXT("Supply -SFCScene=<checked scene.json> -SFCOutput=<new output directory>"));
        FPlatformMisc::RequestExitWithStatus(false, 2);
        return;
    }
    FString Text;
    if (!FFileHelper::LoadFileToString(Text, *InputFile) ||
        !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text), Scene) ||
        !Scene.IsValid() || Scene->GetStringField(TEXT("proof_schema")) != TEXT("sfc.ue5.offline-proof.v1"))
    {
        UE_LOG(LogTemp, Error, TEXT("Cannot read checked SFC proof input"));
        FPlatformMisc::RequestExitWithStatus(false, 3);
        return;
    }
    const auto& Frames = Scene->GetArrayField(TEXT("frames"));
    FParse::Value(FCommandLine::Get(), TEXT("SFCFrame="), FrameIndex);
    check(Frames.IsValidIndex(FrameIndex));
    const auto Frame = Frames[FrameIndex]->AsObject();
    const auto& Model = Frame->GetArrayField(TEXT("model"));
    const auto& View = Frame->GetArrayField(TEXT("view"));
    const auto& Projection = Frame->GetArrayField(TEXT("projection"));
    const auto& Viewport = Frame->GetArrayField(TEXT("viewport"));
    const int32 Width = static_cast<int32>(Viewport[2]->AsNumber());
    const int32 Height = static_cast<int32>(Viewport[3]->AsNumber());
    check(Width > 0 && Width <= 4096 && Height > 0 && Height <= 4096);
    const auto& Points = Scene->GetArrayField(TEXT("positions"));
    const auto& Corners = Scene->GetArrayField(TEXT("corners"));
    const auto& Indices = Scene->GetArrayField(TEXT("indices"));
    const auto& Groups = Scene->GetArrayField(TEXT("groups"));
    CornerCount = Corners.Num();
    IndexCount = Indices.Num();
    GroupCount = Groups.Num();
    Ship = NewObject<UProceduralMeshComponent>(this, TEXT("CapturedShip"));
    SetRootComponent(Ship);
    Ship->RegisterComponent();
    Ship->SetCastShadow(false);
    Ship->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    TArray<FVector> Vertices;
    TArray<FVector> Normals;
    TArray<FVector2D> UVs;
    for (const auto& CornerValue : Corners)
    {
        const auto& Corner = CornerValue->AsArray();
        const auto& Point = Points[static_cast<int32>(Corner[0]->AsNumber())]->AsArray();
        FVector4 Position(Point[0]->AsNumber(), Point[1]->AsNumber(), Point[2]->AsNumber(), 1);
        Position = ApplyMatrix(View, ApplyMatrix(Model, Position));
        Vertices.Add(FVector(-Position.Z, Position.X, Position.Y));
        const auto& Normal = Corner[1]->AsArray();
        FVector4 Direction(Normal[0]->AsNumber(), Normal[1]->AsNumber(), Normal[2]->AsNumber(), 0);
        Direction = ApplyMatrix(View, ApplyMatrix(Model, Direction));
        Normals.Add(FVector(-Direction.Z, Direction.X, Direction.Y).GetSafeNormal());
        const auto& UV = Corner[2]->AsArray();
        UVs.Add(FVector2D(UV[0]->AsNumber(), UV[1]->AsNumber()));
    }
    UMaterialInterface* BaseMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Proof/SourceColour.SourceColour"));
    check(BaseMaterial);
    const auto ImageRecords = Scene->GetObjectField(TEXT("images"));
    TMap<FString, UTexture2D*> ImageCache;
    for (int32 GroupIndex = 0; GroupIndex < Groups.Num(); ++GroupIndex)
    {
        const auto Group = Groups[GroupIndex]->AsObject();
        const FString Name = Group->GetObjectField(TEXT("primary"))->GetStringField(TEXT("filename"));
        UTexture2D* Image = ImageCache.FindRef(Name);
        if (!Image)
        {
            const auto Record = ImageRecords->GetObjectField(Name);
            const int32 ImageWidth = static_cast<int32>(Record->GetNumberField(TEXT("width")));
            const int32 ImageHeight = static_cast<int32>(Record->GetNumberField(TEXT("height")));
            check(ImageWidth > 0 && ImageWidth <= 4096 && ImageHeight > 0 && ImageHeight <= 4096);
            const FString ImageName = Record->GetStringField(TEXT("file"));
            check(FPaths::GetCleanFilename(ImageName) == ImageName);
            TArray<uint8> Pixels;
            check(FFileHelper::LoadFileToArray(Pixels, *(FPaths::GetPath(InputFile) / ImageName)));
            check(Pixels.Num() == ImageWidth * ImageHeight * 4);
            Image = UTexture2D::CreateTransient(ImageWidth, ImageHeight, PF_B8G8R8A8);
            Image->SRGB = false;
            Image->Filter = TF_Nearest;
            Image->AddressX = TA_Wrap;
            Image->AddressY = TA_Wrap;
            auto& Mip = Image->GetPlatformData()->Mips[0];
            void* Destination = Mip.BulkData.Lock(LOCK_READ_WRITE);
            FMemory::Memcpy(Destination, Pixels.GetData(), Pixels.Num());
            Mip.BulkData.Unlock();
            Image->UpdateResource();
            Images.Add(Image);
            ImageCache.Add(Name, Image);
        }
        UMaterialInstanceDynamic* Material = UMaterialInstanceDynamic::Create(BaseMaterial, this);
        Material->SetTextureParameterValue(TEXT("SourceTexture"), Image);
        TArray<int32> GroupIndices;
        const int32 First = static_cast<int32>(Group->GetNumberField(TEXT("first_index")));
        const int32 Count = static_cast<int32>(Group->GetNumberField(TEXT("index_count")));
        check(First >= 0 && Count > 0 && First + Count <= Indices.Num() && Count % 3 == 0);
        for (int32 Index = First; Index < First + Count; ++Index)
            GroupIndices.Add(static_cast<int32>(Indices[Index]->AsNumber()));
        Ship->CreateMeshSection_LinearColor(GroupIndex, Vertices, GroupIndices, Normals, UVs,
            TArray<FLinearColor>(), TArray<FProcMeshTangent>(), false);
        Ship->SetMaterial(GroupIndex, Material);
        const FProcMeshSection* Section = Ship->GetProcMeshSection(GroupIndex);
        check(Section && Section->ProcVertexBuffer.Num() == Vertices.Num());
        check(Section->ProcIndexBuffer.Num() == GroupIndices.Num());
        for (int32 Index = 0; Index < Vertices.Num(); ++Index)
        {
            check(Section->ProcVertexBuffer[Index].Position.Equals(Vertices[Index], .00001));
            check(Section->ProcVertexBuffer[Index].Normal.Equals(Normals[Index], .00001));
            check(Section->ProcVertexBuffer[Index].UV0.Equals(UVs[Index], .00001));
        }
        for (int32 Index = 0; Index < GroupIndices.Num(); ++Index)
            check(Section->ProcIndexBuffer[Index] == static_cast<uint32>(GroupIndices[Index]));
    }
    Output = NewObject<UTextureRenderTarget2D>(this);
    Output->ClearColor = FLinearColor::Black;
    Output->TargetGamma = 1.0f;
    Output->InitCustomFormat(Width, Height, PF_B8G8R8A8, true);
    Output->UpdateResourceImmediate(true);
    Camera = NewObject<USceneCaptureComponent2D>(this, TEXT("SFCCamera"));
    Camera->RegisterComponent();
    Camera->SetWorldLocationAndRotation(FVector::ZeroVector, FRotator::ZeroRotator);
    Camera->TextureTarget = Output;
    Camera->CaptureSource = SCS_SceneColorHDR;
    Camera->bCaptureEveryFrame = false;
    Camera->bCaptureOnMovement = false;
    Camera->PrimitiveRenderMode = ESceneCapturePrimitiveRenderMode::PRM_UseShowOnlyList;
    Camera->ShowOnlyComponent(Ship);
    Camera->ShowFlags.SetAntiAliasing(false);
    Camera->ShowFlags.SetAtmosphere(false);
    Camera->ShowFlags.SetFog(false);
    Camera->ShowFlags.SetPostProcessing(false);
    Camera->bUseCustomProjectionMatrix = true;
    FMatrix ProjectionMatrix = FMatrix::Identity;
    ProjectionMatrix.M[0][0] = ProjectionValue(Projection, 0, 0);
    ProjectionMatrix.M[1][1] = ProjectionValue(Projection, 1, 1);
    ProjectionMatrix.M[2][0] = -ProjectionValue(Projection, 0, 2);
    ProjectionMatrix.M[2][1] = -ProjectionValue(Projection, 1, 2);
    ProjectionMatrix.M[2][2] = (1.0 + ProjectionValue(Projection, 2, 2)) / 2.0;
    ProjectionMatrix.M[2][3] = 1.0;
    ProjectionMatrix.M[3][2] = -ProjectionValue(Projection, 2, 3) / 2.0;
    ProjectionMatrix.M[3][3] = 0.0;
    Camera->CustomProjectionMatrix = ProjectionMatrix;
    Camera->MaxViewDistanceOverride = 10000000.0f;
    ImageBrush = MakeShared<FSlateBrush>();
    ImageBrush->SetResourceObject(Output);
    ImageBrush->ImageSize = FVector2D(Width, Height);
    if (GEngine && GEngine->GameViewport)
    {
        GEngine->GameViewport->AddViewportWidgetContent(
            SNew(SConstraintCanvas)
            + SConstraintCanvas::Slot()
            .Offset(FMargin(Viewport[0]->AsNumber(), Viewport[1]->AsNumber(), Width, Height))
            [SNew(SImage).Image(ImageBrush.Get())]);
    }
    UE_LOG(LogTemp, Display, TEXT("SFC_PROOF_READY model=%s corners=%d indices=%d groups=%d"),
        *Scene->GetObjectField(TEXT("asset"))->GetStringField(TEXT("model")), CornerCount, IndexCount, GroupCount);
}

void AProofGameMode::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!Camera || Finished) return;
    ++Ticks;
    Camera->CaptureScene();
    if (Ticks < 30) return;
    Finished = true;
    TArray<FColor> Pixels;
    FReadSurfaceDataFlags Flags(RCM_UNorm);
    Flags.SetLinearToGamma(false);
    if (!Output->GameThread_GetRenderTargetResource()->ReadPixels(Pixels, Flags))
    {
        FPlatformMisc::RequestExitWithStatus(false, 4);
        return;
    }
    IFileManager::Get().MakeDirectory(*OutputDirectory, true);
    FFileHelper::CreateBitmap(*(OutputDirectory / TEXT("ship")), Output->SizeX, Output->SizeY, Pixels.GetData());
    TSharedRef<FJsonObject> Report = MakeShared<FJsonObject>();
    Report->SetStringField(TEXT("model"), Scene->GetObjectField(TEXT("asset"))->GetStringField(TEXT("model")));
    Report->SetStringField(TEXT("session"), Scene->GetStringField(TEXT("session")));
    Report->SetStringField(TEXT("source_packet_sha256"), Scene->GetStringField(TEXT("source_packet_sha256")));
    Report->SetNumberField(TEXT("corners"), CornerCount);
    Report->SetNumberField(TEXT("indices"), IndexCount);
    Report->SetNumberField(TEXT("groups"), GroupCount);
    Report->SetNumberField(TEXT("textures"), Images.Num());
    Report->SetNumberField(TEXT("width"), Output->SizeX);
    Report->SetNumberField(TEXT("height"), Output->SizeY);
    Report->SetBoolField(TEXT("constructed_arrays_checked"), true);
    Report->SetNumberField(TEXT("frame_index"), FrameIndex);
    Report->SetObjectField(TEXT("source_frame"), Scene->GetArrayField(TEXT("frames"))[FrameIndex]->AsObject());
    Report->SetNumberField(TEXT("first_readback_seconds"), FPlatformTime::Seconds() - Started);
    Report->SetStringField(TEXT("engine"), FEngineVersion::Current().ToString());
    FString Json;
    FJsonSerializer::Serialize(Report, TJsonWriterFactory<>::Create(&Json));
    FFileHelper::SaveStringToFile(Json, *(OutputDirectory / TEXT("result.json")));
    if (FParse::Param(FCommandLine::Get(), TEXT("SFCExit")))
        FPlatformMisc::RequestExit(false);
}
