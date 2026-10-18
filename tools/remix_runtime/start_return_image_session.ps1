# Run only when ready to play, from the established elevated testing parent.
param([switch]$InspectVisibility,[switch]$InspectEarlyDepth,[switch]$ObservationOnly,[switch]$SearchDepth,[switch]$BroadCapture,[switch]$DepthSnapshots,[switch]$Calibration,[switch]$PrivateShip,[switch]$VisibleShip,[switch]$TexturedShip,[switch]$CaptureShipImage)
$ErrorActionPreference='Stop'
if($CaptureShipImage){$TexturedShip=$true}
if($TexturedShip -and ($PrivateShip -or $VisibleShip)){throw 'Choose TexturedShip alone'}
if($TexturedShip){$VisibleShip=$true}
if($VisibleShip -and $PrivateShip){throw 'Choose VisibleShip or PrivateShip,not both'}
if($VisibleShip){$PrivateShip=$true}
if($PrivateShip -and ($InspectVisibility -or $InspectEarlyDepth -or $ObservationOnly -or $SearchDepth -or $BroadCapture -or $DepthSnapshots -or $Calibration)){throw 'PrivateShip is a separate workflow'}
if($Calibration){$DepthSnapshots=$true;$ObservationOnly=$true}
if($InspectVisibility -and $InspectEarlyDepth){throw 'Choose one observation scope; do not combine late and early probes'}
if($SearchDepth -and ($InspectVisibility -or $InspectEarlyDepth)){throw 'SearchDepth cannot be combined with narrow observation modes'}
if($SearchDepth){$ObservationOnly=$true}
if($BroadCapture -and ($SearchDepth -or $InspectVisibility -or $InspectEarlyDepth)){throw 'BroadCapture cannot be combined with other observation modes'}
if($BroadCapture){$ObservationOnly=$true}
if($DepthSnapshots -and ($InspectVisibility -or $InspectEarlyDepth -or $SearchDepth -or $BroadCapture)){throw 'DepthSnapshots must be used alone'}
if($DepthSnapshots){$ObservationOnly=$true}
if($ObservationOnly -and -not ($InspectEarlyDepth -or $SearchDepth -or $BroadCapture -or $DepthSnapshots)){throw 'ObservationOnly requires InspectEarlyDepth, SearchDepth, BroadCapture or DepthSnapshots'}
$modern='C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
if($PSVersionTable.PSVersion.Major -lt 7){
    $forward=@('-NoProfile','-ExecutionPolicy','Bypass','-File',$PSCommandPath)
    if($InspectVisibility){$forward+='-InspectVisibility'}
    if($InspectEarlyDepth){$forward+='-InspectEarlyDepth'}
    if($ObservationOnly){$forward+='-ObservationOnly'}
    if($SearchDepth){$forward+='-SearchDepth'}
    if($BroadCapture){$forward+='-BroadCapture'}
    if($DepthSnapshots){$forward+='-DepthSnapshots'}
    if($Calibration){$forward+='-Calibration'}
    if($CaptureShipImage){$forward+='-CaptureShipImage'}elseif($TexturedShip){$forward+='-TexturedShip'}elseif($VisibleShip){$forward+='-VisibleShip'}elseif($PrivateShip){$forward+='-PrivateShip'}
    & $modern @forward
    if($LASTEXITCODE -ne 0){throw 'Prepared returned-image workflow failed; evidence retained'}
    return
}
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Import-Module (Join-Path $root 'tools/m0_probe/ProbeRunnerPolicy.psm1') -Force
$identity=[Security.Principal.WindowsIdentity]::GetCurrent();$principal=[Security.Principal.WindowsPrincipal]::new($identity)
[void](Test-ProbeElevation -IsElevated $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) -ElevateProbeRequested $false)
$clock=[Diagnostics.Stopwatch]::StartNew()
if($PrivateShip){& (Join-Path $PSScriptRoot 'build_live_return.ps1')}else{& (Join-Path $PSScriptRoot 'build_return_probe.ps1')}
& (Join-Path $root 'tools/m1_component/build_m1_controller.ps1')
# Calibration uses its offline-qualified semantic binary. Do not consume the
# gameplay workflow budget rebuilding every unrelated observer experiment.
$remaining=[Math]::Min(285,[Math]::Floor(300-$clock.Elapsed.TotalSeconds))
if($remaining -lt 120){throw 'Build consumed prepared workflow budget; no game launched'}
$runArgs=@((Join-Path $PSScriptRoot 'run_return_game.py'),'--execute','--budget-seconds',[string]$remaining)
if($InspectVisibility){$runArgs+='--inspect-visibility'}
if($InspectEarlyDepth){$runArgs+='--inspect-early-depth'}
if($ObservationOnly){$runArgs+='--observation-only'}
if($SearchDepth){$runArgs+='--search-depth'}
if($BroadCapture){$runArgs+='--broad-capture'}
if($DepthSnapshots){$runArgs+='--depth-snapshots'}
if($Calibration){$runArgs+='--calibration'}
if($CaptureShipImage){$runArgs+='--capture-ship-image'}elseif($TexturedShip){$runArgs+='--textured-ship'}elseif($VisibleShip){$runArgs+='--visible-ship'}elseif($PrivateShip){$runArgs+='--private-ship'}
& 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' @runArgs
if($LASTEXITCODE -ne 0){throw 'Returned-image test needs review; original installation untouched by runner'}
