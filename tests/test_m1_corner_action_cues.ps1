# Exercise the production action-cue block with a local synthetic gate and
# controlled clock. Replace only the physical sound call; do not launch SFC.
$ErrorActionPreference = 'Stop'
$runner = Join-Path $PSScriptRoot '..\tools\m1_component\run_m1_increment_a.ps1'
$tokens = $null; $errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($runner, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw 'Runner parse failed' }
$block = $ast.FindAll({ param($node)
    $node -is [System.Management.Automation.Language.IfStatementAst] -and
    $node.Extent.Text -match '^if \(\$EnableCornerSnapshot\) \{\s+if \(-not \$cornerGateWait'
}, $true) | Select-Object -First 1
if (-not $block) { throw 'Production cue block missing' }
$testBody = $block.Extent.Text.Replace('[Console]::Beep(800, 150)', '$script:toneCount++; if($script:verifyCueOrder -and $phase -eq 1 -and $copyReady.WaitOne(0)){throw "Capture enabled before start cue finished"}')
$script:verifyCueOrder=$false;$copyReady=$null
$script:clock = [datetime]'2026-10-11T12:00:00'
function Get-Date { $script:clock }
function Start-Sleep { param([int]$Milliseconds) }
$game = @{ Id = $PID }; $EnableCornerSnapshot = $true
$cornerGateWait = $null; $cornerGateObservedAt = $null; $cornerPhase = -1; $cornerCues = @()
$script:toneCount = 0
$gate = [Threading.EventWaitHandle]::new($false, [Threading.EventResetMode]::ManualReset,
    "Local\SFCM1TacticalGate_$PID")
try {
    . ([scriptblock]::Create($testBody)) | Out-Null
    if ($cornerCues.Count -ne 0) { throw 'Cue before gate' }
    [void]$gate.Set()
    . ([scriptblock]::Create($testBody)) | Out-Null
    $script:clock = $script:clock.AddSeconds(15)
    . ([scriptblock]::Create($testBody)) | Out-Null
    $script:clock = $script:clock.AddSeconds(15)
    . ([scriptblock]::Create($testBody)) | Out-Null
    $script:clock = $script:clock.AddSeconds(10)
    . ([scriptblock]::Create($testBody)) | Out-Null
    if ($cornerCues.Count -ne 3 -or $script:toneCount -ne 6 -or
        (($cornerCues.requested_phase -join ',') -ne '0,1,2')) { throw 'Wrong phase/cue bounds' }
    Write-Output 'PASS: automatic gate, three requested phases, one/two/three tones and no repeats.'
    $EnablePrivateCopy=$true;$cornerPhase=-1;$cornerGateObservedAt=$null;$cornerCues=@();$script:toneCount=0
    $copyReady=[Threading.EventWaitHandle]::new($false,[Threading.EventResetMode]::ManualReset,
        "Local\SFCM1PrivateCopyReady_$PID")
    $script:verifyCueOrder=$true
    . ([scriptblock]::Create($testBody))|Out-Null
    $script:clock=$script:clock.AddSeconds(19)
    . ([scriptblock]::Create($testBody))|Out-Null
    if($copyReady.WaitOne(0) -or $cornerCues.Count -ne 1){throw 'Copy started during setup'}
    $script:clock=$script:clock.AddSeconds(1)
    . ([scriptblock]::Create($testBody))|Out-Null
    if(-not $copyReady.WaitOne(0) -or $cornerCues.Count -ne 2 -or $script:toneCount -ne 3){throw 'Copy start cue/gate mismatch'}
    $script:clock=$script:clock.AddSeconds(20)
    . ([scriptblock]::Create($testBody))|Out-Null
    if($cornerCues.Count -ne 2){throw 'Repeated copy cue'}
    Write-Output 'PASS: private-copy setup20s, two-tone start completes before release, no repeats.'
    $EnableCopyEpochRequalification=$true
    . ([scriptblock]::Create($testBody))|Out-Null
    if($cornerCues.Count -ne 3 -or $cornerCues[-1].requested_phase -ne 2 -or $script:toneCount -ne 6 -or
        $cornerCues[-1].requested_action -notmatch 'away from BOTH ships'){throw 'Fresh-epoch third cue missing'}
    $script:clock=$script:clock.AddSeconds(10)
    . ([scriptblock]::Create($testBody))|Out-Null
    if($cornerCues.Count -ne 3){throw 'Repeated fresh-epoch third cue'}
    Write-Output 'PASS: optional fresh-epoch third cue at40s, no second release or repeated cue.'
    # Evaluate only the production metadata value, never the runtime workflow.
    $metadataLine=Get-Content -LiteralPath $runner | Where-Object {$_ -match '^    corner_snapshot_budget ='}
    if(@($metadataLine).Count -ne 1){throw 'Corner budget metadata missing'}
    $metadataBody=$metadataLine -replace '^\s*corner_snapshot_budget =', '$cueBudget ='
    foreach($cueCase in @(
        @{copy=$false;epoch=$false;expected='0,15,30'},
        @{copy=$true;epoch=$false;expected='0,20'},
        @{copy=$true;epoch=$true;expected='0,20,40'})){
        $EnablePrivateCopy=$cueCase.copy;$EnableCopyEpochRequalification=$cueCase.epoch
        . ([scriptblock]::Create($metadataBody))
        if(($cueBudget.cue_seconds -join ',') -ne $cueCase.expected){throw 'Cue metadata differs from actual mode'}
    }
    Write-Output 'PASS: legacy/copy/fresh-epoch metadata matches0/15/30,0/20,0/20/40 cues.'
    $EnableSurfaceLighting=$true;$EnablePrivateCopy=$true;$EnableCopyEpochRequalification=$false
    $cornerPhase=-1;$cornerGateObservedAt=$null;$cornerCues=@();$script:toneCount=0;[void]$copyReady.Reset()
    $surfaceLight=[Threading.EventWaitHandle]::new($false,[Threading.EventResetMode]::ManualReset,"Local\SFCM1SurfaceLighting_$PID")
    $surfaceRestore=[Threading.EventWaitHandle]::new($false,[Threading.EventResetMode]::ManualReset,"Local\SFCM1SurfaceRestored_$PID")
    try{
        . ([scriptblock]::Create($testBody))|Out-Null
        $script:clock=$script:clock.AddSeconds(20)
        . ([scriptblock]::Create($testBody))|Out-Null
        $script:clock=$script:clock.AddSeconds(30)
        . ([scriptblock]::Create($testBody))|Out-Null
        if($cornerCues.Count -ne 2){throw 'Surface phases guessed from runner clock rather than component events'}
        [void]$surfaceLight.Set();. ([scriptblock]::Create($testBody))|Out-Null
        [void]$surfaceRestore.Set();. ([scriptblock]::Create($testBody))|Out-Null
        if($cornerCues.Count -ne 4 -or $script:toneCount -ne 10 -or $cornerCues[1].requested_action -notmatch '20seconds'){
            throw 'Surface identification/lighting/restoration cue mismatch'
        }
        Write-Output 'PASS:20s marker instructions and event-driven lighting/restoration cues; no clock guessing.'
    }finally{$surfaceLight.Dispose();$surfaceRestore.Dispose()}
} finally {
    if($copyReady){$copyReady.Dispose()}
    if ($cornerGateWait) { $cornerGateWait.Dispose() }
    $gate.Dispose()
}
