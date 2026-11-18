using UnrealBuildTool;
public class SFCSceneProof : ModuleRules
{
    public SFCSceneProof(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] {
            "Core", "CoreUObject", "Engine", "InputCore", "ProceduralMeshComponent",
            "Json", "RenderCore", "RHI", "Slate", "SlateCore"
        });
        if (Target.bBuildEditor)
        {
            PrivateDependencyModuleNames.AddRange(new[] { "UnrealEd" });
        }
    }
}
