$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$bin=Join-Path $root 'artifacts/remix-runtime/return-bin'
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
$detours=Join-Path $root 'artifacts/remix-runtime/deps/detours/Detours-e4bfd6b03e50de46b47abfbd1e46b384f0c5f833'
Push-Location $bin
try{
    $build='"{0}" && cl.exe /nologo /std:c++20 /EHsc /W4 /WX /I"{2}\include" "{1}\return_launcher.cpp" /Fe:return_launcher.exe /link /Brepro "{2}\lib.X86\detours.lib" bcrypt.lib user32.lib' -f $vc,$PSScriptRoot,$detours
    & $env:ComSpec /d /s /c $build
    if($LASTEXITCODE -ne 0){throw 'Tuning launcher build failed; no game started'}
}finally{Pop-Location}
