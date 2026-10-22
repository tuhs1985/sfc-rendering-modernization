$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$header=Join-Path $root 'artifacts/remix-runtime/deps/xxhash.h'
if((Get-FileHash -LiteralPath $header).Hash -ne 'FDBF70C5F5CCFFED18A1CF82B635799CA5128743DB8746076AA136A5AA4BC467'){throw 'Pinned hash header mismatch'}
$bin=Join-Path $root 'artifacts/d3d9-proof/material-bin'
New-Item -ItemType Directory -Force -Path $bin | Out-Null
Push-Location $bin
try{
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat'
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /I"{1}\artifacts\remix-runtime\deps" "{1}\tools\d3d9_proof\texture_hash.cpp" /Fe:texture_hash.exe /link /Brepro' -f $vc,$root
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Texture identity helper build failed'}
}finally{Pop-Location}
