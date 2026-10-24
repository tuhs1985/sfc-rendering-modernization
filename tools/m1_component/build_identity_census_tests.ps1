$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/d3d9-proof/identity-tests'
New-Item -ItemType Directory -Force -Path $out | Out-Null
foreach($arch in @('32','64')){
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars'+$arch+'.bat'
 $cmd='"{0}" && cl /nologo /std:c++17 /EHsc /O2 /W4 /WX "{1}\tests\m1_identity_census_tests.cpp" /Fe:"{2}\identity{3}.exe" /Fo:"{2}\identity{3}.obj" /link /Brepro' -f $vc,$root,$out,$arch
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Identity census native build failed'}
 & (Join-Path $out "identity$arch.exe") (Join-Path $out "identity$arch.json") | Tee-Object -FilePath (Join-Path $out "identity$arch.txt")
 if($LASTEXITCODE -ne 0){throw 'Identity census native tests failed'}
}
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
$cmd='"{0}" && cl /nologo /std:c++17 /EHsc /O2 /MT /arch:SSE2 /W4 /WX "{1}\tests\m1_identity_component_tests.cpp" /Fe:"{2}\identity-component.exe" /Fo:"{2}\identity-component.obj" /link /Brepro' -f $vc,$root,$out
& $env:ComSpec /d /s /c $cmd
if($LASTEXITCODE -ne 0){throw 'Production identity recorder fixture build failed'}
& (Join-Path $out 'identity-component.exe') (Join-Path $out 'identity-component.json') | Tee-Object -FilePath (Join-Path $out 'identity-component.txt')
if($LASTEXITCODE -ne 0){throw 'Production identity recorder fixture failed'}
