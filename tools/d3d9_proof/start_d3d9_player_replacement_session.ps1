# Separate opt-in checkout. Never changes the tuning/offset configuration files.
param()
$ErrorActionPreference='Stop'
$modern='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
if($PSVersionTable.PSVersion.Major -lt 7){
 & $modern -NoProfile -ExecutionPolicy Bypass -File $PSCommandPath
 if($LASTEXITCODE -ne 0){throw 'Player replacement checkout needs review;evidence retained'}
 return
}
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Import-Module (Join-Path $root 'tools/m0_probe/ProbeRunnerPolicy.psm1') -Force
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
[void](Test-ProbeElevation -IsElevated $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
$python='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python (Join-Path $root 'tools/remix_runtime/run_return_game.py') --execute --multi-ship --async-material-checkout --player-replacement --pipeline-mode performance --budget-seconds 285
if($LASTEXITCODE -ne 0){throw 'Player replacement needs review;exit copied SFC normally if still open;evidence retained'}
