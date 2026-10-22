$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/d3d9-proof/persistent-tests'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$vcbase='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build'
foreach($arch in @('32','64')){
 $command='"{0}\vcvars{1}.bat" && cl /nologo /std:c++17 /EHsc /W4 /WX "{2}\tests\persistent_scene_tests.cpp" /Fe:"{3}\persistent{1}.exe" /Fo:"{3}\persistent{1}.obj" /link /Brepro' -f $vcbase,$arch,$root,$out
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Persistent scene build failed'}
 & (Join-Path $out "persistent$arch.exe") | Tee-Object -FilePath (Join-Path $out "persistent$arch.txt")
 if($LASTEXITCODE -ne 0){throw 'Persistent scene test failed'}
}
$command='"{0}\vcvars32.bat" && cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /DSFC_NATIVE_LIGHT_DISCOVERY "{1}\tests\m1_persistent_scene_tests.cpp" /Fe:"{2}\native_scene.exe" /Fo:"{2}\native_scene.obj" /link /Brepro' -f $vcbase,$root,$out
& $env:ComSpec /d /s /c $command
if($LASTEXITCODE -ne 0){throw 'Persistent native worker test build failed'}
