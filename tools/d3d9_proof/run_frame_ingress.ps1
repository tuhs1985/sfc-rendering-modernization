$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$parent=Join-Path $root 'artifacts/d3d9-proof/ingress-x64/frame_ingress_fixture.exe'
$child=Join-Path $root 'artifacts/d3d9-proof/ingress-x86/frame_ingress_fixture.exe'
$guard=Join-Path $root 'artifacts/remix-ingest/bin/bounded_job.exe'
foreach($path in @($parent,$child,$guard)){if(-not(Test-Path -LiteralPath $path -PathType Leaf)){throw "Missing prepared input: $path"}}
foreach($mode in @('normal','slow','disconnect','malformed','stop')){
 $stamp=[DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss-ffffff')
 $folder=Join-Path $root "artifacts/d3d9-proof/ingress-runs/$stamp-$mode"
 New-Item -ItemType Directory -Path $folder | Out-Null
 & $guard $folder 15 8388608 1048576 $parent $child $mode (Join-Path $folder 'receipt.json')
 if($LASTEXITCODE -ne 0){throw "Ingress fixture failed; preserve $folder"}
 $job=Get-Content (Join-Path $folder 'job-result.json') -Raw | ConvertFrom-Json
 $receipt=Get-Content (Join-Path $folder 'receipt.json') -Raw | ConvertFrom-Json
 if($job.exit_code -ne 0 -or $job.stop_reason -or $job.remaining_owned_processes -ne 0 -or $receipt.result -ne 'INGRESS_TRANSPORT_FIXTURE_PASS'){throw "Ingress cleanup/result failed; preserve $folder"}
 Write-Output "${mode}: PASS $folder"
}
