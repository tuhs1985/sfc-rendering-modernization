$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/player-replacement/native-insertion-tests'
New-Item -ItemType Directory -Force $out | Out-Null
$files=@{}
foreach($arch in @('32','64')){
 $vc="C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars$arch.bat"
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX /sourceDependencies "{1}\probe{2}.deps.json" "{3}\tools\native_insertion\probe_tests.cpp" /Fe:"{1}\probe{2}.exe" /Fo:"{1}\probe{2}.obj" /link /Brepro d3d11.lib dxgi.lib' -f $vc,$out,$arch,$root
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Insertion observer build failed'}
 $log=& (Join-Path $out "probe$arch.exe")
 $log | Set-Content -Encoding utf8 (Join-Path $out "probe$arch.txt")
 if($LASTEXITCODE -ne 0){throw 'Insertion observer test failed'}
 $log
 $deps=Get-Content -LiteralPath (Join-Path $out "probe$arch.deps.json") -Raw | ConvertFrom-Json
 foreach($path in @($deps.Data.Source)+$deps.Data.Includes){
  if($path.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase)){
   $files[$path.Substring($root.Length+1).Replace('\','/')]=(Get-FileHash -LiteralPath $path).Hash
  }
 }
 foreach($name in @("probe$arch.exe","probe$arch.txt")){$files['artifacts/player-replacement/native-insertion-tests/'+$name]=(Get-FileHash -LiteralPath (Join-Path $out $name)).Hash}
}
$files['tools/native_insertion/build.ps1']=(Get-FileHash -LiteralPath $PSCommandPath).Hash
$files | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 (Join-Path $out 'build.json')
