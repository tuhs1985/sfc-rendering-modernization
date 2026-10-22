# Separate diagnostic copy of the accepted offset-ship entry; normal entry unchanged.
param([switch]$CheckOnly)
$ErrorActionPreference='Stop'
if($CheckOnly){
 $python='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
 & $python (Join-Path $PSScriptRoot '../remix_runtime/run_return_game.py') --d3d9-additive --lifecycle-capture
 if($LASTEXITCODE -ne 0){throw 'Lifecycle preflight failed;no game launched'}
 return
}
& (Join-Path $PSScriptRoot '../remix_runtime/start_return_image_session.ps1') -D3D9Additive -LifecycleCapture
