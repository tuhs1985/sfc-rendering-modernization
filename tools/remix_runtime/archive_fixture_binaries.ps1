# Recoverable compaction of recorded binary copies and optional owned GPU inputs.
param([Parameter(Mandatory)][string]$RunDirectory,[switch]$PartialGeneratedInputs,[switch]$CompletedGame)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$runs=(Resolve-Path (Join-Path $root 'artifacts/remix-runtime/runs')).Path
$run=(Resolve-Path -LiteralPath $RunDirectory).Path
if([IO.Path]::GetDirectoryName($run) -ne $runs -or [IO.Path]::GetFileName($run) -notmatch '^\d{8}-[0-9]{6}-[0-9]+-(live-private|return-fixture|in-game)$'){throw 'Exact dated fixture required'}
if((Get-Item -LiteralPath $run).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse fixture'}
if(Get-Process -Name d3d11_return_fixture,ship_live_host,return_host,return_launcher,d3d9_direct_host,output_receiver -ErrorAction SilentlyContinue){throw 'Owned fixture/host still active'}
$result=Get-Content -LiteralPath (Join-Path $run 'result.json') -Raw | ConvertFrom-Json
$ordinary=[IO.Path]::GetFileName($run).EndsWith('-return-fixture')
$game=[IO.Path]::GetFileName($run).EndsWith('-in-game')
if($game -ne [bool]$CompletedGame){throw 'Actual game compaction requires explicit CompletedGame,not a fixture switch'}
if($game){
 if($PartialGeneratedInputs -or $result.probe -ne 'D3D9-ADDITIVE-001' -or $result.error -or -not $result.normal_game_exit -or -not $result.gate_clean_unloaded -or -not $result.original_critical_unchanged -or -not $result.launcher_settings_unchanged -or -not $result.broad_proxy_restored){throw 'Actual game cleanup not fully confirmed'}
 foreach($property in $result.accepted_critical_after.PSObject.Properties){if($result.copied_critical_after.($property.Name) -ne $property.Value){throw 'Copied critical baseline not restored'}}
}elseif($ordinary){
 if($result.probe -ne 'REMIX-RETURN-001-FIXTURE' -or $null -eq $result.fixture_exit -or $null -eq $result.host_exit -or (-not $PartialGeneratedInputs -and ($result.fixture_exit -ne 0 -or $result.host_exit -ne 0))){throw 'Standalone fixture processes not safely completed'}
 # A partial analysis is retained,not promoted. Only finished generated INPUT
 # copies are compacted;metadata,raw records and failure logs remain loose.
}else{
 $manifest=Get-Content -LiteralPath (Join-Path $run 'manifest.json') -Raw | ConvertFrom-Json
 if($result.result -notin @('OFFLINE_FRESH_PRIVATE_RETURN_PASS','OFFLINE_PROXY_PRIVATE_RETURN_PASS') -or $result.sfc_launched -or $result.fixture_exit -or $result.telemetry.failed){throw 'Fixture not safely completed'}
}
$suffix=if($game){'-generated-inputs.zip'}else{'-binaries.zip'}
$archive=Join-Path $root ('artifacts/remix-runtime/archives/'+[IO.Path]::GetFileName($run)+$suffix)
$receipt=Join-Path $run 'binary-archive.json'
if((Test-Path -LiteralPath $receipt) -and (Test-Path -LiteralPath $archive)){return}
if(Test-Path -LiteralPath $archive){throw 'Archive already exists without receipt;review,do not overwrite'}
$files=@()
$binaryNames=if($game){@()}else{@('d3d11_return_fixture.exe','SFCRemixReturn.dll','dxgi.dll')}
foreach($name in $binaryNames){
 $path=Join-Path $run $name
 if(-not(Test-Path -LiteralPath $path)){continue}
 $file=Get-Item -LiteralPath $path
 if($file.PSIsContainer -or $file.Length -gt 16MB -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -or [IO.Path]::GetDirectoryName($file.FullName) -ne $run){throw 'Unexpected generated file'}
 $hash=(Get-FileHash -LiteralPath $path).Hash
 $expected=if($ordinary -and $name -ne 'dxgi.dll'){$result.source_files.$name}else{switch($name){
  'd3d11_return_fixture.exe' {$manifest.binaries.'ship_live_gpu_fixture.exe'}
  'SFCRemixReturn.dll' {$manifest.binaries.'SFCRemixReturn.dll'}
  'dxgi.dll' {$hash}
 }}
 if($hash -ne $expected -or ($name -eq 'dxgi.dll' -and $hash -notin @('E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7','A1BA732B5E31E0405CDE322CC5EC62CF972B3FBAEFBB6CBDC8A24DA00D58AE24'))){throw 'Generated copy differs from recorded/qualified binary'}
 $files+=$file
}
$gpu=Join-Path $run 'gpu'
if(Test-Path -LiteralPath $gpu){
 if((-not $ordinary -and -not $game) -or (-not $PartialGeneratedInputs -and -not $result.live_owner_timing.normal_owned_exit)){throw 'Nested GPU fixture not safely completed'}
 $jobPath=Join-Path $gpu 'job-result.json'
 if(Test-Path -LiteralPath $jobPath){
  $job=Get-Content -LiteralPath $jobPath -Raw | ConvertFrom-Json
  if($null -eq $job.exit_code -or (-not $PartialGeneratedInputs -and $job.exit_code -ne 0) -or $job.stop_reason -or $job.remaining_owned_processes -ne 0){throw 'GPU job still owned or failed'}
 }elseif(-not $PartialGeneratedInputs -or $null -ne $result.live_owner_timing -or (Test-Path -LiteralPath (Join-Path $gpu 'job-console.log')) -or $result.error -notlike 'Fixture time/output cap*'){
  throw 'Missing owned-job completion;not a recorded prelaunch preparation failure'
 }
 if((Get-Item -LiteralPath $gpu).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse GPU folder'}
 $scene=Get-Content -LiteralPath (Join-Path $gpu 'scene.json') -Raw | ConvertFrom-Json
 foreach($file in @(Get-ChildItem -LiteralPath $gpu -File | Where-Object {$_.Name -eq 'scene.bin' -or $_.Name -match '^texture-\d+\.bin$'})){
  if($file.Length -gt 128MB -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -or [IO.Path]::GetDirectoryName($file.FullName) -ne $gpu){throw 'Unexpected GPU input target'}
  if($file.Name -eq 'scene.bin'){$expected=$scene.replay_sha256}else{
   if($file.BaseName -notmatch '^texture-(\d+)$'){throw 'Invalid GPU image input'}
   $index=[int]$Matches[1];if($index -ge $scene.textures.Count){throw 'Unrecorded GPU image input'}
   $expected=$scene.textures[$index].replay_sha256
  }
  if((Get-FileHash -LiteralPath $file.FullName).Hash -ne $expected){throw 'GPU input differs from manifest'}
  $files+=$file
 }
 $textureDir=Join-Path $gpu 'rtx-remix/mods/sfc-policy/textures'
 if(Test-Path -LiteralPath $textureDir){
  $binding=Get-Content -LiteralPath (Join-Path $gpu 'material-binding.json') -Raw | ConvertFrom-Json
  if((Get-Item -LiteralPath $textureDir).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse derived image folder'}
  foreach($file in @(Get-ChildItem -LiteralPath $textureDir -File)){
   if($file.Name -notmatch '^[0-9a-f]{64}\.dds$' -or $file.Length -gt 128MB -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Unexpected derived image target'}
   $entry='textures/'+$file.Name
   if((Get-FileHash -LiteralPath $file.FullName).Hash -ne $binding.images.$entry.sha256){throw 'Derived image differs from manifest'}
   $files+=$file
  }
 }
}
if(-not $files.Count){return}
$zip=[IO.Compression.ZipFile]::Open($archive,[IO.Compression.ZipArchiveMode]::Create)
try{foreach($file in $files){$entry=[IO.Path]::GetRelativePath($run,$file.FullName).Replace('\','/');[void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,$file.FullName,$entry,[IO.Compression.CompressionLevel]::Optimal)}}finally{$zip.Dispose()}
$zip=[IO.Compression.ZipFile]::OpenRead($archive)
try{
 if($zip.Entries.Count -ne $files.Count){throw 'Entry count mismatch'}
 foreach($file in $files){$entry=[IO.Path]::GetRelativePath($run,$file.FullName).Replace('\','/');$stream=$zip.GetEntry($entry).Open();$sha=[Security.Cryptography.SHA256]::Create()
  try{$digest=[Convert]::ToHexString($sha.ComputeHash($stream))}finally{$sha.Dispose();$stream.Dispose()}
  if($digest -ne (Get-FileHash -LiteralPath $file.FullName).Hash){throw 'Decompressed content mismatch;sources retained'}
 }
}finally{$zip.Dispose()}
$record=[ordered]@{archive=$archive;sha256=(Get-FileHash -LiteralPath $archive).Hash;entries=$files.Count;removed_generated_bytes=($files | Measure-Object Length -Sum).Sum;archive_bytes=(Get-Item -LiteralPath $archive).Length;recoverable=$true;partial_evidence_not_promoted=[bool]$PartialGeneratedInputs}
# Exact resolved file targets checked above. No recursive deletion;no game paths.
$record | ConvertTo-Json | Set-Content -LiteralPath $receipt
foreach($file in $files){Remove-Item -LiteralPath $file.FullName}
$record | ConvertTo-Json
