$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
foreach($arch in @('x86','x64')){
 $bin=Join-Path $root "artifacts/d3d9-proof/ingress-$arch"
 New-Item -ItemType Directory -Force -Path $bin | Out-Null
 $vc=if($arch -eq 'x86'){'vcvars32.bat'}else{'vcvars64.bat'}
 $vc=Join-Path 'C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build' $vc
 Push-Location $bin
 try{
  $command='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 "{1}\tests\d3d9_frame_ingress_tests.cpp" /Fe:frame_ingress_tests.exe /link /Brepro' -f $vc,$root
  & $env:ComSpec /d /s /c $command
  if($LASTEXITCODE -ne 0){throw "Frame ingress $arch build failed"}
  & .\frame_ingress_tests.exe
  if($LASTEXITCODE -ne 0){throw "Frame ingress $arch tests failed"}
  $command='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 "{1}\tools\d3d9_proof\frame_ingress_fixture.cpp" /Fe:frame_ingress_fixture.exe /link /Brepro advapi32.lib ole32.lib' -f $vc,$root
  & $env:ComSpec /d /s /c $command
  if($LASTEXITCODE -ne 0){throw "Frame ingress $arch fixture build failed"}
  $command='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 "{1}\tests\d3d9_live_owner_tests.cpp" /Fe:live_owner_tests.exe /link /Brepro' -f $vc,$root
  & $env:ComSpec /d /s /c $command
  if($LASTEXITCODE -ne 0){throw "Live owner $arch build failed"}
  & .\live_owner_tests.exe
  if($LASTEXITCODE -ne 0){throw "Live owner $arch tests failed"}
  $command='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 "{1}\tests\shared_light_transport_tests.cpp" /Fe:shared_light_transport_tests.exe /link /Brepro' -f $vc,$root
  & $env:ComSpec /d /s /c $command
  if($LASTEXITCODE -ne 0){throw "Shared light $arch build failed"}
  & .\shared_light_transport_tests.exe
  if($LASTEXITCODE -ne 0){throw "Shared light $arch tests failed"}
 }finally{Pop-Location}
}
