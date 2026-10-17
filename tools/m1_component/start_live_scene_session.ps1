# Fresh assets: run from existing elevated parent; no routine UAC/security changes.
param([string]$LiveChannel='', [switch]$Prepared)
$ErrorActionPreference='Stop'
$visualEntryPath=$PSCommandPath
if($PSVersionTable.PSVersion.Major -lt 7){
    $modernArgs=@('-NoProfile','-ExecutionPolicy','Bypass','-File',$visualEntryPath)
    if($LiveChannel){$modernArgs+=@('-LiveChannel',$LiveChannel)}
    if($Prepared){$modernArgs+='-Prepared'}
    & 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe' @modernArgs
    if($LASTEXITCODE -ne 0){throw "Fresh live scene failed: $LASTEXITCODE"};return
}
Import-Module (Join-Path $PSScriptRoot '..\m0_probe\ProbeRunnerPolicy.psm1') -Force
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
[void](Test-ProbeElevation -IsElevated $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
if($Prepared){
    if($LiveChannel -notmatch '^Local\\SFCBridge_[a-f0-9]{32}$'){throw 'Prepared workflow requires exact channel.'}
    Write-Output 'FRESH SHIP TEST: choose the familiar two-ship skirmish, with different ship classes.'
    Write-Output 'Both ships should appear in the separate view, built from data captured NOW. No prepared Klingon is loaded.'
    Write-Output 'Keep both visible briefly. Change camera angle, then move/turn normally. Lighting is provisional; no special colors.'
    Write-Output 'If a ship is missing or looks wrong, keep SFC safe and report it afterward. Do not guess timestamps.'
    Write-Output 'Exit normally at TWO beeps and the console request, about 90 seconds into tactical play.'
    & (Join-Path $PSScriptRoot 'start_m1_enabled_session.ps1') -MaxSeconds 90 -WaitForClientSeconds 30 -WaitForExitSeconds 30 -ArmTimeoutSeconds 90 `
        -MaxFrames 120 -MaxEvents 10000 -MaxOwners 32 -DisableGeometryHook -EnableWrapperObservation -EnableMeshExport -EnableTextureReferences `
        -ContinueAfterBurst -AutomaticArm -LiveChannel $LiveChannel -FreshScene
    return
}
if($LiveChannel){throw 'Default entry generates the session identifier.'}
& (Join-Path $PSScriptRoot 'build_m1_component.ps1')
& (Join-Path $PSScriptRoot '..\remix_ingest\build_remix_job.ps1')
& 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' (Join-Path $PSScriptRoot '..\remix_ingest\run_live_bridge.py') --fresh-scene
if($LASTEXITCODE -ne 0){throw "Fresh live scene requires review: $LASTEXITCODE"}
