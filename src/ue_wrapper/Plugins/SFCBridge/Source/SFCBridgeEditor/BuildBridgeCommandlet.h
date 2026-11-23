#pragma once
#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "BuildBridgeCommandlet.generated.h"

UCLASS()
class UBuildBridgeCommandlet : public UCommandlet
{
    GENERATED_BODY()
public:
    virtual int32 Main(const FString& Params) override;
};
