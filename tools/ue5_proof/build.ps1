param(
    [Parameter(Mandatory=$true)][string]$Engine,
    [Parameter(Mandatory=$true)][string]$ProofRoot
)
$ErrorActionPreference = 'Stop'
$Engine = (Resolve-Path -LiteralPath $Engine).Path
$ProofRoot = (Resolve-Path -LiteralPath $ProofRoot).Path
$project = Join-Path $ProofRoot 'project/SFCSceneProof.uproject'
$version = Get-Content -LiteralPath (Join-Path $Engine 'Engine/Build/Build.version') -Raw | ConvertFrom-Json
if ($version.MajorVersion -ne 5 -or $version.MinorVersion -ne 8 -or $version.PatchVersion -ne 4) {
    throw 'This proof is qualified with Unreal Engine 5.8.4.'
}
function Invoke-Step([string]$Program, [string[]]$Arguments, [string]$Log) {
    & $Program @Arguments *> $Log
    if ($LASTEXITCODE -ne 0) { throw "Build step failed. Read $Log" }
}
Invoke-Step (Join-Path $Engine 'Engine/Build/BatchFiles/Build.bat') @(
    'SFCSceneProofEditor','Win64','Development',"-Project=$project",
    '-WaitMutex','-MaxParallelActions=1','-NoUBA'
) (Join-Path $ProofRoot 'editor-build.log')
Invoke-Step (Join-Path $Engine 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe') @(
    $project,'-run=BuildProof','-unattended','-nop4','-nosplash','-NullRHI',
    '-ini:Engine:[DevOptions.Shaders]:PercentageUnusedShaderCompilingThreads=90'
) (Join-Path $ProofRoot 'content-build.log')
Invoke-Step (Join-Path $Engine 'Engine/Build/BatchFiles/RunUAT.bat') @(
    'BuildCookRun',"-project=$project",'-noP4','-platform=Win64','-clientconfig=Development',
    '-build','-cook','-map=/Game/ProofMap','-stage','-pak','-iostore','-archive',
    "-archivedirectory=$ProofRoot/package",'-unattended','-utf8output','-nocompileeditor',
    '-UbtArgs=-MaxParallelActions=1 -NoUBA',
    '-AdditionalCookerOptions=-ini:Engine:[DevOptions.Shaders]:PercentageUnusedShaderCompilingThreads=90'
) (Join-Path $ProofRoot 'package-build.log')
if (Select-String -LiteralPath (Join-Path $ProofRoot 'package-build.log') -Pattern 'Failed to compile Material' -Quiet) {
    throw 'A material failed to cook. Do not accept the package.'
}
@'
@echo off
"%~dp0package\Windows\SFCSceneProof.exe" -windowed -ResX=1920 -ResY=1080 -SFCScene="%~dp0input\scene.json" -SFCOutput="%~dp0output\manual" -nosound %*
'@ | Set-Content -LiteralPath (Join-Path $ProofRoot 'SFC-UE5-Proof.cmd') -Encoding ascii
Write-Host "Packaged proof: $ProofRoot\SFC-UE5-Proof.cmd"
