$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/m1/bin'
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
Push-Location $out
try {
    foreach($unit in @(@('tools\m1_component\m1_controller.cpp','m1_controller.exe'),@('tests\m1_module_snapshot_tests.cpp','m1_module_snapshot_tests.exe'))){
        $command='"{0}" && cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /arch:SSE2 "{1}\{2}" /Fe:"{3}"' -f $vc,$root,$unit[0],$unit[1]
        & $env:ComSpec /d /s /c $command
        if($LASTEXITCODE -ne 0){throw 'Bounded gate-controller build failed'}
    }
    & (Join-Path $out 'm1_module_snapshot_tests.exe')
    if($LASTEXITCODE -ne 0){throw 'Bounded module snapshot tests failed'}
} finally {Pop-Location}
