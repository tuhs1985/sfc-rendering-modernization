#pragma once
#include "CoreMinimal.h"
// Optional, bounded standalone receipts; no native gameplay orchestration.
class FSFCRegistryCheck {
public:
    bool Start(const FString& Filename,FString& Error);
    bool Tick(class USFCSessionSubsystem* Session,class USFCWorldSubsystem* World,
        const struct FSFCSourceSnapshot& Snapshot,const FString& Output,bool& Finished,bool& Restart,FString& Error);
private:
    TArray<TSharedPtr<class FJsonValue>> Steps;
    FString LastWait;
};
