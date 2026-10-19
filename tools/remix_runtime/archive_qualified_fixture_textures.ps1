# Recoverable compaction of ONLY already-qualified generated fixture textures.
# Never operates on game installs,reference assets,active sessions or arbitrary paths.
param([ValidateSet('image','quality-pre-sampler','quality-final')][string]$Group='image')
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$evidencePath=switch($Group){'image'{'docs/reconnaissance/evidence/20261018-remix-image-controls.json'}'quality-pre-sampler'{'docs/reconnaissance/evidence/20261019-quality-pre-sampler-fixtures.json'}'quality-final'{'docs/reconnaissance/evidence/20261019-quality-controls.json'}}
$evidence=Get-Content (Join-Path $root $evidencePath) -Raw | ConvertFrom-Json
$namePattern=switch($Group){'image'{'^20261019-035[0-9]{3}-[0-9]+-live-private$'}'quality-pre-sampler'{'^20261019-043[0-9]{3}-[0-9]+-live-private$'}'quality-final'{'^20261019-044[0-9]{3}-[0-9]+-live-private$'}}
$runRoot=[IO.Path]::GetFullPath((Join-Path $root 'artifacts/remix-runtime/runs'))+[IO.Path]::DirectorySeparatorChar
$folders=@();$files=@()
foreach($gate in $evidence.gates){
 if($gate.result -notin @('OFFLINE_PROXY_PRIVATE_RETURN_PASS','OFFLINE_FRESH_PRIVATE_RETURN_PASS') -or $gate.failed){throw 'Unqualified fixture'}
 $folder=Join-Path $root ($gate.path+'/textures')
 if(-not(Test-Path -LiteralPath $folder)){continue}
 $absolute=(Resolve-Path -LiteralPath $folder).Path
 if(-not $absolute.StartsWith($runRoot,[StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetFileName($absolute) -ne 'textures' -or [IO.Path]::GetFileName([IO.Path]::GetDirectoryName($absolute)) -notmatch $namePattern){throw 'Not an exact enumerated generated texture directory'}
 if((Get-Item -LiteralPath $absolute).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse point'}
 $children=@(Get-ChildItem -LiteralPath $absolute -Force)
 if($children | Where-Object {$_.PSIsContainer -or ($_.Attributes -band [IO.FileAttributes]::ReparsePoint)}){throw 'Unexpected nested/generated path'}
 $folders+=$absolute;$files+=$children
}
if(-not $folders.Count){throw 'No fixture texture directories to compact'}
$archive=Join-Path $root $(switch($Group){'image'{'artifacts/remix-runtime/archives/20261019-run57-fixture-textures.zip'}'quality-pre-sampler'{'artifacts/remix-runtime/archives/20261019-pre-sampler-fixture-textures.zip'}'quality-final'{'artifacts/remix-runtime/archives/20261019-quality-final-fixture-textures.zip'}})
if(Test-Path -LiteralPath $archive){throw 'Archive exists;inspect before retry,never overwrite'}
if(($files | Measure-Object Length -Sum).Sum -gt 1GB -or $files.Count -gt 4096){throw 'Compaction scope bound'}
$zip=[IO.Compression.ZipFile]::Open($archive,[IO.Compression.ZipArchiveMode]::Create)
try{foreach($file in $files){[void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,$file.FullName,[IO.Path]::GetRelativePath($root,$file.FullName).Replace('\','/'),[IO.Compression.CompressionLevel]::Optimal)}}finally{$zip.Dispose()}
# Fully decompress and hash EVERY archived entry against still-existing source.
$zip=[IO.Compression.ZipFile]::OpenRead($archive)
try{
 if($zip.Entries.Count -ne $files.Count){throw 'Archive entry mismatch'}
 foreach($file in $files){$entry=$zip.GetEntry([IO.Path]::GetRelativePath($root,$file.FullName).Replace('\','/'));$stream=$entry.Open();$sha=[Security.Cryptography.SHA256]::Create()
  try{$actual=[Convert]::ToHexString($sha.ComputeHash($stream))}finally{$stream.Dispose();$sha.Dispose()}
  if($actual -ne (Get-FileHash -LiteralPath $file.FullName).Hash){throw 'Archived texture differs;leave all sources intact'}
 }
}finally{$zip.Dispose()}
$before=($files | Measure-Object Length -Sum).Sum
# Targets were resolved,exactly bounded and verified above;one native shell only.
foreach($folder in $folders){Remove-Item -LiteralPath $folder -Recurse -Force}
[ordered]@{archive=$archive;sha256=(Get-FileHash -LiteralPath $archive).Hash;entries=$files.Count;removed_generated_bytes=$before;archive_bytes=(Get-Item -LiteralPath $archive).Length;recoverable=$true;game_assets_removed=$false} | ConvertTo-Json
