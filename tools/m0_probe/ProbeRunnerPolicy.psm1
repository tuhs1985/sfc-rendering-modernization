function Test-ProbeElevation {
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory)]
        [bool]$IsElevated,

        [Parameter(Mandatory)]
        [bool]$ElevateProbeRequested
    )

    if ($IsElevated) {
        return $false
    }

    if ($ElevateProbeRequested) {
        return $true
    }

    throw @"
The M0 probe requires an elevated parent shell to attach to the launcher-created client.
Prepare one narrowly scoped elevated PowerShell session before sponsor gameplay, then run
this command again without -ElevateProbe. -ElevateProbe is retained only as an explicit
fallback and may display a UAC confirmation dialog.
"@
}

Export-ModuleMember -Function Test-ProbeElevation
