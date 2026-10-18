# Independent copy, never hardlink mutable game assets to the accepted install.
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$source='C:\Games\Taldren Software Inc\Starfleet Command Orion Pirates'
$target='C:\Project\SFC-Remix-Return-Test'
$out=Join-Path $root 'artifacts/remix-runtime/test-install'
$clientHash='4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29'
if((Get-FileHash (Join-Path $source 'StarFleetOP.exe')).Hash -ne $clientHash){throw 'Accepted client baseline mismatch'}
if(Test-Path -LiteralPath $target){throw 'Test directory already exists; inspect it and its manifest. Do not overwrite or clean automatically.'}
$entries=@(Get-ChildItem -LiteralPath $source -Recurse -Force)
if($entries | Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}){throw 'Source contains reparse points; copy scope requires adjudication'}
$files=@($entries | Where-Object {-not $_.PSIsContainer})
$total=($files | Measure-Object Length -Sum).Sum
if($files.Count -gt 20000 -or $total -gt 5GB){throw 'Independent-copy preparation exceeds approved practical envelope'}
if((Get-PSDrive C).Free -lt $total+2GB){throw 'Insufficient copy headroom'}
New-Item -ItemType Directory -Path $target | Out-Null
New-Item -ItemType Directory -Force -Path $out | Out-Null
$manifest=[Collections.Generic.List[object]]::new()
foreach($file in $files){
    $relative=$file.FullName.Substring($source.Length+1)
    $destination=Join-Path $target $relative
    New-Item -ItemType Directory -Force -Path (Split-Path $destination -Parent) | Out-Null
    $before=(Get-FileHash -LiteralPath $file.FullName).Hash
    Copy-Item -LiteralPath $file.FullName -Destination $destination
    $after=(Get-FileHash -LiteralPath $destination).Hash
    if($before -ne $after){throw "Independent copy hash mismatch: $relative"}
    $manifest.Add([ordered]@{path=$relative;bytes=$file.Length;source_sha256=$before;copy_sha256=$after})
}
$launcher=Join-Path $root 'Game Assets/SFCLauncher 2.1.0.22.exe'
if((Get-FileHash $launcher).Hash -ne '84D3A5F89A922C4BEE6815CF0614538C3565C4BDB7DB3AA187C552CB727EF890'){throw 'Reference launcher hash mismatch'}
Copy-Item -LiteralPath $launcher -Destination (Join-Path $target 'SFCLauncher 2.1.0.22.exe')
# Reference copy only: its global HKCU settings still select accepted installation.
# Prepared workflow must use an explicitly verified test-local client launch.
$manifest | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $out 'source-copy-files.json') -Encoding utf8
[ordered]@{source=$source;target=$target;files=$files.Count;bytes=$total;utc=[DateTime]::UtcNow.ToString('o');client_sha256=$clientHash;launcher_sha256=(Get-FileHash $launcher).Hash;reference_launcher_not_qualified_for_execution=$true;original_client_after_sha256=(Get-FileHash (Join-Path $source 'StarFleetOP.exe')).Hash} | ConvertTo-Json | Set-Content (Join-Path $out 'manifest.json') -Encoding utf8
Get-Content (Join-Path $out 'manifest.json')
