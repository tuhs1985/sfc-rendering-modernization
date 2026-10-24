param([Parameter(Mandatory=$true)][string]$Scene)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$scenePath=(Resolve-Path -LiteralPath $Scene).Path
if(-not $scenePath.StartsWith($root+'\artifacts\')){throw 'Use an existing project capture-derived scene'}
$out=Join-Path $root 'artifacts/d3d9-proof/resource-policy-tests'
New-Item -ItemType Directory -Path $out -Force | Out-Null
Push-Location $out
try {
 foreach($arch in @('32','64')){
  $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars'+$arch+'.bat'
  $cmd='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX /fp:precise "{1}\tests\d3d9_resource_policy_tests.cpp" /Fe:resource{2}.exe /Fo:resource{2}.obj /link /Brepro user32.lib d3dcompiler.lib' -f $vc,$root,$arch
  & $env:ComSpec /d /s /c $cmd
  if($LASTEXITCODE -ne 0){throw 'Native resource policy build failed'}
  $result=& (Join-Path $out "resource$arch.exe") $scenePath
  $code=$LASTEXITCODE
  $result | Set-Content -Encoding UTF8 (Join-Path $out "resource$arch.txt")
  $result | Write-Output
  if($code -ne 0){throw 'Native resource policy validation failed'}
 }
} finally {Pop-Location}
