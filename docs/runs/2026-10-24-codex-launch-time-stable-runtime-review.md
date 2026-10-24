# Run133 — stable actual-game retry; loading target remains open

Date2026-10-24 America/New_York. Active bounded ordinary-D3D9 retained multi-ship startup/performance increment. Sponsor reports: worked,loadedandstable,didnotmeasureprecisely,butstilllongerthan2seconds. Review actual `artifacts/remix-runtime/runs/20261024-042240-261146-in-game`; no new gameplay or implementation. Read latestRun132handoff/Run131allocationrecord/Run130startupauthority. FuelGuardverifiedtrustedhook,no taskdaemon/helper/agent. HEAD `d40f8f230fc7504023e4a052c99a81b5a08ce6b4`,indexempty,priorunstaged/untrackedworkpreserved. No commit/push authorization.

## Direct runtime evidence — CONFIRMED

- Resulterrornull;normalgameexittrue;gatecontroller0;hook_bytes_restoredtrue/component_unloadedtrue;originalcritical/launchersettingsunchangedtrue;copiedproxyrestoredtrue. Nativeownedjobexit0,stop_reason0,154984ms,peak_scratch208147273bytes,remainingowned0;runtimeShutdown0. Distinguish native job from separate return supervisor exit. No allocator failure observed.
- Four initial assets(KDD,FDD,FFF,FCA),thenKFF,KFFsharedalias,FMS;7owner/revisioninstances,6contents,allACK1. Initialownersdrawn5276each;laterowners4280/3911/3388. No partials,assetrejections,nativecohortinvalid,header/packet/identitylookup/decode/projectionfailures. This is observed supported coverage,not arbitrarymodel/damagequalification.
-5262matchinggamecompositions,5568auditrecords,304withoutship,1warmup/1reset,0bufferfailed;maximumauditoutputage21.530ms. Outputpublished5276/stale10/invalid0/resourcefailed0. Sponsorstableappearance is corroborated by successful sustained delivery,not interpreted as zero technical omissions. Originals remain visible,commoncamera-leftcopies,existingvisualsettings. Two lateunique material-librarypublications(5layers,then6)remain;fighter/latearrivalblipnotimplemented/fixedhere.
- Performance modeactive,frame_samples0,detailedfalse. Imageoutput226595992bytes/172originalimageswithinaggregatepolicy;artifactinventory17,210,529,459bytes<20,000,000,000. Tacticalstopduration,workflow195.328s<285s. No capturelimitincrease.

## Full startup clocks — CONFIRMED, not physical display latency

QPCfrequency10,000,000;Pythonperf_counter_ns sharesWindowsQPCclock. Firstassetdiscovery568289669473100ns;hoststart568230839453200ns;readyreceipt5682331111069ticks;activation568291849330300ns;firstsuccessfulcompositorstatus1QPC5682954525244ticks.

| Stage relative to first fresh collector discovery | Seconds |
|---|---:|
| Real runtime/devices ready | -56.5583662 |
| Complete initial catalog published / scene activated | 2.1798572 |
| All four initial native assets admitted | 3.1302399 |
| First matching in-game composition | 5.7830513 |

Postactivation->firstmatchingcomposition3.6031941s. Initialnative4assetsCPU+GPUadmissiontotal0.087958s (sum2374+5+25542+2334+19539+1629+31985+4550microseconds). Therefore native meshupload alone doesnotexplainseconds. The remaining gap includes materialactivation/runtimeinitialization/bootstrap/firstoutput; substagesnotisolated. Existing24bootstrapPresents/10mssleepsremain,notprovensolecause. `selected.preparation_seconds=62.547` includeswaitingmenus,NOTmodelconversiontime. Firstnativeadmissionafteractivation~0.861s;lastadmission->firstmatchingcomposition~2.653s. Do not conflate render/composition readiness with physicalscreenlatency.

HistoricalRun129actualfirstcomposition6.6002069s vsnow5.7830513s(~0.817sless). Different initialKFFvsKDDmodelsets/environment,so NOTcontrolledA/Boptimizationproof. Sub2s remainsOPEN even though earlydeviceinitisnowruntimecorroborated. No need anotherdiscoveryrun to reconfirmmodelseam.

## Allocation-failure disposition

This startupreported21.79/31.84GiBphysical,36.48/47.84GiBsystemcommit versusfailedRun13124.22/43.91. Lowercommitconsistentwithpossiblememorypressurecontribution,butcauseNOTproven:models/environmentchanged;onlystartup snapshot,nofailure-timepeakorownedprocessmemoryseries. PriorRun132successful43.46GiBcommitcounterexample remainsvalid. No evidence enough todeclareallRAMexhaustion/VRAMexhaustion,leakfixedorstartupregressionexcluded. Do not silentlylowerqualityorattributeallcommittotheharness.

## Tools, reproducibility and files

Read-onlyPowerShellGet-Content/rg andbundledPython `C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` withpathlib/json/hashlib/struct,`synchronized_buffer.HEADER/RECORD` and`run_offline.storage`. Parseexistingresult andnativejob/gatelogs;findfirststatus1binaryrecordthenconvertQPCusingrecordedfrequency. Sourceassets/clientuntouched. No newGPUtest,processmutation,pagefile/securitychange,appearancechangeorrawcapture. Fastvalidation:curatedJSON/hash/path/numericassertions,gitdiffcheck,indexempty. No fullbuild/regressionnecessaryforreview-onlydocs.

Addedthisrecord and `docs/reconnaissance/evidence/20261024-launch-time-stable-runtime.json`;updated `docs/HANDOFF.md` and `docs/reconnaissance/pipeline-modes.md` actual-gamecaveat. Rawrunresult(sponsorbehaviorPENDINGfield)preservedunchanged;newcuratedrecordcarryssponsorreportseparately. FinalHEADunchanged/allworkunstaged/uncommitted,nopush. No newactive tool/server/ownedprocess; nativejobconfirms0left.

Exactnextengineeringactionwithauthority:boundedofflineprofileofpostactivation3.603sthroughmaterialactivation/bootstrap/firstoutputusingcapturedassets,keepingappearanceandidentity/fences. Deviceinitnowstartsatreallaunchasrequested; assetdependentfirstframeworkstilldominates. Earlierassetdiscoveryandlatefighterreloadremainexplicitlydeferred. Addboundedmemorytimingifneeded toisolateallocationrecurrence,noassumedOSfix.
