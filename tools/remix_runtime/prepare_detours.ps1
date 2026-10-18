# Pinned Microsoft startup-loader library. No system installation or game edits.
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$deps=Join-Path $root 'artifacts/remix-runtime/deps/detours'
New-Item -ItemType Directory -Force -Path $deps | Out-Null
$commit='e4bfd6b03e50de46b47abfbd1e46b384f0c5f833'
$zip=Join-Path $deps 'detours-4.0.1.zip'
if(-not(Test-Path -LiteralPath $zip)){
    $http=[Net.Http.HttpClient]::new();$http.Timeout=[TimeSpan]::FromSeconds(60)
    try{
        $reply=$http.GetAsync("https://codeload.github.com/microsoft/Detours/zip/$commit",[Net.Http.HttpCompletionOption]::ResponseHeadersRead).GetAwaiter().GetResult();[void]$reply.EnsureSuccessStatusCode()
        if($reply.Content.Headers.ContentLength -gt 8MB){throw 'Detours download cap'}
        $inputStream=$reply.Content.ReadAsStream();$outputStream=[IO.File]::Open($zip,[IO.FileMode]::CreateNew)
        try{$buffer=[byte[]]::new(65536);$sum=0;while(($n=$inputStream.Read($buffer,0,$buffer.Length)) -gt 0){$sum+=$n;if($sum -gt 8MB){throw 'Detours download cap'};$outputStream.Write($buffer,0,$n)}}finally{$inputStream.Dispose();$outputStream.Dispose();$reply.Dispose()}
    }finally{$http.Dispose()}
}
$source=Join-Path $deps "Detours-$commit"
if((Get-FileHash $zip).Hash -ne 'FEF0B17C5C3C9356FB8BA7366A3B196149DAADD131FB6A92ABEDA1CB4D3B9B85'){throw 'Pinned Detours archive hash mismatch'}
if(-not(Test-Path -LiteralPath $source)){
    $archive=[IO.Compression.ZipFile]::OpenRead($zip)
    try{
        if($archive.Entries.Count -gt 2048 -or ($archive.Entries | Measure-Object Length -Sum).Sum -gt 16MB){throw 'Detours extraction cap'}
        $base=[IO.Path]::GetFullPath($deps)+[IO.Path]::DirectorySeparatorChar
        foreach($entry in $archive.Entries){if(-not[IO.Path]::GetFullPath((Join-Path $deps $entry.FullName)).StartsWith($base,[StringComparison]::OrdinalIgnoreCase)){throw 'Detours archive traversal'}}
    }finally{$archive.Dispose()}
    Expand-Archive -LiteralPath $zip -DestinationPath $deps
}
$vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat'
Push-Location (Join-Path $source 'src')
try{
    $command='"{0}" && nmake /nologo DETOURS_TARGET_PROCESSOR=X86' -f $vc
    & $env:ComSpec /d /s /c $command
    if($LASTEXITCODE -ne 0){throw 'Pinned Detours x86 build failed'}
}finally{Pop-Location}
[ordered]@{release='v4.0.1';commit=$commit;archive_sha256=(Get-FileHash $zip).Hash;library_sha256=(Get-FileHash (Join-Path $source 'lib.X86/detours.lib')).Hash;source=$source} | ConvertTo-Json | Set-Content (Join-Path $deps 'manifest.json') -Encoding utf8
Get-Content (Join-Path $deps 'manifest.json')
