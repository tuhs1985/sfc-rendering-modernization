# Prepared read-only light discovery;uses established elevated-parent workflow.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'start_return_image_session.ps1') -CaptureNativeLights
