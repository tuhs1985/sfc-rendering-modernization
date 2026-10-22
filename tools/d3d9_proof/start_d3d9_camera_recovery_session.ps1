# Dedicated alive camera-away/back check;uses unchanged elevated-parent workflow.
param([switch]$CheckOnly)
$ErrorActionPreference='Stop'
if($CheckOnly){
 $python='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
 & $python (Join-Path $PSScriptRoot '../remix_runtime/run_return_game.py') --d3d9-additive --camera-recovery
 if($LASTEXITCODE -ne 0){throw 'Camera-return preflight failed;no game launched'}
 return
}
& (Join-Path $PSScriptRoot '../remix_runtime/start_return_image_session.ps1') -D3D9Additive -CameraRecovery
