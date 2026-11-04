$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/player-replacement/damage-tests'
New-Item -ItemType Directory -Force -Path $out | Out-Null
foreach($arch in @('32','64')){
 $vc="C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars$arch.bat"
 $cmd='"{0}" && cl /nologo /std:c++17 /EHsc /O2 /W4 /WX "{1}\tests\damage_state_tests.cpp" /Fe:"{2}\state{3}.exe" /Fo:"{2}\state{3}.obj" /link /Brepro' -f $vc,$root,$out,$arch
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Damage source tests build failed'}
 & (Join-Path $out "state$arch.exe") | Tee-Object -FilePath (Join-Path $out "state$arch.txt")
 if($LASTEXITCODE -ne 0){throw 'Damage source tests failed'}
}
