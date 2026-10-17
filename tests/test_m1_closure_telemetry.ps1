$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot '../tools/m1_component/M1ClosureTelemetry.psm1') -Force
$rows = @(
    @{Name='pid_42_luid_0x0_0x1_phys_0';DedicatedUsage=10;SharedUsage=20},
    @{Name='pid_42_luid_0x0_0x2_phys_1';DedicatedUsage=30;SharedUsage=40},
    @{Name='pid_420_luid_0x0_0x1_phys_0';DedicatedUsage=999;SharedUsage=999})
$sample = ConvertTo-M1GpuMemorySample -TargetProcessId 42 -Rows $rows
if ($sample.dedicated_bytes -ne 40 -or $sample.shared_bytes -ne 60 -or
    $sample.instance_count -ne 2 -or $sample.status -ne 'available') { throw 'PID/adapter aggregation failed' }
$missing = ConvertTo-M1GpuMemorySample -TargetProcessId 9 -Rows $rows
if ($null -ne $missing.dedicated_bytes -or $missing.status -eq 'available') { throw 'Missing != zero' }
foreach ($bad in @(@($rows[0],$rows[0]),@(@{Name=$rows[0].Name;DedicatedUsage=-1;SharedUsage=0}))) {
    $rejected=$false
    try { ConvertTo-M1GpuMemorySample -TargetProcessId 42 -Rows $bad | Out-Null }
    catch { $rejected=$true }
    if (-not $rejected) { throw 'Invalid/duplicate input accepted' }
}
Write-Output 'M1 closure GPU memory contract tests passed.'
