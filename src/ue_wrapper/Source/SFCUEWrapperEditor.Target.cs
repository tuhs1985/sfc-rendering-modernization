using UnrealBuildTool;
public class SFCUEWrapperEditorTarget : TargetRules {
    public SFCUEWrapperEditorTarget(TargetInfo Target) : base(Target) {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("SFCUEWrapper");
    }
}
