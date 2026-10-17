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
    [ValidateRange(1, 32)][int]$MaxOwners = 8,

    [ValidateRange(0, 8)]
    [int]$GeometrySamplesPerOwnerFrame = 1,

    [ValidateRange(0, 8)]
    [int]$UncorrelatedGeometrySamplesPerFrame = 1,

    [switch]$DisableGeometryHook,

    [switch]$EnableVisualTint,
    [switch]$EnableShadingOff,
    [switch]$EnableCornerSnapshot,
    [switch]$EnableWrapperObservation,
    [switch]$EnablePrivateCopy,
    [switch]$EnableRepeatedPrivateCopy,
    [switch]$EnableCopyEpochRequalification,
    [switch]$EnableSurfaceLighting,
    [switch]$EnableMeshExport,
    [switch]$EnableTextureReferences,
    [string]$LiveChannel = '',
    [switch]$FreshScene,

    [ValidateRange(30, 900)][int]$GateTimeoutSeconds = 600,

    [string]$PythonExecutable = 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe',

    [int]$TargetPid = 0,

    [switch]$ContinueAfterBurst,
    [switch]$Endurance
)

$ErrorActionPreference = "Stop"
$meshAnalysisFailure=$false
if($FreshScene -and (-not $LiveChannel -or $MaxOwners -ne 32)){throw 'Fresh scene requires explicit live channel and 32-owner capacity.'}
$meshPacketFailure=$false
$meshObjFailure=$false
if($EnableTextureReferences -and -not $EnableMeshExport){throw 'Texture references require same-run mesh export.'}
if($LiveChannel -and ($LiveChannel -notmatch '^Local\\SFCBridge_[a-f0-9]{32}$' -or -not $EnableTextureReferences)){throw 'Live bridge requires a unique qualified channel and texture mesh mode.'}
if ($Endurance -and ($Mode -ne 'enabled' -or $MaxSeconds -ne 1830 -or
    -not $DisableGeometryHook -or -not $ContinueAfterBurst -or $MaxFrames -ne 120 -or
    $MaxEvents -ne 10000 -or $EnableVisualTint -or $EnableShadingOff -or
    $EnableCornerSnapshot -or $EnableWrapperObservation -or $EnablePrivateCopy -or
    $EnableRepeatedPrivateCopy -or $EnableCopyEpochRequalification -or $EnableSurfaceLighting -or $EnableMeshExport)) {
    throw 'Endurance requires neutral enabled mode, 1830 seconds, 120 frames/10000 detailed events, geometry off and ContinueAfterBurst.'
}
if($EnableWrapperObservation -and -not ($EnableCornerSnapshot -or $EnableMeshExport)){throw 'Wrapper observation requires read-only corner or mesh mode.'}
if($EnableMeshExport -and ($Mode -ne 'enabled' -or -not $EnableWrapperObservation -or
    -not $DisableGeometryHook -or -not $ContinueAfterBurst -or $MaxSeconds -ne 90 -or
    $EnableCornerSnapshot -or $EnablePrivateCopy -or $EnableRepeatedPrivateCopy -or
    $EnableCopyEpochRequalification -or $EnableSurfaceLighting -or $EnableShadingOff -or $EnableVisualTint)) {
    throw 'Mesh export requires exclusive read-only wrapper mode, geometry off, ContinueAfterBurst and 90 seconds.'
}
if($EnablePrivateCopy -and -not $EnableWrapperObservation){throw 'Private copy requires wrapper mode.'}
if($EnableRepeatedPrivateCopy -and -not $EnablePrivateCopy){throw 'Repeated private copy requires private copy mode.'}
if($EnableCopyEpochRequalification -and -not $EnableRepeatedPrivateCopy){throw 'Epoch qualification requires repeated copy mode.'}
if($EnableSurfaceLighting -and (-not $EnablePrivateCopy -or $EnableRepeatedPrivateCopy -or $EnableCopyEpochRequalification)){throw 'Surface lighting requires exclusive private-copy mode.'}
if ($EnableCornerSnapshot -and ($Mode -ne 'enabled' -or $EnableShadingOff -or
    $EnableVisualTint -or -not $DisableGeometryHook -or -not $ContinueAfterBurst -or
    $MaxSeconds -ne 90)) {
    throw 'Corner snapshot requires enabled read-only mode, geometry off, ContinueAfterBurst and 90 seconds.'
}
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
if ($Endurance) {
    Import-Module (Join-Path $toolRoot 'M1MeasurementJobs.psm1') -Force
    $presentMon = Join-Path $workspaceRoot 'artifacts/m1/tools/PresentMon-2.3.1-x64.exe'
    if ((Get-FileHash -LiteralPath $presentMon -Algorithm SHA256).Hash -ne
        '364E5D98D4D134BD54DD25C22ED2CA2F4883F8BC3ED6502BEE0C151E3436D30C') {
        throw 'Pinned PresentMon hash mismatch'
    }
}

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
    probe_id = if($FreshScene){'LIVE-SCENE-001'} elseif($EnableMeshExport){'MESH-EXPORT-001'} elseif($Endurance){'M1-CLOSE-ENDURE-001'} elseif($EnableSurfaceLighting){'M1-C01-RT-010'} elseif($EnableCopyEpochRequalification){'M1-C01-RT-009'} elseif($EnableRepeatedPrivateCopy){'M1-C01-RT-008'} elseif($EnablePrivateCopy){'M1-C01-RT-007'} elseif ($EnableWrapperObservation) { 'M1-C01-RT-006' } elseif ($EnableCornerSnapshot) { 'M1-C01-RT-005' } elseif ($EnableShadingOff) { 'M1-C-RT-001' } elseif ($EnableVisualTint) { 'M1-B-RT-001' } elseif ($Mode -eq "enabled") { "M1-A-RT-001" } else { "M1-A-BASELINE-001" }
    endurance = [bool]$Endurance
    measurement_seconds = if($Endurance){1800}else{0}
    disabled_comparison = if($Endurance){'20261014-002725-disabled-auto-gate'}else{$null}
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
    max_owners = $MaxOwners
    warning_bytes = 16777216
    hard_bytes = 33554432
    geometry_samples_per_owner_frame = $GeometrySamplesPerOwnerFrame
    uncorrelated_geometry_samples_per_frame = $UncorrelatedGeometrySamplesPerFrame
    geometry_hook_enabled = -not [bool]$DisableGeometryHook
    visual_tint_enabled = [bool]$EnableVisualTint
    shading_off_enabled = [bool]$EnableShadingOff
    corner_snapshot_enabled = [bool]$EnableCornerSnapshot
    wrapper_observation_enabled = [bool]$EnableWrapperObservation
    mesh_export_enabled = [bool]$EnableMeshExport
    fresh_scene = [bool]$FreshScene
    texture_references_enabled = [bool]$EnableTextureReferences
    live_channel = $LiveChannel
    texture_probe_id = if($EnableTextureReferences){'TEXTURE-EXPORT-001'}else{$null}
    mesh_export_budget = if($FreshScene){@{revisions=64;slots=4;mapping_bytes=16777216;slot_bytes=2097152;max_polygons=8192;max_positions=65536;geometry_hook=$false;state_bytes_per_process=16777216;max_records_per_owner=2700}}elseif($EnableMeshExport){@{packets=1;attempts=2;storage_bytes=1048576;file_bytes=2097152;summary_bytes=65536;max_polygons=512;max_positions=65536;geometry_hook=$false}}else{$null}
    private_copy_enabled=[bool]$EnablePrivateCopy
    private_copy_budget=if($EnablePrivateCopy -and -not $EnableSurfaceLighting){@{applications=$(if($EnableRepeatedPrivateCopy){32}else{1});slot_max_bytes=22528;bank_max_bytes=716800;interval_ms=1000;setup_seconds=20;pinned_until_exit=$true;reuse=$false}}else{$null}
    repeated_private_copy_enabled=[bool]$EnableRepeatedPrivateCopy
    copy_epoch_requalification_enabled=[bool]$EnableCopyEpochRequalification
    surface_lighting_enabled=[bool]$EnableSurfaceLighting
    surface_lighting_budget=if($EnableSurfaceLighting){@{marker_ms=20000;normal_gap_ms=5000;altered_ms=15000;graphs=2;memory_max_bytes=1048576;immutable=$true;continuous=$true;per_call_original_comparison=$true;phase_clock='actual_first_marker_publication';cue_policy='setup20_then_component_lighting_and_restore_events'}}else{$null}
    copy_epoch_budget=if($EnableCopyEpochRequalification){@{requalifications=2;distinct_frames=3;dwell_ms=250;identity_continuity_claimed=$false}}else{$null}
    wrapper_observation_budget = if($EnableWrapperObservation){@{schema='m1.wrapper.v1';samples=64;substitution_enabled=[bool]$EnablePrivateCopy}}else{$null}
    requested_target_tracking = if($EnablePrivateCopy){'not_required_for_neutral_copy'} elseif ($EnableCornerSnapshot) { 'disabled_by_sponsor_not_automatically_verified' } else { $null }
    rejection_diagnostic_budget = @{ schema='m1.rejections.v1'; signatures=32; examples=64; maximum_section_bytes=65536 }
    corner_snapshot_budget = if ($EnableCornerSnapshot) { @{ schema='m1.c01.corners.v3'; snapshots=36; interest_filters=2; epoch_transition_capacity=64; interval_ms=5000; polygons_per_snapshot=64; corners_per_polygon=8; packet_hard_bytes=3145728; cue_seconds=$(if($EnableCopyEpochRequalification){@(0,20,40)}elseif($EnablePrivateCopy){@(0,20)}else{@(0,15,30)}) } } else { $null }
    shading_phase_boundaries_ms = @(0, 5000, 8000, 13000, 58000)
    tint_delay_ms = 5000
    tint_duration_ms = 10000
    gate_timeout_seconds = if ($Endurance -or $EnableVisualTint -or $EnableShadingOff -or $EnableCornerSnapshot -or $EnableMeshExport) { $GateTimeoutSeconds } else { 0 }
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
        "MaxOwners=$MaxOwners",
        "GeometrySamplesPerOwnerFrame=$GeometrySamplesPerOwnerFrame",
        "UncorrelatedGeometrySamplesPerFrame=$UncorrelatedGeometrySamplesPerFrame",
        "EnableGeometryHook=$(if ($DisableGeometryHook) { 0 } else { 1 })",
        "EnableVisualTint=$(if ($EnableVisualTint) { 1 } else { 0 })",
        "EnableShadingOff=$(if ($EnableShadingOff) { 1 } else { 0 })",
        "EnableCornerSnapshot=$(if ($EnableCornerSnapshot) { 1 } else { 0 })",
        "EnableWrapperObservation=$(if ($EnableWrapperObservation) { 1 } else { 0 })",
        "EnablePrivateCopy=$(if ($EnablePrivateCopy) { 1 } else { 0 })",
        "EnableRepeatedPrivateCopy=$(if ($EnableRepeatedPrivateCopy) { 1 } else { 0 })",
        "EnableCopyEpochRequalification=$(if ($EnableCopyEpochRequalification) { 1 } else { 0 })",
        "EnableSurfaceLighting=$(if ($EnableSurfaceLighting) { 1 } else { 0 })",
        "EnableMeshExport=$(if ($EnableMeshExport) { 1 } else { 0 })",
        "EnableTextureReferences=$(if ($EnableTextureReferences) { 1 } else { 0 })",
        "LiveChannel=$LiveChannel",
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
    if ($Endurance -or $EnableVisualTint -or $EnableShadingOff -or $EnableCornerSnapshot -or $EnableMeshExport) { $controllerArgs += @('--gate-timeout-seconds', $GateTimeoutSeconds) }
    if ($Endurance) { $controllerArgs += @('--unload-after-stop', 1) }
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
$totalEnvelopeSeconds = $MaxSeconds + $(if ($Endurance -or $EnableVisualTint -or $EnableShadingOff -or $EnableCornerSnapshot -or $EnableMeshExport) { $GateTimeoutSeconds } else { 0 })
$enduranceGate = $null
$enduranceGateAt = $null
$measurementJobs = @()
$measurementFailure = $null
$measurementOkay = $null
$cornerGateWait = $null
$cornerGateObservedAt = $null
$cornerPhase = -1
$cornerCues = @()
Write-Output "Client verified (PID $($game.Id)). Recording up to $MaxSeconds seconds: $runDir"
while (-not $game.HasExited) {
    $elapsed = ((Get-Date) - $sampleStart).TotalSeconds
    if ($elapsed -ge $totalEnvelopeSeconds) { break }
    $game.Refresh()
    if ($Endurance -and -not $enduranceGateAt -and -not $controllerJob.HasExited) {
        if (-not $enduranceGate) {
            try { $enduranceGate = [Threading.EventWaitHandle]::OpenExisting("Local\SFCM1TacticalGate_$($game.Id)") }
            catch [Threading.WaitHandleCannotBeOpenedException] { }
        }
        if ($enduranceGate -and $enduranceGate.WaitOne(0)) {
            $enduranceGateAt = Get-Date
            $metadata.endurance_gate_observed_at = $enduranceGateAt.ToString('o')
            try {
                $measurementJobs = @(Start-M1MeasurementJobs -TargetProcessId $game.Id `
                    -Seconds 1800 -OutputDirectory $runDir -PythonExecutable $PythonExecutable)
            } catch { $measurementFailure = $_.Exception.Message }
            $metadata | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $runDir 'run-metadata.json') -Encoding utf8
            Write-Output 'ENDURANCE STARTED: play normally in this tactical mission for about 30 minutes. Exit only when requested; if a problem occurs, exit safely and report it.'
        }
    }
    if ($EnableCornerSnapshot) {
        if (-not $cornerGateWait) {
            try { $cornerGateWait = [Threading.EventWaitHandle]::OpenExisting("Local\SFCM1TacticalGate_$($game.Id)") }
            catch [Threading.WaitHandleCannotBeOpenedException] { }
        }
        if ($cornerGateWait -and -not $cornerGateObservedAt -and $cornerGateWait.WaitOne(0)) {
            $cornerGateObservedAt = Get-Date
        }
        if ($cornerGateObservedAt) {
            $phase = [Math]::Min(2, [int][Math]::Floor(((Get-Date) - $cornerGateObservedAt).TotalSeconds / 15))
            if($EnablePrivateCopy){$phase=[Math]::Min(1,[int][Math]::Floor(((Get-Date)-$cornerGateObservedAt).TotalSeconds/20))}
            if($EnableCopyEpochRequalification){$phase=[Math]::Min(2,[int][Math]::Floor(((Get-Date)-$cornerGateObservedAt).TotalSeconds/20))}
            if($EnableSurfaceLighting){
                $phase=if(((Get-Date)-$cornerGateObservedAt).TotalSeconds -lt 20){0}else{1}
                foreach($phaseSignal in @(@{name='SurfaceLighting';phase=2},@{name='SurfaceRestored';phase=3})){
                    $signal=[Threading.EventWaitHandle]::OpenExisting("Local\SFCM1$($phaseSignal.name)_$($game.Id)")
                    try{if($signal.WaitOne(0)){$phase=$phaseSignal.phase}}finally{$signal.Dispose()}
                }
            }
            if ($phase -gt $cornerPhase) {
                $cornerPhase = $phase
                $action = @('Disable target tracking; keep both ships visible; own ship at rest; hold camera', 'With target tracking disabled: small camera rotation only; keep both ships visible', 'Hold camera angle with target tracking disabled; accelerate and gently turn your ship; keep both ships visible, zoom out if needed')[$phase]
                if($EnablePrivateCopy){
                    $action=@('SETUP: keep both ships visible; stay at rest and hold camera; 20 seconds before copy test','COPY TEST START: keep playing normally; no visual change expected','FRESH IDENTITY TEST: point a free camera away from BOTH ships for about 5 seconds, then bring them back; no target tracking')[$phase]
                    if($EnableRepeatedPrivateCopy -and $phase -eq 1){$action='REPEATED COPY START: keep both ships visible; gently move/turn and make small camera movements; no visual change expected'}
                }
                if($EnableSurfaceLighting){$action=@('SETUP: both ships visible;20seconds before identification','IDENTIFY: selected ship magenta for20seconds; find it and put camera on it; then5seconds normal','LIGHTING: same ship altered for15seconds; keep it visible; report difference','RESTORED: original rendering; keep playing until exit request')[$phase]}
                Write-Output "CORNER TEST: $action"
                $audible = $true
                try { for ($tone = 0; $tone -le $phase; $tone++) { [Console]::Beep(800, 150); Start-Sleep -Milliseconds 100 } }
                catch { $audible = $false }
                if($EnablePrivateCopy -and $phase -eq 1){
                    $ready=[Threading.EventWaitHandle]::OpenExisting("Local\SFCM1PrivateCopyReady_$($game.Id)")
                    try{[void]$ready.Set()}finally{$ready.Dispose()}
                }
                $cornerCues += [ordered]@{ requested_phase = $phase; requested_action = $action; emitted_at = (Get-Date).ToString('o'); audible_call_succeeded = $audible }
            }
        }
    }
    $line = '"{0}",{1:F3},{2:F3},{3},{4},{5},{6}' -f `
        (Get-Date).ToString("o"),$elapsed,$game.CPU,$game.WorkingSet64,
        $game.PrivateMemorySize64,$game.HandleCount,$game.Threads.Count
    Add-Content -LiteralPath $telemetryPath -Value $line -Encoding utf8
    if ($Mode -eq "enabled" -and $controllerJob.HasExited) { break }
    Start-Sleep -Seconds 1
}

if ($Mode -eq "enabled") {
    if ($enduranceGate) { $enduranceGate.Dispose() }
    if ($cornerGateWait) { $cornerGateWait.Dispose() }
    if ($EnableCornerSnapshot) {
        ConvertTo-Json -InputObject @($cornerCues) -Depth 4 |
            Set-Content -LiteralPath (Join-Path $runDir 'corner-action-cues.json') -Encoding utf8
    }
    if (-not $controllerJob.HasExited) {
        if (-not $Endurance) { Wait-Process -Id $controllerJob.Id }
        elseif (-not $controllerJob.WaitForExit(45000)) {
            if ($Endurance -and $measurementJobs.Count) {
                [void](Complete-M1MeasurementJobs -Jobs $measurementJobs -OutputDirectory $runDir -Cancel)
            }
            throw 'Controller cleanup exceeded its bound. Exit SFC normally; do not kill the runner with active hooks.'
        }
    }
    $controllerJob.Refresh()
    $controllerJob.StandardOutput.ReadToEnd() |
        Set-Content -LiteralPath (Join-Path $runDir "controller.stdout.txt") -Encoding utf8
    $controllerJob.StandardError.ReadToEnd() |
        Set-Content -LiteralPath (Join-Path $runDir "controller.stderr.txt") -Encoding utf8
    if ($Endurance -and $measurementJobs.Count) {
        $cancelMeasurement = $controllerJob.ExitCode -ne 0 -or -not $enduranceGateAt -or
            ((Get-Date) - $enduranceGateAt).TotalSeconds -lt 1800
        $measurementOkay = Complete-M1MeasurementJobs -Jobs $measurementJobs -OutputDirectory $runDir -Cancel:$cancelMeasurement
    }
    if ($Endurance) {
        $metadata.endurance_controller_exit_observed_at = (Get-Date).ToString('o')
        $metadata.endurance_controller_exit_observed_tick_ms = [Environment]::TickCount64
        $metadata.measurement_collectors_passed = $measurementOkay
        $metadata.measurement_start_failure = $measurementFailure
        $metadata | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $runDir 'run-metadata.json') -Encoding utf8
        if (-not $measurementOkay) { Write-Warning 'Measurement incomplete; evidence must be reviewed, not promoted to PASS.' }
    }
    if ($controllerJob.ExitCode -ne 0) {
        if ($Endurance) {
            @{
                completed=(Get-Date).ToString('o'); endurance=$true;
                result='incomplete-controller-failure';controller_exit_code=$controllerJob.ExitCode;
                measurement_collectors_passed=$measurementOkay;
                measurement_start_failure=$measurementFailure;
                normal_exit_observed=$false;exit_outcome='not-adjudicated-early-exit-or-cleanup-failure';
                client_sha256_after=(Get-FileHash -LiteralPath $client -Algorithm SHA256).Hash
            } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runDir 'run-result.json') -Encoding utf8
        }
        throw "M1 controller failed with exit code $($controllerJob.ExitCode). See $runDir."
    }
    & $PythonExecutable (Join-Path $toolRoot "analyze_m1_log.py") $runDir
    if ($LASTEXITCODE -ne 0) { throw 'Semantic evidence analyzer failed.' }
    if ($EnableVisualTint) {
        & $PythonExecutable (Join-Path $toolRoot 'analyze_m1_visual_tint.py') $runDir
        if ($LASTEXITCODE -ne 0) { throw 'Visual tint evidence analyzer failed.' }
    }
    if($EnableMeshExport -and -not $FreshScene){
        & $PythonExecutable (Join-Path $toolRoot 'analyze_mesh_export.py') (Join-Path $runDir 'MESH-EXPORT-001.bin') --receipt (Join-Path $runDir 'MESH-EXPORT-001-receipt.json') --output (Join-Path $runDir 'MESH-EXPORT-001-analysis.json')
        $meshAnalysisFailure=$LASTEXITCODE -ne 0
        $meshPacketFailure=$meshAnalysisFailure
        if(-not $meshAnalysisFailure){
            & $PythonExecutable (Join-Path $toolRoot 'export_mesh_obj.py') (Join-Path $runDir 'MESH-EXPORT-001.bin') --receipt (Join-Path $runDir 'MESH-EXPORT-001-receipt.json') --output (Join-Path $runDir 'MESH-EXPORT-001.obj')
            $meshAnalysisFailure=$LASTEXITCODE -ne 0
            $meshObjFailure=$meshAnalysisFailure
            if(-not $meshAnalysisFailure){Write-Output "REMIX INPUT READY: $(Join-Path $runDir 'MESH-EXPORT-001.obj'). Import into the separate Toolkit after normal SFC exit; no live Remix integration was run."}
        }
        if($meshAnalysisFailure){Write-Warning 'Mesh export pipeline incomplete; preserve raw packet/analysis. Still exit normally when requested.'}
    }
    if ($EnableShadingOff) {
        & $PythonExecutable (Join-Path $toolRoot 'analyze_m1_shading_off.py') $runDir
        if ($LASTEXITCODE -ne 0) { throw 'Shading-off evidence analyzer failed.' }
    }
    if ($EnableCornerSnapshot) {
        & $PythonExecutable (Join-Path $toolRoot 'analyze_m1_corner_snapshot.py') $runDir
        if ($LASTEXITCODE -ne 0) { throw 'Corner snapshot analyzer failed.' }
        & $PythonExecutable (Join-Path $toolRoot 'analyze_m1_rejections.py') $runDir
        if ($LASTEXITCODE -ne 0) { throw 'Rejection diagnostic analyzer failed.' }
        if($EnableWrapperObservation){
            & $PythonExecutable (Join-Path $toolRoot 'analyze_m1_wrapper.py') $runDir
            if($LASTEXITCODE -ne 0){throw 'Wrapper observation analyzer failed.'}
        }
        if($EnablePrivateCopy){
            $copyAnalyzer=if($EnableSurfaceLighting){'analyze_m1_surface_lighting.py'}else{'analyze_m1_private_copy.py'}
            & $PythonExecutable (Join-Path $toolRoot $copyAnalyzer) $runDir
            if($LASTEXITCODE -ne 0){throw 'Private copy analyzer failed.'}
        }
    }
}

if (-not $game.HasExited) {
    if ($Endurance -or $EnableMeshExport) { try { [Console]::Beep(1000, 700); [Console]::Beep(1000, 700) } catch { } }
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
    endurance = [bool]$Endurance
    measurement_collectors_passed = $measurementOkay
    measurement_start_failure = $measurementFailure
    client_md5_after = $postMd5
    client_sha256_after = $postSha
    client_unchanged = ($postMd5 -eq $observedMd5 -and $postSha -eq $observedSha256)
    normal_exit_observed = $normalExitObserved
    mesh_packet_validation_failed = $meshPacketFailure
    mesh_obj_conversion_failed = $meshObjFailure
    mesh_export_pipeline_failed = $meshAnalysisFailure
    exit_outcome = if ($exitObservation) { $exitObservation.Outcome } else { 'game-exited-before-wait' }
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runDir "run-result.json") -Encoding utf8

Write-Output "Run complete: $runDir"
Write-Output "Client unchanged: $($postMd5 -eq $observedMd5 -and $postSha -eq $observedSha256)"
Write-Output "Normal exit observed: $normalExitObserved"
if($EnableTextureReferences -and -not $FreshScene -and -not $meshAnalysisFailure -and $normalExitObserved -and $postSha -eq $observedSha256){
    & $PythonExecutable (Join-Path $toolRoot 'export_mesh_textures.py') $runDir
    if($LASTEXITCODE -ne 0){Write-Warning 'Texture recovery PARTIAL. Preserve the association/manifest for review; no substitute textures or game changes.'}
    else {Write-Output 'Primary-image derivative prepared. Glow role and visual comparison still require review; not a texture-recovery PASS.'}
}
if($meshAnalysisFailure){throw 'Mesh packet/OBJ pipeline incomplete; cleanup/exit and available raw evidence were preserved.'}
