using UnrealBuildTool;
public class SFCUEWrapper : ModuleRules {
    public SFCUEWrapper(ReadOnlyTargetRules Target) : base(Target) {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "SFCBridgeRuntime" });
    }
}
