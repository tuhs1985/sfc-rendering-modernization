# Sponsor-operated only; existing elevated parent, no unattended gameplay.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'start_m1_corner_snapshot_session.ps1') -EnableWrapperObservation -EnablePrivateCopy -EnableSurfaceLighting
