param([ValidateSet('Off','Speed')][string]$Optimization='Speed')
$ErrorActionPreference='Stop'
$opt=if($Optimization -eq 'Speed'){'/O2'}else{'/Od'}
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$bin=Join-Path $root 'artifacts/d3d9-proof/receiver-bin'
New-Item -ItemType Directory -Force -Path $bin | Out-Null
Push-Location $bin
try{
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
 $cmd='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /W4 /WX {2} /fp:precise "{1}\tools\d3d9_proof\output_receiver.cpp" /Fe:output_receiver.exe /link /Brepro d3d11.lib dxgi.lib' -f $vc,$root,$opt
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'x86 output receiver build failed'}
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\tests\d3d9_output_wire_tests.cpp" /Fe:output_wire_tests.exe /link /Brepro' -f $vc,$root
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Output wire tests build failed'}
 & .\output_wire_tests.exe
 if($LASTEXITCODE -ne 0){throw 'Output wire tests failed'}
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\tests\d3d9_source_timing_tests.cpp" /Fe:source_timing_tests.exe /link /Brepro' -f $vc,$root
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Source timing tests build failed'}
 & .\source_timing_tests.exe
 if($LASTEXITCODE -ne 0){throw 'Source timing tests failed'}
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\tests\d3d9_game_output_tests.cpp" /Fe:game_output_tests.exe /link /Brepro' -f $vc,$root
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Game output wire tests build failed'}
 & .\game_output_tests.exe
 if($LASTEXITCODE -ne 0){throw 'Game output wire tests failed'}
 $cmd='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /W4 /WX {2} /fp:precise "{1}\tests\d3d9_deferred_diagnostics_tests.cpp" /Fe:deferred_diagnostics_tests.exe /link /Brepro' -f $vc,$root,$opt
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Deferred diagnostics x86 build failed'}
 & .\deferred_diagnostics_tests.exe
 if($LASTEXITCODE -ne 0){throw 'Deferred diagnostics x86 tests failed'}
 @{optimization=$opt;floating_point='/fp:precise';inherited_cl_options='cleared in compiler child';architecture='x86'} | ConvertTo-Json | Set-Content build-policy.json
}finally{Pop-Location}
