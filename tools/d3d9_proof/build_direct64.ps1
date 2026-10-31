param([ValidateSet('Off','Speed')][string]$Optimization='Speed')
$ErrorActionPreference='Stop'
$opt=if($Optimization -eq 'Speed'){'/O2'}else{'/Od'}
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$manifest=Get-Content (Join-Path $root 'artifacts/remix-runtime/deps/manifest.json') -Raw | ConvertFrom-Json
if($manifest.source_commit -ne 'b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4' -or (Get-FileHash (Join-Path $root 'artifacts/remix-runtime/deps/remix_c.h')).Hash -ne $manifest.header_sha256){throw 'Pinned header mismatch'}
$bin=Join-Path $root 'artifacts/d3d9-proof/direct64-bin'
New-Item -ItemType Directory -Force -Path $bin | Out-Null
Push-Location $bin
try{
 $vc='C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat'
 $cmd='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /W4 /WX {2} /fp:precise /I"{1}\artifacts\remix-runtime\deps" "{1}\tools\d3d9_proof\d3d9_direct_host.cpp" /Fe:d3d9_direct_host.exe /link /Brepro user32.lib d3d11.lib dxgi.lib d3dcompiler.lib advapi32.lib ole32.lib' -f $vc,$root,$opt
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Direct64 ordinary D3D9 host build failed'}
 $cmd='"{0}" && cl /nologo /std:c++20 /EHsc /W4 /WX "{1}\tests\remix_loaded_light_tests.cpp" /Fe:loaded_light_tests.exe /link /Brepro' -f $vc,$root
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Loaded light tests build failed'}
 & .\loaded_light_tests.exe
 if($LASTEXITCODE -ne 0){throw 'Loaded light tests failed'}
 $cmd='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /W4 /WX {2} /fp:precise "{1}\tests\d3d9_deferred_diagnostics_tests.cpp" /Fe:deferred_diagnostics_tests.exe /link /Brepro' -f $vc,$root,$opt
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Deferred diagnostics build failed'}
 & .\deferred_diagnostics_tests.exe
 if($LASTEXITCODE -ne 0){throw 'Deferred diagnostics tests failed'}
 $cmd='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /W4 /WX {2} /fp:precise "{1}\tests\d3d9_worker_poll_tests.cpp" /Fe:worker_poll_tests.exe /link /Brepro' -f $vc,$root,$opt
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Worker poll tests build failed'}
 & .\worker_poll_tests.exe
 if($LASTEXITCODE -ne 0){throw 'Worker poll tests failed'}
 $cmd='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /W4 /WX {2} /fp:precise "{1}\tests\d3d9_asset_service_tests.cpp" /Fe:asset_service_tests.exe /link /Brepro user32.lib' -f $vc,$root,$opt
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Asset service native test build failed'}
 $serviceResult=& .\asset_service_tests.exe
 if($LASTEXITCODE -ne 0){throw 'Asset service native test failed'}
 $serviceResult | Set-Content -Encoding UTF8 asset-service-tests.txt
 $serviceResult | Write-Output
 $cmd='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /W4 /WX {2} /fp:precise "{1}\tests\d3d9_combined_post_tests.cpp" /Fe:combined_post_tests.exe /link /Brepro d3d11.lib dxgi.lib d3dcompiler.lib' -f $vc,$root,$opt
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Combined post test build failed'}
 $combinedResult=& .\combined_post_tests.exe
 if($LASTEXITCODE -ne 0){throw 'Combined post GPU test failed'}
 $combinedResult | Set-Content -Encoding UTF8 combined-post-tests.txt
 $combinedResult | Write-Output
 $cmd='"{0}" && set "CL=" && set "_CL_=" && cl /nologo /std:c++20 /EHsc /W4 /WX {2} /fp:precise "{1}\tests\physical_hull_depth_tests.cpp" /Fe:physical_hull_depth_tests.exe /link /Brepro user32.lib d3d11.lib dxgi.lib d3dcompiler.lib' -f $vc,$root,$opt
 & $env:ComSpec /d /s /c $cmd
 if($LASTEXITCODE -ne 0){throw 'Physical hull depth GPU test build failed'}
 $hullResult=& .\physical_hull_depth_tests.exe
 if($LASTEXITCODE -ne 0){throw 'Physical hull depth GPU test failed'}
 $hullResult | Set-Content -Encoding UTF8 physical-hull-depth-tests.txt
 $hullResult | Write-Output
 @{optimization=$opt;floating_point='/fp:precise';inherited_cl_options='cleared in compiler child';architecture='x64'} | ConvertTo-Json | Set-Content build-policy.json
}finally{Pop-Location}
