#Requires -Version 7.0

$ErrorActionPreference = "Stop"

$modulePath = Join-Path $PSScriptRoot "..\tools\m0_probe\ProbeRunnerPolicy.psm1"
Import-Module $modulePath -Force

$failures = 0

function Assert-PolicyResult {
    param(
        [bool]$IsElevated,
        [bool]$ElevateProbeRequested,
        [bool]$Expected
    )

    $actual = Test-ProbeElevation `
        -IsElevated $IsElevated `
        -ElevateProbeRequested $ElevateProbeRequested
    if ($actual -ne $Expected) {
        Write-Error "Expected $Expected for elevated=$IsElevated requested=$ElevateProbeRequested; got $actual."
        $script:failures++
    }
}

Assert-PolicyResult -IsElevated $true -ElevateProbeRequested $false -Expected $false
Assert-PolicyResult -IsElevated $true -ElevateProbeRequested $true -Expected $false
Assert-PolicyResult -IsElevated $false -ElevateProbeRequested $true -Expected $true

try {
    Test-ProbeElevation -IsElevated $false -ElevateProbeRequested $false
    Write-Error "Expected non-elevated execution without the fallback to throw."
    $failures++
} catch {
    if ($_.Exception.Message -notmatch "elevated parent shell") {
        Write-Error "Policy threw an unexpected error: $($_.Exception.Message)"
        $failures++
    }
}

if ($failures -ne 0) {
    throw "$failures probe elevation policy test(s) failed."
}

Write-Output "All probe elevation policy tests passed."
