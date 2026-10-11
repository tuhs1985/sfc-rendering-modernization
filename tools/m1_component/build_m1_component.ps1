$ErrorActionPreference = "Stop"

$toolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Resolve-Path (Join-Path $toolRoot "..\..")
$outputDir = Join-Path $workspaceRoot "artifacts\m1\bin"
$vcvars = "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat"

if (-not (Test-Path -LiteralPath $vcvars)) {
    throw "Visual Studio x86 build environment was not found."
}

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$dllSource = Join-Path $toolRoot "m1_component.cpp"
$definition = Join-Path $toolRoot "m1_component.def"
$gateDefinition = Join-Path $toolRoot "m1_gate.def"
$dllOutput = Join-Path $outputDir "m1_component.dll"
$proxyDefinition = Join-Path $toolRoot "m1_proxy_winmm.def"
$proxyOutput = Join-Path $outputDir "winmm.dll"
$gateOutput = Join-Path $outputDir "m1_gate.dll"
$controllerSource = Join-Path $toolRoot "m1_controller.cpp"
$controllerOutput = Join-Path $outputDir "m1_controller.exe"
$testSource = Join-Path $workspaceRoot "tests\m1_contract_tests.cpp"
$testOutput = Join-Path $outputDir "m1_contract_tests.exe"
$proxyTestSource = Join-Path $workspaceRoot "tests\m1_proxy_forwarding_tests.cpp"
$proxyTestOutput = Join-Path $outputDir "m1_proxy_forwarding_tests.exe"
$dllObject = Join-Path $outputDir "m1_component.obj"
$proxyObject = Join-Path $outputDir "m1_proxy_winmm.obj"
$gateObject = Join-Path $outputDir "m1_gate.obj"
$controllerObject = Join-Path $outputDir "m1_controller.obj"
$testObject = Join-Path $outputDir "m1_contract_tests.obj"
$proxyTestObject = Join-Path $outputDir "m1_proxy_forwarding_tests.obj"
$tintTestSource = Join-Path $workspaceRoot "tests\m1_visual_tint_tests.cpp"
$tintTestOutput = Join-Path $outputDir "m1_visual_tint_tests.exe"
$tintTestObject = Join-Path $outputDir "m1_visual_tint_tests.obj"
$tintComponentTestSource = Join-Path $workspaceRoot "tests\m1_visual_tint_component_tests.cpp"
$tintComponentTestOutput = Join-Path $outputDir "m1_visual_tint_component_tests.exe"
$tintComponentTestObject = Join-Path $outputDir "m1_visual_tint_component_tests.obj"

$commands = @(
    ('cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /arch:SSE2 /LD /Fo:"{0}" /Fe:"{1}" "{2}" /link /DEF:"{3}"' -f $dllObject, $dllOutput, $dllSource, $definition),
    ('cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /arch:SSE2 /DM1_WINMM_PROXY /LD /Fo:"{0}" /Fe:"{1}" "{2}" /link /DEF:"{3}"' -f $proxyObject, $proxyOutput, $dllSource, $proxyDefinition),
    ('cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /arch:SSE2 /DM1_GATE_ONLY /LD /Fo:"{0}" /Fe:"{1}" "{2}" /link /DEF:"{3}"' -f $gateObject, $gateOutput, $dllSource, $gateDefinition),
    ('cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /Fo:"{0}" /Fe:"{1}" "{2}" /link advapi32.lib' -f $controllerObject, $controllerOutput, $controllerSource),
    ('cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /Fo:"{0}" /Fe:"{1}" "{2}"' -f $testObject, $testOutput, $testSource),
    ('cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /Fo:"{0}" /Fe:"{1}" "{2}"' -f $proxyTestObject, $proxyTestOutput, $proxyTestSource),
    ('cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /Fo:"{0}" /Fe:"{1}" "{2}"' -f $tintTestObject, $tintTestOutput, $tintTestSource),
    ('cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /arch:SSE2 /Fo:"{0}" /Fe:"{1}" "{2}"' -f $tintComponentTestObject, $tintComponentTestOutput, $tintComponentTestSource),
    ('cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /arch:SSE2 /Fo:"{0}\m1_shading_off_component_tests.obj" /Fe:"{0}\m1_shading_off_component_tests.exe" "{1}\tests\m1_shading_off_component_tests.cpp"' -f $outputDir, $workspaceRoot)
)

foreach ($compile in $commands) {
    $command = '"{0}" && {1}' -f $vcvars, $compile
    & $env:ComSpec /d /s /c $command
    if ($LASTEXITCODE -ne 0) {
        throw "M1 component build failed with exit code $LASTEXITCODE."
    }
}

& $testOutput
if ($LASTEXITCODE -ne 0) {
    throw "M1 contract regression test failed with exit code $LASTEXITCODE."
}

& $tintTestOutput
if ($LASTEXITCODE -ne 0) { throw "M1 visual tint regression test failed." }
& $tintComponentTestOutput
if ($LASTEXITCODE -ne 0) { throw "M1 production tint lifecycle test failed." }
& (Join-Path $outputDir 'm1_shading_off_component_tests.exe')
if ($LASTEXITCODE -ne 0) { throw 'M1 production shading-off test failed.' }

& $proxyTestOutput $proxyOutput
if ($LASTEXITCODE -ne 0) {
    throw "M1 WINMM proxy forwarding test failed with exit code $LASTEXITCODE."
}

$dumpbin = "dumpbin"
$exportsCommand = '"{0}" && {1} /nologo /exports "{2}"' -f $vcvars, $dumpbin, $dllOutput
$exports = & $env:ComSpec /d /s /c $exportsCommand
$exportsText = $exports -join "`n"
if ($LASTEXITCODE -ne 0 -or $exportsText -notmatch "M1StartW" -or $exportsText -notmatch "M1Stop") {
    throw "M1 component exports were not produced as expected."
}

$proxyExportsCommand = '"{0}" && {1} /nologo /exports "{2}"' -f $vcvars, $dumpbin, $proxyOutput
$proxyExports = & $env:ComSpec /d /s /c $proxyExportsCommand
$proxyExportsText = $proxyExports -join "`n"
foreach ($required in @("M1StartW", "M1Stop", "timeGetTime", "timeKillEvent", "timeSetEvent")) {
    if ($LASTEXITCODE -ne 0 -or $proxyExportsText -notmatch $required) {
        throw "M1 WINMM proxy export '$required' was not produced."
    }
}

$gateExportsCommand = '"{0}" && {1} /nologo /exports "{2}"' -f $vcvars, $dumpbin, $gateOutput
$gateExports = & $env:ComSpec /d /s /c $gateExportsCommand
$gateExportsText = $gateExports -join "`n"
foreach ($required in @("M1StartW", "M1Stop")) {
    if ($LASTEXITCODE -ne 0 -or $gateExportsText -notmatch $required) {
        throw "M1 gate export '$required' was not produced."
    }
}

Write-Output $dllOutput
Write-Output $proxyOutput
Write-Output $gateOutput
Write-Output $controllerOutput
Write-Output $testOutput
Write-Output $proxyTestOutput
