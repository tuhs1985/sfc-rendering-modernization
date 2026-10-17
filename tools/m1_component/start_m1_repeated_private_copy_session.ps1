# Sponsor-operated only. Inherit an elevated shell; no new UAC workflow.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'start_m1_corner_snapshot_session.ps1') -EnableWrapperObservation -EnablePrivateCopy -EnableRepeatedPrivateCopy
