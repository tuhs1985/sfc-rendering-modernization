# Metadata-only boundary checkout; original SFC drawing stays enabled.
param()
$ErrorActionPreference='Stop'
$modern='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
if($PSVersionTable.PSVersion.Major -lt 7){
 & $modern -NoProfile -ExecutionPolicy Bypass -File $PSCommandPath
 if($LASTEXITCODE -ne 0){throw 'Native insertion observation needs review;evidence retained'}
 return
}
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Import-Module (Join-Path $root 'tools/m0_probe/ProbeRunnerPolicy.psm1') -Force
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
[void](Test-ProbeElevation -IsElevated $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
'Use your usual F-CA against a different ship. You will see the original game picture only.'
'Play normally: camera changes, weapons/shields, and briefly pause/unpause.'
'Keep the game open until TWO LOW beeps request normal exit; observation and hook removal finish first.'
$python='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python -B (Join-Path $root 'tools/remix_runtime/run_return_game.py') --execute --native-insertion-observe --pipeline-mode performance --budget-seconds 285
if($LASTEXITCODE -ne 0){throw 'Draw-order observation needs review;exit copied SFC normally if open;evidence retained'}
