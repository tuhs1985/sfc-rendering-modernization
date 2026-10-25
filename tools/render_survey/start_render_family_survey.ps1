param([switch]$CheckOnly)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$python='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
Push-Location $root
try {
 if(-not $CheckOnly){Write-Host 'Expanded survey: up to2GiB total;light changes and effects-type census included. No model/image contents and no Remix renderer.'}
 $argsList=@('-B',(Join-Path $PSScriptRoot 'run_survey.py'))
 if(-not $CheckOnly){$argsList+='--execute'}
 & $python @argsList
 if($LASTEXITCODE -ne 0){throw 'Rendering survey needs review;preserve evidence and exit copied SFC normally if still open'}
} finally {Pop-Location}
