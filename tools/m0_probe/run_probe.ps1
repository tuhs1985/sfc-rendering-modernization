param(
    [ValidateRange(30, 900)]
    [int]$MaxSeconds = 300,

    [ValidateRange(30, 900)]
    [int]$WaitForClientSeconds = 600,

    [int]$TargetPid = 0,

    [switch]$ElevateProbe,

    [ValidateSet("m0-rt-001", "m0-rt-002", "m0-rt-003")]
    [string]$ProbeProfile = "m0-rt-001"
)

$ErrorActionPreference = "Stop"

$toolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module (Join-Path $toolRoot "ProbeRunnerPolicy.psm1") -Force

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
$isElevated = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$selfElevateProbe = Test-ProbeElevation `
    -IsElevated $isElevated `
    -ElevateProbeRequested ([bool]$ElevateProbe)

if ($isElevated -and $ElevateProbe) {
    Write-Warning "The parent shell is already elevated; inheriting its privilege without a second runas request."
}

$workspaceRoot = Resolve-Path (Join-Path $toolRoot "..\..")
$probe = Join-Path $workspaceRoot "artifacts\pre-m0\bin\m0_probe.exe"

if (-not (Test-Path -LiteralPath $probe)) {
    & (Join-Path $toolRoot "build_probe.ps1")
}

$expectedMd5 = "2BE8F713F81B1C68D50EAD6088C32886"
if ($TargetPid -gt 0) {
    $game = Get-Process -Id $TargetPid -ErrorAction Stop
} else {
    $deadline = (Get-Date).AddSeconds($WaitForClientSeconds)
    Write-Output "Waiting for SFC Launcher to create StarFleetOP.exe..."
    do {
        $candidates = @(Get-Process -Name "StarFleetOP" -ErrorAction SilentlyContinue)
        if ($candidates.Count -gt 1) {
            throw "More than one StarFleetOP process is running; pass -TargetPid explicitly."
        }
        if ($candidates.Count -eq 1) {
            $game = $candidates[0]
            break
        }
        Start-Sleep -Milliseconds 250
    } while ((Get-Date) -lt $deadline)

    if (-not $game) {
        throw "Timed out waiting for SFC Launcher to create StarFleetOP.exe."
    }
}

$client = $null
try {
    $client = $game.MainModule.FileName
} catch {
    Write-Output "Runner could not resolve the live image path; exact-build validation is deferred to the native probe."
}
if ($client -and (Test-Path -LiteralPath $client)) {
    $observedMd5 = (Get-FileHash -LiteralPath $client -Algorithm MD5).Hash
    if ($observedMd5 -ne $expectedMd5) {
        throw "The launcher-created client MD5 does not match the supported M0 build: $client"
    }
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$runDir = Join-Path $workspaceRoot "artifacts\pre-m0\runs\$stamp"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$probeId = $ProbeProfile.ToUpper()
$logPath = Join-Path $runDir "$probeId.csv"
$modulePath = Join-Path $runDir "loaded-modules.csv"

try {
    Get-Process -Id $game.Id -Module -ErrorAction Stop |
        Select-Object ModuleName, FileName, FileVersionInfo |
        Export-Csv -LiteralPath $modulePath -NoTypeInformation
} catch {
    Set-Content -LiteralPath $modulePath -Value "Module inventory unavailable: $($_.Exception.Message)"
}

$startInfo = [System.Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $probe
$startInfo.WorkingDirectory = $workspaceRoot
$startInfo.UseShellExecute = $selfElevateProbe
if ($selfElevateProbe) {
    $startInfo.Verb = "runas"
    $startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
} else {
    $startInfo.CreateNoWindow = $true
}
foreach ($argument in @("--pid", $game.Id, "--log", $logPath, "--max-seconds", $MaxSeconds, "--profile", $ProbeProfile)) {
    [void]$startInfo.ArgumentList.Add([string]$argument)
}
$probeProcess = [System.Diagnostics.Process]::Start($startInfo)

Write-Output "$probeId is attached to StarFleetOP process $($game.Id)."
Write-Output "Enter a tactical scene, exercise one camera or ship control, then exit the game."
Write-Output "Evidence log: $logPath"
Write-Output "Module inventory: $modulePath"

if ($selfElevateProbe) {
    while (Get-Process -Id $probeProcess.Id -ErrorAction SilentlyContinue) {
        Start-Sleep -Milliseconds 500
    }
} else {
    Wait-Process -Id $probeProcess.Id
}
if (Test-Path -LiteralPath $logPath) {
    & python (Join-Path $toolRoot "analyze_probe_log.py") $logPath
}
