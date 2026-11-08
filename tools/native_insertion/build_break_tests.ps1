# Focused debris tests. No SFC launch, installed hooks, or user settings changes.
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$out=Join-Path $root 'artifacts/break-live/bin'
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build'
$python='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
New-Item -ItemType Directory -Force -Path $out | Out-Null
Push-Location $out
try {
 foreach($test in @('m1_break_hook_tests','m1_break_scene_tests','break_piece_tests')){
  $standard=if($test -eq 'break_piece_tests'){'20'}else{'17'}
  $command='"{0}\vcvars32.bat" && cl /nologo /std:c++{1} /EHsc /W4 /WX /O2 /MT /DSFC_NATIVE_LIGHT_DISCOVERY "{2}\tests\{3}.cpp" /Fe:{3}.exe /link /Brepro user32.lib' -f $vc,$standard,$root,$test
  & $env:ComSpec /d /s /c $command
  if($LASTEXITCODE -ne 0){throw "Debris fixture build failed: $test"}
  if($test -ne 'm1_break_scene_tests'){
   & (Join-Path $out "$test.exe") | Tee-Object -FilePath (Join-Path $out "$test.txt")
   if($LASTEXITCODE -ne 0){throw "Debris fixture failed: $test"}
  }
 }
 # The transport test names a stable fixture executable; do not duplicate its logic.
 Copy-Item -LiteralPath (Join-Path $out 'm1_break_scene_tests.exe') -Destination (Join-Path $out 'break_scene_tests.exe') -Force
} finally {Pop-Location}
$env:TEMP=Join-Path $root 'artifacts/test-temp';$env:TMP=$env:TEMP
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
Push-Location $root
try {
 & $python -B -m unittest discover -s tests -p test_break_transport.py
 if($LASTEXITCODE -ne 0){throw 'Actual debris transport/admission tests failed'}
 & $python -B -m unittest discover -s tests -p test_break_replay_output.py
 if($LASTEXITCODE -ne 0){throw 'Debris output qualification tests failed'}
} finally {Pop-Location}
