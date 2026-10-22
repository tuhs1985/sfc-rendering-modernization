# No game launch until offline source/binary qualification exists and matches.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot '../remix_runtime/start_return_image_session.ps1') -LiveOwnerTiming
