# Explicit long, low-recording mode. Exit SFC normally when finished.
$ErrorActionPreference='Stop'
Write-Host 'CURRENT D3D9 / Remix 1.6.1 live tuning. Your rendering.toml and lights.toml are used; no factory reset.'
& (Join-Path $PSScriptRoot '../d3d9_proof/start_d3d9_multiship_session.ps1') -Tuning
