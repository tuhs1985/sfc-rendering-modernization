param(
    [ValidateRange(5, 2100)][int]$MaxSeconds = 300,
    [ValidateRange(30, 900)][int]$WaitForClientSeconds = 600,
    [ValidateRange(30, 900)][int]$WaitForExitSeconds = 600,
    [ValidateRange(30, 900)][int]$ArmTimeoutSeconds = 600,
    [ValidateRange(1, 6000)][int]$MaxFrames = 120,
    [ValidateRange(1, 100000)][int]$MaxEvents = 10000,
    [ValidateRange(0, 8)][int]$GeometrySamplesPerOwnerFrame = 1,
    [ValidateRange(0, 8)][int]$UncorrelatedGeometrySamplesPerFrame = 1,
    [switch]$DisableGeometryHook,
    [switch]$EnableVisualTint,
    [switch]$EnableShadingOff,
    [switch]$ContinueAfterBurst,
    [switch]$AutomaticArm,
    [string]$PythonExecutable = 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
)

$ErrorActionPreference = 'Stop'
$toolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Resolve-Path (Join-Path $toolRoot '..\..')
$runner = Join-Path $toolRoot 'run_m1_increment_a.ps1'
$launcher = Join-Path $workspaceRoot 'Game Assets\SFCLauncher 2.1.0.22.exe'
$armSignal = Join-Path $workspaceRoot 'artifacts\m1\enabled-tactical-arm.signal'
$expectedLauncherMd5 = '5974EA36E3C4E3DFE4F8E243607FC3CF'
$expectedLauncherSha256 = '84D3A5F89A922C4BEE6815CF0614538C3565C4BDB7DB3AA187C552CB727EF890'
$pwsh = (Get-Process -Id $PID).Path
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (($EnableVisualTint -or $EnableShadingOff) -and (-not $isAdmin -or -not $DisableGeometryHook)) {
    throw 'Visual tint must inherit an elevated parent and keep the geometry hook disabled.'
}
if ($EnableShadingOff -and ($EnableVisualTint -or -not $ContinueAfterBurst -or $MaxSeconds -lt 75 -or $MaxSeconds -gt 90)) {
    throw 'Shading diagnostic requires no tint mode, ContinueAfterBurst and 75-90 seconds.'
}
if (-not (Test-Path -LiteralPath $PythonExecutable)) {
    throw "Configured Python runtime was not found: $PythonExecutable"
}

if (-not $isAdmin) {
    $arguments = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
        ('"{0}"' -f $MyInvocation.MyCommand.Path),
        '-MaxSeconds', $MaxSeconds,
        '-WaitForClientSeconds', $WaitForClientSeconds,
        '-WaitForExitSeconds', $WaitForExitSeconds,
        '-ArmTimeoutSeconds', $ArmTimeoutSeconds,
        '-MaxFrames', $MaxFrames,
        '-MaxEvents', $MaxEvents,
        '-GeometrySamplesPerOwnerFrame', $GeometrySamplesPerOwnerFrame,
        '-UncorrelatedGeometrySamplesPerFrame', $UncorrelatedGeometrySamplesPerFrame
    ) -join ' '
    if ($DisableGeometryHook) { $arguments += ' -DisableGeometryHook' }
    if ($EnableVisualTint) { $arguments += ' -EnableVisualTint' }
    if ($AutomaticArm) { $arguments += ' -AutomaticArm' }
    if ($ContinueAfterBurst) { $arguments += ' -ContinueAfterBurst' }
    $arguments += (' -PythonExecutable "{0}"' -f $PythonExecutable)
    [void](Start-Process -FilePath $pwsh -ArgumentList $arguments -Verb RunAs `
        -WindowStyle Hidden)
    Write-Output "Elevated enabled workflow requested; tactical arm signal: $armSignal"
    return
}

if (Get-Process -Name StarFleetOP -ErrorAction SilentlyContinue) {
    throw 'Exit every StarFleetOP process before preparing the enabled session.'
}
$launcherMd5 = (Get-FileHash -LiteralPath $launcher -Algorithm MD5).Hash
$launcherSha = (Get-FileHash -LiteralPath $launcher -Algorithm SHA256).Hash
if ($launcherMd5 -ne $expectedLauncherMd5 -or
    $launcherSha -ne $expectedLauncherSha256) {
    throw 'The restored SFC Launcher does not match the frozen baseline.'
}
Remove-Item -LiteralPath $armSignal -Force -ErrorAction SilentlyContinue

$logDir = Join-Path $workspaceRoot 'artifacts\m1'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ('enabled-bootstrap-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
Start-Transcript -LiteralPath $log -Force | Out-Null
try {
    [void](Start-Process -FilePath $launcher -WorkingDirectory (Split-Path -Parent $launcher))
    $discoveryDeadline = (Get-Date).AddSeconds($WaitForClientSeconds)
    $game = $null
    do {
        $candidates = @(Get-Process -Name StarFleetOP -ErrorAction SilentlyContinue)
        if ($candidates.Count -gt 1) { throw 'More than one StarFleetOP process is running.' }
        if ($candidates.Count -eq 1) { $game = $candidates[0]; break }
        Start-Sleep -Milliseconds 250
    } while ((Get-Date) -lt $discoveryDeadline)
    if (-not $game) { throw 'Timed out waiting for SFC Launcher.' }

    if (-not $AutomaticArm) {
    Write-Output "Client PID $($game.Id) found; waiting for tactical arm signal: $armSignal"
    $armDeadline = (Get-Date).AddSeconds($ArmTimeoutSeconds)
    do {
        if (-not (Get-Process -Id $game.Id -ErrorAction SilentlyContinue)) {
            throw 'SFC exited before the tactical arm signal.'
        }
        if (Test-Path -LiteralPath $armSignal) { break }
        Start-Sleep -Milliseconds 100
    } while ((Get-Date) -lt $armDeadline)
    if (-not (Test-Path -LiteralPath $armSignal)) {
        throw 'Timed out waiting for the tactical arm signal.'
    }
    }

    & $runner -Mode enabled -MaxSeconds $MaxSeconds -TargetPid $game.Id `
        -WaitForClientSeconds $WaitForClientSeconds `
        -WaitForExitSeconds $WaitForExitSeconds -MaxFrames $MaxFrames `
        -MaxEvents $MaxEvents `
        -GeometrySamplesPerOwnerFrame $GeometrySamplesPerOwnerFrame `
        -UncorrelatedGeometrySamplesPerFrame $UncorrelatedGeometrySamplesPerFrame `
        -DisableGeometryHook:$DisableGeometryHook -EnableVisualTint:$EnableVisualTint `
        -EnableShadingOff:$EnableShadingOff -ContinueAfterBurst:$ContinueAfterBurst `
        -PythonExecutable $PythonExecutable
} finally {
    Remove-Item -LiteralPath $armSignal -Force -ErrorAction SilentlyContinue
    Stop-Transcript | Out-Null
}
