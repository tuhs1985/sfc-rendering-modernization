param([switch]$CheckOnly)
$ErrorActionPreference='Stop'
if($CheckOnly){
 & 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' (Join-Path $PSScriptRoot '../remix_runtime/run_return_game.py') --d3d9-additive --persistent-scene
 if($LASTEXITCODE -ne 0){throw 'Persistent scene preflight failed;no game started'}
 return
}
& (Join-Path $PSScriptRoot '../remix_runtime/start_return_image_session.ps1') -D3D9Additive -PersistentScene
