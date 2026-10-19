# Offline test only;does not rebuild or deploy the accepted SFC component.
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/remix-runtime/native-light-tests'
New-Item -ItemType Directory -Path $out -Force | Out-Null
$vcbase='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build'
Push-Location $out
try {
    foreach($arch in @('32','64')){
        $command='"{0}\vcvars{1}.bat" && cl /nologo /std:c++17 /EHsc /W4 /WX "{2}\tests\native_light_snapshot_tests.cpp" /Fe:light_core{1}.exe /link /Brepro' -f $vcbase,$arch,$root
        & $env:ComSpec /d /s /c $command
        if($LASTEXITCODE -ne 0){throw 'Native light core compile failed'}
        & (Join-Path $out "light_core$arch.exe")
        if($LASTEXITCODE -ne 0){throw 'Native light core test failed'}
    }
}finally{Pop-Location}
