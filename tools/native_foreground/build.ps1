$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/player-replacement/native-foreground-tests'
New-Item -ItemType Directory -Force $out | Out-Null
$detours=Join-Path $root 'artifacts/remix-runtime/deps/detours/Detours-e4bfd6b03e50de46b47abfbd1e46b384f0c5f833'
$vcroot='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build'
foreach($case in @(@('64','retained_resources_tests','resources'),@('32','shield_scope_hooks_tests','scope'))){
 $arch=$case[0];$source=$case[1];$name=$case[2]
 $command='"{0}\vcvars{1}.bat" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX /fp:precise /sourceDependencies "{5}\{6}.deps.json" /I"{2}\include" "{3}\tools\native_foreground\{4}.cpp" /Fe:"{5}\{6}.exe" /Fo:"{5}\{6}.obj" /link /Brepro d3d11.lib dxgi.lib d3dcompiler.lib advapi32.lib ole32.lib user32.lib' -f $vcroot,$arch,$detours,$root,$source,$out,$name
 if($arch -eq '32'){$command+=' "'+$detours+'\lib.X86\detours.lib"'}
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw "Native foreground $name build failed"}
 $result=& (Join-Path $out "$name.exe")
 $result | Set-Content -Encoding utf8 (Join-Path $out "$name.txt")
 if($LASTEXITCODE -ne 0){throw "Native foreground $name test failed"}
 $result
}
$files=@{}
foreach($name in @('resources','scope')){
 $deps=Get-Content -LiteralPath (Join-Path $out "$name.deps.json") -Raw | ConvertFrom-Json
 foreach($path in $deps.Data.Includes){if($path.StartsWith($root+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){
  $files[$path.Substring($root.Length+1).Replace([IO.Path]::DirectorySeparatorChar,[char]'/')]=(Get-FileHash -LiteralPath $path).Hash}}
}
Get-ChildItem -LiteralPath $PSScriptRoot -File | Where-Object {$_.Extension -in '.h','.cpp','.ps1'} | ForEach-Object {$files[$_.FullName.Substring($root.Length+1).Replace([IO.Path]::DirectorySeparatorChar,[char]'/')]=(Get-FileHash -LiteralPath $_.FullName).Hash}
foreach($name in @('resources.exe','resources.txt','scope.exe','scope.txt')){$files['artifacts/player-replacement/native-foreground-tests/'+$name]=(Get-FileHash -LiteralPath (Join-Path $out $name)).Hash}
$files | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 (Join-Path $out 'build.json')
