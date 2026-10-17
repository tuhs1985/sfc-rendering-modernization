$ErrorActionPreference='Stop'
$runner=Join-Path $PSScriptRoot '../tools/m1_component/run_m1_increment_a.ps1'
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($runner,[ref]$tokens,[ref]$errors)
if($errors.Count){throw 'Runner parse failure'}
$validation=$ast.FindAll({param($node)
    $node -is [Management.Automation.Language.IfStatementAst] -and
    $node.Extent.Text.StartsWith('if ($Endurance -and ($Mode')},$true) | Select-Object -First 1
$gateBlock=$ast.FindAll({param($node)
    $node -is [Management.Automation.Language.IfStatementAst] -and
    $node.Extent.Text.StartsWith('if ($Endurance -and -not $enduranceGateAt')},$true) | Select-Object -First 1
if(-not $validation -or -not $gateBlock){throw 'Production endurance blocks missing'}
$Endurance=$true;$Mode='enabled';$MaxSeconds=1830;$DisableGeometryHook=$true
$ContinueAfterBurst=$true;$MaxFrames=120;$MaxEvents=10000
$EnableVisualTint=$false;$EnableShadingOff=$false;$EnableCornerSnapshot=$false
$EnableWrapperObservation=$false;$EnablePrivateCopy=$false;$EnableRepeatedPrivateCopy=$false
$EnableCopyEpochRequalification=$false;$EnableSurfaceLighting=$false
. ([scriptblock]::Create($validation.Extent.Text))
foreach($setting in @('EnableVisualTint','EnableShadingOff','EnableCornerSnapshot',
    'EnableWrapperObservation','EnablePrivateCopy','EnableRepeatedPrivateCopy',
    'EnableCopyEpochRequalification','EnableSurfaceLighting')){
    Set-Variable -Name $setting -Value $true
    $rejected=$false
    try{. ([scriptblock]::Create($validation.Extent.Text))}catch{$rejected=$true}
    Set-Variable -Name $setting -Value $false
    if(-not $rejected){throw "Endurance accepted unsafe setting $setting"}
}
$MaxSeconds=90;$rejected=$false
try{. ([scriptblock]::Create($validation.Extent.Text))}catch{$rejected=$true}
if(-not $rejected){throw 'Short duration admitted as formal endurance'}
$MaxSeconds=1830
foreach($bad in @(@{Name='DisableGeometryHook';Value=$false;Original=$true},
    @{Name='ContinueAfterBurst';Value=$false;Original=$true},
    @{Name='Mode';Value='disabled';Original='enabled'},
    @{Name='MaxFrames';Value=6000;Original=120},
    @{Name='MaxEvents';Value=50000;Original=10000})){
    Set-Variable -Name $bad.Name -Value $bad.Value
    $rejected=$false
    try{. ([scriptblock]::Create($validation.Extent.Text))}catch{$rejected=$true}
    Set-Variable -Name $bad.Name -Value $bad.Original
    if(-not $rejected){throw "Invalid endurance configuration accepted: $($bad.Name)"}
}
$game=@{Id=42};$controllerJob=@{HasExited=$false};$metadata=[ordered]@{}
$enduranceGateAt=$null;$measurementFailure=$null;$measurementJobs=@()
$script:startCount=0;$runDir='unused';$PythonExecutable='fixture'
function Start-M1MeasurementJobs {param($TargetProcessId,$Seconds,$OutputDirectory,$PythonExecutable)
    if($TargetProcessId -ne 42 -or $Seconds -ne 1800){throw 'Wrong collector window/PID'}
    $script:startCount++;[pscustomobject]@{Name='fixture'}
}
function Set-Content {param($LiteralPath,$Encoding,[Parameter(ValueFromPipeline)]$Value)
    process{if(-not $Value){throw 'Missing gate metadata'}}
}
$enduranceGate=[Threading.EventWaitHandle]::new($false,[Threading.EventResetMode]::ManualReset)
try{
    . ([scriptblock]::Create($gateBlock.Extent.Text))
    if($script:startCount -ne 0){throw 'Measurement started before tactical gate'}
    [void]$enduranceGate.Set()
    . ([scriptblock]::Create($gateBlock.Extent.Text))
    . ([scriptblock]::Create($gateBlock.Extent.Text))
    if($script:startCount -ne 1 -or -not $enduranceGateAt -or $measurementFailure){throw 'Gate did not start exactly once'}
}finally{$enduranceGate.Dispose()}
Write-Output 'M1 endurance policy and production gate tests passed; no SFC launched.'
