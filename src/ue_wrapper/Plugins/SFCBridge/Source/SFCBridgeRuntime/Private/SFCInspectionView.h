#pragma once
#include "Widgets/SLeafWidget.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Text/STextBlock.h"
#include "Rendering/DrawElements.h"
#include "Styling/CoreStyle.h"
#include "Engine/TextureRenderTarget2D.h"

// Inspection only: native capture alpha is inverse opacity, not Slate opacity.
// Do not rewrite the capture target or change its GPU export interpretation.
class SSFCInspectionImage : public SLeafWidget {
public:
    SLATE_BEGIN_ARGS(SSFCInspectionImage){} SLATE_ARGUMENT(const FSlateBrush*,Image) SLATE_END_ARGS()
    void Construct(const FArguments& Args){Image=Args._Image;}
    virtual FVector2D ComputeDesiredSize(float)const override{return Image?FVector2D(Image->ImageSize):FVector2D(1,1);}
    virtual int32 OnPaint(const FPaintArgs&,const FGeometry& Geometry,const FSlateRect&,
        FSlateWindowElementList& Elements,int32 Layer,const FWidgetStyle&,bool)const override{
        FSlateDrawElement::MakeBox(Elements,Layer,Geometry.ToPaintGeometry(),FCoreStyle::Get().GetBrush(TEXT("WhiteBrush")),ESlateDrawEffect::None,FLinearColor::Black);
        if(!Image)return Layer;
        FVector2f Source(Image->ImageSize);
        if(const auto* Target=Cast<UTextureRenderTarget2D>(Image->GetResourceObject()))Source=FVector2f(Target->SizeX,Target->SizeY);
        const FVector2f Available(Geometry.GetLocalSize());
        if(Source.X<=0||Source.Y<=0||Available.X<=0||Available.Y<=0)return Layer;
        const float Scale=FMath::Min(Available.X/Source.X,Available.Y/Source.Y);
        const FVector2f Size=Source*Scale,Offset=(Available-Size)*.5f;
        FSlateDrawElement::MakeBox(Elements,Layer+1,Geometry.ToPaintGeometry(Size,FSlateLayoutTransform(Offset)),Image,ESlateDrawEffect::IgnoreTextureAlpha);
        return Layer+1;
    }
private:
    const FSlateBrush* Image=nullptr;
};

inline TSharedRef<SWidget> SFCInspectionView(const FSlateBrush* Brush){
    return SNew(SOverlay)
        +SOverlay::Slot()[SNew(SSFCInspectionImage).Image(Brush)]
        +SOverlay::Slot().HAlign(HAlign_Left).VAlign(VAlign_Top).Padding(12,8)[
            SNew(SButton).OnClicked_Lambda([]{FPlatformMisc::RequestExit(false);return FReply::Handled();})[
                SNew(STextBlock).Text(FText::FromString(TEXT("Exit (Escape)")))]];
}
