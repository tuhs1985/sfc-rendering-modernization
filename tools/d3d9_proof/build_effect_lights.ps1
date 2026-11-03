$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/player-replacement/effect-light-tests'
New-Item -ItemType Directory -Force $out | Out-Null
foreach($arch in @('32','64')){
 $vc="C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars$arch.bat"
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 "{1}\tests\effect_light_tests.cpp" /Fe:"{2}\effect{3}.exe" /Fo:"{2}\effect{3}.obj" /link /Brepro' -f $vc,$root,$out,$arch
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Effect-light test build failed'}
 & (Join-Path $out "effect$arch.exe") (Join-Path $out "trace$arch.bin") | Tee-Object -FilePath (Join-Path $out "effect$arch.txt")
 if($LASTEXITCODE -ne 0){throw 'Effect-light source/lifecycle test failed'}
}
