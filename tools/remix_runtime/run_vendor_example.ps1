# Control: unmodified source from the pinned official SDK; no game integration.
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$runtime=Join-Path $root 'artifacts/remix-runtime/deps/remix-1.5.2/.trex'
$exe=Join-Path $root 'artifacts/remix-runtime/bin/vendor_example.exe'
if((Get-FileHash (Join-Path $runtime 'd3d9.dll')).Hash -ne 'F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F'){throw 'Pinned runtime hash mismatch'}
$work=Join-Path $root ('artifacts/remix-runtime/runs/'+[DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss-fff')+'-vendor')
New-Item -ItemType Directory -Path $work | Out-Null
# Separate immutable DLL alias; no runtime binary edited. Excluded from log budget/archive.
New-Item -ItemType HardLink -Path (Join-Path $work 'd3d9.dll') -Target (Join-Path $runtime 'd3d9.dll') | Out-Null
$settings=@{PATH="$runtime;$env:PATH";DXVK_LOG_PATH=$work;DXVK_LOG_LEVEL='info';DXVK_GRAPHICS_PRESET_TYPE='4';RTX_INTEGRATE_INDIRECT_MODE='0';DXVK_UPSCALER_TYPE='0';DXVK_RAY_RECONSTRUCTION='False';RTX_DLSS_PRESET='0';RTX_ENABLE_ASYNC_COMPILATION='False'}
$saved=@{};foreach($key in $settings.Keys){$saved[$key]=[Environment]::GetEnvironmentVariable($key,'Process');[Environment]::SetEnvironmentVariable($key,$settings[$key],'Process')}
try{
    $p=Start-Process -FilePath $exe -ArgumentList '32' -WorkingDirectory $work -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $work 'stdout.log') -RedirectStandardError (Join-Path $work 'stderr.log')
    $timer=[Diagnostics.Stopwatch]::StartNew();$stopReason=$null;$warned=$false
    while(-not $p.HasExited){
        $size=(Get-ChildItem -LiteralPath $work -File -Recurse | Where-Object Name -ne 'd3d9.dll' | Measure-Object Length -Sum).Sum
        if($size -gt 16MB -and -not $warned){Write-Warning 'Vendor probe output exceeds16MiB';$warned=$true}
        if($timer.Elapsed.TotalSeconds -gt 120 -or $size -gt 32MB){$stopReason='time/output cap';$p.Kill($true);$p.WaitForExit();break}
        Start-Sleep -Milliseconds 250;$p.Refresh()
    }
    $p.WaitForExit()
    [ordered]@{probe='REMIX-OUTPUT-001';mode='official-unmodified-example';source_sha256=(Get-FileHash (Join-Path $root 'artifacts/remix-runtime/deps/remixapi_example_c.c')).Hash;exe_sha256=(Get-FileHash $exe).Hash;dll_sha256=(Get-FileHash (Join-Path $work 'd3d9.dll')).Hash;exit_code=$p.ExitCode;stop_reason=$stopReason;seconds=$timer.Elapsed.TotalSeconds;frames=32;bounds_seconds=120;bounds_bytes=32MB;environment=$settings} | ConvertTo-Json | Set-Content (Join-Path $work 'result.json')
    Get-Content (Join-Path $work 'stdout.log');Write-Output "Evidence: $work"
    if($p.ExitCode -ne 0 -or $stopReason){throw 'Official SDK control did not exit normally'}
}finally{foreach($key in $saved.Keys){[Environment]::SetEnvironmentVariable($key,$saved[$key],'Process')}}
