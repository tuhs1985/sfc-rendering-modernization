$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$bin=Join-Path $root 'artifacts/d3d9-proof/texture-memory-tests'
New-Item -ItemType Directory -Force -Path $bin | Out-Null
Push-Location $bin
try {
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat'
 $command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 "{1}\tests\texture_memory_probe.cpp" /Fe:texture_memory_probe.exe' -f $vc,$root
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Texture memory probe build failed'}
 $command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 "{1}\tests\slow_completion_tests.cpp" /Fe:slow_completion_tests.exe' -f $vc,$root
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Slow completion tests build failed'}
 & .\slow_completion_tests.exe
 if($LASTEXITCODE -ne 0){throw 'Slow completion tests failed'}
} finally {Pop-Location}
