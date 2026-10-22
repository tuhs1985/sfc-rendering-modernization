$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$bin=Join-Path $root 'artifacts/d3d9-proof/bin'
New-Item -ItemType Directory -Force -Path $bin | Out-Null
Push-Location $bin
try {
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\tools\d3d9_proof\d3d9_replay.cpp" /Fe:d3d9_replay.exe /link /Brepro user32.lib' -f $vc,$root
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Offline D3D9 proof build failed'}
 $probe='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\tools\d3d9_proof\d3d9_startup_probe.cpp" /Fe:d3d9_startup_probe.exe /link /Brepro user32.lib advapi32.lib' -f $vc,$root
 & $env:ComSpec /d /s /c $probe
 if($LASTEXITCODE -ne 0){throw 'Native D3D9 startup diagnostic build failed'}
} finally { Pop-Location }
