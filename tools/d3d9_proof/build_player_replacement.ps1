$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/player-replacement/native-tests'
New-Item -ItemType Directory -Force $out | Out-Null
foreach($arch in @('32','64')){
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars'+$arch+'.bat'
 $command='"{0}" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX /fp:precise "{1}\tests\player_replacement_tests.cpp" /Fe:"{2}\transaction{3}.exe" /Fo:"{2}\transaction{3}.obj" /link /Brepro d3d11.lib dxgi.lib d3dcompiler.lib' -f $vc,$root,$out,$arch
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Replacement transaction build failed'}
 $result=& (Join-Path $out "transaction$arch.exe")
 $result | Set-Content (Join-Path $out "transaction$arch.txt")
 if($LASTEXITCODE -ne 0){throw 'Replacement transaction check failed'}
 $result | Write-Output
 if($arch -eq '32'){
  $command='"{0}" && cl /nologo /std:c++17 /EHsc /O2 /MT /W4 /WX /fp:precise "{1}\tests\m1_player_replacement_component_tests.cpp" /Fe:"{2}\component.exe" /Fo:"{2}\component.obj" /link /Brepro user32.lib' -f $vc,$root,$out
  & $env:ComSpec /d /s /c $command
  if($LASTEXITCODE -ne 0){throw 'Replacement recorder build failed'}
  $result=& (Join-Path $out 'component.exe')
  $result | Set-Content (Join-Path $out 'component.txt')
  if($LASTEXITCODE -ne 0){throw 'Replacement recorder check failed'}
  $result | Write-Output
 }
}
