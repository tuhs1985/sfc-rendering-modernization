using UnrealBuildTool;
public class SFCBridgeEditor : ModuleRules {
    public SFCBridgeEditor(ReadOnlyTargetRules Target) : base(Target) {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PrivateDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "UnrealEd" });
    }
}
