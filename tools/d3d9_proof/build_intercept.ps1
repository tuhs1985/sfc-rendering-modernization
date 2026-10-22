$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$bin=Join-Path $root 'artifacts/d3d9-proof/intercept-bin'
New-Item -ItemType Directory -Force -Path $bin | Out-Null
Push-Location $bin
try {
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /DSFC_D3D9_REMIX_PROOF "{1}\tools\d3d9_proof\d3d9_replay.cpp" /Fe:d3d9_intercept.exe /link /Brepro user32.lib' -f $vc,$root
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Offline interception build failed'}
} finally { Pop-Location }
