using UnrealBuildTool;
public class SFCSceneProofEditorTarget : TargetRules
{
    public SFCSceneProofEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("SFCSceneProof");
    }
}
