# Fresh supported ships,zero offset,owner-qualified native insertion.
param([ValidateSet('Strict','ExtraFrame')][string]$TimingPolicy='ExtraFrame',[switch]$LegacyStartupWarmup,[switch]$CompletionDiagnostics,[switch]$LightDiagnostics,[switch]$DamageTextures)
$ErrorActionPreference='Stop'
$modern='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
if($PSVersionTable.PSVersion.Major -lt 7){
 $forward=@('-NoProfile','-ExecutionPolicy','Bypass','-File',$PSCommandPath,'-TimingPolicy',$TimingPolicy)
 if($LegacyStartupWarmup){$forward+='-LegacyStartupWarmup'}
 if($CompletionDiagnostics){$forward+='-CompletionDiagnostics'}
 if($LightDiagnostics){$forward+='-LightDiagnostics'}
 if($DamageTextures){$forward+='-DamageTextures'}
 & $modern @forward
 if($LASTEXITCODE -ne 0){throw 'Native multi-ship replacement needs review;evidence retained'}
 return
}
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Import-Module (Join-Path $root 'tools/m0_probe/ProbeRunnerPolicy.psm1') -Force
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
[void](Test-ProbeElevation -IsElevated $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
$python='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$runArgs=@('-B',(Join-Path $root 'tools/remix_runtime/run_return_game.py'),'--execute','--native-insertion-policy',$TimingPolicy,'--native-all-ships','--pipeline-mode','performance','--budget-seconds','285')
if($LegacyStartupWarmup){$runArgs+='--legacy-startup-warmup'}
if($CompletionDiagnostics){$runArgs+='--completion-diagnostics'}
if($LightDiagnostics){$runArgs+='--light-diagnostics'}
if($DamageTextures){$runArgs+='--damage-textures'}
& $python @runArgs
if($LASTEXITCODE -ne 0){throw 'Native multi-ship replacement needs review;copied-install recovery evidence retained'}
