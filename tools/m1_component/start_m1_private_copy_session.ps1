# Sponsor-operated only; inherited elevation, no unattended launch.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'start_m1_corner_snapshot_session.ps1') -EnableWrapperObservation -EnablePrivateCopy
