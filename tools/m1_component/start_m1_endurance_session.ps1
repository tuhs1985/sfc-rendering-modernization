$ErrorActionPreference = 'Stop'
$visualEntryPath = $MyInvocation.MyCommand.Path
if ($PSVersionTable.PSVersion.Major -lt 7) {
    $modern = 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
    if (-not (Test-Path -LiteralPath $modern)) { throw 'Required modern PowerShell runtime missing' }
    & $modern -NoProfile -ExecutionPolicy Bypass -File $visualEntryPath
    if ($LASTEXITCODE) { throw "Endurance workflow failed: $LASTEXITCODE" }
    return
}
Import-Module (Join-Path $PSScriptRoot '../m0_probe/ProbeRunnerPolicy.psm1') -Force
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
[void](Test-ProbeElevation -IsElevated $principal.IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
if (Get-Process -Name StarFleetOP -ErrorAction SilentlyContinue) { throw 'Exit SFC normally before starting the endurance workflow.' }
$tool=Join-Path $PSScriptRoot '../../artifacts/m1/tools/PresentMon-2.3.1-x64.exe'
if ((Get-FileHash -LiteralPath $tool -Algorithm SHA256).Hash -ne
    '364E5D98D4D134BD54DD25C22ED2CA2F4883F8BC3ED6502BEE0C151E3436D30C') { throw 'Pinned measurement tool missing/mismatched' }
& (Join-Path $PSScriptRoot 'build_m1_component.ps1')
Write-Output 'NEUTRAL ENDURANCE: normal appearance, no magenta or lighting changes.'
Write-Output 'Use the usual two-ship choices if possible. Keep one tactical mission running for at least30 minutes; play normally, no camera choreography.'
Write-Output 'The clock starts automatically in tactical play. Do not count menu time or start another battle to make up time.'
Write-Output 'If the mission ends early or you notice a problem, report that; exit safely if needed. Do not force a failing game to keep running.'
Write-Output 'Wait for the exit request/two long beeps at the end (about30minutes30seconds), then exit SFC normally. Keep this runner open.'
& (Join-Path $PSScriptRoot 'start_m1_enabled_session.ps1') -MaxSeconds 1830 `
    -MaxFrames 120 -MaxEvents 10000 -DisableGeometryHook -ContinueAfterBurst -AutomaticArm -Endurance
