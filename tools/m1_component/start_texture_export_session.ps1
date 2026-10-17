# Explicit opt-in; same fixture, gate and cleanup as the accepted read-only export.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'start_mesh_export_session.ps1') -EnableTextureReferences
