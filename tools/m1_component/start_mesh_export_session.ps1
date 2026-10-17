param([switch]$EnableTextureReferences)
# Prepared opt-in only. Do not launch during offline preparation.
$ErrorActionPreference='Stop'
$visualEntryPath=$PSCommandPath
if($PSVersionTable.PSVersion.Major -lt 7){
    $modern='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
    if(-not (Test-Path -LiteralPath $modern)){throw 'Bundled PowerShell 7 not found.'}
    & $modern -NoProfile -ExecutionPolicy Bypass -File $visualEntryPath -EnableTextureReferences:$EnableTextureReferences
    if($LASTEXITCODE -ne 0){throw "Modern PowerShell workflow failed: $LASTEXITCODE"}
    return
}
Import-Module (Join-Path $PSScriptRoot '..\m0_probe\ProbeRunnerPolicy.psm1') -Force
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
[void](Test-ProbeElevation -IsElevated $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
& (Join-Path $PSScriptRoot 'build_m1_component.ps1')
Write-Output 'READ-ONLY SHIP EXPORT: enter the usual two-ship skirmish. Keep both ships visible initially.'
Write-Output 'Expect NORMAL appearance. No magenta, lighting changes, camera phases or special maneuvers.'
Write-Output 'After capture, the runner also prepares an OBJ for a SEPARATE Remix Toolkit import. Nothing is routed through Remix inside SFC yet.'
Write-Output 'Play normally until TWO exit beeps and the console exit request, about 90 seconds after tactical rendering starts. If cues are inaudible, check the console.'
& (Join-Path $PSScriptRoot 'start_m1_enabled_session.ps1') -MaxSeconds 90 -MaxFrames 120 -MaxEvents 10000 `
    -DisableGeometryHook -EnableWrapperObservation -EnableMeshExport -EnableTextureReferences:$EnableTextureReferences -ContinueAfterBurst -AutomaticArm
