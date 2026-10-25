$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/render-survey/bin'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
$detours=Join-Path $root 'artifacts/remix-runtime/deps/detours/Detours-e4bfd6b03e50de46b47abfbd1e46b384f0c5f833'
Push-Location $out
try {
 $command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHa /O2 /Oy- /W4 /WX /LD /I"{1}\artifacts\remix-runtime\deps\reshade\include" /I"{1}\tools\remix_runtime" /I"{2}\include" "{1}\tools\render_survey\survey_addon.cpp" /Fe:SFCRemixReturn.dll /link /Brepro "{2}\lib.X86\detours.lib" "{1}\artifacts\remix-runtime\return-bin\reshade_registration.lib" advapi32.lib ole32.lib user32.lib' -f $vc,$root,$detours
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Isolated survey observer build failed'}
 $command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX /I"{1}\tools\remix_runtime" "{1}\tools\render_survey\tests\trace_tests.cpp" /Fe:trace_tests.exe /link /Brepro advapi32.lib ole32.lib' -f $vc,$root
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Survey trace tests build failed'}
 & .\trace_tests.exe
 if($LASTEXITCODE -ne 0){throw 'Survey trace tests failed'}
 $command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHa /O2 /Oy- /W4 /WX /I"{1}\tools\remix_runtime" /I"{2}\include" "{1}\tools\render_survey\tests\native_tests.cpp" /Fe:native_tests.exe /link /Brepro "{2}\lib.X86\detours.lib" advapi32.lib ole32.lib' -f $vc,$root,$detours
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Native light/census tests build failed'}
 & .\native_tests.exe
 if($LASTEXITCODE -ne 0){throw 'Native light/census tests failed'}
 $command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /O2 /Oy- /W4 /WX /I"{1}\tools\remix_runtime" "{1}\tools\render_survey\survey_fixture.cpp" /Fe:d3d11_return_fixture.exe /link /Brepro d3d11.lib d3dcompiler.lib advapi32.lib ole32.lib user32.lib dbghelp.lib' -f $vc,$root
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Isolated90second survey fixture build failed'}
 $command='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /O2 /W4 /WX /I"{2}\include" "{1}\tools\render_survey\survey_fixture_launcher.cpp" /Fe:survey_fixture_launcher.exe /link /Brepro "{2}\lib.X86\detours.lib" bcrypt.lib user32.lib' -f $vc,$root,$detours
 & $env:ComSpec /d /s /c $command
 if($LASTEXITCODE -ne 0){throw 'Isolated survey fixture launcher build failed'}
} finally {Pop-Location}
