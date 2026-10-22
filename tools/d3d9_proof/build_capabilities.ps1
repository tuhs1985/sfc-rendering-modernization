$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$manifest=Get-Content (Join-Path $root 'artifacts/remix-runtime/deps/manifest.json') -Raw | ConvertFrom-Json
$header=Join-Path $root 'artifacts/remix-runtime/deps/remix_c.h'
if($manifest.source_commit -ne 'b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4' -or (Get-FileHash $header).Hash -ne $manifest.header_sha256){throw 'Pinned header mismatch'}
$bin=Join-Path $root 'artifacts/d3d9-proof/intercept-bin'
New-Item -ItemType Directory -Force -Path $bin | Out-Null
Push-Location $bin
try{
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /I"{1}\artifacts\remix-runtime\deps" "{1}\tools\d3d9_proof\remix_bridge_capabilities.cpp" /Fe:remix_bridge_capabilities.exe /link /Brepro user32.lib' -f $vc,$root
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Normal bridge capability probe build failed'}
}finally{Pop-Location}
