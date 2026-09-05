param(
    [ValidateRange(5, 2100)][int]$CaptureSeconds = 120,
    [ValidateRange(30, 900)][int]$WaitForClientSeconds = 600,
    [ValidateRange(30, 900)][int]$GateTimeoutSeconds = 600,
    [ValidateRange(30, 900)][int]$WaitForExitSeconds = 600,
    [ValidateSet('Auto', 'Manual')][string]$GateMode = 'Auto',
    [switch]$LaunchSfc
)

$ErrorActionPreference = 'Stop'
$toolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Resolve-Path (Join-Path $toolRoot '..\..')
Import-Module (Join-Path $toolRoot 'ProcessImagePath.psm1') -Force

$gameDir = 'C:\Games\Taldren Software Inc\Starfleet Command Orion Pirates'
$client = Join-Path $gameDir 'StarFleetOP.exe'
$binDir = Join-Path $workspaceRoot 'artifacts\m1\bin'
$gateDll = Join-Path $binDir 'm1_gate.dll'
$controller = Join-Path $binDir 'm1_controller.exe'
$launcher = Join-Path $workspaceRoot 'Game Assets\SFCLauncher 2.1.0.22.exe'
$expectedMd5 = '2BE8F713F81B1C68D50EAD6088C32886'
$expectedSha256 = '4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29'
$expectedLauncherMd5 = '5974EA36E3C4E3DFE4F8E243607FC3CF'
$expectedLauncherSha256 = '84D3A5F89A922C4BEE6815CF0614538C3565C4BDB7DB3AA187C552CB727EF890'

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Baseline preparation requires the scoped elevated launcher workflow: start_m1_disabled_baseline.ps1.'
}

if (Get-Process -Name StarFleetOP -ErrorAction SilentlyContinue) {
    throw 'Exit every StarFleetOP process before preparing the baseline.'
}
& (Join-Path $toolRoot 'build_m1_component.ps1')
$beforeMd5 = (Get-FileHash -LiteralPath $client -Algorithm MD5).Hash
$beforeSha = (Get-FileHash -LiteralPath $client -Algorithm SHA256).Hash
if ($beforeMd5 -ne $expectedMd5 -or $beforeSha -ne $expectedSha256) {
    throw 'The installed client does not match the supported exact build.'
}
if ($LaunchSfc) {
    $launcherMd5 = (Get-FileHash -LiteralPath $launcher -Algorithm MD5).Hash
    $launcherSha = (Get-FileHash -LiteralPath $launcher -Algorithm SHA256).Hash
    if ($launcherMd5 -ne $expectedLauncherMd5 -or
        $launcherSha -ne $expectedLauncherSha256) {
        throw 'The restored SFC Launcher does not match the frozen baseline.'
    }
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$runDir = Join-Path $workspaceRoot "artifacts\m1\runs\$stamp-disabled-$($GateMode.ToLower())-gate"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$manualSignal = Join-Path $runDir 'manual-scene-gate.signal'
$metadataPath = Join-Path $runDir 'run-metadata.json'
$resultPath = Join-Path $runDir 'run-result.json'
$telemetryPath = Join-Path $runDir 'process-telemetry.csv'
$controllerOut = Join-Path $runDir 'controller.stdout.txt'
$controllerErr = Join-Path $runDir 'controller.stderr.txt'

$metadata = [ordered]@{
    probe_id = 'M1-A-BASELINE-002'
    mode = 'disabled-semantic-gate'
    prepared = (Get-Date).ToString('o')
    gate_mode = $GateMode.ToLower()
    gate_source = if ($GateMode -eq 'Auto') { 'validated tEntityShip::render entry 0x004162B9' } else { 'manual signal file' }
    gate_timeout_seconds = $GateTimeoutSeconds
    capture_seconds = $CaptureSeconds
    wait_for_client_seconds = $WaitForClientSeconds
    wait_for_exit_seconds = $WaitForExitSeconds
    target_path = $client
    target_md5 = $beforeMd5
    target_sha256 = $beforeSha
    launcher_path = if ($LaunchSfc) { $launcher } else { $null }
    launcher_md5 = if ($LaunchSfc) { $launcherMd5 } else { $null }
    launcher_sha256 = if ($LaunchSfc) { $launcherSha } else { $null }
    max_gate_events = if ($GateMode -eq 'Auto') { 1 } else { 0 }
    max_detailed_owners = if ($GateMode -eq 'Auto') { 1 } else { 0 }
    warning_bytes = 16777216
    hard_bytes = 33554432
    manual_signal_path = if ($GateMode -eq 'Manual') { $manualSignal } else { $null }
}
$metadata | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $metadataPath -Encoding utf8

$game = $null
$gateDetected = $false
$gateRestored = $false
$gateObservedAt = $null
$normalExit = $false
$exitOutcome = 'not-waited'
$gateUnloaded = $GateMode -eq 'Manual'
$failure = $null

try {
    if ($GateMode -eq 'Auto') {
        $savedConfig = Join-Path $runDir 'm1-component.ini'
        @(
            '[m1]',
            "OutputDirectory=$runDir",
            "ControllerPath=$controller",
            "MaxSeconds=$GateTimeoutSeconds",
            'StopOnBurst=1',
            'MaxFrames=1',
            'MaxEvents=1',
            'MaxOwners=1',
            'WarningBytes=16777216',
            'HardBytes=33554432'
        ) | Set-Content -LiteralPath $savedConfig -Encoding ascii
    }

    if ($LaunchSfc) {
        [void](Start-Process -FilePath $launcher -WorkingDirectory (Split-Path -Parent $launcher))
        Write-Output 'Disabled baseline prepared; verified SFC Launcher started by the elevated parent.'
    } else {
        Write-Output 'Disabled baseline prepared. Launch SFC and enter a two-ship skirmish.'
    }
    $discoveryDeadline = (Get-Date).AddSeconds($WaitForClientSeconds)
    do {
        $candidates = @(Get-Process -Name StarFleetOP -ErrorAction SilentlyContinue)
        if ($candidates.Count -gt 1) { throw 'More than one StarFleetOP process is running.' }
        if ($candidates.Count -eq 1) { $game = $candidates[0]; break }
        Start-Sleep -Milliseconds 250
    } while ((Get-Date) -lt $discoveryDeadline)
    if (-not $game) { throw 'Timed out waiting for SFC Launcher.' }

    $actualClient = Get-M1ProcessImagePath -ProcessId $game.Id
    $actualMd5 = (Get-FileHash -LiteralPath $actualClient -Algorithm MD5).Hash
    $actualSha = (Get-FileHash -LiteralPath $actualClient -Algorithm SHA256).Hash
    if ($actualMd5 -ne $expectedMd5 -or $actualSha -ne $expectedSha256) {
        throw 'The launcher-created process does not match the supported exact build.'
    }
    $metadata.target_pid = $game.Id
    $metadata.target_actual_path = $actualClient
    $metadata.target_path_method = 'QueryFullProcessImageNameW/PROCESS_QUERY_LIMITED_INFORMATION'
    $metadata.discovered = (Get-Date).ToString('o')
    $metadata | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $metadataPath -Encoding utf8

    if ($GateMode -eq 'Auto') {
        $startInfo = [Diagnostics.ProcessStartInfo]::new()
        $startInfo.FileName = $controller
        $startInfo.WorkingDirectory = $workspaceRoot
        $startInfo.UseShellExecute = $false
        $startInfo.CreateNoWindow = $true
        $startInfo.RedirectStandardOutput = $true
        $startInfo.RedirectStandardError = $true
        foreach ($argument in @('--pid', $game.Id, '--dll', $gateDll,
                '--config', $savedConfig, '--max-seconds', $GateTimeoutSeconds,
                '--stop-on-burst', 1, '--already-loaded', 0,
                '--unload-after-stop', 1)) {
            [void]$startInfo.ArgumentList.Add([string]$argument)
        }
        $controllerJob = [Diagnostics.Process]::Start($startInfo)
        $gateDeadline = (Get-Date).AddSeconds($GateTimeoutSeconds + 30)
        do {
            if (-not (Get-Process -Id $game.Id -ErrorAction SilentlyContinue)) {
                throw 'Game exited before the automatic tactical gate.'
            }
            if ($controllerJob.HasExited) {
                $controllerJob.Refresh()
                $state = $controllerJob.StandardOutput.ReadToEnd()
                $controllerError = $controllerJob.StandardError.ReadToEnd()
                $state | Set-Content -LiteralPath $controllerOut -Encoding utf8
                $controllerError | Set-Content -LiteralPath $controllerErr -Encoding utf8
                if ($controllerJob.ExitCode -ne 0) {
                    throw "Gate controller failed ($($controllerJob.ExitCode)): $controllerError"
                }
                if (Test-Path -LiteralPath (Join-Path $runDir 'M1-A-summary.json')) {
                if ($state -match 'component_state=removed' -and
                    $state -match 'hook_bytes_restored=true' -and
                    $state -match 'component_unloaded=true') {
                    $gateRestored = $true
                    $gateUnloaded = $true
                    $summary = Get-Content -Raw -LiteralPath (Join-Path $runDir 'M1-A-summary.json') | ConvertFrom-Json
                    $gateDetected = [bool]$summary.gate_activated
                    if ($gateDetected) {
                        $ageMs = [Environment]::TickCount64 - [long]$summary.gate_tick_ms
                        $gateObservedAt = (Get-Date).AddMilliseconds(-$ageMs).ToString('o')
                    }
                    break
                }
                }
                throw 'Gate controller exited without confirmed restoration and unload.'
            }
            Start-Sleep -Milliseconds 100
        } while ((Get-Date) -lt $gateDeadline)
        if (-not $gateRestored) { throw 'Gate detector removal was not confirmed within the bound.' }
        if (-not $gateDetected) { throw 'Automatic tactical gate was not observed within the bound.' }
    } else {
        Write-Output "Manual fallback armed: create $manualSignal after tactical entry."
        $gateDeadline = (Get-Date).AddSeconds($GateTimeoutSeconds)
        do {
            if (-not (Get-Process -Id $game.Id -ErrorAction SilentlyContinue)) {
                throw 'Game exited before the manual tactical gate.'
            }
            if (Test-Path -LiteralPath $manualSignal) {
                $gateDetected = $true
                $gateRestored = $true
                $gateObservedAt = (Get-Item -LiteralPath $manualSignal).LastWriteTime.ToString('o')
                break
            }
            Start-Sleep -Milliseconds 100
        } while ((Get-Date) -lt $gateDeadline)
        if (-not $gateDetected) { throw 'Manual tactical gate timed out.' }
    }

    $metadata.gate_detected = $true
    $metadata.gate_observed_at = $gateObservedAt
    $metadata.gate_hook_restored_before_capture = $gateRestored
    $metadata.capture_started = (Get-Date).ToString('o')
    $metadata | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $metadataPath -Encoding utf8
    Write-Output "Tactical scene gate detected at $gateObservedAt; gate hook restored."
    Write-Output "Recording $CaptureSeconds seconds of disabled baseline telemetry."

    'timestamp,elapsed_seconds,cpu_seconds,working_set_bytes,private_bytes,handle_count,thread_count' |
        Set-Content -LiteralPath $telemetryPath -Encoding utf8
    $captureStart = Get-Date
    while ((Get-Date) -lt $captureStart.AddSeconds($CaptureSeconds)) {
        $current = Get-Process -Id $game.Id -ErrorAction SilentlyContinue
        if (-not $current) { break }
        $elapsed = ((Get-Date) - $captureStart).TotalSeconds
        $line = '"{0}",{1:F3},{2:F3},{3},{4},{5},{6}' -f
            (Get-Date).ToString('o'),$elapsed,$current.CPU,$current.WorkingSet64,
            $current.PrivateMemorySize64,$current.HandleCount,$current.Threads.Count
        Add-Content -LiteralPath $telemetryPath -Value $line -Encoding utf8
        Start-Sleep -Seconds 1
    }

    Write-Output 'Baseline capture complete. Exit SFC normally now.'
    $exit = Wait-M1ProcessExit -ProcessId $game.Id -TimeoutSeconds $WaitForExitSeconds
    $exitOutcome = $exit.Outcome
    $normalExit = $exitOutcome -eq 'exited'
} catch {
    $failure = $_.Exception.Message
    [ordered]@{
        completed = (Get-Date).ToString('o')
        result = 'failed'
        failure = $failure
        gate_detected = $gateDetected
        gate_hook_restored = $gateRestored
        gate_module_unloaded = $gateUnloaded
        exit_outcome = $exitOutcome
    } | ConvertTo-Json | Set-Content -LiteralPath $resultPath -Encoding utf8
    throw
} finally {
    # The automatic gate uses direct, scoped injection and writes no files to the
    # game directory. Its controller must restore and unload before capture.
}

$afterMd5 = (Get-FileHash -LiteralPath $client -Algorithm MD5).Hash
$afterSha = (Get-FileHash -LiteralPath $client -Algorithm SHA256).Hash
$files = @(Get-ChildItem -LiteralPath $runDir -File -ErrorAction SilentlyContinue)
[ordered]@{
    completed = (Get-Date).ToString('o')
    gate_detected = $gateDetected
    gate_observed_at = $gateObservedAt
    gate_hook_restored_before_capture = $gateRestored
    gate_module_unloaded_before_capture = $gateUnloaded
    exit_outcome = $exitOutcome
    normal_exit_observed = $normalExit
    client_md5_after = $afterMd5
    client_sha256_after = $afterSha
    client_unchanged = ($afterMd5 -eq $beforeMd5 -and $afterSha -eq $beforeSha)
    output_bytes_excluding_result = ($files | Measure-Object -Property Length -Sum).Sum
    game_directory_files_added = 0
} | ConvertTo-Json | Set-Content -LiteralPath $resultPath -Encoding utf8

Write-Output "Run complete: $runDir"
Write-Output "Exit outcome: $exitOutcome"
Write-Output "Client unchanged: $($afterMd5 -eq $beforeMd5 -and $afterSha -eq $beforeSha)"
