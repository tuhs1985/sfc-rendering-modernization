Set-StrictMode -Version Latest

function ConvertTo-M1GpuMemorySample {
    param([Parameter(Mandatory)][int]$TargetProcessId,
          [AllowEmptyCollection()][object[]]$Rows = @())
    $seen = @{}
    [decimal]$dedicated = 0
    [decimal]$shared = 0
    foreach ($row in $Rows) {
        if ($row.Name -notmatch ('^pid_' + $TargetProcessId + '_luid_.+_phys_\d+$')) { continue }
        if ($seen.ContainsKey($row.Name)) { throw 'Duplicate GPU process memory instance' }
        $seen[$row.Name] = $true
        foreach ($field in @('DedicatedUsage', 'SharedUsage')) {
            if ($null -eq $row.$field -or [decimal]$row.$field -lt 0) {
                throw "Invalid GPU memory field: $field"
            }
        }
        $dedicated += [decimal]$row.DedicatedUsage
        $shared += [decimal]$row.SharedUsage
    }
    [pscustomobject]@{
        status = if ($seen.Count) { 'available' } else { 'unavailable-no-pid-instance' }
        instance_count = $seen.Count
        dedicated_bytes = if ($seen.Count) { $dedicated } else { $null }
        shared_bytes = if ($seen.Count) { $shared } else { $null }
    }
}

Export-ModuleMember -Function ConvertTo-M1GpuMemorySample
