param(
    [ValidateRange(5, 2100)]
    [int]$MaxSeconds = 300,

    [ValidateRange(30, 900)]
    [int]$WaitForClientSeconds = 600,

    [ValidateRange(30, 900)]
    [int]$WaitForExitSeconds = 600,

    [switch]$ContinueAfterBurst
)

$ErrorActionPreference = "Stop"

$toolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Resolve-Path (Join-Path $toolRoot "..\..")
Import-Module (Join-Path $toolRoot "ProcessImagePath.psm1") -Force
$gameDir = "C:\Games\Taldren Software Inc\Starfleet Command Orion Pirates"
$client = Join-Path $gameDir "StarFleetOP.exe"
$installedProxy = Join-Path $gameDir "winmm.dll"
$installedConfig = Join-Path $gameDir "m1-component.ini"
$binDir = Join-Path $workspaceRoot "artifacts\m1\bin"
$builtProxy = Join-Path $binDir "winmm.dll"
$controller = Join-Path $binDir "m1_controller.exe"

if (Get-Process -Name "StarFleetOP" -ErrorAction SilentlyContinue) {
    throw "Exit every StarFleetOP process before preparing the proxy session."
}
if (Test-Path -LiteralPath $installedProxy) {
    throw "Refusing to replace an existing game-directory winmm.dll: $installedProxy"
}
if (Test-Path -LiteralPath $installedConfig) {
    throw "Refusing to replace an existing M1 component configuration: $installedConfig"
}

& (Join-Path $toolRoot "build_m1_component.ps1")

$expectedMd5 = "2BE8F713F81B1C68D50EAD6088C32886"
$beforeMd5 = (Get-FileHash -LiteralPath $client -Algorithm MD5).Hash
$beforeSha = (Get-FileHash -LiteralPath $client -Algorithm SHA256).Hash
if ($beforeMd5 -ne $expectedMd5) {
    throw "The installed client does not match the supported exact build."
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$runDir = Join-Path $workspaceRoot "artifacts\m1\runs\$stamp-enabled-proxy"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$savedConfig = Join-Path $runDir "m1-component.ini"
@(
    "[m1]",
    "OutputDirectory=$runDir",
    "ControllerPath=$controller",
    "MaxSeconds=$MaxSeconds",
    "StopOnBurst=$(if ($ContinueAfterBurst) { 0 } else { 1 })",
    "MaxFrames=120",
    "MaxEvents=10000",
    "MaxOwners=8",
    "WarningBytes=16777216",
    "HardBytes=33554432"
) | Set-Content -LiteralPath $savedConfig -Encoding ascii

$metadata = [ordered]@{
    probe_id = "M1-A-RT-001"
    mode = "enabled-proxy"
    prepared = (Get-Date).ToString("o")
    target_path = $client
    target_md5 = $beforeMd5
    target_sha256 = $beforeSha
    loader = "local WINMM three-export forwarder"
    launcher_version = "2.1.0.22 (M0 evidence; exact path pending)"
    max_seconds = $MaxSeconds
    wait_for_client_seconds = $WaitForClientSeconds
    wait_for_exit_seconds = $WaitForExitSeconds
    max_frames = 120
    max_events = 10000
    max_owners = 8
    warning_bytes = 16777216
    hard_bytes = 33554432
    stop_on_burst = -not [bool]$ContinueAfterBurst
    installed_proxy_path = $installedProxy
    proxy_sha256 = (Get-FileHash -LiteralPath $builtProxy -Algorithm SHA256).Hash
    controller_path = $controller
    controller_sha256 = (Get-FileHash -LiteralPath $controller -Algorithm SHA256).Hash
}
$metadata | ConvertTo-Json -Depth 4 |
    Set-Content -LiteralPath (Join-Path $runDir "run-metadata.json") -Encoding utf8

Copy-Item -LiteralPath $builtProxy -Destination $installedProxy
Copy-Item -LiteralPath $savedConfig -Destination $installedConfig
if ((Get-FileHash -LiteralPath $installedProxy -Algorithm SHA256).Hash -ne
    $metadata.proxy_sha256) {
    throw "Installed proxy hash verification failed."
}

$game = $null
$normalExitObserved = $false
$componentRemoved = $false
$telemetryPath = Join-Path $runDir "process-telemetry.csv"
"timestamp,elapsed_seconds,cpu_seconds,working_set_bytes,private_bytes,handle_count,thread_count" |
    Set-Content -LiteralPath $telemetryPath -Encoding utf8

try {
    Write-Output "M1-A-RT-001 is prepared without a second UAC request."
    Write-Output "Launch SFC through SFC Launcher and enter M1-A-FIXTURE-01."
    $deadline = (Get-Date).AddSeconds($WaitForClientSeconds)
    do {
        $candidates = @(Get-Process -Name "StarFleetOP" -ErrorAction SilentlyContinue)
        if ($candidates.Count -gt 1) {
            throw "More than one StarFleetOP process is running."
        }
        if ($candidates.Count -eq 1) { $game = $candidates[0]; break }
        Start-Sleep -Milliseconds 250
    } while ((Get-Date) -lt $deadline)
    if (-not $game) { throw "Timed out waiting for SFC Launcher." }

    $metadata.target_pid = $game.Id
    $metadata.launched = (Get-Date).ToString("o")
    $metadata | ConvertTo-Json -Depth 4 |
        Set-Content -LiteralPath (Join-Path $runDir "run-metadata.json") -Encoding utf8
    try {
        Get-Process -Id $game.Id -Module -ErrorAction Stop |
            Select-Object ModuleName,FileName,@{n="FileVersion";e={$_.FileVersionInfo.FileVersion}} |
            Export-Csv -LiteralPath (Join-Path $runDir "loaded-modules.csv") -NoTypeInformation
    } catch {
        Set-Content -LiteralPath (Join-Path $runDir "loaded-modules-error.txt") `
            -Value $_.Exception.Message
    }

    $start = Get-Date
    $controllerOut = Join-Path $runDir "controller.stdout.txt"
    $controllerErr = Join-Path $runDir "controller.stderr.txt"
    $controllerDeadline = (Get-Date).AddSeconds($MaxSeconds + 30)
    while (-not $game.HasExited -and (Get-Date) -lt $controllerDeadline) {
        try {
            $game.Refresh()
            $elapsed = ((Get-Date) - $start).TotalSeconds
            $line = '"{0}",{1:F3},{2:F3},{3},{4},{5},{6}' -f `
                (Get-Date).ToString("o"),$elapsed,$game.CPU,$game.WorkingSet64,
                $game.PrivateMemorySize64,$game.HandleCount,$game.Threads.Count
            Add-Content -LiteralPath $telemetryPath -Value $line -Encoding utf8
        } catch {
            Add-Content -LiteralPath $telemetryPath `
                -Value ('"{0}",unavailable' -f (Get-Date).ToString("o")) -Encoding utf8
        }
        if (Test-Path -LiteralPath $controllerOut) {
            $state = Get-Content -Raw -LiteralPath $controllerOut -ErrorAction SilentlyContinue
            if ($state -match 'component_state=removed' -and
                $state -match 'hook_bytes_restored=true') {
                $componentRemoved = $true
                break
            }
        }
        if (Test-Path -LiteralPath $controllerErr) {
            $errorText = Get-Content -Raw -LiteralPath $controllerErr -ErrorAction SilentlyContinue
            if ($errorText.Trim()) { throw "M1 controller reported an error: $errorText" }
        }
        Start-Sleep -Seconds 1
    }
    if (-not $componentRemoved) {
        throw "Controlled component removal was not confirmed within the bound."
    }

    & python (Join-Path $toolRoot "analyze_m1_log.py") $runDir
    Write-Output "Component removed and hook bytes independently verified."
    Write-Output "Confirm rendering/HUD/controls, then exit SFC normally."
    $exitObservation = Wait-M1ProcessExit -ProcessId $game.Id `
        -TimeoutSeconds $WaitForExitSeconds
    $normalExitObserved = $exitObservation.Outcome -eq 'exited'
} finally {
    $gameStillRunning = $game -and -not $game.HasExited
    if (-not $gameStillRunning) {
        if (Test-Path -LiteralPath $installedProxy) {
            Remove-Item -LiteralPath $installedProxy
        }
        if (Test-Path -LiteralPath $installedConfig) {
            Remove-Item -LiteralPath $installedConfig
        }
    }
}

$afterMd5 = (Get-FileHash -LiteralPath $client -Algorithm MD5).Hash
$afterSha = (Get-FileHash -LiteralPath $client -Algorithm SHA256).Hash
@{
    completed = (Get-Date).ToString("o")
    component_removed = $componentRemoved
    normal_exit_observed = $normalExitObserved
    exit_outcome = if ($exitObservation) { $exitObservation.Outcome } else { 'not-waited' }
    proxy_removed_after_exit = -not (Test-Path -LiteralPath $installedProxy)
    config_removed_after_exit = -not (Test-Path -LiteralPath $installedConfig)
    client_md5_after = $afterMd5
    client_sha256_after = $afterSha
    client_unchanged = ($afterMd5 -eq $beforeMd5 -and $afterSha -eq $beforeSha)
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runDir "run-result.json") -Encoding utf8

Write-Output "Run complete: $runDir"
Write-Output "Normal exit observed: $normalExitObserved"
Write-Output "Client unchanged: $($afterMd5 -eq $beforeMd5 -and $afterSha -eq $beforeSha)"
