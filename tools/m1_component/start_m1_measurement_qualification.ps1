$ErrorActionPreference = 'Stop'
$visualEntryPath = $MyInvocation.MyCommand.Path
if ($PSVersionTable.PSVersion.Major -lt 7) {
    $modern = 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
    if (-not (Test-Path -LiteralPath $modern)) { throw 'Required modern PowerShell runtime missing' }
    & $modern -NoProfile -ExecutionPolicy Bypass -File $visualEntryPath
    if ($LASTEXITCODE -ne 0) { throw "Measurement workflow failed: $LASTEXITCODE" }
    return
}
Import-Module (Join-Path $PSScriptRoot '../m0_probe/ProbeRunnerPolicy.psm1') -Force
$principal = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
[void](Test-ProbeElevation -IsElevated $principal.IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
Write-Output 'MEASUREMENT CHECK ONLY: appearance stays normal. Enter your usual two-ship skirmish and play normally.'
Write-Output 'No camera choreography or timestamps needed. The automatic gate starts a short measurement after tactical entry.'
Write-Output 'Wait until the runner asks you to exit SFC normally. This is not the 30-minute endurance run.'
& (Join-Path $PSScriptRoot 'run_m1_disabled_baseline.ps1') -LaunchSfc -GateMode Auto `
    -CaptureSeconds 10 -CaptureMetrics
