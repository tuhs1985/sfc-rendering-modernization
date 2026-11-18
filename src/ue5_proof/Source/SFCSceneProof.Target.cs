using UnrealBuildTool;
public class SFCSceneProofTarget : TargetRules
{
    public SFCSceneProofTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("SFCSceneProof");
    }
}
