# Run from the established elevated parent; never requests routine UAC.
param([string]$LiveChannel='', [switch]$Prepared)
$ErrorActionPreference='Stop'
if($PSVersionTable.PSVersion.Major -lt 7){
    $modernArgs=@('-NoProfile','-ExecutionPolicy','Bypass','-File',$PSCommandPath)
    if($LiveChannel){$modernArgs+=@('-LiveChannel',$LiveChannel)}
    if($Prepared){$modernArgs+='-Prepared'}
    & 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe' @modernArgs
    if($LASTEXITCODE -ne 0){throw "Live bridge workflow failed: $LASTEXITCODE"};return
}
Import-Module (Join-Path $PSScriptRoot '..\m0_probe\ProbeRunnerPolicy.psm1') -Force
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
[void](Test-ProbeElevation -IsElevated $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
if($Prepared){
    if($LiveChannel -notmatch '^Local\\SFCBridge_[a-f0-9]{32}$'){throw 'Prepared live session requires exact channel name.'}
    Write-Output 'The separate window uses the SFC camera, but shows ONLY the selected Klingon ship, possibly the enemy.'
    Write-Output 'Angle, zoom and position within the tactical view should agree; background, HUD and other ships are not copied.'
    Write-Output 'Initially hold still, then move the game camera and zoom while keeping the Klingon visible. Play normally afterward.'
    Write-Output 'No separate view buttons are needed. If the Klingon leaves the game camera, it should leave the separate view too.'
    Write-Output 'Exit SFC normally after TWO exit beeps and the console request. No manual timestamps needed.'
    & (Join-Path $PSScriptRoot 'start_m1_enabled_session.ps1') -MaxSeconds 90 -WaitForClientSeconds 30 -WaitForExitSeconds 30 -ArmTimeoutSeconds 90 `
        -MaxFrames 120 -MaxEvents 10000 -DisableGeometryHook -EnableWrapperObservation -EnableMeshExport -EnableTextureReferences `
        -ContinueAfterBurst -AutomaticArm -LiveChannel $LiveChannel
    return
}
if($LiveChannel){throw 'Use the default entry; session identifiers are generated automatically.'}
& (Join-Path $PSScriptRoot 'build_m1_component.ps1')
& (Join-Path $PSScriptRoot '..\remix_ingest\build_remix_job.ps1')
& 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' (Join-Path $PSScriptRoot '..\remix_ingest\run_live_bridge.py')
if($LASTEXITCODE -ne 0){throw "Live bridge requires review: $LASTEXITCODE"}
