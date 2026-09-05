param(
    [ValidateRange(5, 2100)][int]$CaptureSeconds = 120,
    [ValidateRange(30, 900)][int]$WaitForClientSeconds = 600,
    [ValidateRange(30, 900)][int]$GateTimeoutSeconds = 600,
    [ValidateRange(30, 900)][int]$WaitForExitSeconds = 600,
    [ValidateSet('Auto', 'Manual')][string]$GateMode = 'Auto'
)

$ErrorActionPreference = 'Stop'
$toolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Resolve-Path (Join-Path $toolRoot '..\..')
$runner = Join-Path $toolRoot 'run_m1_disabled_baseline.ps1'
$pwsh = (Get-Process -Id $PID).Path
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    $arguments = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
        ('"{0}"' -f $MyInvocation.MyCommand.Path),
        '-CaptureSeconds', $CaptureSeconds,
        '-WaitForClientSeconds', $WaitForClientSeconds,
        '-GateTimeoutSeconds', $GateTimeoutSeconds,
        '-WaitForExitSeconds', $WaitForExitSeconds,
        '-GateMode', $GateMode
    ) -join ' '
    [void](Start-Process -FilePath $pwsh -ArgumentList $arguments -Verb RunAs `
        -WindowStyle Hidden)
    Write-Output 'Elevated baseline workflow requested; it will launch the verified SFC Launcher.'
    return
}

$logDir = Join-Path $workspaceRoot 'artifacts\m1'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ('baseline-bootstrap-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
Start-Transcript -LiteralPath $log -Force | Out-Null
try {
    & $runner -CaptureSeconds $CaptureSeconds `
        -WaitForClientSeconds $WaitForClientSeconds `
        -GateTimeoutSeconds $GateTimeoutSeconds `
        -WaitForExitSeconds $WaitForExitSeconds -GateMode $GateMode -LaunchSfc
} finally {
    Stop-Transcript | Out-Null
}
