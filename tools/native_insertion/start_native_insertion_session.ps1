# Default-off F-CA native early insertion comparison. Run from the established elevated parent.
param([Parameter(Mandatory=$true)][ValidateSet('Strict','ExtraFrame')][string]$TimingPolicy)
$ErrorActionPreference='Stop'
$modern='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
if($PSVersionTable.PSVersion.Major -lt 7){
 & $modern -NoProfile -ExecutionPolicy Bypass -File $PSCommandPath -TimingPolicy $TimingPolicy
 if($LASTEXITCODE -ne 0){throw 'Native insertion comparison needs review;evidence retained'}
 return
}
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Import-Module (Join-Path $root 'tools/m0_probe/ProbeRunnerPolicy.psm1') -Force
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
$principal=[Security.Principal.WindowsPrincipal]::new($identity)
[void](Test-ProbeElevation -IsElevated $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
$python='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python -B (Join-Path $root 'tools/remix_runtime/run_return_game.py') --execute --native-insertion-policy $TimingPolicy --pipeline-mode performance --budget-seconds 285
if($LASTEXITCODE -ne 0){throw 'Native insertion comparison needs review;copied-install recovery evidence retained'}
