$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out = Join-Path $root 'artifacts/effect-probe/bin'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$vc = 'C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
$command = '"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /arch:SSE2 /DSFC_EFFECT_JOIN_PRODUCER /LD /Fo:"{2}\m1_effect_join.obj" /Fe:"{2}\m1_effect_join.dll" "{1}\tools\m1_component\m1_component.cpp" /link /Brepro /DEF:"{1}\tools\m1_component\m1_component.def"' -f $vc,$root,$out
& $env:ComSpec /d /s /c $command
if ($LASTEXITCODE -ne 0) { throw 'Diagnostic retained-frame producer build failed' }
