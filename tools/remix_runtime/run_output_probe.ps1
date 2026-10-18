param([ValidateSet('sharing','rendering','crossprocess','crossprocess-slow','crossprocess-exit','crossprocess-x86')][string]$Mode='sharing')
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$run=Join-Path $root ('artifacts/remix-runtime/runs/'+[DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss-fff'))
New-Item -ItemType Directory -Path $run | Out-Null
$dll=Join-Path $root 'artifacts/remix-runtime/deps/remix-1.5.2/.trex/d3d9.dll'
$exe=Join-Path $root 'artifacts/remix-runtime/bin/output_probe.exe'
if((Get-FileHash $dll).Hash -ne 'F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F'){throw 'Pinned runtime hash mismatch'}
$names=@('DXVK_LOG_LEVEL','DXVK_LOG_PATH','DXVK_GRAPHICS_PRESET_TYPE','RTX_INTEGRATE_INDIRECT_MODE','DXVK_UPSCALER_TYPE','DXVK_RAY_RECONSTRUCTION','RTX_DLSS_PRESET','RTX_ENABLE_ASYNC_COMPILATION')
$saved=@{};foreach($name in $names){$saved[$name]=[Environment]::GetEnvironmentVariable($name,'Process')}
try{
    $env:DXVK_LOG_LEVEL=if($Mode -eq 'rendering'){'info'}else{'error'};$env:DXVK_LOG_PATH=$run
    $env:DXVK_GRAPHICS_PRESET_TYPE='4';$env:RTX_INTEGRATE_INDIRECT_MODE='0'
    # Diagnostic return-path qualification, not DLSS/NRC feature integration.
    $env:DXVK_UPSCALER_TYPE='0';$env:DXVK_RAY_RECONSTRUCTION='False';$env:RTX_DLSS_PRESET='0'
    # Pinned RtxContext::injectRTX skips rendering while async shaders compile.
    # This tiny qualification waits for required compilation, bounded by watchdog.
    $env:RTX_ENABLE_ASYNC_COMPILATION='False'
    $p=Start-Process -FilePath $exe -ArgumentList ('"'+$dll+'" '+$Mode) -WorkingDirectory $run -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $run 'stdout.log') -RedirectStandardError (Join-Path $run 'stderr.log')
    $timer=[Diagnostics.Stopwatch]::StartNew();$warned=$false;$stopReason=$null
    while(-not $p.HasExited){
        $size=(Get-ChildItem -LiteralPath $run -File -Recurse | Measure-Object Length -Sum).Sum
        if($size -gt 16MB -and -not $warned){Write-Warning 'Probe output exceeds16MiB';$warned=$true}
        if($timer.Elapsed.TotalSeconds -gt 120 -or $size -gt 32MB){$stopReason='time/output cap';$p.Kill($true);$p.WaitForExit();break}
        Start-Sleep -Milliseconds 250;$p.Refresh()
    }
    $p.WaitForExit()
    [ordered]@{probe='REMIX-OUTPUT-001';mode=$Mode;exit_code=$p.ExitCode;stop_reason=$stopReason;seconds=$timer.Elapsed.TotalSeconds;dll_sha256=(Get-FileHash $dll).Hash;exe_sha256=(Get-FileHash $exe).Hash;bounds_seconds=120;bounds_bytes=32MB} | ConvertTo-Json | Set-Content (Join-Path $run 'result.json')
    Get-Content (Join-Path $run 'stdout.log');Write-Output "Evidence: $run"
    if($p.ExitCode -ne 0 -or $stopReason){throw 'Standalone output probe did not pass; inspect preserved evidence'}
}finally{foreach($name in $names){[Environment]::SetEnvironmentVariable($name,$saved[$name],'Process')}}
