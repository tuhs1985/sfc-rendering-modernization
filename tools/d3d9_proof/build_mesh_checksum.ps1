$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/d3d9-proof/mesh-checksum'
New-Item -ItemType Directory -Force -Path $out | Out-Null
Push-Location $out
try {
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat'
 $cmd='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX /LD "{1}\tools\d3d9_proof\mesh_checksum.cpp" /Fe:mesh_checksum.dll /link /Brepro' -f $vc,$root
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Native mesh checksum build failed'}
 @{source_sha256=(Get-FileHash -LiteralPath (Join-Path $root 'tools/d3d9_proof/mesh_checksum.cpp')).Hash.ToLowerInvariant();dll_sha256=(Get-FileHash -LiteralPath (Join-Path $out 'mesh_checksum.dll')).Hash.ToLowerInvariant();architecture='x64';flags='/O2 /W4 /WX /LD /Brepro'} | ConvertTo-Json | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $out 'build.json')
} finally {Pop-Location}
