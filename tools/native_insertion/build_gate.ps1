$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/player-replacement/native-gate-tests'
New-Item -ItemType Directory -Force $out | Out-Null
foreach($arch in @('32','64')){
 $vc="C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars$arch.bat"
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX /sourceDependencies "{1}\core{2}.deps.json" "{3}\tools\native_insertion\gate_tests.cpp" /Fe:"{1}\core{2}.exe" /Fo:"{1}\core{2}.obj" /link /Brepro advapi32.lib ole32.lib' -f $vc,$out,$arch,$root
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Native gate core build failed'}
 & (Join-Path $out "core$arch.exe") | Tee-Object -FilePath (Join-Path $out "core$arch.txt")
 if($LASTEXITCODE -ne 0){throw 'Native gate core failed'}
}
$client='C:\Games\Taldren Software Inc\Starfleet Command Orion Pirates\StarFleetOP.exe'
if((Get-FileHash -LiteralPath $client).Hash -ne '4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29'){throw 'Pinned native client mismatch'}
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
$cmd='"{0}" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX "{1}\tools\native_insertion\flush_qualification.cpp" /Fe:"{2}\flush.exe" /Fo:"{2}\flush.obj" /link /Brepro' -f $vc,$root,$out
& $env:ComSpec /d /s /c $cmd
if($LASTEXITCODE -ne 0){throw 'Native flush build failed'}
& (Join-Path $out 'flush.exe') $client | Tee-Object -FilePath (Join-Path $out 'flush.txt')
if($LASTEXITCODE -ne 0){throw 'Native flush qualification failed'}
$bin=Join-Path $root 'artifacts/remix-runtime/return-bin'
Push-Location $bin
try{
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\tools\remix_runtime\return_fixture.cpp" /Fe:d3d11_return_fixture.exe /link d3d11.lib d3dcompiler.lib advapi32.lib ole32.lib user32.lib dbghelp.lib' -f $vc,$root
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Native gate genuine-return fixture build failed'}
}finally{Pop-Location}
# Build the actual interface endpoints,not just test-local copies.
$detours=Join-Path $root 'artifacts/remix-runtime/deps/detours/Detours-e4bfd6b03e50de46b47abfbd1e46b384f0c5f833'
Push-Location $bin
try{
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /LD /I"{1}/artifacts/remix-runtime/deps/reshade/include" /I"{2}/include" "{1}/tools/remix_runtime/return_addon.cpp" /Fe:SFCRemixReturn.dll /link /Brepro /DEF:"{1}/tools/remix_runtime/return_addon.def" "{2}/lib.X86/detours.lib" reshade_registration.lib d3d11.lib d3dcompiler.lib advapi32.lib ole32.lib user32.lib' -f $vc,$root,$detours
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Native insertion return adapter build failed'}
}finally{Pop-Location}
$component=Join-Path $root 'artifacts/remix-runtime/native-light-tests'
$cmd='"{0}" && cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /arch:SSE2 /DSFC_NATIVE_LIGHT_DISCOVERY /LD "{1}/tools/m1_component/m1_component.cpp" /Fo:"{2}/m1_component.obj" /Fe:"{2}/m1_light_component.dll" /link /Brepro /DEF:"{1}/tools/m1_component/native_light_component.def"' -f $vc,$root,$component
& $env:ComSpec /d /s /c $cmd
if($LASTEXITCODE -ne 0){throw 'Native insertion capture component build failed'}
foreach($test in @('m1_player_replacement_component_tests','m1_corner_snapshot_tests')){
 $cmd='"{0}" && cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT "{1}/tests/{2}.cpp" /Fo:"{3}/{2}.obj" /Fe:"{3}/{2}.exe" /link /Brepro user32.lib' -f $vc,$root,$test,$out
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Actual capture/hook lifetime fixture build failed'}
 & (Join-Path $out "$test.exe") | Tee-Object -FilePath (Join-Path $out "$test.txt")
 if($LASTEXITCODE -ne 0){throw 'Actual capture/hook lifetime fixture failed'}
}
