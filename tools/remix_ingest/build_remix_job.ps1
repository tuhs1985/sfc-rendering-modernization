$ErrorActionPreference='Stop'
$root=Resolve-Path (Join-Path $PSScriptRoot '../..')
$bin=Join-Path $root 'artifacts/remix-ingest/bin'
New-Item -ItemType Directory -Force -Path $bin | Out-Null
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
$line='"{0}" && cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /MT /Fo:"{1}\bounded_job.obj" /Fe:"{1}\bounded_job.exe" "{2}\bounded_job.cpp"' -f $vc,$bin,$PSScriptRoot
& $env:ComSpec /d /s /c $line
if($LASTEXITCODE){throw 'Bounded Remix job build failed'}
