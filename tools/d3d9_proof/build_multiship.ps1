$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/d3d9-proof/multiship-tests'
New-Item -ItemType Directory -Force -Path $out | Out-Null
foreach($arch in @('32','64')){
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars'+$arch+'.bat'
 $command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX /fp:precise "{1}\tests\d3d9_multi_scene_tests.cpp" /Fe:"{2}\wire{3}.exe" /Fo:"{2}\wire{3}.obj" /link /Brepro' -f $vc,$root,$out,$arch
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Multi-ship wire build failed'}
 $result=& (Join-Path $out "wire$arch.exe")
 if($LASTEXITCODE -ne 0){throw 'Multi-ship wire test failed'}
 $result | Set-Content -Encoding UTF8 (Join-Path $out "wire$arch.txt")
 $result | Write-Output
}
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat'
$command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX "{1}\tools\d3d9_proof\multi_asset_hash.cpp" /Fe:"{2}\asset_hash.exe" /Fo:"{2}\asset_hash.obj" /link /Brepro' -f $vc,$root,$out
& $env:ComSpec /d /s /c $command
if($LASTEXITCODE -ne 0){throw 'Bounded asset hash worker build failed'}
