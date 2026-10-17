# Explicit opt-in; never launched automatically by preparation.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'start_m1_corner_snapshot_session.ps1') -EnableWrapperObservation
