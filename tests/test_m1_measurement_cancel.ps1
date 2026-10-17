$ErrorActionPreference='Stop'
Import-Module (Join-Path $PSScriptRoot '../tools/m1_component/M1MeasurementJobs.psm1') -Force
$root=Join-Path $PSScriptRoot ('../artifacts/m1/test-temp/cancel-'+[guid]::NewGuid().ToString('N'))
[void][IO.Directory]::CreateDirectory($root)
$stopPath=Join-Path $root 'measurement-stop.signal'
$process=[pscustomobject]@{ExitCode=1;Disposed=$false}
$process | Add-Member ScriptMethod WaitForExit {param($milliseconds) return $true}
$process | Add-Member ScriptMethod Dispose {$this.Disposed=$true}
$job=[pscustomobject]@{Name='fixture';Process=$process;StopPath=$stopPath;
    Out=[Threading.Tasks.Task]::FromResult[string]('{"complete":false}');
    Err=[Threading.Tasks.Task]::FromResult[string]('cancelled')}
$result=Complete-M1MeasurementJobs -Jobs @($job) -OutputDirectory $root -Cancel
if($result -or -not(Test-Path -LiteralPath $stopPath) -or -not $process.Disposed){throw 'Cancellation was not recorded/failed correctly'}
if((Get-Content -Raw -LiteralPath (Join-Path $root 'fixture.stderr.txt')) -ne 'cancelled'){throw 'Evidence lost on cancellation'}
Write-Output 'M1 measurement cancellation/failed-result tests passed; fixture retained ignored.'
