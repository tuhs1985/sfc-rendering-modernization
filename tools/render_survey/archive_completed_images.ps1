# Recoverable admission maintenance: only derived DDS in completed owned runs.
param([switch]$Execute,[long]$TargetFreedBytes=3800000000)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$runs=(Resolve-Path (Join-Path $root 'artifacts/remix-runtime/runs')).Path
if(Get-Process -Name StarFleetOP,d3d11_return_fixture,return_host,ship_live_host,d3d9_direct_host -ErrorAction SilentlyContinue){throw 'A game/owned renderer is active;do not archive'}
$saved=0L;$count=0
foreach($directory in Get-ChildItem -LiteralPath $runs -Directory | Sort-Object Name){
 if($saved -ge $TargetFreedBytes){break}
 if($directory.Name -notmatch '^\d{8}-\d{6}-\d+-(in-game|return-fixture|live-private)$'){continue}
 if($directory.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse run rejected'}
 $run=$directory.FullName;$resultPath=Join-Path $run 'result.json'
 if(-not(Test-Path -LiteralPath $resultPath)){continue}
 $r=Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json
 if(-not($r.normal_exit -eq $true -or ($null -ne $r.fixture_exit -and $null -ne $r.host_exit))){continue}
 $receipt=Join-Path $run 'survey-admission-images-archive.json';$archive=Join-Path $run 'survey-admission-images.zip'
 if(Test-Path -LiteralPath $receipt){continue}
 if(Test-Path -LiteralPath $archive){throw 'Unreceipted archive;never overwrite'}
 $files=@(Get-ChildItem -LiteralPath $run -Recurse -File | Where-Object {
  $relative=[IO.Path]::GetRelativePath($run,$_.FullName).Replace('\','/')
  $relative -match '^(textures/[^/]+\.dds|gpu/assets/\d+/rtx-remix/mods/sfc-policy/textures/[a-f0-9]{64}\.dds)$'
 })
 if(-not $files.Count){continue}
 foreach($file in $files){
  $resolved=[IO.Path]::GetFullPath($file.FullName)
  if(-not $resolved.StartsWith($run+'\',[StringComparison]::OrdinalIgnoreCase) -or $file.Length -gt 67108864){throw 'Unexpected derived-image target'}
  $parent=$file.Directory
  while($parent.FullName -ne $runs){if($parent.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse ancestor rejected'};$parent=$parent.Parent}
 }
 $before=($files | Measure-Object Length -Sum).Sum
 if(-not $Execute){$saved+=$before;$count++;continue}
 $rows=@();$zip=[IO.Compression.ZipFile]::Open($archive,[IO.Compression.ZipArchiveMode]::Create)
 try{foreach($file in $files){
  $name=[IO.Path]::GetRelativePath($run,$file.FullName).Replace('\','/')
  $rows+=@{name=$name;bytes=$file.Length;sha256=(Get-FileHash -LiteralPath $file.FullName).Hash}
  [void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,$file.FullName,$name,[IO.Compression.CompressionLevel]::Optimal)
 }}finally{$zip.Dispose()}
 $zip=[IO.Compression.ZipFile]::OpenRead($archive)
 try{if($zip.Entries.Count -ne $rows.Count){throw 'ZIP entry mismatch'}
  foreach($row in $rows){$stream=$zip.GetEntry($row.name).Open();$sha=[Security.Cryptography.SHA256]::Create()
   try{$hash=[Convert]::ToHexString($sha.ComputeHash($stream))}finally{$sha.Dispose();$stream.Dispose()}
   if($hash -ne $row.sha256 -or (Get-FileHash -LiteralPath (Join-Path $run $row.name)).Hash -ne $row.sha256){throw 'Source/decompressed SHA mismatch;retain loose copies'}
  }
 }finally{$zip.Dispose()}
 $size=(Get-Item -LiteralPath $archive).Length
 @{archive=$archive;archive_sha256=(Get-FileHash -LiteralPath $archive).Hash;archive_bytes=$size;source_bytes=$before;files=$rows;recoverable=$true;restore='Extract each recorded relative entry into this exact run directory;verify its SHA256 before replaying historical GPU inputs.'} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receipt
 # Exact resolved files validated above; no recursive directory deletion.
 foreach($file in $files){Remove-Item -LiteralPath $file.FullName}
 $saved+=$before-$size;$count++
 Write-Output ([pscustomobject]@{run=$directory.Name;source_bytes=$before;archive_bytes=$size;net_saved=$before-$size;recoverable=$true})
}
[pscustomobject]@{execute=[bool]$Execute;runs=$count;net_saved_or_preview_source_bytes=$saved;target=$TargetFreedBytes}
