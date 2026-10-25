param([switch]$CheckOnly)
$ErrorActionPreference='Stop'
$modern='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
if($PSVersionTable.PSVersion.Major -lt 7){
 $forward=@('-NoProfile','-ExecutionPolicy','Bypass','-File',$PSCommandPath)
 if($CheckOnly){$forward+='-CheckOnly'}
 & $modern @forward
 if($LASTEXITCODE -ne 0){throw 'Effects observation needs review;evidence retained'}
 return
}
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Import-Module (Join-Path $root 'tools/m0_probe/ProbeRunnerPolicy.psm1') -Force
if(-not $CheckOnly){
 $who=[Security.Principal.WindowsIdentity]::GetCurrent()
 $principal=[Security.Principal.WindowsPrincipal]::new($who)
 [void](Test-ProbeElevation -IsElevated $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
}
$python='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
Push-Location $root
try{
 $params=@('-B',(Join-Path $PSScriptRoot 'run_probe.py'))
 if(-not $CheckOnly){$params+='--execute'}
 & $python @params
 if($LASTEXITCODE -ne 0){throw 'Effects observation needs review;exit copied SFC normally if still open'}
}finally{Pop-Location}
