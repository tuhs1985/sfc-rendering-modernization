using UnrealBuildTool;
public class SFCBridgeRuntime : ModuleRules {
    public SFCBridgeRuntime(ReadOnlyTargetRules Target) : base(Target) {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine" });
        PrivateDependencyModuleNames.AddRange(new[] { "Json", "MeshDescription", "StaticMeshDescription",
            "ProceduralMeshComponent", "RenderCore", "RHI", "Slate", "SlateCore", "InputCore" });
        PrivateDependencyModuleNames.Add("D3D12RHI");
        PrivateIncludePaths.Add(System.IO.Path.GetFullPath(System.IO.Path.Combine(ModuleDirectory,"../../../../../rendering/ue")));
        PrivateIncludePaths.Add(System.IO.Path.GetFullPath(System.IO.Path.Combine(ModuleDirectory,"../../../../../transport")));
        bEnableExceptions = true; // Contain recoverable Windows IPC admission failures.
        PublicSystemLibraries.AddRange(new[] { "d3d11.lib", "d3d12.lib", "dxgi.lib", "advapi32.lib", "ole32.lib" });
    }
}
