# Run in the desktop session from an Administrator PowerShell window.
param(
    [ValidateSet('First','Repeat')][string]$Pass='First',
    [switch]$Launch,
    [switch]$TimingOnly,
    [switch]$CheckOnly
)
$ErrorActionPreference='Stop'
$root=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$profile=(Join-Path $PSScriptRoot 'sfc23-startup.wprp')+'!SfcStartup'
$wpr=Join-Path $env:SystemRoot 'System32\wpr.exe'
$gameExe='C:\Games\Taldren Software Inc\Starfleet Command Orion Pirates\StarFleetOP.exe'

function Get-DesktopShell {
    $shell=New-Object -ComObject Shell.Application
    $desktopHandle=0
    $desktop=$shell.Windows().FindWindowSW(0,0,8,[ref]$desktopHandle,1)
    if($null -eq $desktop -or $desktopHandle -eq 0){throw 'Run from the signed-in Windows desktop session with Explorer running.'}
    $desktop.Document.Application
}

function Invoke-Wpr {
    $output=& $wpr @args | Out-String
    if($LASTEXITCODE -ne 0){throw "WPR failed ($LASTEXITCODE): $output"}
    $output.Trim()
}

if($CheckOnly){
    if(-not $TimingOnly){
        Invoke-Wpr -profiledetails $profile -filemode
        Invoke-Wpr -status
    }
    if($Launch){
        if(-not (Test-Path -LiteralPath $gameExe -PathType Leaf)){throw "SFC executable missing: $gameExe"}
        if(-not (Get-DesktopShell | Get-Member -Name ShellExecute)){throw 'Explorer launch interface unavailable.'}
        Write-Host 'SFC target and Explorer launch interface verified.'
    }
    return
}
if(Get-Process StarFleetOP -ErrorAction SilentlyContinue){throw 'Exit SFC normally before starting the capture.'}
if(-not $TimingOnly){
    if(-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){
        throw 'Open Administrator PowerShell for this Windows kernel capture.'
    }
    if((Invoke-Wpr -status) -notmatch 'WPR is not recording'){throw 'An existing WPR recording is active.'}
    $drive=[IO.DriveInfo]::new([IO.Path]::GetPathRoot($root))
    if($drive.AvailableFreeSpace -lt 3GB){throw 'At least 3 GiB free is required for trace recording and finalization.'}
}
$boot=(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime().ToString('o')
$stamp=[DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss-fff')
$folder=Join-Path $root "artifacts/player-replacement/sfc23/$stamp-$Pass"
New-Item -ItemType Directory -Path $folder | Out-Null
$etl=Join-Path $folder 'startup.etl'
$clock=[Diagnostics.Stopwatch]::new()
$events=[Collections.Generic.List[object]]::new()
$gamePid=$null
$menuMarked=$false
$lastWindow=$null
$owned=$false
$saved=$false
$reason='capture_window_elapsed'
$recordingLimit=768MB
$desktopShell=$null
if($Launch){
    if(-not (Test-Path -LiteralPath $gameExe -PathType Leaf)){throw "SFC executable missing: $gameExe"}
    $desktopShell=Get-DesktopShell
}

function Mark([string]$Event, $Data=$null){
    $events.Add([ordered]@{event=$Event;utc=[DateTime]::UtcNow.ToString('o');elapsed_ms=$clock.ElapsedMilliseconds;data=$Data})
}

try {
    if(-not $TimingOnly){
        Invoke-Wpr -start $profile -filemode -recordtempto $folder
        $owned=$true
    }
    $clock.Start()
    $readyEvent=if($TimingOnly){'timing_ready'}else{'trace_ready'}
    Mark $readyEvent @{pass=$Pass;boot_utc=$boot}
    $readyMessage=if($TimingOnly){'TIMING READY'}else{'TRACE READY'}
    if($Launch){
        Write-Host "$readyMessage. Starting SFC through Explorer."
        Mark 'launch_requested' @{path=$gameExe;via='explorer_desktop'}
        $desktopShell.ShellExecute($gameExe,'',(Split-Path -Parent $gameExe),'open',1)
        Mark 'launch_request_returned'
    }else{
        Write-Host "$readyMessage. Launch SFC promptly using the same shortcut or Play button on both passes."
        Write-Host 'Optional: press L just before switching to the launcher to mark when you requested the launch.'
    }
    Write-Host 'Once the menu accepts input, return to this console and press R. You can also let the capture time out.'
    while($clock.Elapsed.TotalSeconds -lt 65){
        $game=Get-Process StarFleetOP -ErrorAction SilentlyContinue | Select-Object -First 1
        if($game -and -not $gamePid){
            $gamePid=$game.Id
            Mark 'game_seen' @{pid=$gamePid;path=$game.Path;process_start_utc=$game.StartTime.ToUniversalTime().ToString('o')}
            if($Launch -and $game.Path -ne $gameExe){
                $reason='unexpected_game_path'
                Write-Warning 'Observed a different SFC executable. This capture cannot qualify as a direct-launch comparison.'
                break
            }
        }
        if($game -and $game.Id -eq $gamePid){
            $window=$game.MainWindowHandle -ne [IntPtr]::Zero
            $state=if($window){'main_window_seen'}else{'no_main_window'}
            if($state -ne $lastWindow){Mark $state; $lastWindow=$state}
        }elseif($gamePid){Mark 'game_exited'; $reason='game_exited'; break}
        if(-not [Console]::IsInputRedirected -and [Console]::KeyAvailable){
            $key=[Console]::ReadKey($true).Key
            if($key -eq [ConsoleKey]::L -and -not $gamePid){Mark 'operator_about_to_launch'}
            if($key -eq [ConsoleKey]::R -and $gamePid){
                $menuMarked=$true
                Mark 'operator_confirmed_menu_input'
                $reason='menu_confirmed'
                break
            }
        }
        if($owned){
            $traceBytes=(Get-ChildItem -LiteralPath $folder -File -Recurse -Filter '*.etl' | Measure-Object Length -Sum).Sum
            if($traceBytes -ge $recordingLimit){
                $reason='recording_size_threshold'
                Mark 'recording_size_threshold' @{bytes=$traceBytes}
                break
            }
        }
        Start-Sleep -Milliseconds 250
    }
} finally {
    try {
        if($owned){
            Mark 'trace_stop_requested'
            try {
                Invoke-Wpr -status collectors -details | Set-Content -LiteralPath (Join-Path $folder 'collectors.txt') -Encoding UTF8
            } finally {
                Invoke-Wpr -stop $etl 'SFC-23 startup comparison' -skipPdbGen
                $saved=Test-Path -LiteralPath $etl -PathType Leaf
            }
        }
    } finally {
        [ordered]@{pass=$Pass;timing_only=[bool]$TimingOnly;game_pid=$gamePid;menu_confirmed=$menuMarked;reason=$reason;trace_saved=$saved;events=$events} |
            ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $folder 'timeline.json') -Encoding UTF8
        Write-Host "Evidence: $folder"
    }
}
if(-not $TimingOnly -and -not $saved){throw 'WPR did not save a trace.'}
if($saved -and ($reason -eq 'recording_size_threshold' -or (Get-Item -LiteralPath $etl).Length -gt 1GB)){Write-Warning 'Trace reached its recording threshold or exceeded 1 GiB after finalization. The saved trace is available for review.'}
if(-not $gamePid){Write-Warning 'No SFC process was observed. This capture does not qualify as a comparison run.'}
