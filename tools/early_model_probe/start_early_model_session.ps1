param([switch]$CheckOnly)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$python='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
Push-Location $root
try {
 $taskArgs=@('-B',(Join-Path $PSScriptRoot 'run_probe.py'))
 if(-not $CheckOnly){$taskArgs+='--execute'}
 & $python @taskArgs
 if($LASTEXITCODE -ne 0){throw 'Early-model observation needs review;evidence retained;original drawing unchanged'}
} finally {Pop-Location}
