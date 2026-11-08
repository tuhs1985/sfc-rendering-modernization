param([Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$output=[IO.Path]::GetFullPath($OutputDirectory)
if(-not $output.StartsWith((Join-Path $root 'artifacts\') ,[StringComparison]::OrdinalIgnoreCase)){throw 'Build output must be under project artifacts'}
New-Item -ItemType Directory -Force -Path $output | Out-Null
$include=Join-Path $root 'artifacts/remix-runtime/deps/candidate-1.6.1'
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat'
Push-Location $output
try {
 $command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 /fp:precise /I"{1}" "{2}\tools\d3d9_proof\d3d9_direct_host.cpp" /Fe:d3d9_direct_host.exe /link /Brepro user32.lib d3d11.lib dxgi.lib d3dcompiler.lib advapi32.lib ole32.lib' -f $vc,$include,$root
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Standalone debris replay host build failed'}
} finally {Pop-Location}
