# Official pinned dependencies only, generated under ignored artifacts; no game edits.
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$deps=Join-Path $root 'artifacts/remix-runtime/deps'
New-Item -ItemType Directory -Force -Path $deps | Out-Null
$release=Invoke-RestMethod 'https://api.github.com/repos/NVIDIAGameWorks/rtx-remix/releases/tags/remix-1.5.2'
$tree=Invoke-RestMethod 'https://api.github.com/repos/NVIDIAGameWorks/rtx-remix/git/trees/remix-1.5.2'
$source='b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4'
if(($tree.tree | Where-Object path -eq 'dxvk-remix').sha -ne $source){throw 'Release source changed'}
$asset=$release.assets | Where-Object name -eq 'remix-1.5.2-release.zip'
if($asset.size -ne 231778218 -or $asset.digest -ne 'sha256:cc424be4dd1a0c6fd922bc6a7f8e5f6582baea7043a38afa6686d8b6faabad01'){throw 'Release archive metadata changed'}
$zip=Join-Path $deps $asset.name
if(-not(Test-Path -LiteralPath $zip)){
    # Headers-first bounded download; never exceed 250MiB or 180 seconds.
    $client=[Net.Http.HttpClient]::new();$client.Timeout=[TimeSpan]::FromSeconds(180)
    try{
        $response=$client.GetAsync($asset.browser_download_url,[Net.Http.HttpCompletionOption]::ResponseHeadersRead).GetAwaiter().GetResult()
        [void]$response.EnsureSuccessStatusCode()
        if($response.Content.Headers.ContentLength -gt 250MB){throw 'Download length cap'}
        $inputStream=$response.Content.ReadAsStream();$outputStream=[IO.File]::Open($zip,[IO.FileMode]::CreateNew)
        try{
            $buffer=[byte[]]::new(65536);$total=0;$deadline=[DateTime]::UtcNow.AddSeconds(180)
            while(($n=$inputStream.Read($buffer,0,$buffer.Length)) -gt 0){
                $total+=$n;if($total -gt 250MB -or [DateTime]::UtcNow -gt $deadline){throw 'Download limit'}
                $outputStream.Write($buffer,0,$n)
            }
        }finally{$inputStream.Dispose();$outputStream.Dispose();$response.Dispose()}
    }finally{$client.Dispose()}
}
$sha=(Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLower()
if((Get-Item -LiteralPath $zip).Length -ne $asset.size -or "sha256:$sha" -ne $asset.digest){throw 'Archive hash/size mismatch; preserve invalid file for review'}
$runtime=Join-Path $deps 'remix-1.5.2'
if(-not(Test-Path -LiteralPath $runtime)){
    $archive=[IO.Compression.ZipFile]::OpenRead($zip)
    try{
        if($archive.Entries.Count -gt 4096 -or ($archive.Entries | Measure-Object Length -Sum).Sum -gt 2GB){throw 'Extraction bounds'}
        $absolute=[IO.Path]::GetFullPath($runtime)+[IO.Path]::DirectorySeparatorChar
        foreach($entry in $archive.Entries){if(-not[IO.Path]::GetFullPath((Join-Path $runtime $entry.FullName)).StartsWith($absolute,[StringComparison]::OrdinalIgnoreCase)){throw 'Unsafe archive entry'}}
    }finally{$archive.Dispose()}
    Expand-Archive -LiteralPath $zip -DestinationPath $runtime
}
$include=Join-Path $deps 'include/remix';New-Item -ItemType Directory -Force -Path $include | Out-Null
foreach($relative in @('public/include/remix/remix_c.h','src/dxvk/rtx_render/rtx_remix_api.cpp','src/d3d9/d3d9_device.cpp','src/d3d9/d3d9_common_texture.cpp','src/d3d9/d3d9_common_texture.h','tests/rtx/apps/RemixAPI_C/remixapi_example_c.c')){
    $name=Split-Path $relative -Leaf;$destination=Join-Path $deps $name
    if(-not(Test-Path -LiteralPath $destination)){Invoke-WebRequest -Uri "https://raw.githubusercontent.com/NVIDIAGameWorks/dxvk-remix/$source/$relative" -OutFile $destination -TimeoutSec 60}
    if($name -eq 'remix_c.h'){Copy-Item -LiteralPath $destination -Destination (Join-Path $include $name)}
}
$manifest=[ordered]@{release='remix-1.5.2';source_commit=$source;archive_sha256=$sha;archive_bytes=$asset.size;header_sha256=(Get-FileHash (Join-Path $include 'remix_c.h')).Hash;runtime_path=$runtime}
$manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $deps 'manifest.json') -Encoding utf8
$manifest | ConvertTo-Json
