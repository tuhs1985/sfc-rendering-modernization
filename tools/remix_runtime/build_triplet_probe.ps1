$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$bin=Join-Path $root 'artifacts/remix-runtime/triplet-bin'
New-Item -ItemType Directory -Force -Path $bin | Out-Null
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat'
$vc32=Join-Path (Split-Path $vc -Parent) 'vcvars32.bat'
$header=Join-Path $root 'artifacts/remix-runtime/deps/include/remix/remix_c.h'
if((Get-FileHash $header).Hash -ne 'E623E4956A76894EEEF02361334C7C0458D4EC8BF49F729EC9038C36128BBF47'){throw 'Pinned SDK header mismatch'}
Push-Location $bin
try{
    $build='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /DSFC_TRIPLET_PROBE /DUNICODE /D_UNICODE /I"{1}\artifacts\remix-runtime\deps\include" "{2}\output_probe.cpp" /Fe:output_probe.exe /link /Brepro user32.lib d3d11.lib d3dcompiler.lib advapi32.lib ole32.lib' -f $vc,$root,$PSScriptRoot
    & $env:ComSpec /d /s /c $build
    if($LASTEXITCODE -ne 0){throw 'Triplet x64 producer build failed'}
    $build='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\ship_triplet_consumer.cpp" /Fe:ship_triplet_consumer_x86.exe /link /Brepro d3d11.lib d3dcompiler.lib advapi32.lib ole32.lib' -f $vc32,$PSScriptRoot
    & $env:ComSpec /d /s /c $build
    if($LASTEXITCODE -ne 0){throw 'Triplet x86 consumer build failed'}
    $build='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\tests\ship_compositor_gpu_tests.cpp" /Fe:ship_compositor_gpu_tests.exe /link /Brepro d3d11.lib d3dcompiler.lib advapi32.lib ole32.lib' -f $vc32,$root
    & $env:ComSpec /d /s /c $build
    if($LASTEXITCODE -ne 0){throw 'Ship compositor GPU tests build failed'}
    foreach($compiler in @($vc,$vc32)){
        $name=if($compiler -eq $vc){'wire64.exe'}else{'wire32.exe'}
        $build='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\tests\ship_triplet_tests.cpp" /Fe:{2} /link advapi32.lib ole32.lib' -f $compiler,$root,$name
        & $env:ComSpec /d /s /c $build
        if($LASTEXITCODE -ne 0){throw 'Triplet native wire build failed'}
        & (Join-Path $bin $name)
        if($LASTEXITCODE -ne 0){throw 'Triplet wire test failed'}
    }
}finally{Pop-Location}
