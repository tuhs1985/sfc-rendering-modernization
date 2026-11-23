#pragma once
#include "CoreMinimal.h"
bool SFCCheckGpuExchange(class UTextureRenderTarget2D* Target,TArray<FColor>& Pixels,FString& Error,const TCHAR* Label=TEXT("colour"),double P22=0,double P23=0,uint32 Owner=0);
