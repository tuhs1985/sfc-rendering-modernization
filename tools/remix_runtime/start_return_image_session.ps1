# Run only when ready to play, from the established elevated testing parent.
param([switch]$InspectVisibility,[switch]$InspectEarlyDepth,[switch]$ObservationOnly,[switch]$SearchDepth,[switch]$BroadCapture,[switch]$DepthSnapshots,[switch]$Calibration,[switch]$PrivateShip,[switch]$VisibleShip,[switch]$TexturedShip,[switch]$CaptureShipImage,[switch]$CaptureNativeLights,[switch]$LightWiring,[switch]$LightTuning,[switch]$SceneDepth,[switch]$SourceTiming,[switch]$LiveOwnerTiming,[switch]$D3D9Additive,[switch]$LifecycleCapture,[switch]$CameraRecovery,[switch]$OffscreenPosition)
$ErrorActionPreference='Stop'
if($OffscreenPosition){if(-not $D3D9Additive){throw 'OffscreenPosition requires D3D9Additive'};$CameraRecovery=$true}
if($CameraRecovery){$LifecycleCapture=$true}
if($LifecycleCapture -and -not $D3D9Additive){throw 'LifecycleCapture requires the separate D3D9Additive test'}
if($D3D9Additive){$LiveOwnerTiming=$true;$SourceTiming=$true}
if($LiveOwnerTiming){$SourceTiming=$true}
if($SourceTiming){
 if($InspectVisibility -or $InspectEarlyDepth -or $SearchDepth -or $BroadCapture -or $DepthSnapshots -or $Calibration -or $PrivateShip -or $VisibleShip -or $TexturedShip -or $CaptureShipImage -or $CaptureNativeLights -or $LightWiring -or $LightTuning -or $SceneDepth){throw 'SourceTiming is a separate metadata-only workflow'}
 $ObservationOnly=$true
}
if($SceneDepth){if($LightTuning -or $CaptureShipImage){throw 'SceneDepth is separate from tuning/image capture'};$LightWiring=$true}
if($LightTuning){$LightWiring=$true}
if($CaptureShipImage){$TexturedShip=$true}
if($CaptureNativeLights){$TexturedShip=$true}
if($LightWiring){$CaptureNativeLights=$true;$TexturedShip=$true}
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
if($ObservationOnly -and -not ($InspectEarlyDepth -or $SearchDepth -or $BroadCapture -or $DepthSnapshots -or $SourceTiming)){throw 'ObservationOnly requires InspectEarlyDepth, SearchDepth, BroadCapture, DepthSnapshots or SourceTiming'}
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
    if($SourceTiming){$forward+='-SourceTiming'}
    if($LiveOwnerTiming){$forward+='-LiveOwnerTiming'}
    if($D3D9Additive){$forward+='-D3D9Additive'}
    if($LifecycleCapture){$forward+='-LifecycleCapture'}
    if($CameraRecovery){$forward+='-CameraRecovery'}
    if($OffscreenPosition){$forward+='-OffscreenPosition'}
    if($CaptureNativeLights){$forward+='-CaptureNativeLights'}
    if($LightWiring){$forward+='-LightWiring'}
    if($LightTuning){$forward+='-LightTuning'}
    if($SceneDepth){$forward+='-SceneDepth'}
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
if($SourceTiming){
 $module=if($D3D9Additive){'additive_qualification'}elseif($LiveOwnerTiming){'live_owner_timing'}else{'source_timing'}
 $check='import sys;sys.path.insert(0,r"'+$PSScriptRoot+'");from '+$module+' import require_qualification;require_qualification();print("Qualified timing binaries verified;no rebuild during setup")'
 & 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c $check
 if($LASTEXITCODE -ne 0){throw 'Source timing needs offline qualification;no game launched'}
}else{
 if($LightTuning){& (Join-Path $PSScriptRoot 'build_tuning_launcher.ps1')}
 if($PrivateShip){& (Join-Path $PSScriptRoot 'build_live_return.ps1')}else{& (Join-Path $PSScriptRoot 'build_return_probe.ps1')}
 & (Join-Path $root 'tools/m1_component/build_m1_controller.ps1')
 if($CaptureNativeLights){& (Join-Path $root 'tools/m1_component/build_light_discovery.ps1')}
}
# Calibration uses its offline-qualified semantic binary. Do not consume the
# gameplay workflow budget rebuilding every unrelated observer experiment.
$remaining=[Math]::Min(285,[Math]::Floor(300-$clock.Elapsed.TotalSeconds))
if($remaining -lt 120){throw 'Build consumed prepared workflow budget; no game launched'}
$runArgs=@((Join-Path $PSScriptRoot 'run_return_game.py'),'--execute','--budget-seconds',[string]$remaining)
if($CaptureNativeLights){$runArgs+='--capture-native-lights'}
if($LightWiring){$runArgs+='--light-wiring'}
if($LightTuning){$runArgs+='--light-tuning'}
if($SceneDepth){$runArgs+='--scene-depth'}
if($InspectVisibility){$runArgs+='--inspect-visibility'}
if($InspectEarlyDepth){$runArgs+='--inspect-early-depth'}
if($ObservationOnly){$runArgs+='--observation-only'}
if($SearchDepth){$runArgs+='--search-depth'}
if($BroadCapture){$runArgs+='--broad-capture'}
if($DepthSnapshots){$runArgs+='--depth-snapshots'}
if($Calibration){$runArgs+='--calibration'}
if($SourceTiming){$runArgs+='--source-timing'}
if($LiveOwnerTiming){$runArgs+='--live-owner-timing'}
if($D3D9Additive){$runArgs+='--d3d9-additive'}
if($LifecycleCapture){$runArgs+='--lifecycle-capture'}
if($CameraRecovery){$runArgs+='--camera-recovery'}
if($OffscreenPosition){$runArgs+='--offscreen-position'}
if($CaptureShipImage){$runArgs+='--capture-ship-image'}elseif($TexturedShip){$runArgs+='--textured-ship'}elseif($VisibleShip){$runArgs+='--visible-ship'}elseif($PrivateShip){$runArgs+='--private-ship'}
& 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' @runArgs
if($LASTEXITCODE -ne 0){throw 'Returned-image test needs review; original installation untouched by runner'}
