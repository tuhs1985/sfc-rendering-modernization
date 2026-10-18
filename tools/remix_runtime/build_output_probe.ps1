$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$bin=Join-Path $root 'artifacts/remix-runtime/bin'
New-Item -ItemType Directory -Force -Path $bin | Out-Null
$header=Join-Path $root 'artifacts/remix-runtime/deps/include/remix/remix_c.h'
if((Get-FileHash $header).Hash -ne 'E623E4956A76894EEEF02361334C7C0458D4EC8BF49F729EC9038C36128BBF47'){throw 'Pinned SDK header mismatch'}
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat'
if(-not(Test-Path $vc)){throw 'Pinned VS2026 x64 environment missing'}
Push-Location $bin
try{
    $command='"{0}" && cl.exe /nologo /std:c++20 /EHsc /W4 /WX /DUNICODE /D_UNICODE /I"{1}\artifacts\remix-runtime\deps\include" "{2}\output_probe.cpp" /Fe:output_probe.exe /link user32.lib d3d11.lib d3dcompiler.lib advapi32.lib ole32.lib' -f $vc,$root,$PSScriptRoot
    & $env:ComSpec /d /s /c $command
    if($LASTEXITCODE -ne 0){throw "Compiler failed: $LASTEXITCODE"}
    $vendor='"{0}" && cl.exe /nologo /std:c11 /W3 /I"{1}\artifacts\remix-runtime\deps\include" "{1}\artifacts\remix-runtime\deps\remixapi_example_c.c" /Fe:vendor_example.exe /link user32.lib' -f $vc,$root
    & $env:ComSpec /d /s /c $vendor
    if($LASTEXITCODE -ne 0){throw 'Official unmodified SDK example build failed'}
    $test='"{0}" && cl.exe /nologo /std:c++20 /EHsc /W4 /WX "{1}\tests\remix_output_contract_tests.cpp" /Fe:output_contract_tests.exe /link advapi32.lib ole32.lib d3d11.lib' -f $vc,$root
    & $env:ComSpec /d /s /c $test
    if($LASTEXITCODE -ne 0){throw 'Output contract test build failed'}
    & (Join-Path $bin 'output_contract_tests.exe')
    if($LASTEXITCODE -ne 0){throw 'Output contract tests failed'}
    $vc32=Join-Path (Split-Path $vc -Parent) 'vcvars32.bat'
    $consumer='"{0}" && cl.exe /nologo /std:c++20 /EHsc /W4 /WX "{1}\output_consumer.cpp" /Fe:output_consumer_x86.exe /link d3d11.lib advapi32.lib ole32.lib' -f $vc32,$PSScriptRoot
    & $env:ComSpec /d /s /c $consumer
    if($LASTEXITCODE -ne 0){throw 'x86 output consumer build failed'}
}finally{Pop-Location}
