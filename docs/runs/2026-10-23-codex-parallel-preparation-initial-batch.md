# Run125 — parallel preparation and one initial material batch

2026-10-23 America/New_York. Sponsor explicitly authorizes multi-threaded
preparation andinitialshipsfix,not a vendorpatch ornewrenderarchitecture.
Starting/final HEADd40f8f230fc7504023e4a052c99a81b5a08ce6b4,codex/github-sanitized;
indexempty,substantial inherited Run113–124work preserved unstaged/untracked.
Read HANDOFF/Run124,capturedsix-ship evidence,currentcontract,relay/supervisor,
worker guards and native D3D9 catalog code. Approved capability boundaries
unchanged. FuelGuard attached;nohelper/subagent/gameplaylaunch/stage/commit/push.

## Starting evidence and implementation decisions

CONFIRMED Run124:all6shipownerscorrect,5uniqueassets+1sharedalias,noownership
orimagebudgetfailure. Serialpreparation andfourlate-libraryrewrites;four1.1–1.6s
outputwaits. Lastnativeownerfirstoffered29.906s,so multithreadingcannotpromiseall
shipsbeforetheexistingseamoffers them. Earlierassetdiscoveryremainsseparatework.

Implemented PreparationQueue:4workerthreads,64bounded descriptors;identify/decode/
contenthashandfullimage/material/prepared-bytehash work offcoordinator. Noqueued
executorbacklogbeyond4actualtasks;readydecodedworkgetspriority. First-observed
contentcanonical chosen deterministically despiteout-of-order completions.
Aliases wait in coordinator state,not executor threads,and never reconvert content.
Only coordinator mutates shared catalogs,material conflicts andimageledger.

Initial known set sealsafter750msand200msquiet,or2smaximum discovery interval.
Joininitialpreparation(up to25s insideexisting30s first-imagewatchdog),construct
allmateriallayers,atomically publishONCE,andonlythenstartRemix. Immutable
same-volume bootstraplinksreuse firstasset bytes without copying/rewriting its
ownmaterialstage. Allinitial entries getnativeGPUadmissionbarrier beforevisible
return. DeviceworkstillowningD3D9thread;no waits/allocations/IOinSFCcallbacks.

Four256MiBtemporarydiskreservations account forconcurrentwrites against20GB
projectallowance;actualGPUresident256MiBprotectionunchanged. Metadata snapshot
gate/run-metadata.json preventsmutable runner manifest racesduringconcurrent
conversions;containsfreshsession,notreused resourceIDs. Budgetenumeration tolerates
latest-light atomicrename. Existingimageformats/hashes/UVs/materialpolicy preserved.
Shutdown joinsallrunningworkers/cancelsqueuedwork before mappingrelease.

No optimization bydroppingmaterials,guessingtextures,usingMODgeometry,stale-frame
holding,skipping nativeidentity checks orchangingoutputarchitecture. In-place
deformation/transparency/earlier engine assetinventoryremainunqualified. Later
unique materialadmissionstillusesknownreloadpath;latealiasesreuseexistingcontent.

## Files changed

New:tools/remix_runtime/asset_preparation.py,tests/test_asset_preparation.py,
thisrecord andcuratedevidence.
Modified:tools/remix_runtime/multi_scene_relay.py,multi_scene_resources.py,
live_owner_timing.py,qualify_multiship.py,run_return_fixture.py,
source_timing_fixture.h;tools/d3d9_proof/multi_scene_wire.h,multi_scene_runtime.h,
run_offline.py;tests/test_d3d9_multi_scene.py,d3d9_multi_scene_tests.cpp;
currentcontract/probe andHANDOFF. Originalgameobserver/hooks unchanged.

## Validation / exact reproduction

Bundled Python3.12,modernPowerShell,VS2026Community x86/x64 /W4/WX,current
optimizedhost /O2/fp:precise. PinnedRemix1.5.2/configuration andaccepted game
installation unchanged. Commands(normaltest runners neverlaunchSFC):

```powershell
python -m unittest discover -s tests -p 'test_*.py'
pwsh -NoProfile -File tools/d3d9_proof/build_multiship.ps1
pwsh -NoProfile -File tools/d3d9_proof/build_direct64.ps1
pwsh -NoProfile -File tools/m1_component/build_light_discovery.ps1
pwsh -NoProfile -File tools/d3d9_proof/build_persistent_scene.ps1
python tools/remix_runtime/light_discovery.py
python tools/remix_runtime/run_return_fixture.py --multi-ship --multi-ship-resources
python tools/remix_runtime/run_return_fixture.py --multi-ship --multi-ship-resources --multi-ship-late-asset
python tools/remix_runtime/qualify_multiship.py --fixture artifacts/remix-runtime/runs/20261023-201728-165994-return-fixture
python tools/remix_runtime/run_return_game.py --multi-ship
git diff --check
```

Standalonefixturealso recompiled fromreturn_fixture.cpp usingexisting x86
build_return_probe.ps1 compiler/linksettings;no compositorbinarychange required.
No formal M1/TRL completionclaim;allruntimefixturesuseexplicitlysynthetic poses/
aliasidentity and realhistoricalcapturedgeometry,never nativeMODfiles.

456Python testsPASS. Newactualthreadbarriertestproves4simultaneouspreparations;
coalescing,oppositeidentifycompletionorder,failures,shutdownjoin,queuebounds,
parallelreservationsandoneinitialUSDcommit/independentaliasesPASS. Nativewire50
checks×2architecturePASS,includinginitialmaskpending/success/failure/highbit.
Persistent18checks×2andactual120updatecollectorPASS;native light9core/17observer
checks×2andnativeworkerPASS;loadedlights11,combinedGPUpost65,workerpoll,
deferreddiagnosticsPASS. No change to game ABI/callingconvention.

Intermediate201258-751906replayPASS600/600butprofilingexposedserialfinalproof
hashing in coordinator;subsequently moved that work into workers. Historical
intermediatereceipt isNOTthe finalsourcequalification. Lowresolutionmonotonic_ns
initiallyhid sub-ms testoverlap;changedprofiling toperf_counter_ns/QPC andretained
explicitclocknames. Not a gamefailure or unsupported successclaim.

## Final source-locked results

Initialbatchfixture201728-165994:4owners(FCA,RCA,FDD,FCAalias),3uniqueassets,
4configuredworkers/3overlappingpreparations,allACKed,all4drawn841times.
One3-layermaterialpublication BEFORErendererstart;initialnativeGPUcatalogmask15
resolved before firstvisiblecopy(first_draws=0whenallassetsready).
Initialbatchready10.416secondsafterfirstjob discovery in thisfixture. Perasset
fullworker durations6.877/7.066/9.820s overlap;these areNOTa controlledserial
speedupbenchmark andincludeproofhashing/preparation. Source-seamfirstoffer and
runtimeinit latency remain distinct. Zerolookup/decode/projection failures or
assetpartials.594/600steady deliveries,Hud/scene/state/resize/exitPASS. Maximum
outputGPUwait17.794ms,zero>50mswaits;not literalzero single-frame omissions.

Deliberatelatefixture201855-869087:initialFCA/RCA/sharedaliaspublishedonce,then
FDDfirstofferedonlyafter120returnedframes. LateFDDadmittedsafely;all4owners,
noassetpartial/cohort/decode/projectionfailure.2overlappingpreparations,workers
closed/noneunfinished. Oneadditionalmaterialpublication,one1439.768msGPUwait:
knownLATEreloaddeficiencystillpresent,not claimedfixed.595/600steadydeliveries;
HUD/state/resize/normalownedexitPASS. No stale-imageworkaround introduced.

Bothfinalfixturespassedexact-buildinspection;initialfixtureusedtoqualify
preparedsponsorworkflow. Read-onlypreflightPASS,noSFC/game/rendererstartedbyit.
Fullsource/binary/configreceipt hashes incuratedevidence. Original/copiedclient
SHA256both4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29;
copiedproxyE35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7.
Artifactinventory13,464,786,710bytes<20GB;allcaptures/generatedbinariesignored.
No active owned game/host/fixture/receiver remains. Allchangesunstaged/uncommitted,
indexempty,HEADunchanged,nopush. Evidence/oldcheckpoints preserved.

## Exact next action

Sponsor repeats6shipfixturewithFCAandduplicateKlingons,usingexisting
start_d3d9_multiship_session.ps1. Enterwithin120secondsofsetupmessage;show/cycle
eachship,playnormally,exitattwoLOWbeepsafter90secondtacticalrecording. Expected
knowninitialcopiesappeartogetherafterpreparationwithnormaltexture/lightsettings.
Modelsfirstobservedlatermaystillcauseareloadpause;reportseparately. No manual
timestamps,admininteractionorREworkneeded. ThisdoesNOTimplementloading-screen
preload orpromiseinstantallmissionassetavailability.
