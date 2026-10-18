# Codex run — diagnostic world offset and masked compositor

Run SFC-RETURN-20261017-22;2026-10-17 America/New_York. Sponsor approved temporary
3D offset of the Remix ship,original enabled. Approved return-path investigation;
no milestone/TRL completion. HEAD `e96765a1a34c15212ed22f11edeb9a708b9fc18d`;
large prior dirty/untracked state and empty index preserved. FuelGuard attached
actual thread via recent hook receipt;no daemon/helper/subagent/game launched.

## Actual result and partial work

**CONFIRMED OFFLINE:** actual Remix draws offset FCA geometry; coherent color,
picking and corrected depth reach the native x86 receiver. New reusable masked
compositor draws only the selected opaque owner and preserves background and
tested immediate-context state. Original pose/camera/geometry unchanged. World
translation[0,14.3611755371,0] gives roughly51pixels leftward at256square,not a
finished-image shift. Two source poses120/720 independently match shifted native
projection with maskIoU1.0;depth median errors1.8237e-7/4.4851e-7.

**PARTIAL relative to requested in-game offset test:** no actual addon adoption,
fresh live request scheduling/UI-safe composition or game launch prepared yet.
Current producer is a recorded-pose standalone fixture,NOT a current game feed.
Do not attach it and pretend it is synchronized. Original ships were never
suppressed;game renderer and semantic hooks unchanged. No sponsor input needed
for the remaining implementation. Not READY FOR SPONSOR RUNTIME TEST.

Visual inspection of generated comparison confirms displacement but shows the
default-material ship is very dark under the provisional fixture light. This is
not a textured ship/appearance result. Do not assume this diagnostic material will
be unmistakable on SFC's black background;live test needs the existing qualified
textures or an explicit diagnostic material,not local counterfeit ship color.
No light/appearance tuning performed in this run.

## Sources reviewed / engineering decisions

Read HANDOFF newest Run21 checkpoint and operating convention,approved M1 plan
current amendment,Run21/contract/probe/readiness,return_addon/host/game runner,
native consumer/fixture/wire,coverage runner/host and pinned SDK types. Mainline
and depth correction from Runs19/20 not reopened. Existing M1 plan is component
gate,not aggregate TRL4 authority. This is authorized later return-path work.

- Native instance translation before DrawInstance;no asset edits,pixel shift,
  camera fitting or silent geometry repair. Reject clipping/bad camera basis.
- Wirev3 Wire496B/Key152B,explicit offset mode/translation;native source pose hash
  retained. Both architectures65checks. Previousv2 evidence preserved,not active
  layout. Wrong offset/mode cannot claim another packet.
- Reusable compositor constructor compiles SM4.1 shaders and creates deferred
  context. Draw admits exact ID bits plus finite nativeZ[0,1],opaque color only.
  Executes command list with automatic immediate-context state restoration.
  No waits/readbacks/files in draw;normal graphics command-list creation may
  entail driver allocations,not a claim of zero internal driver allocation.
- GPU test-only receiver compares all returned composite pixels and border with
  expected mask/color,then ACKs after GPU completion. Separate synthetic tests
  cover foreign IDs,bad depth,invalid key/viewport and two destination sizes.
- Exact observed state checks:RTV,viewport,topology,PSconstant/SRV;synthetic adds
  blend/factors/sample mask,depth/ref,raster/scissor. This does not establish SFC
  HUD ordering or effects preservation. No scene-depth occlusion writes/tests.

## Changed files this run

Added:

- `tools/remix_runtime/ship_triplet_compositor.h`
- `tools/remix_runtime/analyze_ship_offset.py`
- `tests/ship_compositor_gpu_tests.cpp`
- `tests/test_ship_diagnostic_offset.py`
- `docs/reconnaissance/probes/REMIX-OFFSET-001.md`
- `docs/reconnaissance/evidence/20261017-ship-offset-compositor.json`
- this run record.

Modified:ship_triplet_wire.h,ship_triplet_fixture.h,ship_triplet_consumer.cpp,
coverage_probe.h,run_coverage_probe.py,build_triplet_probe.ps1,
tests/ship_triplet_tests.cpp,tests/test_ship_triplet_runner.py,
ship-triplet-return-contract.md,ship-replacement-readiness.md,HANDOFF.md.
All relative to repo unless basename is unambiguous in tools/remix_runtime.
Game addon/host/controller/observer/game runner and installations not changed.

## Commands / results / bounded evidence

Definitions/reproduction in [REMIX-OFFSET-001](../reconnaissance/probes/REMIX-OFFSET-001.md).
Build:PS7 `-NoProfile -File tools/remix_runtime/build_triplet_probe.ps1`;
VS2026 18.7.3,/W4 /WX,/Brepro,C++20. Native65wirechecks eachx64/x86 PASS.
`artifacts/remix-runtime/triplet-bin/ship_compositor_gpu_tests.exe`:22GPUchecks
PASS,explicit10_1,synthetic16/24square outputs. FullPython188tests PASS3.696s.
Python bundled runtime,TEMP/TMP=artifacts/test-temp. Later only analyzer size guard
and docs added;final188test rerun PASS3.688s. `git diff --check` PASS(line-ending
warnings only);index empty. Process inventory found no owned fixture/game/host.

`python tools/remix_runtime/run_coverage_probe.py --execute --triplet --native-depth
--calibration-run artifacts/remix-runtime/runs/20261018-025737-262069-in-game
--snapshot N` plus `--diagnostic-offset` for displaced copy. Only owned standalone
processes. `--triplet-fault slow|exit` negative controls;no gameplay/UAC required.
GPU fixture uses scoped external execution due sandbox GPU/child restrictions;
no security policy or target privileges changed.

Evidence folders under artifacts/remix-runtime/runs:

| UTC folder | Result |
|---|---|
|20261018-033618-648042-coverage|Initial sandbox control failed before child-ready;no composite accepted. Exact child cause unlogged,NOT proven compositor/code failure. Added bounded child log;external control passes.|
|20261018-033712-466567-coverage|Unmodified control PASS;two triplets/composites,state restore,normal child0.|
|20261018-033724-728737-coverage|Offset pose120 PASS;reanalysis label corrected to offset-specific qualification,not original nativeGPUdepth.|
|20261018-033936-688936-coverage|Offset pose720 PASS;mask505/505,medianZerror4.4851e-7.|
|20261018-033954-610616-coverage|Slow6s EXPECTED fault;published1/ACK0/accepted0/READY,no overwrite.|
|20261018-034320-402636-coverage|Exit receiver EXPECTED fault;same refusal,no false nominal PASS.|
|20261018-034342-239613-coverage|Final documented offset pose120 PASS;mask512/512,medianZerror1.8237e-7,child exact/state restore,3.703s.|

Final source/executable pins and exact sizes in curated evidence. Probe bounds
in code inherited before tests;new prose offset runbook completed after initial
offline executions and before final negative/positive runs. This timing is
recorded rather than implying prose documentation preceded the initial tests.
No undocumented gameplay test occurred.

Each positive~5.42MB;fixed96frames,120s/32MiB cap(warn16). Receiver private target,
sentinel and staging are bounded fixture resources,not transport-pool additions.
No image firehose. Final comparison:original478maskpixels vs512offset,
centroidshift[-51.0293,.4831]pixels. Geometry/camera hashes equal;source pose
unchanged. Figure is masked checkerboard analysis,not an in-game screenshot.

Archive `artifacts/remix-runtime/archives/20261018-034415-245677-coverage.zip`,
1,700,179bytes/226entries/33,046,024sourcebytes,CRCverified,
SHA256 `5101456E8FE395779FA337916C0FE82F85244E3A85C7F148D9CE120BDD343478`.
Includes all7attempts,raw retained under10GB. No evidence deleted.

## Remaining / repository close

SDK common-object teardown warning persists(in observed control,37objects);
normal0 is not warning-free cleanup. Historical SFC54/67not exercised here.
No new engine addresses/ABI conclusions. Native10_1 fullsize device-loss/hot-unload,
real-addon UI order,scene occlusion/effects and live timing remain unqualified.
Exact-frame wire equality must not be loosened silently to display stale poses.

Both installations'all7critical hashes compared with Run19 accepted/copy after
records;clientSHA `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`
unchanged. Pinned runtime unchanged. No active SFC/fixture/host/receiver required
to resume. HEAD e96765a,indexempty,all current edits unstaged/untracked,prior work
preserved,no stage/commit. Docs do not overwrite previous run evidence.

**Exact next action:**connect the qualified receiver/compositor to a fresh live
request in the copied-game path,originals ON,with offline state/lifecycle and
UI-safe insertion validation before preparing sponsor gameplay. Do not run the
recorded-pose fixture as if it were live or hide either original ship.
