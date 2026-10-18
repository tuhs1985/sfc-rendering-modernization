$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$bin=Join-Path $root 'artifacts/remix-runtime/return-bin'
New-Item -ItemType Directory -Force -Path $bin | Out-Null
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
$detours=Join-Path $root 'artifacts/remix-runtime/deps/detours/Detours-e4bfd6b03e50de46b47abfbd1e46b384f0c5f833'
Push-Location $bin
try{
    $command='"{0}" && cl.exe /nologo /std:c++20 /EHsc /W4 /WX /I"{1}\artifacts\remix-runtime\deps\reshade\include" "{2}\reshade_abi_probe.cpp" /Fe:reshade_abi_probe.exe /link user32.lib' -f $vc,$root,$PSScriptRoot
    & $env:ComSpec /d /s /c $command
    if($LASTEXITCODE -ne 0){throw 'ReShade ABI probe build failed'}
    $import='"{0}" && lib.exe /nologo /machine:X86 /def:"{1}\reshade_registration.def" /out:reshade_registration.lib' -f $vc,$PSScriptRoot
    & $env:ComSpec /d /s /c $import
    if($LASTEXITCODE -ne 0){throw 'Copied proxy registration import library failed'}
    $addon='"{0}" && cl.exe /nologo /std:c++20 /EHsc /W4 /WX /LD /I"{1}\artifacts\remix-runtime\deps\reshade\include" /I"{3}\include" "{2}\return_addon.cpp" /Fe:SFCRemixReturn.dll /link /Brepro /DEF:"{2}\return_addon.def" "{3}\lib.X86\detours.lib" reshade_registration.lib d3d11.lib d3dcompiler.lib advapi32.lib ole32.lib user32.lib' -f $vc,$root,$PSScriptRoot,$detours
    & $env:ComSpec /d /s /c $addon
    if($LASTEXITCODE -ne 0){throw 'Return add-on build failed'}
    $fixture='"{0}" && cl.exe /nologo /std:c++20 /EHsc /W4 /WX "{1}\return_fixture.cpp" /Fe:d3d11_return_fixture.exe /link d3d11.lib d3dcompiler.lib advapi32.lib ole32.lib user32.lib dbghelp.lib' -f $vc,$PSScriptRoot
    & $env:ComSpec /d /s /c $fixture
    if($LASTEXITCODE -ne 0){throw 'Return fixture build failed'}
    $launcher='"{0}" && cl.exe /nologo /std:c++20 /EHsc /W4 /WX /I"{2}\include" "{1}\return_launcher.cpp" /Fe:return_launcher.exe /link "{2}\lib.X86\detours.lib" bcrypt.lib user32.lib' -f $vc,$PSScriptRoot,$detours
    & $env:ComSpec /d /s /c $launcher
    if($LASTEXITCODE -ne 0){throw 'Verified startup launcher build failed'}
    $test='"{0}" && cl.exe /nologo /std:c++20 /EHsc /W4 /WX "{1}\tests\remix_return_wire_tests.cpp" /Fe:return_wire_tests.exe /link advapi32.lib ole32.lib' -f $vc,$root
    & $env:ComSpec /d /s /c $test
    if($LASTEXITCODE -ne 0){throw 'Return wire native tests build failed'}
    & (Join-Path $bin 'return_wire_tests.exe')
    if($LASTEXITCODE -ne 0){throw 'Return wire native tests failed'}
    $searchTest='"{0}" && cl.exe /nologo /std:c++20 /EHsc /W4 /WX "{1}\tests\depth_search_wire_tests.cpp" /Fe:depth_search_wire_tests.exe' -f $vc,$root
    & $env:ComSpec /d /s /c $searchTest
    if($LASTEXITCODE -ne 0){throw 'Expanded search tests build failed'}
    & (Join-Path $bin 'depth_search_wire_tests.exe')
    if($LASTEXITCODE -ne 0){throw 'Expanded search tests failed'}
    $broadTest='"{0}" && cl.exe /nologo /std:c++20 /EHsc /W4 /WX "{1}\tests\broad_trace_tests.cpp" /Fe:broad_trace_tests.exe /link advapi32.lib ole32.lib' -f $vc,$root
    & $env:ComSpec /d /s /c $broadTest
    if($LASTEXITCODE -ne 0){throw 'Broad metadata tests build failed'}
    & (Join-Path $bin 'broad_trace_tests.exe')
    if($LASTEXITCODE -ne 0){throw 'Broad metadata tests failed'}
    $depthTest='"{0}" && cl.exe /nologo /std:c++20 /EHsc /W4 /WX /I"{1}\artifacts\remix-runtime\deps\reshade\include" "{1}\tests\depth_snapshot_gpu_tests.cpp" /Fe:depth_snapshot_gpu_tests.exe /link d3d11.lib d3dcompiler.lib advapi32.lib ole32.lib' -f $vc,$root
    & $env:ComSpec /d /s /c $depthTest
    if($LASTEXITCODE -ne 0){throw 'Depth snapshot GPU test build failed'}
    $vc64=Join-Path (Split-Path $vc -Parent) 'vcvars64.bat'
    $calibrationTest='"{0}" && cl.exe /nologo /std:c++20 /EHsc /W4 /WX "{1}\tests\present_calibration_tests.cpp" /Fe:present_calibration_tests.exe' -f $vc,$root
    & $env:ComSpec /d /s /c $calibrationTest
    if($LASTEXITCODE -ne 0){throw 'Present calibration tests build failed'}
    & (Join-Path $bin 'present_calibration_tests.exe')
    if($LASTEXITCODE -ne 0){throw 'Present calibration tests failed'}
    $hostBuild='"{0}" && cl.exe /nologo /std:c++20 /EHsc /W4 /WX /I"{1}\artifacts\remix-runtime\deps\include" "{2}\return_host.cpp" /Fe:return_host.exe /link user32.lib advapi32.lib ole32.lib d3d11.lib' -f $vc64,$root,$PSScriptRoot
    & $env:ComSpec /d /s /c $hostBuild
    if($LASTEXITCODE -ne 0){throw 'Return runtime host build failed'}
}finally{Pop-Location}
