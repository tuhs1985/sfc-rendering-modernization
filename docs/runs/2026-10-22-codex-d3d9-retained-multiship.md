# Run113 — fresh retained multi-ship D3D9 scene / aligned overlay

2026-10-22. Active increment: generic fresh asset admission and multiple retained
instances through ordinary D3D9→pinned Remix→existing synchronized GPU return.
Starting HEAD `d40f8f230fc7504023e4a052c99a81b5a08ce6b4`, clean
`codex/github-sanitized`, synced origin/master. Fuel Guard attach confirmed recent
trusted hook; no daemon/helper/subagent. No staging/commit/push authorized.

Sponsor addition selects first **aligned overlay** test, originals underneath,
not true suppression/replacement. Test is a skirmish with **different models**,
not “mixed race” (earlier tests already mixed races). No requirement/TRL change.

Authority reviewed: HANDOFF Run112/111/110/109 and operating convention, approved
M1 plan/amended gate allocation, existing source/owner/asset/buffer evidence.
Do not repeat camera/simulation position discovery or treat historical FCA-only
selection as proof of another model's unsupported geometry.

## Engineering decisions and implementation in progress

See [contract](../reconnaissance/d3d9-retained-multiship-contract.md).
Default-off `SFC_D3D9_MULTISCENE=1`; legacy FCA path remains separate. Fixed
107072-byte version1 tracked-set/catalog block at map15MiB−128KiB, below lights15MiB;
32 rows/frame,8 frame slots,64 immutable asset catalog entries with ACK. Selected
anchor schedules source input/light context; whole-set checksum binds returned
frame to every sampled row. No complete-engine-scene seal claim.

Native persistent registry publishes same-camera rows once per qualified scene
frame, without30Hz cap. Existing four2MiB mesh capture slots reused; new mode
allows64 revisions instead of calibration baseline8. Worker prepares assets from
fresh packets and original IMAGE files, never MOD geometry/OBJ/templates. One
asset-preparation worker,one host,content sharing,own instance world transforms,
one D3D9 Present;128MiB image and256MiB retained-asset bounds remain.

Aligned zero-displacement compositor coverage is explicitly the union of
submitted qualified instances, tagged with scene/anchor provenance. It is NOT
a per-pixel native owner map; cannot authorize owner-specific suppression.
Material-only USD layers remain Remix adapter policy; no Toolkit geometry or
SDK mesh path introduced. Installed pinned material hot reload needs offline
corroboration; official1.5.2 source supports root-mod timestamp reload,not yet
proof of this installed binary's behavior. In-place deformation/native alpha/
effects/death qualification remain limitations,not silently repaired.

## Validation log — provisional, update before handoff

- Native new wire29 checks PASS x86 and x64, exact107072-byte cross-ABI layout.
- OrdinaryD3D9 host builds `/O2 /W4 /WX /fp:precise`; existing light11,
  deferred diagnostics,worker poll and combined post65 GPU checks PASS.
- x86 receiver output29/source18/slot649 tests PASS; return add-on/fixture
  compilation and native semantic component build underway.
- Python syntax checks passed for new relay/protocol/fixture modules.
- Standalone multi-ship fixture underway; no SFC/gameplay started by Codex.
- First two fixtures caught a proposed12MiB layout overlapping existing source
  timing evidence. Corrected to15MiB−128KiB,with explicit compile-time lower and
  upper overlap checks. No game run used that defective experimental layout.

Reproduction uses bundled Python and modern pwsh identified in existing project
scripts: `build_multiship.ps1`, `build_direct64.ps1`, `build_receiver.ps1`,
`tools/remix_runtime/build_return_probe.ps1`,
`tools/m1_component/build_light_discovery.ps1`, then
`tools/remix_runtime/run_return_fixture.py --multi-ship`. All GPU/map checks
run on host with approved elevation; no routine UAC/security-policy change.

Current files: contract,this run record; new multi_scene_wire.h,
multi_scene_runtime.h,multi_scene.py,multi_scene_fixture.py,multi_scene_relay.py,
build_multiship.ps1,d3d9_multi_scene_tests.cpp; modified native live scene,
D3D9 host/replay/output writer,Python relay,game receiver/frame history and
standalone source/return fixture. Exact final list/status must be recorded after
validation. Generated binaries/capture assets ignored; source assets preserved.

Runtime status: no game test authorized as completed; no replacement PASS.
Implementation is not ready for sponsor until new-source fixture and gates pass.
All current implementation/evidence changes unstaged/uncommitted.

## Final checkpoint — prepared,not yet tested in SFC

**READY FOR SPONSOR RUNTIME TEST.**
[Probe and launcher](../reconnaissance/d3d9-retained-multiship-probe.md),
[curated results](../reconnaissance/evidence/20261022-d3d9-retained-multiship.json).
This section supersedes provisional build/test statuses above;retains failures
as engineering history rather than deleting them. No SFC gameplay run this turn.

Final builds/native checks PASS:both new wire ABIs29 each,persistent core18 each,
actual native collector fixture120changing pose/camera updates,one capture/one
instance generation,120cohort publications,one expected rejected publication
after retirement,worker joins and stopped-store checksum verified. Existing
receiver wire29/source18/outputslots649,return37/search13/broad14/calibration22,
native light9/observer17 perarchitecture,combinedpost65 and GPUbuffer33×2 pass.
431Python regressions PASS,including6new protocol/sharing/workflow tests.
Initial sandbox full-suite temporary-file permission failures were environment
errors;normal host rerun passed. PowerShell launcher parser and`git diff --check`
PASS. Current generic read-only preflight passes without game/renderer launch.

Final source-locked standalone runs:

| Fixture suffix | Timing lead | Steady matched overlays | Total paired / without returned cohort | Owner1 / owner3 draws |
| --- | --- | --- | --- | --- |
| 061042-924464 | ~3.5ms | 568/600 | 719/105 | 788/894 |
| 061206-530221 | ~16.4ms | 569/600 | 688/75 | 761/862 |

Both date20261022,in`artifacts/remix-runtime/runs`,same final source/binary/config
locks. Two distinct historical native packets FCA/RCA,simultaneous SYNTHETIC
poses,actualD3D9buffers/indices/UVs/grouptextures with byte/row readbacks,one host,
late second admission after≥90displayed first outputs. Installed pinnedruntime
loaded the additional material sublayer/search paths.24,602changed returned
pixels,native HUD/scene exact,untouched border,state_errors0,resize/recreation,
zero output overwrites/resource errors,normal owned exit/APIshutdown0. Record
all warm-up/late-admission omissions;separate unchanged≥90%600-frame steady gate
starts60fixtureframes afterbothassetACKs. Not a seamless-production claim.

Both use45,271,248bytes conservative retainedCPU+managedGPUasset backing and
91,506,338bytes original/derived images,91originalimages.64MiBwarning expected,
128MiBhardcap not exceeded.17/16sampled rawcohortframes plus107072-byte stopped
store;no full-rate disk transcript/image dump.120sample cap and one per60source
frames does not throttle native render submission. File checksums use bounded
native`asset_hash.exe`,not Python image-byte loops on the live-service GIL.

Other corrections before finalqualification:explicit shared-memory alignment
padding;presentation mayinitialize before semantic PIDclaim;nonblocking table
read miss must not immediately rebind light context;offline historical light
replay follows explicitly synthetic rebind;backend admits queued assets while
waiting for a retired scheduling anchor,avoiding rebind/admission deadlock.
No detour/calling-convention redesign or unproven engine-field substitution.

Client original/copy SHA256 both
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Copied proxy SHA256
`E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7`.
Original/accepted installation untouched;all preparation used standalone fixtures.

Useful logs,manifests,raw observations and original source captures preserved.
Nine exact completed fixtures054818,055047,055405,055554,055931,060337,060504,
061042,061206 generated root binaries/textures compressed with existing
`archive_fixture_binaries.ps1 -PartialGeneratedInputs`,everyarchive entry
decompressed/hash-verified before exact generated-file removal. This compaction
flag preserves failed/partial history;does not downgrade passed final fixtures
or promote failed ones.739,869,368generatedbytes→61,842,148archivebytes,recoverable
under`artifacts/remix-runtime/archives/*-return-fixture-binaries.zip`;individual
`binary-archive.json`receipts retained. Smaller second-asset derivatives remain
available for inspection. Totalartifact inventory11,293,274,781bytes<20GBcap.

### Exact changed files

Created:

- `docs/reconnaissance/d3d9-retained-multiship-contract.md`
- `docs/reconnaissance/d3d9-retained-multiship-probe.md`
- `docs/reconnaissance/evidence/20261022-d3d9-retained-multiship.json`
- this Run113record
- `tests/d3d9_multi_scene_tests.cpp`
- `tests/test_d3d9_multi_scene.py`
- `tools/d3d9_proof/build_multiship.ps1`
- `tools/d3d9_proof/multi_asset_hash.cpp`
- `tools/d3d9_proof/multi_scene.py`
- `tools/d3d9_proof/multi_scene_fixture.py`
- `tools/d3d9_proof/multi_scene_runtime.h`
- `tools/d3d9_proof/multi_scene_wire.h`
- `tools/d3d9_proof/start_d3d9_multiship_session.ps1`
- `tools/remix_runtime/multi_scene_relay.py`
- `tools/remix_runtime/qualify_multiship.py`

Modified:

- `docs/HANDOFF.md`(older checkpoints preserved)
- `tools/d3d9_proof/d3d9_direct_host.cpp`
- `tools/d3d9_proof/d3d9_replay.cpp`
- `tools/d3d9_proof/game_output_writer.h`
- `tools/d3d9_proof/live_owner_input.h`
- `tools/m1_component/m1_live_scene.h`
- `tools/remix_runtime/d3d9_game_receiver.h`
- `tools/remix_runtime/live_owner_timing.py`
- `tools/remix_runtime/return_fixture.cpp`
- `tools/remix_runtime/run_return_fixture.py`
- `tools/remix_runtime/run_return_game.py`
- `tools/remix_runtime/scene_frame_buffer.h`
- `tools/remix_runtime/source_timing_fixture.h`

Additional reviewed source:`source_timing.h`,`game_output_wire.h`,
`synchronized_frame.h`,`owner_rebind.py/.h`,`live_owner_decode.h`,
`live_light_binding.py`,`direct_lights.h`,`material_binding.py`,
`scene_bundle.py`,`remix_live_lights.h`,fixture/qualification/archive workflows.
No requirements/config baseline/README/accepted artifacts modified.

Native build commands listed earlier plus`build_persistent_scene.ps1` and
`build_synchronized_buffer.ps1`;Python`-m unittest discover -s tests -p test_*.py`.
Final receipt from`qualify_multiship.py --fixture
artifacts/remix-runtime/runs/20261022-061042-924464-return-fixture`;matching early
fixture separately verified with`qualify_multiship.inspect`. Exact current
source/binary/config locks live in ignoredqualification receipt and fixture
results. Changing code/build/config invalidates gate;do not hand-edit receipts.

Runtime limitations:actual multi-model SFC placement/gameplay pending,first
sponsor test keeps ships alive. Actualdestructor and removal of all retired
Remix pixels,deformation/native alpha/effectsoverlap,stress/allmodel coverage
remain unqualified. Protocol alias/reuse tests are not universal runtime proof.
No original suppression,fullscene replacement,appearance tuning,newarchitecture,
helper,agent,commit orpush. New source changes can stale legacy source-locked
receipts;refresh their own fixtures before using legacy launcher again.

Final Git:HEAD remains startingd40f8f2,branchunchanged,indexempty;13trackedfiles
modified and15newversionablefiles,all unstaged/uncommitted. Generated outputs
ignored. No active game/owned renderer/worker/mapping survives;no session to
reattach afterrestart. Next exact action:launch prepared multi-ship script from
the established elevated parent and perform the two-model aligned-overlay test.
