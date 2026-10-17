# Execute only extracted policy/parameter blocks, never launch the runner.
$ErrorActionPreference='Stop'
$root=Join-Path $PSScriptRoot '../tools/m1_component'
$Mode='enabled';$MaxSeconds=90;$EnableMeshExport=$true;$EnableWrapperObservation=$true
$DisableGeometryHook=$true;$ContinueAfterBurst=$true
$EnableCornerSnapshot=$EnablePrivateCopy=$EnableRepeatedPrivateCopy=$false
$EnableCopyEpochRequalification=$EnableSurfaceLighting=$EnableShadingOff=$EnableVisualTint=$Endurance=$false
foreach($name in @('run_m1_increment_a.ps1','start_m1_enabled_session.ps1')){
    $tokens=$null;$errors=$null
    $ast=[Management.Automation.Language.Parser]::ParseFile((Join-Path $root $name),[ref]$tokens,[ref]$errors)
    if($errors.Count){throw "$name parse failed"}
    $block=$ast.FindAll({param($node) $node -is [Management.Automation.Language.IfStatementAst] -and
        $node.Extent.Text.StartsWith('if($EnableMeshExport -and')},$true) | Select-Object -First 1
    if(-not $block){throw "$name mesh validation missing"}
    if($name -eq 'run_m1_increment_a.ps1'){
        $conversion=$ast.FindAll({param($node) $node -is [Management.Automation.Language.CommandAst] -and
            $node.Extent.Text -match "'export_mesh_obj.py'"},$true) | Select-Object -First 1
        if(-not $conversion -or -not $conversion.Extent.Text.Contains('--receipt') -or
            -not $conversion.Extent.Text.Contains('--output')){throw 'Validated OBJ conversion forwarding missing'}
    }
    . ([scriptblock]::Create($block.Extent.Text))
    foreach($bad in @(@{n='DisableGeometryHook';v=$false;o=$true},@{n='ContinueAfterBurst';v=$false;o=$true},
        @{n='EnableWrapperObservation';v=$false;o=$true},@{n='MaxSeconds';v=300;o=90},
        @{n='EnableVisualTint';v=$true;o=$false},@{n='EnablePrivateCopy';v=$true;o=$false},
        @{n='EnableCornerSnapshot';v=$true;o=$false},@{n='EnableShadingOff';v=$true;o=$false})){
        Set-Variable $bad.n $bad.v
        $rejected=$false
        try{. ([scriptblock]::Create($block.Extent.Text))}catch{$rejected=$true}
        Set-Variable $bad.n $bad.o
        if(-not $rejected){throw "$name admitted unsafe $($bad.n)"}
    }
}
$tokens=$null;$errors=$null
$entry=[Management.Automation.Language.Parser]::ParseFile((Join-Path $root 'start_mesh_export_session.ps1'),[ref]$tokens,[ref]$errors)
if($errors.Count){throw 'Entry parse failed'}
$call=$entry.FindAll({param($node) $node -is [Management.Automation.Language.CommandAst] -and
    $node.Extent.Text -match 'start_m1_enabled_session.ps1'},$true) | Select-Object -First 1
if(-not $call){throw 'Entry forwarding missing'}
foreach($required in @('-MaxSeconds 90','-DisableGeometryHook','-EnableWrapperObservation','-EnableMeshExport','-ContinueAfterBurst','-AutomaticArm')){
    if(-not $call.Extent.Text.Contains($required)){throw "Missing entry argument $required"}
}
Write-Output 'Mesh workflow policy/forwarding checks passed; no game launched.'
