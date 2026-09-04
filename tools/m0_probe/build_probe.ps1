$ErrorActionPreference = "Stop"

$toolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Resolve-Path (Join-Path $toolRoot "..\..")
$outputDir = Join-Path $workspaceRoot "artifacts\pre-m0\bin"
$source = Join-Path $toolRoot "m0_probe.cpp"
$output = Join-Path $outputDir "m0_probe.exe"

$vcvars = "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat"
if (-not (Test-Path -LiteralPath $vcvars)) {
    throw "Visual Studio x86 build environment was not found."
}

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
$command = '"{0}" && cl /nologo /std:c++17 /EHsc /W4 /O2 /MT /Fe:"{1}" "{2}" /link advapi32.lib' -f $vcvars, $output, $source
& $env:ComSpec /d /s /c $command
if ($LASTEXITCODE -ne 0) {
    throw "Probe compilation failed with exit code $LASTEXITCODE."
}

Write-Output $output

