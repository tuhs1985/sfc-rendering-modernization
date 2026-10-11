# Inherit the established elevated parent; never request UAC or change policy.
param()
$ErrorActionPreference = 'Stop'
$visualEntryPath = $PSCommandPath
if ($PSVersionTable.PSVersion.Major -lt 7) {
    $modernPowerShell = 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
    if (-not (Test-Path -LiteralPath $modernPowerShell)) {
        throw "PowerShell 7 runtime is required but was not found: $modernPowerShell"
    }
    & $modernPowerShell -NoProfile -ExecutionPolicy Bypass -File $visualEntryPath
    if ($LASTEXITCODE -ne 0) { throw "Modern PowerShell workflow failed with exit code $LASTEXITCODE." }
    return
}
$toolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module (Join-Path $toolRoot '..\m0_probe\ProbeRunnerPolicy.psm1') -Force
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
[void](Test-ProbeElevation -IsElevated $principal.IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
& (Join-Path $toolRoot 'build_m1_component.ps1')
Write-Output 'Two-ship skirmish: watch both ships. After 5 seconds one is magenta for 3 seconds.'
Write-Output 'That ship returns to normal for 5 seconds, then its inspected lighting is off for 45 seconds.'
Write-Output 'It returns to normal automatically. Keep playing until the runner asks you to exit normally.'
& (Join-Path $toolRoot 'start_m1_enabled_session.ps1') `
    -MaxSeconds 75 -MaxFrames 120 -MaxEvents 10000 -DisableGeometryHook `
    -EnableShadingOff -ContinueAfterBurst -AutomaticArm
