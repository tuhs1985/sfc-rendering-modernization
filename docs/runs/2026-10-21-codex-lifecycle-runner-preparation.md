# Run94 — separate bounded lifecycle-test runner

2026-10-21 America/New_York. Sponsor ran anyway,then explicitly requested a copied
runner tuned for camera gaps and player destruction. HEADd29111f7,branch
codex/github-sanitized,index empty;prior dirty work preserved. Read HANDOFF,
Run92/93,approved M1 plan context and current scene worker/runner/qualification.
Fuel Guard attach returned SANDBOX_ACCESS_DENIED,no daemon started;continued.
No helper/agents/stage/commit/push and no SFC launch by Codex.

## New sponsor run review

`artifacts/remix-runtime/runs/20261021-051331-856002-in-game`:normal game exit,
renderer0,1905draws,20stale,zero invalid/resource/depth failures. Selected2/2.
Source timing stage1 has owner1/1:2457records and owner2/2:2212records. Detailed
state only100rows each:owner1 through4844ms,owner2 through4860ms. No worker summary
because target exited before controlled removal;controller8. Original critical
hashes,launcher settings,proxy restoration confirmed by result. No destruction
timestamp/native death flag. Later selected-owner absence does NOT establish death.
Retain PARTIAL duration/unload classification,not a crash or useless-data claim.

Also reviewed044755run:5272draws,108stale;full90s history but final relay error
`Live renderer exited before source stopped`,controlled unload not established.
Five observed epochs;old100row cap loses later transitions for first two epochs.
No broad cleanup or reinterpretation of either run as lifetime proof.

## Implementation / engineering disposition

New `tools/d3d9_proof/start_d3d9_lifecycle_session.ps1` copies normal entry pattern,
adds opt-in LifecycleCapture,retains CheckOnly and common validated elevated parent.
Original offset launcher unchanged. Common PS/Python entry adds explicit separate
flag,clears inherited override for normal runs and records bounded phase schedule
plus actual cue-issuance times. Requested actions are NOT verified action timestamps.

Native LiveScene default-off lifecycle mode retains detail throughout120s watchdog
at <=20Hz,2700rows/slot,16MiB;normal light-tuning100row cap unchanged. Independent
prefaulted256*96word transition ring under existing try-lock retains retirement
even if latest state overwritten by a return. Worker emits <=1MiB event JSONL,
counts queue/output/lock losses,drains before unmapping. No callback allocations,
I/O,waits,guessed health reads,new hooks or modified ABI. Geometry hook remains OFF.
No camera-recovery implementation,stale pixels or retirement bypass. Existing8
calibration asset revisions remain a limit,not silently expanded.

Analyzer explicitly distinguishes observation retirement from destruction;missing
summary/events,malformed rows/loss/saturation ->PARTIAL. Complete journal never
claims native death proof. New offline qualifier checks actual worker's late
detail/coalesced events and hashes;runtime entry fails closed if unqualified.

Files changed this run:

- tools/m1_component/m1_live_scene.h
- tests/m1_live_scene_tests.cpp
- tools/remix_runtime/run_return_game.py
- tools/remix_runtime/start_return_image_session.ps1
- New tools/d3d9_proof/start_d3d9_lifecycle_session.ps1
- New tools/remix_runtime/lifecycle_capture.py
- New tools/remix_runtime/qualify_lifecycle_capture.py
- New tests/test_lifecycle_capture.py
- New docs/reconnaissance/probes/D3D9-LIFECYCLE-001.md,this run record,HANDOFF update.

## Validation / reproducibility

Use bundled modern pwsh/Python paths established in project run records:

1. `tools/m1_component/build_light_discovery.ps1`
2. `tools/remix_runtime/qualify_lifecycle_capture.py`
3. `python -m unittest discover -s tests -p "test_*.py"`
4. `python tools/remix_runtime/run_return_fixture.py --d3d9-additive`
5. `additive_qualification.qualify(exact_fixture_directory)`
6. New lifecycle entry `-CheckOnly`;PS/Python parser checks;git diff --check.

Initial test build correctly failed /WX for a shadowed local;renamed test local.
First qualifier ran stale old test binary after build failure and rejected missing
journal. Later corrected assertion:worker try-lock may naturally add contention
to explicitly forced one drop;do not require exactly one. Required transition
receipts and zero journal overflow/omission/pending still mandatory. These failures
are retained under ignored generated evidence;none were promoted to runtime proof.

381Python tests PASS. Native x86/x64 light core9/observer13checks and actual
normal/tuning worker tests PASS. Fixed journal test verifies256retained+44dropped,
ordered/no overwrite and default-off mode. Actual lifecycle-worker qualification
checks >100late records,retirement/new epoch retained,join and bounded output.

Standalone fixture20261021-052314-646705-return-fixture:599/600delivered,
152939changed pixels,border untouched,state_errors0,resize/recreation,normal
owned child/renderer exit. Actual ordinary-D3D9/Remix+proxy test,NOT gameplay.
Final prepared qualification/storage/hash/parser status follows.

## Final checkpoint

Final dedicated rebuild/normal+tuning qualification PASS after prefault and
partial-report refinements. Actual lifecycle evidence:
artifacts/remix-runtime/native-light-tests/lifecycle-bee3a938e9244679879adab47de7e21d.
147detail rows/29744bytes,owner2has139rows through107050ms;14transition rows/
2850bytes,zero journal drops/omissions/pending,saturation or I/O failure. Two
mailbox drops include deliberate contention;one capture failure/four unsent assets
are synthetic no-ACK/revision-limit exercise,not clean gameplay claims. Analyzer
correctly labels this synthetic capture PARTIAL while required journal assertions
pass. No lossless-real-runtime claim. Fixed queue256/44overflow checks PASS.

Final381Python tests PASS,Python/PowerShell parsers PASS,additive and separate
lifecycle receipts refreshed;new entry CheckOnly PASS/no game or renderer start.
Client original and copy SHA256 both unchanged:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Fixture199generated copies recoverably archived and decompressed hashes verified:
artifacts/remix-runtime/archives/20261021-052314-646705-return-fixture-binaries.zip,
SHA2560D5AE60BBE6CF5F4E7E78AAF7089C693C7C7993109F1F33061EABBFC6EAB47A3;
82187512bytes->6861548bytes. Raw metadata/logs/source packets retained. Actual
partial games not compacted through clean-game guard. Aggregate10156544476B/20GB.
No game/owned renderer active at final check. Vendor warning40 remains unresolved.
Final HEADd29111f7,index empty,prior and new work unstaged/uncommitted;git diff
--check PASS. No accepted client/settings modifications or automatic game launch.
M1 CONTINUES. No native destruction discriminator or camera epoch recovery claim.
Exact next action after preparation:sponsor uses dedicated lifecycle launcher and
follows one/two/three/four-high cues,then exits only at two-low cue. Report alive
camera return and actual own-ship destruction. Do not rerun30minute endurance.
