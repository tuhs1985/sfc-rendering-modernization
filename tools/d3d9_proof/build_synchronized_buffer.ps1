$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/d3d9-proof/buffer-tests'
New-Item -ItemType Directory -Force -Path $out | Out-Null
foreach($arch in @('32','64')){
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars'+$arch+'.bat'
 $command='"{0}" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX /fp:precise "{1}\tests\d3d9_synchronized_buffer_tests.cpp" /Fe:"{2}\buffer{3}.exe" /Fo:"{2}\buffer{3}.obj" /link /Brepro d3d11.lib dxgi.lib d3dcompiler.lib' -f $vc,$root,$out,$arch
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Synchronized GPU test build failed'}
 $result=& (Join-Path $out "buffer$arch.exe")
 if($LASTEXITCODE -ne 0){throw 'Synchronized GPU test failed'}
 $result | Set-Content -Encoding UTF8 (Join-Path $out "buffer$arch.txt")
 $result | Write-Output
}
