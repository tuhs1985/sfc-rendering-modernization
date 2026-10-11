# Execute from Windows PowerShell 5.1. Exercise the production runtime shim
# against this harmless fixture, not the real gameplay/injection workflow.
param([string]$EntryName = 'start_m1_visual_tint_session.ps1')
$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSVersion.Major -ge 7) {
    Write-Output 'M1_RUNTIME_SHIM_OK'
    return
}
$entry = Join-Path (Join-Path $PSScriptRoot '..\tools\m1_component') $EntryName
$tokens = $null
$errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    $entry, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw 'Visual entry script parse failed.' }
$shim = $ast.EndBlock.Statements | Where-Object {
    $_ -is [System.Management.Automation.Language.IfStatementAst]
} | Select-Object -First 1
if (-not $shim) { throw 'Production runtime shim not found.' }
# Use this fixture path; child prints a marker and exits.
$visualEntryPath = $PSCommandPath
$output = & ([scriptblock]::Create($shim.Extent.Text))
if ($output -notcontains 'M1_RUNTIME_SHIM_OK') {
    throw 'Runtime shim did not successfully execute the fixture in PowerShell 7.'
}
Write-Output 'PASS: Windows PowerShell entry re-executes in PowerShell 7 without launching SFC.'
