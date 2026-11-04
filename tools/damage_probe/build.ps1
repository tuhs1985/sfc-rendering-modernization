$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/render-survey/damage-probe/bin'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
$detours=Join-Path $root 'artifacts/remix-runtime/deps/detours/Detours-e4bfd6b03e50de46b47abfbd1e46b384f0c5f833'
Push-Location $out
try {
 foreach($item in @(@('damage_component.cpp','damage_component.dll','/LD'),@('native_tests.cpp','damage_native_tests.exe',''))){
  $cmd='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHa /O2 /Oy- /W4 /WX /DSFC_DAMAGE_PROBE {1} /I"{2}\include" "{3}\tools\damage_probe\{4}" /Fe:{5} /link /Brepro /OPT:NOICF "{2}\lib.X86\detours.lib" advapi32.lib ole32.lib' -f $vc,$item[2],$detours,$root,$item[0],$item[1]
  & $env:ComSpec /d /s /c $cmd
  if($LASTEXITCODE -ne 0){throw 'Damage observer strict native build failed'}
 }
} finally {Pop-Location}
