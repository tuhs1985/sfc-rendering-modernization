# Recoverably compact only generated data from one exact,finished owned replay.
param([Parameter(Mandatory)][string]$RunDirectory)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$run=(Resolve-Path -LiteralPath $RunDirectory).Path
$runs=[IO.Path]::GetDirectoryName($run)
$allowed=@([IO.Path]::GetFullPath((Join-Path $root 'artifacts/d3d9-intercept/runs')),[IO.Path]::GetFullPath((Join-Path $root 'artifacts/d3d9-intercept/direct64-runs')))
if($runs -notin $allowed -or [IO.Path]::GetFileName($run) -notmatch '^\d{8}-\d{6}-\d{6}$'){throw 'Exact owned replay run required'}
if(Get-Process -Name d3d9_intercept,d3d9_direct_host,output_receiver,NvRemixBridge -ErrorAction SilentlyContinue){throw 'Replay/bridge active'}
$result=Get-Content -LiteralPath (Join-Path $run 'result.json') -Raw | ConvertFrom-Json
if($result.sfc_launched -or $result.sdk_registration -or $result.sdk_mesh_calls -gt 0 -or $result.job.remaining_owned_processes -ne 0 -or $result.job.exit_code -ne 0 -or $result.job.stop_reason){throw 'Run not safely completed'}
$archive=Join-Path $runs ([IO.Path]::GetFileName($run)+'-generated.zip')
$receipt=Join-Path $run 'generated-archive.json'
if((Test-Path -LiteralPath $archive) -and (Test-Path -LiteralPath $receipt)){return}
if(Test-Path -LiteralPath $archive){throw 'Unreceipted archive;do not overwrite'}
$files=@(Get-ChildItem -LiteralPath $run -Recurse -File | Where-Object {
 $relative=[IO.Path]::GetRelativePath($run,$_.FullName).Replace('\','/')
 $relative -match '^(scene\.bin|texture-\d+\.bin|(?:returned|receiver)-\d+-[012]\.raw32|ordinary-color-\d+\.bgra|Screenshots/[^/]+\.dds|rtx-remix/captures/.+)$'
})
if(-not $files.Count){throw 'No generated payload'}
foreach($item in @((Get-Item -LiteralPath $run)) + @(Get-ChildItem -LiteralPath $run -Recurse)){
 if($item.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse target'}
 if(-not $item.FullName.StartsWith($run+[IO.Path]::DirectorySeparatorChar) -and $item.FullName -ne $run){throw 'Escaped run'}
}
$records=@();$zip=[IO.Compression.ZipFile]::Open($archive,[IO.Compression.ZipArchiveMode]::Create)
try{foreach($file in $files){$relative=[IO.Path]::GetRelativePath($run,$file.FullName).Replace('\','/');[void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,$file.FullName,$relative,[IO.Compression.CompressionLevel]::Optimal);$records+=@{name=$relative;sha256=(Get-FileHash -LiteralPath $file.FullName).Hash;bytes=$file.Length}}}finally{$zip.Dispose()}
$zip=[IO.Compression.ZipFile]::OpenRead($archive)
try{if($zip.Entries.Count -ne $records.Count){throw 'ZIP count mismatch'};foreach($row in $records){$stream=$zip.GetEntry($row.name).Open();$sha=[Security.Cryptography.SHA256]::Create();try{$digest=[Convert]::ToHexString($sha.ComputeHash($stream))}finally{$sha.Dispose();$stream.Dispose()};if($digest -ne $row.sha256){throw 'ZIP decompressed mismatch;original retained'}}}finally{$zip.Dispose()}
$record=@{archive=$archive;sha256=(Get-FileHash -LiteralPath $archive).Hash;recoverable=$true;files=$records;removed_generated_bytes=($files | Measure-Object Length -Sum).Sum;archive_bytes=(Get-Item -LiteralPath $archive).Length}
$record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receipt
foreach($file in $files){Remove-Item -LiteralPath $file.FullName}
$record | Select-Object archive,removed_generated_bytes,archive_bytes,recoverable | ConvertTo-Json
