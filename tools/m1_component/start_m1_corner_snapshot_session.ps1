# Read-only diagnostic; inherit elevated parent, never request UAC.
param([switch]$EnableWrapperObservation,[switch]$EnablePrivateCopy,[switch]$EnableRepeatedPrivateCopy,[switch]$EnableCopyEpochRequalification,[switch]$EnableSurfaceLighting)
$ErrorActionPreference = 'Stop'
$visualEntryPath = $PSCommandPath
if ($PSVersionTable.PSVersion.Major -lt 7) {
    $modernPowerShell = 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
    if (-not (Test-Path -LiteralPath $modernPowerShell)) { throw 'Bundled PowerShell 7 not found.' }
    & $modernPowerShell -NoProfile -ExecutionPolicy Bypass -File $visualEntryPath -EnableWrapperObservation:$EnableWrapperObservation -EnablePrivateCopy:$EnablePrivateCopy -EnableRepeatedPrivateCopy:$EnableRepeatedPrivateCopy -EnableCopyEpochRequalification:$EnableCopyEpochRequalification -EnableSurfaceLighting:$EnableSurfaceLighting
    if ($LASTEXITCODE -ne 0) { throw "Modern PowerShell workflow failed: $LASTEXITCODE" }
    return
}
$toolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module (Join-Path $toolRoot '..\m0_probe\ProbeRunnerPolicy.psm1') -Force
$principal = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
[void](Test-ProbeElevation -IsElevated $principal.IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
& (Join-Path $toolRoot 'build_m1_component.ps1')
if($EnableSurfaceLighting){
    Write-Output 'LIGHTING TEST: ONE beep means20s setup. TWO beeps release identification: one ship turns magenta for20s so you can find it and put the camera on it.'
    Write-Output 'That SAME ship returns to normal color for5s, then THREE beeps mark15s of altered lighting. FOUR beeps mean original rendering restored.'
    Write-Output 'Keep the marked ship visible. Do NOT deliberately look away. No target tracking changes required. Report whether lighting changed after magenta cleared and returned to normal afterward.'
}elseif($EnablePrivateCopy){
    Write-Output 'Normal appearance throughout; no magenta or shading change.'
    if($EnableCopyEpochRequalification){
        Write-Output 'FRESH IDENTITY TEST: up to 32 fresh copies, at most one per second. Keep both ships visible EXCEPT during the requested third-cue look-away.'
    }elseif($EnableRepeatedPrivateCopy){
        Write-Output 'REPEATED COPY TEST: up to 32 fresh copies, at most one per second. Keep both ships visible during the test; small camera movements and gentle ship movement are fine.'
    }
    Write-Output 'COPY TEST: one beep means setup; keep both ships visible, stay at rest and hold camera.'
    if($EnableCopyEpochRequalification){
        Write-Output 'After 20 seconds, TWO beeps: small camera moves and gentle ship movement, both ships visible.'
        Write-Output 'At THREE beeps (40 seconds): point a FREE camera away from BOTH ships for about 5 seconds, then bring them back. No target tracking. If the camera cannot do this, report that afterward.'
        Write-Output 'Keep both ships visible after returning; expect normal appearance. Wait for the exit request.'
    }elseif($EnableRepeatedPrivateCopy){
        Write-Output 'After 20 seconds, two beeps mean copies begin. Keep both ships visible; gently move/turn and use small camera movements until asked to exit. Expect no visual change.'
    }else{
        Write-Output 'After 20 seconds, two beeps mean the one-use copy test begins. Then play normally until asked to exit. Expect no visual change.'
    }
}else{
Write-Output 'Normal appearance throughout; no magenta or shading change.'
Write-Output 'DISABLE TARGET TRACKING before the observation phases; use a non-following camera if available. Report any remaining camera limits.'
Write-Output 'KEEP BOTH SHIPS VISIBLE throughout. Use small camera rotations; zoom out if necessary.'
Write-Output 'One beep: leave your ship at rest and hold camera. Two beeps (15s): small camera rotation only.'
Write-Output 'Three beeps (30s): hold camera angle, accelerate and gently turn your ship; keep both in view.'
Write-Output 'If cues cannot be heard, report that afterward; do not guess timestamps.'
}
Write-Output 'Keep playing until the runner asks you to exit normally.'
& (Join-Path $toolRoot 'start_m1_enabled_session.ps1') -MaxSeconds 90 `
    -MaxFrames 120 -MaxEvents 10000 -DisableGeometryHook -EnableCornerSnapshot `
    -EnableWrapperObservation:$EnableWrapperObservation `
    -EnablePrivateCopy:$EnablePrivateCopy `
    -EnableRepeatedPrivateCopy:$EnableRepeatedPrivateCopy `
    -EnableCopyEpochRequalification:$EnableCopyEpochRequalification `
    -EnableSurfaceLighting:$EnableSurfaceLighting `
    -ContinueAfterBurst -AutomaticArm
