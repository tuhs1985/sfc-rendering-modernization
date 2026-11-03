$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/player-replacement/environment-tests'
New-Item -ItemType Directory -Force -Path $out | Out-Null
Push-Location $out
try {
 foreach($arch in @('32','64')) {
  $vc="C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars$arch.bat"
  $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 "{1}\tests\prepared_environment_tests.cpp" /Fe:wire{2}.exe /Fo:wire{2}.obj /link /Brepro' -f $vc,$root,$arch
  & $env:ComSpec /d /s /c $cmd
  if($LASTEXITCODE -ne 0){throw 'Prepared environment wire build failed'}
  & (Join-Path $out "wire$arch.exe") | Tee-Object -FilePath "wire$arch.txt"
  if($LASTEXITCODE -ne 0){throw 'Prepared environment wire tests failed'}
 }
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat'
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 /I"{1}\artifacts\remix-runtime\deps" "{1}\tests\prepared_environment_probe.cpp" /Fe:probe.exe /link /Brepro user32.lib d3d11.lib dxgi.lib d3dcompiler.lib advapi32.lib ole32.lib' -f $vc,$root
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Prepared environment IPC probe build failed'}
} finally {Pop-Location}
