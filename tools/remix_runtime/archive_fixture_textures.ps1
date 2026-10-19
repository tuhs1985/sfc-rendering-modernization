# Exact, finished private fixtures only. Originals and provenance are never removed.
param([Parameter(Mandatory)][string]$RunDirectory,[switch]$AllowCompletedPartial)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$runs=(Resolve-Path (Join-Path $root 'artifacts/remix-runtime/runs')).Path
$run=(Resolve-Path -LiteralPath $RunDirectory).Path
if([IO.Path]::GetDirectoryName($run) -ne $runs -or [IO.Path]::GetFileName($run) -notmatch '^20261019-[0-9]{6}-[0-9]+-live-private$'){throw 'Not an exact current-day private fixture'}
if((Get-Item -LiteralPath $run).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse run'}
$result=Get-Content (Join-Path $run 'result.json') -Raw | ConvertFrom-Json
$completedPartial=$AllowCompletedPartial -and $result.result -eq 'PARTIAL' -and $result.error -eq 'Material SDK hot-reload/last-good proof incomplete'
if($completedPartial){
 if((Get-Content (Join-Path $run 'host.log') -Raw) -notmatch 'LIVE_SHUTDOWN api=0' -or (Get-Content (Join-Path $run 'fixture.log') -Raw) -notmatch 'PRIVATE_GPU_FIXTURE_PASS'){throw 'Partial fixture did not finish safely'}
}
if(($result.result -notin @('OFFLINE_FRESH_PRIVATE_RETURN_PASS','OFFLINE_PROXY_PRIVATE_RETURN_PASS') -and -not $completedPartial) -or $result.sfc_launched -or $result.fixture_exit -or $result.telemetry.failed){throw 'Fixture not safely completed'}
$target=Join-Path $run 'textures'
if(-not(Test-Path -LiteralPath $target)){return}
$target=(Resolve-Path -LiteralPath $target).Path
if([IO.Path]::GetDirectoryName($target) -ne $run -or (Get-Item -LiteralPath $target).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Unexpected texture target'}
$files=@(Get-ChildItem -LiteralPath $target -Force)
if($files | Where-Object {$_.PSIsContainer -or ($_.Attributes -band [IO.FileAttributes]::ReparsePoint)}){throw 'Nested/reparse input'}
if($files.Count -gt 4096 -or ($files | Measure-Object Length -Sum).Sum -gt 128MB){throw 'Fixture image bound'}
$archive=Join-Path $root ('artifacts/remix-runtime/archives/'+[IO.Path]::GetFileName($run)+'-textures.zip')
if(Test-Path -LiteralPath $archive){throw 'Archive already exists;never overwrite'}
$zip=[IO.Compression.ZipFile]::Open($archive,[IO.Compression.ZipArchiveMode]::Create)
try{foreach($file in $files){[void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,$file.FullName,$file.Name,[IO.Compression.CompressionLevel]::Optimal)}}finally{$zip.Dispose()}
$zip=[IO.Compression.ZipFile]::OpenRead($archive)
try{
 if($zip.Entries.Count -ne $files.Count){throw 'Entry count mismatch'}
 foreach($file in $files){$stream=$zip.GetEntry($file.Name).Open();$sha=[Security.Cryptography.SHA256]::Create()
  try{$digest=[Convert]::ToHexString($sha.ComputeHash($stream))}finally{$sha.Dispose();$stream.Dispose()}
  if($digest -ne (Get-FileHash -LiteralPath $file.FullName).Hash){throw 'Decompressed content mismatch;retain sources'}
 }
}finally{$zip.Dispose()}
$receipt=[ordered]@{archive=$archive;sha256=(Get-FileHash -LiteralPath $archive).Hash;entries=$files.Count;removed_generated_bytes=($files | Measure-Object Length -Sum).Sum;archive_bytes=(Get-Item -LiteralPath $archive).Length;recoverable=$true}
# Resolved exact generated target verified above; same native shell end-to-end.
Remove-Item -LiteralPath $target -Recurse -Force
$receipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $run 'texture-archive.json')
$receipt | ConvertTo-Json
