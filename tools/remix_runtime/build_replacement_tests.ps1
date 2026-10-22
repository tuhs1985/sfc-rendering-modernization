$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$bin=Join-Path $root 'artifacts/remix-runtime/replacement-bin'
New-Item -ItemType Directory -Force -Path $bin | Out-Null
$vcroot='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build'
Push-Location $bin
try{
    foreach($arch in @('32','64')){
        $vc=Join-Path $vcroot "vcvars$arch.bat"
        $name="replacement$arch.exe"
        $build='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\tests\ship_replacement_tests.cpp" /Fe:{2} /link /Brepro d3d11.lib d3dcompiler.lib advapi32.lib ole32.lib' -f $vc,$root,$name
        & $env:ComSpec /d /s /c $build
        if($LASTEXITCODE -ne 0){throw "Replacement $arch build failed"}
        $stdout=Join-Path $bin "replacement$arch.stdout.txt"
        $stderr=Join-Path $bin "replacement$arch.stderr.txt"
        $fixture=Start-Process -FilePath (Join-Path $bin $name) -WindowStyle Hidden -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
        if(-not $fixture.WaitForExit(20000)){
            $fixture.Kill()
            [void]$fixture.WaitForExit(5000)
            throw "Owned replacement $arch fixture exceeded 20 seconds"
        }
        $fixture.WaitForExit()
        foreach($log in @($stdout,$stderr)){
            if((Get-Item -LiteralPath $log).Length -gt 2MB){throw 'Offline fixture output cap exceeded'}
            Get-Content -LiteralPath $log
        }
        if($fixture.ExitCode -ne 0){throw "Replacement $arch tests failed"}
    }
}finally{Pop-Location}
