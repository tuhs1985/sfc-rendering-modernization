$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/remix-runtime/deps/reshade/include'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$source='8cf85bd12d56697d756d4fcb45e501f5d1b540fa'
$imgui='3912b3d9a9c1b3f17431aebafd86d2f40ee6e59c'
$files=@('reshade.hpp','reshade_api.hpp','reshade_api_device.hpp','reshade_api_format.hpp','reshade_api_pipeline.hpp','reshade_api_resource.hpp','reshade_events.hpp','reshade_overlay.hpp')
foreach($name in $files){
    $file=Join-Path $out $name
    if(-not(Test-Path -LiteralPath $file)){Invoke-WebRequest "https://raw.githubusercontent.com/crosire/reshade/$source/include/$name" -OutFile $file -TimeoutSec 45}
}
foreach($name in @('imgui.h','imconfig.h')){
    $file=Join-Path $out $name
    if(-not(Test-Path -LiteralPath $file)){Invoke-WebRequest "https://raw.githubusercontent.com/ocornut/imgui/$imgui/$name" -OutFile $file -TimeoutSec 45}
}
$manifest=[ordered]@{reshade_release='v6.7.1';source_commit=$source;imgui_commit=$imgui;headers=@(Get-ChildItem -LiteralPath $out -File | ForEach-Object {[ordered]@{name=$_.Name;bytes=$_.Length;sha256=(Get-FileHash $_.FullName).Hash}})}
$manifest | ConvertTo-Json -Depth 4 | Set-Content (Join-Path (Split-Path $out -Parent) 'manifest.json') -Encoding utf8
