$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$python='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python (Join-Path $root 'tools/remix_runtime/runtime_candidate.py')
if($LASTEXITCODE -ne 0){throw 'Isolated runtime/header verification failed'}
$include=Join-Path $root 'artifacts/remix-runtime/deps/candidate-1.6.1'
$bin=Join-Path $root 'artifacts/remix-runtime/candidate-1.6.1-bin'
New-Item -ItemType Directory -Force -Path $bin | Out-Null
Push-Location $bin
try {
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat'
 $command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 /fp:precise /I"{1}" "{2}\tools\d3d9_proof\d3d9_direct_host.cpp" /Fe:d3d9_direct_host.exe /link /Brepro user32.lib d3d11.lib dxgi.lib d3dcompiler.lib advapi32.lib ole32.lib' -f $vc,$include,$root
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Candidate host build failed;normal host untouched'}
} finally {Pop-Location}
& $python (Join-Path $root 'tools/remix_runtime/runtime_candidate.py') --record-build
if($LASTEXITCODE -ne 0){throw 'Candidate host build receipt failed'}
