param(
    [Parameter(Mandatory)][ValidateRange(1, 2147483647)][int]$TargetProcessId,
    [Parameter(Mandatory)][ValidateRange(1, 2100)][int]$Seconds,
    [Parameter(Mandatory)][string]$OutputPath,
    [string]$StopFile
)
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'M1ClosureTelemetry.psm1') -Force
$game = Get-Process -Id $TargetProcessId
$identityStart = $game.StartTime.ToUniversalTime().ToString('o')
$fullOutput = [IO.Path]::GetFullPath($OutputPath)
$summaryPath = $fullOutput + '.summary.json'
if ((Test-Path -LiteralPath $fullOutput) -or (Test-Path -LiteralPath $summaryPath)) {
    throw 'Use fresh output paths; evidence is never overwritten'
}
[void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($fullOutput))
$encoding = [Text.UTF8Encoding]::new($false)
$file = [IO.FileStream]::new($fullOutput, [IO.FileMode]::CreateNew,
    [IO.FileAccess]::Write, [IO.FileShare]::Read)
$clock = [Diagnostics.Stopwatch]::StartNew()
$records = 0; $available = 0; $reason = 'duration'; $failure = $null
try {
    while ($clock.Elapsed.TotalSeconds -lt $Seconds -and $records -lt 2101) {
        if ($StopFile -and (Test-Path -LiteralPath $StopFile)) { $reason='cancelled'; break }
        $nextSample = $clock.Elapsed.TotalSeconds + 1
        $game.Refresh()
        if ($game.HasExited) { $reason = 'process-exited'; break }
        if ($game.StartTime.ToUniversalTime().ToString('o') -ne $identityStart) {
            $reason = 'process-identity-changed'; break
        }
        $gpuError = $null
        try {
            $rows = @(Get-CimInstance -ClassName Win32_PerfFormattedData_GPUPerformanceCounters_GPUProcessMemory `
                -Filter "Name LIKE 'pid_${TargetProcessId}_%'" -OperationTimeoutSec 2)
            $gpu = ConvertTo-M1GpuMemorySample -TargetProcessId $TargetProcessId -Rows $rows
        } catch {
            $gpuError = $_.Exception.Message.Substring(0, [Math]::Min(512, $_.Exception.Message.Length))
            $gpu = [pscustomobject]@{status='unavailable-query-error';instance_count=0;
                dedicated_bytes=$null;shared_bytes=$null}
        }
        $record = [ordered]@{timestamp=[DateTime]::UtcNow.ToString('o');
            elapsed_seconds=$clock.Elapsed.TotalSeconds;target_pid=$TargetProcessId;
            process_start_utc=$identityStart;working_set_bytes=$game.WorkingSet64;
            private_bytes=$game.PrivateMemorySize64;gpu=$gpu;gpu_error=$gpuError}
        $bytes = $encoding.GetBytes(($record | ConvertTo-Json -Compress -Depth 4) + "`n")
        if ($file.Length + $bytes.Length -gt 2097152) { $reason = 'size-cap'; break }
        $file.Write($bytes, 0, $bytes.Length)
        $file.Flush()
        $records++
        if ($gpu.status -eq 'available') { $available++ }
        $next = [Math]::Min($Seconds, $nextSample)
        $sleepMs = [Math]::Max(0, [int](1000 * ($next - $clock.Elapsed.TotalSeconds)))
        if ($sleepMs) { Start-Sleep -Milliseconds $sleepMs }
    }
} catch { $failure = $_.Exception.Message; $reason = 'error' }
finally { $file.Dispose(); $clock.Stop() }
$summary = [ordered]@{schema='m1.memory.v1';target_pid=$TargetProcessId;
    process_start_utc=$identityStart;requested_seconds=$Seconds;
    elapsed_seconds=$clock.Elapsed.TotalSeconds;records=$records;
    gpu_available_records=$available;stop_reason=$reason;error=$failure;
    bytes=(Get-Item -LiteralPath $fullOutput).Length;
    complete=($reason -eq 'duration' -and $available -eq $records -and $records -gt 0)}
[IO.File]::WriteAllText($summaryPath, ($summary | ConvertTo-Json), $encoding)
$summary | ConvertTo-Json
if (-not $summary.complete) { exit 1 }
