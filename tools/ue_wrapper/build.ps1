param(
    [string]$Engine='C:/Project/Dependencies/UE_5.8',
    [ValidateSet('Development','Shipping')][string]$Configuration='Development',
    [switch]$SkipEditor
)
$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$project=Join-Path $root 'src/ue_wrapper/SFCUEWrapper.uproject'
$projectRoot=Split-Path $project -Parent
$output=Join-Path $root "artifacts/ue-foundation/$Configuration"
New-Item -ItemType Directory -Path $output -Force | Out-Null
$version=Get-Content (Join-Path $Engine 'Engine/Build/Build.version') -Raw | ConvertFrom-Json
if($version.MajorVersion -ne 5 -or $version.MinorVersion -ne 8 -or $version.PatchVersion -ne 4 -or $version.Changelist -ne 58902052) { throw 'Use qualified UE 5.8.4 CL 58902052.' }
# The pinned compiler ignores PercentageUnusedShaderCompilingThreads in commandlets.
# NumUnusedShaderCompilingThreads is the documented config read on that path.
$reserved=[Math]::Max(0,[Environment]::ProcessorCount-2)
$shaderLimit="-ini:Engine:[DevOptions.Shaders]:NumUnusedShaderCompilingThreads=$reserved,NumUnusedShaderCompilingThreadsDuringGame=$reserved"
function Source-Hashes {
    $files=@(Get-Item $project)
    $files+=Get-Item (Join-Path $projectRoot 'Plugins/SFCBridge/SFCBridge.uplugin')
    foreach($part in @('Config','Source','Plugins/SFCBridge/Source')) {
        $files+=Get-ChildItem (Join-Path $projectRoot $part) -Recurse -File
    }
    $result=[ordered]@{}
    foreach($file in ($files | Sort-Object FullName)) {
        $result[$file.FullName.Substring($projectRoot.Length+1).Replace('\','/')]=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    foreach($file in (Get-ChildItem (Join-Path $root 'src/rendering/ue') -Filter '*.h' -File | Sort-Object Name)) {
        $result["external/rendering/ue/$($file.Name)"]=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    foreach($name in @('src/transport/source_scene_view.h','src/transport/source_scene_channel.h','src/transport/source_target_view.h','tools/scene_bridge/scene_capacity.h')) {
        $result["external/$name"]=(Get-FileHash -LiteralPath (Join-Path $root $name) -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    return $result
}
$sourceHashes=Source-Hashes
function Run([string]$Program,[string[]]$Arguments,[string]$Log) {
    & $Program @Arguments *> $Log
    if($LASTEXITCODE -ne 0) { throw "UE build failed; inspect $Log" }
}
if(!$SkipEditor) {
    Run (Join-Path $Engine 'Engine/Build/BatchFiles/Build.bat') @('SFCUEWrapperEditor','Win64','Development',"-Project=$project",'-WaitMutex','-MaxParallelActions=1','-NoUBA') (Join-Path $output 'editor.log')
    Run (Join-Path $Engine 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe') @($project,'-run=BuildBridge','-unattended','-nop4','-nosplash','-NullRHI',$shaderLimit) (Join-Path $output 'content.log')
}
Run (Join-Path $Engine 'Engine/Build/BatchFiles/RunUAT.bat') @('BuildCookRun',"-project=$project",'-noP4','-platform=Win64',"-clientconfig=$Configuration",'-build','-cook','-map=/Game/BridgeMap','-stage','-pak','-iostore','-archive',"-archivedirectory=$output/package",'-unattended','-utf8output','-nocompileeditor','-UbtArgs=-MaxParallelActions=1 -NoUBA',"-AdditionalCookerOptions=$shaderLimit") (Join-Path $output 'package.log')
if(Select-String (Join-Path $output 'package.log') -Pattern 'Failed to compile Material' -Quiet) { throw 'Material cook failed.' }
if(($sourceHashes | ConvertTo-Json -Compress) -cne ((Source-Hashes) | ConvertTo-Json -Compress)) { throw 'Source changed during build; re-run before qualification.' }
$receipt=@{ engine=$version; configuration=$Configuration; project=$project; package="$output/package/Windows"; source=(git -C $root rev-parse HEAD); source_hashes=$sourceHashes; local_changes=(git -C $root status --short) }
$receipt | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $output 'build-receipt.json') -Encoding utf8
Write-Host "UE package: $output/package/Windows/SFCUEWrapper.exe"
