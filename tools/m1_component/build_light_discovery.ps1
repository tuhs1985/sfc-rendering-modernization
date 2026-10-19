# Dedicated observer variant;accepted m1_component.dll is NOT overwritten.
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/remix-runtime/native-light-tests'
$vcbase='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build'
& (Join-Path $PSScriptRoot 'build_native_light_tests.ps1')
Push-Location $out
try {
    foreach($arch in @('32','64')){
        $command='"{0}\vcvars{1}.bat" && cl /nologo /std:c++17 /EHsc /W4 /WX "{2}\tests\native_light_observer_tests.cpp" /Fe:observer{1}.exe /link /Brepro' -f $vcbase,$arch,$root
        & $env:ComSpec /d /s /c $command
        if($LASTEXITCODE -ne 0){throw 'Light observer test build failed'}
        & (Join-Path $out "observer$arch.exe") (Join-Path $out "observer$arch.bin") | Tee-Object -FilePath (Join-Path $out "observer$arch.txt")
        if($LASTEXITCODE -ne 0){throw 'Light observer tests failed'}
    }
    $command='"{0}\vcvars32.bat" && cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /arch:SSE2 /DSFC_NATIVE_LIGHT_DISCOVERY /LD "{1}\m1_component.cpp" /Fe:m1_light_component.dll /link /Brepro /DEF:"{1}\native_light_component.def"' -f $vcbase,$PSScriptRoot
    & $env:ComSpec /d /s /c $command
    if($LASTEXITCODE -ne 0){throw 'Dedicated light component build failed'}
    $command='"{0}\vcvars32.bat" && cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /arch:SSE2 /DSFC_NATIVE_LIGHT_DISCOVERY "{1}\tests\m1_live_scene_tests.cpp" /Fe:scene_observer.exe /link /Brepro' -f $vcbase,$root
    & $env:ComSpec /d /s /c $command
    if($LASTEXITCODE -ne 0){throw 'Actual scene/worker observer test build failed'}
}finally{Pop-Location}
& 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' (Join-Path $root 'tools/remix_runtime/light_discovery.py')
if($LASTEXITCODE -ne 0){throw 'Light discovery qualification failed'}
