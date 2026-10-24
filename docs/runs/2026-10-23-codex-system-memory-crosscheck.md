# Run132 — distinguish system commit from renderer memory

Date2026-10-23 America/New_York, final checks21:48local. Request: verify apparently greater-than-installed memory, compare earlier successful runs, ensure our setup is right. Diagnosis only, no implementation authority inferred. Active bounded D3D9 retained multi-ship startup investigation; no milestone acceptance. Read Run131/Run130 handoff and latest allocation-failure record. FuelGuard attached via verified hook; no daemon/helper/agent. Starting/finalHEAD `d40f8f230fc7504023e4a052c99a81b5a08ce6b4`,indexempty,priorunstaged/untrackedworkpreserved.

## Findings and correction

CONFIRMED: runtime SystemInformationReport's physical/committed values are machine-wide, not SFC or Remix private consumption. Failed010857-214073 startup reports physical24.22/31.84GiB,commit43.91/47.84GiB. Microsoft's [page-file explanation](https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/introduction-to-the-page-file) defines systemcommit as promised memory backed by RAM/pagefiles; it can exceed installedRAM. Commit is not actual pagefile usage or GPUVRAM. The reported4.78GiB process virtual address-space figure is another distinct metric, not equivalent to private committed or resident RAM. Never add these metrics together as usage.

| Actual game run | Physical usedGiB at host startup | System commitGiB at host startup | Native outcome |
|---|---:|---:|---|
| 20261023-191630-707670 |26.00|41.18|exit0,noallocatorfailure|
| 20261023-194205-307246 |26.08|42.26|exit0,noallocatorfailure|
| 20261023-205121-223108 |23.90|40.86|exit0,noallocatorfailure|
| 20261024-000410-735623 |26.69|43.46|exit0,noallocatorfailure|
| 20261024-010857-214073 |24.22|43.91|exit1,allocatorfailure|

Successful final-source standalonePerformance004135-988733startup23.33GiBphysical/40.98GiBcommit;Test004236-43469523.47/41.46. OlderPerformance215456-18400223.98/40.29. Same47.84GiBcommitlimit/31.84GiBphysical in all compared logs. These are STARTUP snapshots, not peaks or failure-time measurements. Failed vs nearest successful actualgame:commit+0.45GiB,physical-2.47GiB. Therefore highcommit alone does not explain failure. Run131's STRONG HYPOTHESIS contributor label is superseded: contribution remains possible/unproven, not a demonstrated environmental cause. Confirmed Remix allocator rejection remains; neither startup regression nor environmental exhaustion isolated.

Read-only live host checks (post-failure, different times):

- Windows32GiBphysical(total34,190,008,320bytes);C:\\pagefile.sysallocated16384MiB,currentusage339MiB,peak362MiB;automaticpagefilemanagementfalse. Observedcommitlimit51,369,877,504bytes(47.84GiB). Do not infer cause or recommend resizing from this alone; no settings changed.
- Performance countercommit43,078,246,400bytes(~40.12GiB),availablephysical9212MiB,pagedpool1,748,226,048bytes,nonpagedpool1,289,297,920bytes. Approximateheadroom7.72GiB at that snapshot. Post-runnvidia-smi5778MiB/12282MiBdeviceuse;notcrashtelemetry.
- ProcessPrivateBytesgrouped:WebView29.261GiB across20processes;ChatGPT3.975GiB/16processes;vmmemWSL2.806GiB;lghub_agent1.978GiB. These counters are not resident RAM, do not sum exactly to systemcommit, and do not establish the cause of Remix failure. WebView parent-name inspection identifies two largest under `C:\Program Files\FLC\flc.exe` (FLC8.0.0,phenomen):private4.801+3.833GiB at later sample,~8.63GiBcombined. EarlierRun131roundedprivate3.93+2.53GiB for same twoPIDs was~6.46GiB. This suggests growth, not proven leak; application workload/lifecycle not captured. Do not attribute allWebViews toFLC/ChatGPT or read application content.
- No liveStarFleetOP,d3d9_direct_host,output_receiver,return_host,bounded_job,d3d11_return_fixture,m1_controller/Python found in complete outside-sandboxhostinventory. No abandoned harness process currently retaining assets. This does NOT prove no transient leak/driver allocation issue during actualrun.

## Tools / reproduction / limits

Read existing `gpu/job-console.log` firstMemoryline and `result.json`/`gpu/job-result.json` for eight explicitly selected historicalfolders in `artifacts/remix-runtime/runs`; no recursive rawcapturesparse/imageconversion. BundledPython pathlib/re/json,PowerShell read-onlyGet-Process,Get-CimInstance(Win32_PerfFormattedData_PerfOS_Memory,Win32_PageFileUsage,Win32_ComputerSystem,Win32_Process selecting ONLYnames/PIDs/parentPIDs),Get-FileHash andnvidia-smi. Approved outside-sandboxreads necessary because sandboxprocessinventory incomplete. No command-line/environmentsecrets,chatcontent,screenshots,apptermination,systempolicy/pagefilechange or newGPU/gameexecution. Microsoft'sprimarysource used only formemorymetricdefinitions. Existingcapturebounds unchanged; added onlysmallcuratedrecords.

ClientsSHA256accepted/copyboth `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`;copiedproxy `E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7`,unchanged. Historical runtime/job folders identified in newevidenceJSON; original Run130/131 curated hashes preserved. No newbuild/tests needed for docs-onlydiagnosis. JSON/historical-value/path checks andgitdiffcheckPASS,indexempty;nostage/commit/push. No active newtool/server/ownedprocess.

## Files and exact next action

Addedthisrecord and `docs/reconnaissance/evidence/20261023-system-memory-crosscheck.json`;updated `docs/HANDOFF.md`, `docs/reconnaissance/pipeline-modes.md` qualificationcaveat. Olderrecords remain historical; no raw evidence overwritten or deleted.

Nextengineeringaction(withimplementationauthority):boundedmemorytiming probe aroundverifiedlaunch/menuidle/activation/firstoutput;systemcommit plusownedprocessprivate/working-set counters,thencomparelong-idle vs near-tacticalstartup using samecapturedscene andsettings. No randomqualityreduction,assetcapremoval or claimmoreRAMfixesit. Sponsor maynormallyclose/restart unusedFLC to freeheadroom, but that is not a proven rendering fix. No consequential OS/app changes authorized by this review.
