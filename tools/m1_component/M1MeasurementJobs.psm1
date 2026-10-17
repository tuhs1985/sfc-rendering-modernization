function Start-M1MeasurementJobs {
    param([int]$TargetProcessId, [int]$Seconds, [string]$OutputDirectory,
          [string]$PythonExecutable)
    $tool = Join-Path $PSScriptRoot '../../artifacts/m1/tools/PresentMon-2.3.1-x64.exe'
    if ((Get-FileHash -LiteralPath $tool -Algorithm SHA256).Hash -ne
        '364E5D98D4D134BD54DD25C22ED2CA2F4883F8BC3ED6502BEE0C151E3436D30C') {
        throw 'Pinned PresentMon hash mismatch'
    }
    $stopPath = Join-Path $OutputDirectory 'measurement-stop.signal'
    if (Test-Path -LiteralPath $stopPath) { throw 'Existing measurement stop signal; use a fresh directory' }
    $specs = @(
        @{Name='frames';Exe=$PythonExecutable;Args=@((Join-Path $PSScriptRoot 'capture_m1_frametimes.py'),
            '--tool',$tool,'--pid',"$TargetProcessId",'--seconds',"$Seconds",'--output',
            (Join-Path $OutputDirectory 'frames.csv'),'--stop-file',$stopPath)},
        @{Name='memory';Exe=(Get-Process -Id $PID).Path;Args=@('-NoProfile','-File',
            (Join-Path $PSScriptRoot 'capture_m1_memory.ps1'),'-TargetProcessId',"$TargetProcessId",
            '-Seconds',"$Seconds",'-OutputPath',(Join-Path $OutputDirectory 'memory.jsonl'),
            '-StopFile',$stopPath)})
    $jobs = @()
    try {
        foreach ($spec in $specs) {
            $info = [Diagnostics.ProcessStartInfo]::new()
            $info.FileName=$spec.Exe; $info.UseShellExecute=$false; $info.CreateNoWindow=$true
            $info.RedirectStandardOutput=$true; $info.RedirectStandardError=$true
            foreach ($argument in $spec.Args) { [void]$info.ArgumentList.Add($argument) }
            $process = [Diagnostics.Process]::Start($info)
            $jobs += [pscustomobject]@{Name=$spec.Name;Process=$process;StopPath=$stopPath;
                Out=$process.StandardOutput.ReadToEndAsync();Err=$process.StandardError.ReadToEndAsync()}
        }
    } catch {
        # Request owned collectors' graceful cancellation; never kill SFC or
        # orphan an ETW grandchild while waiting for a full endurance duration.
        [IO.File]::WriteAllText($stopPath, 'collector-start-failure')
        foreach ($job in $jobs) { [void]$job.Process.WaitForExit(25000) }
        throw
    }
    return $jobs
}

function Complete-M1MeasurementJobs {
    param([object[]]$Jobs, [string]$OutputDirectory, [switch]$Cancel)
    if ($Cancel -and $Jobs.Count) {
        [IO.File]::WriteAllText($Jobs[0].StopPath, 'runner-ended-before-capture-complete')
    }
    $okay=$true
    foreach ($job in $Jobs) {
        if (-not $job.Process.WaitForExit(25000)) {
            throw "Bounded measurement collector failed to stop: $($job.Name); do not kill SFC"
        }
        $stdout=$job.Out.GetAwaiter().GetResult()
        $stderr=$job.Err.GetAwaiter().GetResult()
        [IO.File]::WriteAllText((Join-Path $OutputDirectory ($job.Name+'.result.json')), $stdout)
        [IO.File]::WriteAllText((Join-Path $OutputDirectory ($job.Name+'.stderr.txt')), $stderr)
        if ($job.Process.ExitCode -ne 0) { $okay=$false }
        $job.Process.Dispose()
    }
    return $okay
}
Export-ModuleMember -Function Start-M1MeasurementJobs,Complete-M1MeasurementJobs
