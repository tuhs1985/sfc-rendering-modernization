$ErrorActionPreference = 'Stop'
Import-Module "$PSScriptRoot\..\tools\m1_component\ProcessImagePath.psm1" -Force
$expected = [Diagnostics.Process]::GetCurrentProcess().MainModule.FileName
$actual = Get-M1ProcessImagePath -ProcessId $PID
if ($actual -ne $expected) { throw "Wrong image path: $actual; expected $expected" }
# A missing PID must throw, never silently return an assumed installed client.
$rejected = $false
try { Get-M1ProcessImagePath -ProcessId 2147483647 | Out-Null }
catch { $rejected = $true }
if (-not $rejected) { throw 'Missing PID was accepted.' }
$missing = Wait-M1ProcessExit -ProcessId 2147483647 -TimeoutSeconds 1
if ($missing.Outcome -ne 'exited') { throw 'Missing PID was not classified as exited.' }
$self = Wait-M1ProcessExit -ProcessId $PID -TimeoutSeconds 1
if ($self.Outcome -ne 'timeout-running') { throw 'Live PID was not classified as running.' }
Write-Output 'PASS: image query and bounded exit classifications.'
