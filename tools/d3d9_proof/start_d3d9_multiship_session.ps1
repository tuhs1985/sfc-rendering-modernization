# Configured camera-left fresh retained models. No original ship suppression.
param([ValidateSet('Performance','Test')][string]$Mode='Performance',[switch]$StartupProfile,[switch]$ExperimentalParallelAssets,[switch]$AsyncMaterialCheckout,[switch]$Tuning)
$ErrorActionPreference='Stop'
$modern='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
if($PSVersionTable.PSVersion.Major -lt 7){
 $forward=@('-NoProfile','-ExecutionPolicy','Bypass','-File',$PSCommandPath,'-Mode',$Mode)
 if($StartupProfile){$forward+='-StartupProfile'}
 if($ExperimentalParallelAssets){$forward+='-ExperimentalParallelAssets'}
 if($AsyncMaterialCheckout){$forward+='-AsyncMaterialCheckout'}
 if($Tuning){$forward+='-Tuning'}
 & $modern @forward
 if($LASTEXITCODE -ne 0){throw 'Multi-ship workflow needs review;evidence retained'}
 return
}
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Import-Module (Join-Path $root 'tools/m0_probe/ProbeRunnerPolicy.psm1') -Force
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
$principal=[Security.Principal.WindowsPrincipal]::new($identity)
[void](Test-ProbeElevation -IsElevated $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
$python='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$oldStartupProfile=$env:SFC_D3D9_STARTUP_PROFILE
try{
 $env:SFC_D3D9_STARTUP_PROFILE=if($StartupProfile){'1'}else{$null}
 $runArguments=@((Join-Path $root 'tools/remix_runtime/run_return_game.py'),'--execute','--multi-ship','--pipeline-mode',$Mode.ToLowerInvariant(),'--budget-seconds','285')
 if($ExperimentalParallelAssets){$runArguments+='--experimental-parallel-assets'}
 if($AsyncMaterialCheckout){$runArguments+='--async-material-checkout'}
 if($Tuning){if($Mode -ne 'Performance' -or $ExperimentalParallelAssets){throw 'Tuning requires the current performance baseline'};$runArguments+='--light-tuning';if(-not $AsyncMaterialCheckout){$runArguments+='--async-material-checkout'}}
 & $python @runArguments
 if($LASTEXITCODE -ne 0){throw 'Multi-ship returned overlay needs review;original installation untouched by runner'}
}finally{$env:SFC_D3D9_STARTUP_PROFILE=$oldStartupProfile}
