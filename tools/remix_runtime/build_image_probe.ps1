$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/remix-runtime/live-return-bin'
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat'
Push-Location $out
try{
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX /I"{1}\artifacts\remix-runtime\deps\include" "{2}\image_controls_probe.cpp" /Fe:image_controls_probe.exe /link /Brepro d3d11.lib d3dcompiler.lib user32.lib ole32.lib' -f $vc,$root,$PSScriptRoot
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Image probe build failed'}
}finally{Pop-Location}
