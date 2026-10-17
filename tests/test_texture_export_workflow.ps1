# Policy/AST only: never launches SFC, elevates, injects or installs anything.
$ErrorActionPreference='Stop'
$root=Join-Path $PSScriptRoot '../tools/m1_component'
foreach($name in @('run_m1_increment_a.ps1','start_m1_enabled_session.ps1','start_mesh_export_session.ps1','start_texture_export_session.ps1')){
    $tokens=$null;$errors=$null
    $ast=[Management.Automation.Language.Parser]::ParseFile((Join-Path $root $name),[ref]$tokens,[ref]$errors)
    if($errors.Count){throw "$name parse failed: $errors"}
    if($name -in @('run_m1_increment_a.ps1','start_m1_enabled_session.ps1')){
        $block=$ast.FindAll({param($n) $n -is [Management.Automation.Language.IfStatementAst] -and
            $n.Extent.Text.StartsWith('if($EnableTextureReferences -and -not $EnableMeshExport)')},$true) | Select-Object -First 1
        if(-not $block){throw "$name missing same-run policy"}
        $EnableTextureReferences=$true;$EnableMeshExport=$false;$rejected=$false
        try{. ([scriptblock]::Create($block.Extent.Text))}catch{$rejected=$true}
        if(-not $rejected){throw 'References without mesh accepted'}
        $EnableMeshExport=$true;. ([scriptblock]::Create($block.Extent.Text))
    }
}
foreach($name in @('run_m1_increment_a.ps1','start_m1_enabled_session.ps1','start_mesh_export_session.ps1')){
    $text=Get-Content -LiteralPath (Join-Path $root $name) -Raw
    if(-not $text.Contains('EnableTextureReferences')){throw 'Opt-in forwarding missing'}
}
$runner=Get-Content -LiteralPath (Join-Path $root 'run_m1_increment_a.ps1') -Raw
if($runner.IndexOf("'export_mesh_textures.py'") -lt $runner.IndexOf('Normal exit observed:')){throw 'Images must be recovered after normal exit'}
Write-Output 'Texture export policy/parser/forwarding checks passed; no game launched.'
