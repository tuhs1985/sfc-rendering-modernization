# Builds only the no-GPU startup-wire/lifetime probes. Run the Python qualifier separately.
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$vcRoot='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build'
foreach($arch in @('x86','x64')){
 $bin=Join-Path $root ('artifacts/player-replacement/receiver-startup/'+$arch)
 New-Item -ItemType Directory -Force -Path $bin | Out-Null
 $vc=Join-Path $vcRoot $(if($arch -eq 'x86'){'vcvars32.bat'}else{'vcvars64.bat'})
 Push-Location $bin
 try{
  $command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 "{1}\tests\receiver_startup_probe.cpp" /Fe:receiver_startup_probe.exe /link /Brepro user32.lib advapi32.lib ole32.lib' -f $vc,$root
  & $env:ComSpec /d /s /c $command
  if($LASTEXITCODE -ne 0){throw 'Receiver-startup probe build failed'}
  $command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 "{1}\tests\output_startup_tests.cpp" /Fe:output_startup_tests.exe /link /Brepro' -f $vc,$root
  & $env:ComSpec /d /s /c $command
  if($LASTEXITCODE -ne 0){throw 'Receiver-startup wire build failed'}
  & .\output_startup_tests.exe
  if($LASTEXITCODE -ne 0){throw 'Receiver-startup wire checks failed'}
 }finally{Pop-Location}
}
