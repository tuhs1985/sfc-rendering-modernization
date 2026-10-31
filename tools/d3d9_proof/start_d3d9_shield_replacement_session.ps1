# Separate opt-in shield checkout. Existing replacement/tuning launchers remain.
param()
$ErrorActionPreference='Stop'
$modern='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
if($PSVersionTable.PSVersion.Major -lt 7){
 & $modern -NoProfile -ExecutionPolicy Bypass -File $PSCommandPath
 if($LASTEXITCODE -ne 0){throw 'Shield replacement checkout needs review;evidence retained'}
 return
}
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Import-Module (Join-Path $root 'tools/m0_probe/ProbeRunnerPolicy.psm1') -Force
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
[void](Test-ProbeElevation -IsElevated $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
'Use your F-CA against a different ship. Stay still briefly, then let the enemy hit your shields.'
'Look for shields covering the ship normally. Rotate the camera, move/turn, and switch away and back.'
'Current appearance settings; no offset, magenta or on/off sequence. Exit normally when requested.'
$python='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python (Join-Path $root 'tools/remix_runtime/run_return_game.py') --execute --multi-ship --async-material-checkout --player-replacement --native-foreground --pipeline-mode performance --budget-seconds 285
if($LASTEXITCODE -ne 0){throw 'Shield checkout needs review;exit copied SFC normally if still open;evidence retained'}
