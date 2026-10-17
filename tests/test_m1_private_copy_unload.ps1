# Reject before any process access. Impossible PID, no SFC launch/injection.
param([string]$FixtureName='m1_private_copy_unload.ini')
$ErrorActionPreference='Stop'
$PSNativeCommandUseErrorActionPreference=$false
$root=Split-Path $PSScriptRoot -Parent
$controller=Join-Path $root 'artifacts\m1\bin\m1_controller.exe'
$fixture=Join-Path (Join-Path $PSScriptRoot 'fixtures') $FixtureName
$output=& $controller --pid 2147483647 --dll (Join-Path $root 'artifacts\m1\bin\m1_component.dll') --config $fixture --unload-after-stop 1 2>&1
if($LASTEXITCODE -ne 2 -or ($output -join "`n") -notmatch 'forced unload refused') {
    throw 'Private copy forced-unload guard failed'
}
Write-Output 'PASS: private-copy forced unload refused before process access.'
