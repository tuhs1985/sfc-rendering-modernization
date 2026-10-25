param([Parameter(Mandatory=$true)][string]$TestScene)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$manifest=Get-Content (Join-Path $root 'artifacts/remix-runtime/deps/manifest.json') -Raw | ConvertFrom-Json
if($manifest.source_commit -ne 'b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4' -or (Get-FileHash (Join-Path $root 'artifacts/remix-runtime/deps/remix_c.h')).Hash -ne $manifest.header_sha256){throw 'Pinned API header mismatch'}
$out=Join-Path $root 'artifacts/remix-api-proof/bin'
New-Item -ItemType Directory -Force -Path $out | Out-Null
Push-Location $out
try {
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat'
 $command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX /fp:precise /I"{1}\artifacts\remix-runtime\deps" /I"{1}\tools\d3d9_proof" "{1}\tools\remix_api_proof\api_host.cpp" /Fe:api_host.exe /link /Brepro user32.lib d3d11.lib dxgi.lib d3dcompiler.lib advapi32.lib ole32.lib' -f $vc,$root
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Isolated API host build failed;normal host unchanged'}
 $command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX /fp:precise /I"{1}\artifacts\remix-runtime\deps" /I"{1}\tools\d3d9_proof" "{1}\tools\remix_api_proof\tests\api_renderer_tests.cpp" /Fe:api_renderer_tests.exe /link /Brepro user32.lib' -f $vc,$root
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Isolated API mock build failed'}
 $scene=Join-Path $root $TestScene
 $result=& .\api_renderer_tests.exe $scene
 if($LASTEXITCODE -ne 0){throw 'Isolated API mock failed'}
 $result | Set-Content -Encoding UTF8 api-renderer-tests.txt
 $result | Write-Output
} finally {Pop-Location}
$python='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python -B (Join-Path $PSScriptRoot 'build_record.py') --record
if($LASTEXITCODE -ne 0){throw 'Isolated API lock failed'}
