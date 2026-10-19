# Explicit long, low-recording mode. Exit SFC normally when finished.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'start_return_image_session.ps1') -LightTuning
