$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$bin=Join-Path $root 'artifacts/remix-runtime/live-return-bin'
New-Item -ItemType Directory -Force -Path $bin | Out-Null
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
$vc64=Join-Path (Split-Path $vc -Parent) 'vcvars64.bat'
$detours=Join-Path $root 'artifacts/remix-runtime/deps/detours/Detours-e4bfd6b03e50de46b47abfbd1e46b384f0c5f833'
$header=Join-Path $root 'artifacts/remix-runtime/deps/include/remix/remix_c.h'
if((Get-FileHash $header).Hash -ne 'E623E4956A76894EEEF02361334C7C0458D4EC8BF49F729EC9038C36128BBF47'){throw 'Pinned SDK mismatch'}
Push-Location $bin
try{
    $import='"{0}" && lib /nologo /machine:X86 /def:"{1}\reshade_registration.def" /out:reshade_registration.lib' -f $vc,$PSScriptRoot
    & $env:ComSpec /d /s /c $import
    if($LASTEXITCODE -ne 0){throw 'Live return import failed'}
    $build='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /DSFC_LIVE_RETURN /LD /I"{1}\artifacts\remix-runtime\deps\reshade\include" /I"{3}\include" "{2}\return_addon.cpp" /Fe:SFCRemixReturn.dll /link /Brepro /DEF:"{2}\return_addon.def" "{3}\lib.X86\detours.lib" reshade_registration.lib d3d11.lib d3dcompiler.lib advapi32.lib ole32.lib user32.lib' -f $vc,$root,$PSScriptRoot,$detours
    & $env:ComSpec /d /s /c $build
    if($LASTEXITCODE -ne 0){throw 'Private live addon build failed'}
    $build='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /I"{1}\artifacts\remix-runtime\deps\include" "{2}\ship_live_host.cpp" /Fe:ship_live_host.exe /link /Brepro d3d11.lib user32.lib advapi32.lib ole32.lib' -f $vc64,$root,$PSScriptRoot
    & $env:ComSpec /d /s /c $build
    if($LASTEXITCODE -ne 0){throw 'Fresh SDK host build failed'}
    $build='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\ship_image_reader.cpp" /Fe:ship_image_reader.exe /link /Brepro d3d11.lib dxgi.lib user32.lib advapi32.lib ole32.lib' -f $vc64,$PSScriptRoot
    & $env:ComSpec /d /s /c $build
    if($LASTEXITCODE -ne 0){throw 'Prepared-image external reader build failed'}
    $build='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\ship_live_gpu_fixture.cpp" /Fe:ship_live_gpu_fixture.exe /link /Brepro d3d11.lib d3dcompiler.lib advapi32.lib ole32.lib user32.lib' -f $vc,$PSScriptRoot
    & $env:ComSpec /d /s /c $build
    if($LASTEXITCODE -ne 0){throw 'Private native fixture build failed'}
    foreach($compiler in @($vc,$vc64)){
        $name=if($compiler -eq $vc){'live_request32.exe'}else{'live_request64.exe'}
        $build='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\tests\ship_live_request_tests.cpp" /Fe:{2} /link /Brepro advapi32.lib ole32.lib' -f $compiler,$root,$name
        & $env:ComSpec /d /s /c $build
        if($LASTEXITCODE -ne 0){throw 'Fresh request test build failed'}
        & (Join-Path $bin $name)
        if($LASTEXITCODE -ne 0){throw 'Fresh request tests failed'}
        $uvname=if($compiler -eq $vc){'remix_uv32.exe'}else{'remix_uv64.exe'}
        $build='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\tests\remix_texture_coordinate_tests.cpp" /Fe:{2} /link /Brepro' -f $compiler,$root,$uvname
        & $env:ComSpec /d /s /c $build
        if($LASTEXITCODE -ne 0){throw 'Remix UV adapter test build failed'}
        & (Join-Path $bin $uvname)
        if($LASTEXITCODE -ne 0){throw 'Remix UV adapter tests failed'}
    }
}finally{Pop-Location}
