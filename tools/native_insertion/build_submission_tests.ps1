$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/player-replacement/submission-tests'
New-Item -ItemType Directory -Force $out | Out-Null
foreach($arch in @('32','64')){
 $vc="C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars$arch.bat"
 foreach($test in @('d3d9_submission_policy_tests','remix_loaded_light_tests')){
  $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX "{1}\tests\{2}.cpp" /Fe:"{3}\{2}-{4}.exe" /Fo:"{3}\{2}-{4}.obj" /link /Brepro' -f $vc,$root,$test,$out,$arch
  & $env:ComSpec /d /s /c $cmd
  if($LASTEXITCODE -ne 0){throw 'Submission/light policy build failed'}
  & (Join-Path $out "$test-$arch.exe") | Tee-Object -FilePath (Join-Path $out "$test-$arch.txt")
  if($LASTEXITCODE -ne 0){throw 'Submission/light policy failed'}
 }
}
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
$cmd='"{0}" && cl /nologo /std:c++17 /EHsc /O2 /W4 /WX /MT "{1}\tests\m1_persistent_scene_tests.cpp" /Fe:"{2}\native_scene.exe" /Fo:"{2}\native_scene.obj" /link /Brepro user32.lib' -f $vc,$root,$out
& $env:ComSpec /d /s /c $cmd
if($LASTEXITCODE -ne 0){throw 'Persistent diagnostic-isolation fixture build failed'}
