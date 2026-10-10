# Run from the established, scoped elevated analyst parent shell. This entry
# point refuses to request a new UAC prompt and does not change security policy.
param()
$ErrorActionPreference = 'Stop'
$visualEntryPath = $PSCommandPath
# Windows PowerShell 5.1 lacks ProcessStartInfo.ArgumentList. Re-execute only
# this entry point in the installed modern runtime, inheriting the parent token.
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
$elevated = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
[void](Test-ProbeElevation -IsElevated $elevated -ElevateProbeRequested $false)
& (Join-Path $toolRoot 'start_m1_enabled_session.ps1') `
    -MaxSeconds 60 -MaxFrames 3000 -MaxEvents 50000 `
    -DisableGeometryHook -EnableVisualTint -AutomaticArm
