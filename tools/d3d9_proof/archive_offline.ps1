# Recover only completed offline proof's generated binary inputs/readbacks.
param([Parameter(Mandatory)][string]$RunDirectory,[switch]$AllowPartial)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$runs=(Resolve-Path (Join-Path $root 'artifacts/d3d9-proof/runs')).Path
$run=(Resolve-Path -LiteralPath $RunDirectory).Path
if([IO.Path]::GetDirectoryName($run) -ne $runs -or [IO.Path]::GetFileName($run) -notmatch '^\d{8}-\d{6}-\d{6}$'){throw 'Exact completed offline run required'}
if((Get-Item -LiteralPath $run).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse run'}
$r=Get-Content -LiteralPath (Join-Path $run 'result.json') -Raw | ConvertFrom-Json
if($r.sfc_launched -or $r.remix_loaded -or ($r.result -ne 'OFFLINE_PLAIN_D3D9_TWO_ASSET_PASS' -and -not($AllowPartial -and $r.result -eq 'PARTIAL'))){throw 'Not completed offline proof'}
if(Get-Process -Name d3d9_replay -ErrorAction SilentlyContinue){throw 'Offline renderer still running'}
$receipt=Join-Path $run 'generated-archive.json'
$archive=Join-Path $runs ([IO.Path]::GetFileName($run)+'-generated.zip')
if((Test-Path -LiteralPath $receipt) -and (Test-Path -LiteralPath $archive)){return}
if(Test-Path -LiteralPath $archive){throw 'Unreceipted archive exists;do not overwrite'}
$files=@()
foreach($directory in Get-ChildItem -LiteralPath $run -Directory){
 if($directory.Name -notmatch '^(asset-\d+|synthetic|truncated|nonfinite|bad-index|bad-group|bad-frame|missing-texture|startup)$' -or ($directory.Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Unexpected proof subdirectory'}
 foreach($file in Get-ChildItem -LiteralPath $directory.FullName -File){
  if($file.Name -notmatch '^(scene\.bin|texture-\d+\.(bin|unavailable)|(color|mask)-([0-9]+|resized)\.bgra)$'){continue}
  if(($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $file.Length -gt 64MB+16 -or [IO.Path]::GetDirectoryName($file.FullName) -ne $directory.FullName){throw 'Unexpected generated file'}
  $files+=$file
 }
}
if(-not $files.Count){throw 'No generated files to compact'}
$records=@();$zip=[IO.Compression.ZipFile]::Open($archive,[IO.Compression.ZipArchiveMode]::Create)
try{foreach($file in $files){$relative=[IO.Path]::GetRelativePath($run,$file.FullName).Replace('\','/');[void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,$file.FullName,$relative,[IO.Compression.CompressionLevel]::Optimal);$records+=@{name=$relative;sha256=(Get-FileHash -LiteralPath $file.FullName).Hash;bytes=$file.Length}}}finally{$zip.Dispose()}
$zip=[IO.Compression.ZipFile]::OpenRead($archive)
try{if($zip.Entries.Count -ne $files.Count){throw 'ZIP count mismatch'};foreach($row in $records){$stream=$zip.GetEntry($row.name).Open();$sha=[Security.Cryptography.SHA256]::Create();try{$digest=[Convert]::ToHexString($sha.ComputeHash($stream))}finally{$sha.Dispose();$stream.Dispose()};if($digest -ne $row.sha256){throw 'Decompressed bytes mismatch;source files retained'}}}finally{$zip.Dispose()}
$record=@{archive=$archive;sha256=(Get-FileHash -LiteralPath $archive).Hash;recoverable=$true;files=$records;removed_generated_bytes=($files | Measure-Object Length -Sum).Sum;archive_bytes=(Get-Item -LiteralPath $archive).Length}
$record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receipt
# Every literal target resolved/validated above inside the exact owned run.
foreach($file in $files){Remove-Item -LiteralPath $file.FullName}
$record | Select-Object archive,removed_generated_bytes,archive_bytes,recoverable | ConvertTo-Json
