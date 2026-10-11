param(
    [ValidateSet("disabled", "enabled")]
    [string]$Mode = "enabled",

    [ValidateRange(5, 2100)]
    [int]$MaxSeconds = 300,

    [ValidateRange(30, 900)]
    [int]$WaitForClientSeconds = 600,

    [ValidateRange(30, 900)]
    [int]$WaitForExitSeconds = 600,

    [ValidateRange(1, 6000)]
    [int]$MaxFrames = 120,

    [ValidateRange(1, 100000)]
    [int]$MaxEvents = 10000,

    [ValidateRange(0, 8)]
    [int]$GeometrySamplesPerOwnerFrame = 1,

    [ValidateRange(0, 8)]
    [int]$UncorrelatedGeometrySamplesPerFrame = 1,

    [switch]$DisableGeometryHook,

    [switch]$EnableVisualTint,
    [switch]$EnableShadingOff,

    [ValidateRange(30, 900)][int]$GateTimeoutSeconds = 600,

    [string]$PythonExecutable = 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe',

    [int]$TargetPid = 0,

    [switch]$ContinueAfterBurst
)

$ErrorActionPreference = "Stop"
if ($EnableShadingOff -and ($EnableVisualTint -or $Mode -ne 'enabled' -or
    -not $DisableGeometryHook -or -not $ContinueAfterBurst -or $MaxSeconds -lt 75 -or $MaxSeconds -gt 90)) {
    throw 'Shading diagnostic requires enabled mode, geometry off, no tint mode, ContinueAfterBurst and 75-90 seconds.'
}
if ($EnableVisualTint -and ($Mode -ne 'enabled' -or -not $DisableGeometryHook)) {
    throw 'Visual tint requires enabled mode with the geometry hook disabled.'
}
if ($Mode -eq 'enabled' -and -not (Test-Path -LiteralPath $PythonExecutable)) {
    throw "Configured Python runtime was not found: $PythonExecutable"
}

$toolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Resolve-Path (Join-Path $toolRoot "..\..")
Import-Module (Join-Path $workspaceRoot "tools\m0_probe\ProbeRunnerPolicy.psm1") -Force
Import-Module (Join-Path $toolRoot "ProcessImagePath.psm1") -Force

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
$isElevated = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($Mode -eq "enabled") {
    [void](Test-ProbeElevation -IsElevated $isElevated -ElevateProbeRequested $false)
}

$binDir = Join-Path $workspaceRoot "artifacts\m1\bin"
$controller = Join-Path $binDir "m1_controller.exe"
$component = Join-Path $binDir "m1_component.dll"
if (-not (Test-Path -LiteralPath $controller) -or
    -not (Test-Path -LiteralPath $component)) {
    & (Join-Path $toolRoot "build_m1_component.ps1")
}

if ($TargetPid -gt 0) {
    $game = Get-Process -Id $TargetPid -ErrorAction Stop
} else {
    $deadline = (Get-Date).AddSeconds($WaitForClientSeconds)
    Write-Output "Waiting for SFC Launcher to create StarFleetOP.exe..."
    do {
        $candidates = @(Get-Process -Name "StarFleetOP" -ErrorAction SilentlyContinue)
        if ($candidates.Count -gt 1) {
            throw "More than one StarFleetOP process is running; pass -TargetPid."
        }
        if ($candidates.Count -eq 1) {
            $game = $candidates[0]
            break
        }
        Start-Sleep -Milliseconds 250
    } while ((Get-Date) -lt $deadline)
    if (-not $game) { throw "Timed out waiting for SFC Launcher." }
}

$client = Get-M1ProcessImagePath -ProcessId $game.Id
$expectedMd5 = "2BE8F713F81B1C68D50EAD6088C32886"
$expectedSha256 = "4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29"
$observedMd5 = (Get-FileHash -LiteralPath $client -Algorithm MD5).Hash
$observedSha256 = (Get-FileHash -LiteralPath $client -Algorithm SHA256).Hash
if ($observedMd5 -ne $expectedMd5 -or $observedSha256 -ne $expectedSha256) {
    throw "The launcher-created client does not match the supported exact build."
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$runDir = Join-Path $workspaceRoot "artifacts\m1\runs\$stamp-$Mode"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$metadata = [ordered]@{
    probe_id = if ($EnableShadingOff) { 'M1-C-RT-001' } elseif ($EnableVisualTint) { 'M1-B-RT-001' } elseif ($Mode -eq "enabled") { "M1-A-RT-001" } else { "M1-A-BASELINE-001" }
    mode = $Mode
    started = (Get-Date).ToString("o")
    target_pid = $game.Id
    target_path = $client
    target_path_method = "QueryFullProcessImageNameW/PROCESS_QUERY_LIMITED_INFORMATION"
    target_md5 = $observedMd5
    target_sha256 = $observedSha256
    max_seconds = $MaxSeconds
    max_frames = $MaxFrames
    max_events = $MaxEvents
    max_owners = 8
    warning_bytes = 16777216
    hard_bytes = 33554432
    geometry_samples_per_owner_frame = $GeometrySamplesPerOwnerFrame
    uncorrelated_geometry_samples_per_frame = $UncorrelatedGeometrySamplesPerFrame
    geometry_hook_enabled = -not [bool]$DisableGeometryHook
    visual_tint_enabled = [bool]$EnableVisualTint
    shading_off_enabled = [bool]$EnableShadingOff
    shading_phase_boundaries_ms = @(0, 5000, 8000, 13000, 58000)
    tint_delay_ms = 5000
    tint_duration_ms = 10000
    gate_timeout_seconds = if ($EnableVisualTint -or $EnableShadingOff) { $GateTimeoutSeconds } else { 0 }
    python_executable = $PythonExecutable
    component_sha256 = if ($Mode -eq 'enabled') { (Get-FileHash -LiteralPath $component -Algorithm SHA256).Hash } else { $null }
    controller_sha256 = if ($Mode -eq 'enabled') { (Get-FileHash -LiteralPath $controller -Algorithm SHA256).Hash } else { $null }
    stop_on_burst = -not [bool]$ContinueAfterBurst
    component = if ($Mode -eq "enabled") { $component } else { $null }
    controller = if ($Mode -eq "enabled") { $controller } else { $null }
}
$metadata | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $runDir "run-metadata.json") -Encoding utf8

try {
    Get-Process -Id $game.Id -Module -ErrorAction Stop |
        Select-Object ModuleName,FileName,@{n="FileVersion";e={$_.FileVersionInfo.FileVersion}} |
        Export-Csv -LiteralPath (Join-Path $runDir "loaded-modules.csv") -NoTypeInformation
} catch {
    Set-Content -LiteralPath (Join-Path $runDir "loaded-modules-error.txt") -Value $_.Exception.Message
}

$telemetryPath = Join-Path $runDir "process-telemetry.csv"
"timestamp,elapsed_seconds,cpu_seconds,working_set_bytes,private_bytes,handle_count,thread_count" |
    Set-Content -LiteralPath $telemetryPath -Encoding utf8

if ($Mode -eq "enabled") {
    $configPath = Join-Path $runDir "m1-component.ini"
    @(
        "[m1]",
        "OutputDirectory=$runDir",
        "MaxFrames=$MaxFrames",
        "MaxEvents=$MaxEvents",
        "MaxOwners=8",
        "GeometrySamplesPerOwnerFrame=$GeometrySamplesPerOwnerFrame",
        "UncorrelatedGeometrySamplesPerFrame=$UncorrelatedGeometrySamplesPerFrame",
        "EnableGeometryHook=$(if ($DisableGeometryHook) { 0 } else { 1 })",
        "EnableVisualTint=$(if ($EnableVisualTint) { 1 } else { 0 })",
        "EnableShadingOff=$(if ($EnableShadingOff) { 1 } else { 0 })",
        "TintDelayMs=5000",
        "TintDurationMs=10000",
        "WarningBytes=16777216",
        "HardBytes=33554432"
    ) | Set-Content -LiteralPath $configPath -Encoding ascii

    $controllerArgs = @(
        "--pid", $game.Id,
        "--dll", $component,
        "--config", $configPath,
        "--max-seconds", $MaxSeconds,
        "--stop-on-burst", $(if ($ContinueAfterBurst) { 0 } else { 1 })
    )
    if ($EnableVisualTint -or $EnableShadingOff) { $controllerArgs += @('--gate-timeout-seconds', $GateTimeoutSeconds) }
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $controller
    $startInfo.WorkingDirectory = $workspaceRoot
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    foreach ($argument in $controllerArgs) {
        [void]$startInfo.ArgumentList.Add([string]$argument)
    }
    $controllerJob = [System.Diagnostics.Process]::Start($startInfo)
}

$sampleStart = Get-Date
$totalEnvelopeSeconds = $MaxSeconds + $(if ($EnableVisualTint -or $EnableShadingOff) { $GateTimeoutSeconds } else { 0 })
Write-Output "Client verified (PID $($game.Id)). Recording up to $MaxSeconds seconds: $runDir"
while (-not $game.HasExited) {
    $elapsed = ((Get-Date) - $sampleStart).TotalSeconds
    if ($elapsed -ge $totalEnvelopeSeconds) { break }
    $game.Refresh()
    $line = '"{0}",{1:F3},{2:F3},{3},{4},{5},{6}' -f `
        (Get-Date).ToString("o"),$elapsed,$game.CPU,$game.WorkingSet64,
        $game.PrivateMemorySize64,$game.HandleCount,$game.Threads.Count
    Add-Content -LiteralPath $telemetryPath -Value $line -Encoding utf8
    if ($Mode -eq "enabled" -and $controllerJob.HasExited) { break }
    Start-Sleep -Seconds 1
}

if ($Mode -eq "enabled") {
    if (-not $controllerJob.HasExited) { Wait-Process -Id $controllerJob.Id }
    $controllerJob.Refresh()
    $controllerJob.StandardOutput.ReadToEnd() |
        Set-Content -LiteralPath (Join-Path $runDir "controller.stdout.txt") -Encoding utf8
    $controllerJob.StandardError.ReadToEnd() |
        Set-Content -LiteralPath (Join-Path $runDir "controller.stderr.txt") -Encoding utf8
    if ($controllerJob.ExitCode -ne 0) {
        throw "M1 controller failed with exit code $($controllerJob.ExitCode). See $runDir."
    }
    & $PythonExecutable (Join-Path $toolRoot "analyze_m1_log.py") $runDir
    if ($LASTEXITCODE -ne 0) { throw 'Semantic evidence analyzer failed.' }
    if ($EnableVisualTint) {
        & $PythonExecutable (Join-Path $toolRoot 'analyze_m1_visual_tint.py') $runDir
        if ($LASTEXITCODE -ne 0) { throw 'Visual tint evidence analyzer failed.' }
    }
    if ($EnableShadingOff) {
        & $PythonExecutable (Join-Path $toolRoot 'analyze_m1_shading_off.py') $runDir
        if ($LASTEXITCODE -ne 0) { throw 'Shading-off evidence analyzer failed.' }
    }
}

if (-not $game.HasExited) {
    Write-Output "Capture/component activity is complete. Exit SFC normally now."
    $exitObservation = Wait-M1ProcessExit -ProcessId $game.Id `
        -TimeoutSeconds $WaitForExitSeconds
    $normalExitObserved = $exitObservation.Outcome -eq 'exited'
} else {
    $normalExitObserved = $true
}

$postMd5 = (Get-FileHash -LiteralPath $client -Algorithm MD5).Hash
$postSha = (Get-FileHash -LiteralPath $client -Algorithm SHA256).Hash
@{
    completed = (Get-Date).ToString("o")
    client_md5_after = $postMd5
    client_sha256_after = $postSha
    client_unchanged = ($postMd5 -eq $observedMd5 -and $postSha -eq $observedSha256)
    normal_exit_observed = $normalExitObserved
    exit_outcome = if ($exitObservation) { $exitObservation.Outcome } else { 'game-exited-before-wait' }
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runDir "run-result.json") -Encoding utf8

Write-Output "Run complete: $runDir"
Write-Output "Client unchanged: $($postMd5 -eq $observedMd5 -and $postSha -eq $observedSha256)"
Write-Output "Normal exit observed: $normalExitObserved"
