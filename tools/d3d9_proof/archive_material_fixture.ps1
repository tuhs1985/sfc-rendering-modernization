param([Parameter(Mandatory)][string]$RunDirectory)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$allowed=[IO.Path]::GetFullPath((Join-Path $root 'artifacts/d3d9-proof/material-runs'))
$run=(Resolve-Path -LiteralPath $RunDirectory).Path
if([IO.Path]::GetDirectoryName($run) -ne $allowed -or [IO.Path]::GetFileName($run) -notmatch '^\d{8}-\d{6}-\d{6}$'){throw 'Exact material fixture required'}
if(Get-Process d3d9_direct_host,output_receiver -ErrorAction SilentlyContinue){throw 'Renderer still active'}
if(-not(Test-Path -LiteralPath (Join-Path $run 'result.json'))){throw 'Final fixture record required'}
$archive=$run+'-generated.zip';$receipt=Join-Path $run 'generated-archive.json'
if((Test-Path -LiteralPath $archive) -or (Test-Path -LiteralPath $receipt)){throw 'Do not overwrite existing archive/receipt'}
$records=@()
foreach($f in Get-ChildItem -LiteralPath $run -Recurse -File){
 if($f.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse fixture'}
 $relative=[IO.Path]::GetRelativePath($run,$f.FullName).Replace('\','/')
 if(-not $f.FullName.StartsWith($run+'\')){throw 'Escaped fixture'}
 if($relative -match '^(off|baseline|tuned|lit)/(texture-\d+\.bin|returned-\d+-[012]\.raw32|rtx-remix/mods/sfc-policy/textures/[a-f0-9]{64}\.dds)$'){
  if($f.Length -gt 64MB+16){throw 'Unexpected generated size'}
  $records+=@{name=$relative;sha256=(Get-FileHash -LiteralPath $f.FullName).Hash;bytes=$f.Length}
 }
}
if(-not $records.Count){throw 'No exact generated files'}
$zip=[IO.Compression.ZipFile]::Open($archive,[IO.Compression.ZipArchiveMode]::Create)
try{foreach($r in $records){[void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,(Join-Path $run $r.name),$r.name,[IO.Compression.CompressionLevel]::Optimal)}}finally{$zip.Dispose()}
$zip=[IO.Compression.ZipFile]::OpenRead($archive)
try{foreach($r in $records){$s=$zip.GetEntry($r.name).Open();$sha=[Security.Cryptography.SHA256]::Create();try{if([Convert]::ToHexString($sha.ComputeHash($s)) -ne $r.sha256){throw 'Archive content mismatch'}}finally{$s.Dispose();$sha.Dispose()}}}finally{$zip.Dispose()}
foreach($r in $records){if((Get-FileHash -LiteralPath (Join-Path $run $r.name)).Hash -ne $r.sha256){throw 'Source changed'}}
@{archive=$archive;sha256=(Get-FileHash -LiteralPath $archive).Hash;recoverable=$true;files=$records} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receipt
foreach($r in $records){Remove-Item -LiteralPath (Join-Path $run $r.name)}
[pscustomobject]@{archive=$archive;original_bytes=($records|Measure-Object bytes -Sum).Sum;archive_bytes=(Get-Item -LiteralPath $archive).Length}
