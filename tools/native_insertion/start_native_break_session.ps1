# Default-off destruction checkout; existing ExtraFrame timing and appearance.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'start_native_multiship_session.ps1') -BreakModels -TimedTest
if($LASTEXITCODE -ne 0){throw 'Native debris checkout needs review;evidence retained'}
