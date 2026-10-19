# First-pass normal90s wiring check. Longer tuning remains gated by review.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'start_return_image_session.ps1') -LightWiring
