using UnrealBuildTool;
public class SFCBridgeRuntime : ModuleRules {
    public SFCBridgeRuntime(ReadOnlyTargetRules Target) : base(Target) {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine" });
        PrivateDependencyModuleNames.AddRange(new[] { "Json", "MeshDescription", "StaticMeshDescription",
            "ProceduralMeshComponent", "RenderCore", "RHI", "Slate", "SlateCore", "InputCore" });
        PrivateDependencyModuleNames.Add("D3D12RHI");
        PublicSystemLibraries.AddRange(new[] { "d3d11.lib", "d3d12.lib", "dxgi.lib" });
    }
}
