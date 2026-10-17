# Sponsor-operated only. Inherit the existing elevated parent.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'start_m1_corner_snapshot_session.ps1') -EnableWrapperObservation -EnablePrivateCopy -EnableRepeatedPrivateCopy -EnableCopyEpochRequalification
