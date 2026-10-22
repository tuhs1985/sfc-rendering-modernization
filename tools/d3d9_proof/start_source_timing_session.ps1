# Run from the already validated elevated testing parent. No additional UAC.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot '../remix_runtime/start_return_image_session.ps1') -SourceTiming
