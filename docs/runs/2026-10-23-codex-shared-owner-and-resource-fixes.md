# Run123 — shared-owner correction and active test-restriction audit

Date2026-10-23 America/New_York. Sponsor authorizes both Run122fixes and review
for test-only constraints accidentally left in the active multi-ship workflow.
HEADd40f8f230fc7504023e4a052c99a81b5a08ce6b4,codex/github-sanitized,indexempty;
substantial inherited Run113–122work preserved unstaged/untracked. Read HANDOFF,
Run122raw/evidence,approved M1authority/contract and narrowly related current code.
FuelGuard attached;no helper,subagent,staging,commit,push or SFC launch.

## Engineering decisions / implementation

CONFIRMED Run122:second KDD ship's qualified incoming owner overwritten by first
visual match4482times. NewOwnerTable::model_owner prefers exact native ship/epoch/
visual,refuses stale or mismatched context,and accepts context-free lookup only
if unique. RecordHook rechecks readable native shipvtable/link without nativecalls
before using it. No hooks/ABI/wire redesign. Ownertable retired/reused addresses
cannot revive oldepochs. Captured/shared asset content stays distinct frominstance.
Existing persistent registry then keeps each successfully admitted owner alive
independent of camera visibility,without reconstruction when it returns.

FCA exclusion was not rendering incompatibility:the small-scene SCENE-WIDEimage
budget was duplicated in estimator,actual ledger,game supervisor,standalone
supervisor and process guard. Removed those multi-ship restrictions and global
256image count. Real20GBproject/disk-space protection replaces them;32MiBreserved
for bounded evidence. Checks run once perasset outside render callback. Actual
worker guard accepts20GBupperbound and multi-ship requests it;other callers retain
their smaller requested cap. Warning now80percent of actual guard allowance.
Hash-qualified guard/source included in new-mode preparation receipt.

## Active-path restriction audit

| Item | Disposition |
| --- | --- |
| 128MiBscene-wide original/derived images | REMOVED from all active multi-ship supervisors/admission/guard/qualification |
| 256original images perwhole scene | REMOVED;per-asset schema guard remains |
| First-matchvisual ownership | FIXED;qualified context or unique-only fallback |
| ExactFCAfilename/fixedmesh/template selector | Already bypassed in multi-ship mode;single-ship diagnostic retains it |
| Artificial90frame late-admission delay | Exists ONLYwhen offline_fixture true;not gameplay |
| Synthetic pose generators/Sleep3or16ms | Standalone fixture only,never native game component |
| Inherited fixture/backbuffer diagnostic environment | Explicitly stripped for normal worker launch |
| Camera-recovery action beeps/instructions | Suppressed for multi-ship;normal start/exit cue remains |
| Magenta/on-off/shading interventions | Not enabled in this live multi-ship configuration |
| Camera-left offset/original shipsON | Retained by sponsor request to judge copies;replacement separate |
| 30Hzrecord sampling | Low-volume diagnostic table only;native simulation/cohort updates remain full scene rate |
| 120frame detailed trace limit | Retained bounded evidence only;tracking/rendering/census continue |
| 90scapture/120sselection/285stotal/30spreparation watchdog | Retained test operating envelope,NOT production load-latency claim |
| 32owners/64revisions/four2MiBslots | Finite versioned transport capacity;exceeding reportedPARTIAL |
| Per-asset128MiBdecode/256resources/4096² | Explicit parser/allocation/format protection;not the removed aggregate export budget |
| 256MiBpending+resident CPU/managedGPU backing | Retained memory protection;not measuredGPUfreeVRAM,not20GBdisk allowance |
| Opaque rigid triangle meshes/fixed1920x1080return | Current qualified format/output envelope,not universal engine coverage |
| Current lights/material/image policy | Preserved;no appearance tuning,fullscene-light parity or asset redesign |
| Material hot reload stall/~5sfirstload | Known remaining work,NOT fixed by these correctness changes |

Audit scope is current semantic→persistentregistry→ordinaryD3D9→Remix→GPUreturn
workflow and its supervisors,not a claim to audit unrelated historical tools.

## Files changed this run

- tools/m1_component/m1_contract.h,m1_component.cpp
- tests/m1_identity_census_tests.cpp,m1_identity_component_tests.cpp,
  m1_shading_off_component_tests.cpp
- tools/remix_runtime/multi_scene_resources.py(new),multi_scene_relay.py,
  live_owner_timing.py,run_return_game.py,run_return_fixture.py,qualify_multiship.py,
  source_timing_fixture.h,return_fixture.cpp
- tools/remix_ingest/bounded_job.cpp,test_bounded_job.py
- tools/d3d9_proof/multi_scene_fixture.py
- tests/test_multi_scene_resources.py(new)
- current multi-ship contract/probe,thisrecord,HANDOFF and curated evidence.

## Validation and reproduction

Bundled Python3.12/modernPowerShell,VS2026Community x86/x64 /W4/WX;
nativecomponent /O2/MT/SSE2. Existing pinned runtime/configuration unchanged.

```powershell
pwsh -NoProfile -File tools/m1_component/build_identity_census_tests.ps1
pwsh -NoProfile -File tools/m1_component/build_m1_component.ps1
pwsh -NoProfile -File tools/m1_component/build_light_discovery.ps1
pwsh -NoProfile -File tools/d3d9_proof/build_persistent_scene.ps1
pwsh -NoProfile -File tools/remix_ingest/build_remix_job.ps1
python tools/remix_ingest/test_bounded_job.py
python -m unittest discover -s tests -p 'test_*.py'
python tools/remix_runtime/light_discovery.py
python tools/remix_runtime/run_return_fixture.py --multi-ship --multi-ship-resources
python tools/remix_runtime/qualify_multiship.py --fixture <completed-current-fixture>
python tools/remix_runtime/run_return_game.py --multi-ship
git diff --check
```

Only standalone fixture recompiled from return_fixture.cpp with existing x86
build_return_probe.ps1compiler/link settings;actual compositor binary unchanged.
Newresource fixture uses3different captured assets(FCA/RCA/FDD) and1synthetic
independently positioned FCAowner alias. Syntheticpacketheader/owner/checksum
rewritten ONLYinsidefixture;geometry/corners/UV/groups/images unchanged and tested.
No MOD geometry source. Requireall4ownersdraw,3residentcontents,sharedpathreuse,
actualimageoutput>128MiB,normal HUD/state/resize/shutdown and unchanged hashes.

Completed so far:448PythonPASS;13portablecensuschecks perarchitecturePASS;
actualx86recorder3shared-visualowners/zerochoice mismatches and3guardednegative
casesPASS;fullM1native regressionsPASS;persistent18checks/arch andlightobserver
17checks/arch/nativeworkerPASS;5actualboundedjob testsPASS,including sparse129MiB
output accepted under20GB and log/time/disk/owned-descendant isolation.

Validation caught:oldshading syntheticfixture used unreadable0x1000shipidentity;
replaced with readable synthetic ship/link,NOTweakened productionguard. Compiler
signedness warning inextendedfixture corrected. FirstextendedGPUattempt
20261023-193614-605283stopped at duplicated standalone128MiBcheck;preservedPARTIAL,
fixed check rather than promoting failed run. FinalGPU/preflight below.

Exact next action after offline validation:sponsor repeats six-ship fixture with
FCA plus duplicated Klingon model;inspectall6nativeinstances,sharedcontentreuse,
FCAadmission,lifetime/camera andoutput bounds. No additional root-cause discovery
run needed. Do not claim universal coverage,perfect flicker or replacementPASS.

No staging/commit/push. Originalacceptedclient andassets preserved. Runtime
evidence/binariesignored. FinalGit andhash/fixture receipts recordedbeforehandoff.

## Final validated checkpoint

Extended actualGPUfixture20261023-193719-104356-return-fixturePASS. FCA/RCA/FDD
andindependentFCAalias31allACK1,4owner drawcounters,3content/pathIDs;alias31uses
FCApath1withoutconversion/reload. Draws:RCA1126,FDD795,FCA1510,alias786.
Imageaccounting157,271,228bytes andjobactualscratch144,463,338bytes BOTHexceedold
128MiB134,217,728cutoff.130originalimages,zeropartials/assetrejects/lookup/decode/
projectionfailures;595of600steadypresentationspaired. NativeHUD/sceneexact,
stateerrors0,resize/recreationPASS. Ownedjobexit0/stopreason0/noownedprocesses.
This proves old restriction removed in realCPU/GPUworkflow,notjust mockedlimits.
Knownlate-materialreloadstillpresent;595/600isnotperfectseamlessdelivery.

Exactbuildqualificationrefreshedandread-onlygamepreflightPASS. No SFC launched.
Currentevidenceinventory12,721,524,396<20,000,000,000bytes;no deletionneeded.
Original/copiedclientbothSHA256
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29,
copiedproxyE35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7.
[Curated evidence](../reconnaissance/evidence/20261023-d3d9-shared-owner-resource-fixes.json)
retains exactfixture/qualification/componenthashes. HEADunchanged,indexempty,
allworkunstaged/uncommitted,nopush,gitdiff--checkPASS. No active owned process.

Prepared sponsor command remains:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_multiship_session.ps1"
```
Enter skirmish within120seconds of setupmessage;90secondrecording starts atgate.
Repeat6shipsincludingFCAandduplicatedKlingons;cycleeachintoview,playnormally,
exit atfinaltwoLOWbeeps. ExpectedFCAadmissionandseparatecopiesofidenticalships.
Actualruntimeacceptancepending;no claimthesearealreadyconfirmedinthegame.
