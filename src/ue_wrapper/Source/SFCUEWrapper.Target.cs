using UnrealBuildTool;
public class SFCUEWrapperTarget : TargetRules {
    public SFCUEWrapperTarget(TargetInfo Target) : base(Target) {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("SFCUEWrapper");
    }
}
