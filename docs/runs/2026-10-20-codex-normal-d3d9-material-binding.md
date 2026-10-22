# Run81 — normal D3D9 material policy and offset ship (READY FOR SPONSOR TEST)

2026-10-20 sponsor authorized proceeding with automatic,global-default policy
applied to each fresh ship material. Continue toward offset-ship insertion using
existing lights/materials/image/quality settings;no geometry SDK rollback.
HEADd29111f7,index0,prior dirty work preserved. Fuel Guard attached via trusted
hook. No game launch,helper/agents,staging/commit/push. Read HANDOFF,Run80,
ordinary renderer,existing appearance adapters and pinned vendor source.

## Confirmed material relationship

Pinned1.5.2 AssetReplacer separates external SDK materials from normal mod material
replacements. Normal replacements use `/RootNode/Looks/mat_<texture hash>`.
Downloaded limited vendor implementation/header files into ignored dependency
cache only;MIT notices retained. Existing pinned runtime/header not changed.
Native texture helper uses pinned XXH3 over tightly packed uploaded BGRA8.
All5fresh KFF images exactly match independently saved runtime capture identities:
86F7A1EDDD1756B2,FE1F4010BB5DF756,A9C75CFFC5A30DF9,585F568EA417F2AE,
20A79E887A64238E. No game pointers/filenames used as runtime texture hash guesses.
Hash header SHA256 FDBF70C5F5CCFFED18A1CF82B635799CA5128743DB8746076AA136A5AA4BC467.

`material_binding.py` emits native Remix material-only USDA and own DDS images
from fresh packet associations. Does not emit geometry,SDK meshes or Toolkit
imports. Preserves raw packet,indices,UVs,camera andoriginal assets. Reuses existing
roughness formula and provisional primary*secondary emission;does not promote
that artistic policy to exact native material fidelity. All4sponsor TOMLs unchanged.
Initial width/pitch guard was subsequently disproved and removed;see final
adjudication below. Reject negative USD-clamped anisotropy,
same-primary/different-pair conflicts,changed source/images and safety-limit excess.
These are explicit current coverage limits,not a universal any-model claim.

## Offline evidence so far

- Initial fixture212121validates startup but ship only10pixels;A/B inconclusive,
  retained PARTIAL. Switched only to an existing captured useful camera view,
  not a fitted or altered camera.
-212218normal material A/B passed338covered pixels,197changed. Zero SDK mesh calls.
-212437material+image/quality A/B passed338covered,178emission-changed pixels,
  mean19.119RGB units,319image/quality-changed pixels. Native runtime options
  accepted existing controls;GPU-only post-grade preserves depth/picking.
-212733material+image/quality+historical-light replay fixture passed;inspect final
  result for exact light difference. This is explicitly OFFLINE historical native
  directions with synthetic identity/time,NOT proof of live light synchronization.
- All fixtures under artifacts/d3d9-proof/material-runs;normal owned exit/API
  shutdown0,warning40retained. First3generated payloads recoverably zipped using
  archive_material_fixture.ps1,all decompressed SHA256s checked before exact deletion.
  Raw source captures,manifests,logs and material layers retained.10GB cap unchanged.
-350Python tests PASS;native hash helper anddirect64host builds PASS. Receiver
  timeout correction fromRun80 preserved. Old gameplay qualification remains stale.

## Implementation checkpoints / remaining

Added texture_hash.cpp,build_material_binding.ps1,material_binding.py,
qualify_material_binding.py,visual_controls.h,direct_lights.h,light_fixture.py,
archive_material_fixture.ps1,test_normal_material_binding.py. Modified direct64
host/build only to opt in existing image/quality/light adapters;default remains OFF.
Host reads files only on its worker,never SFC callbacks. Native source/pose hooks
and original rendering untouched. Native light replay uses SDK LIGHT functions,
not SDK geometry submission. Need inspect final offline light receipt/revalidate.

Important discovery for game-side wiring: normal Remix picking values include0
for a real material as well as background. NEVER discard all picking0pixels or
assume normal picking IDs equal semantic owner. For isolated one-owner output,
qualified depth sentinel(-1234background versus finite0..1coverage) can generate
a backend-specific owner-coverage mask,subject to independent GPU pixel tests.
Do not change existing SDK compositor semantics globally.

Exact next action:finish bounded shared-output pool/game consumer with exact
current raw owner/frame/hash/sequence admission and GPU-fenced leases. Keep source
publisher and output worker nonblocking with respect to SFC;do not ACK a displayed
surface before its GPU work finishes. Preserve current native-depth correlation
and graphics state. Live native lights must be fresh same-session observations,
never substitute offline light replay. Then qualify enabled/disabled/failure,
offset/depth/UI/resource bounds and source/binary hashes before sponsor launcher.
No additive game image enabled and no launcher ready at this checkpoint.

## Later implementation checkpoint (still NOT GAMEPLAY READY)

212733final A/B:338covered pixels,197emission-changed,319image/quality-changed,
253light-changed. All4finished material fixtures'generated images/texture copies
are now hash-verified recoverable ZIPs;logs/manifests/material layers/source packets
retained. Rebuildable historical vendor example d3d9.dll190,838,384B,exact same
SHA256 F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F as
still-present pinned runtime,was archived/decompressed-hash-verified then removed
ONLY from artifacts/remix-runtime/runs/20261017-042137-854-vendor.
Recover from archives/20261017-042137-854-vendor-runtime-copy.zip(63,746,067B).
No dependency/client installation removed or modified. This releases~127MB within
the existing10GB counted cap;do not raise cap to accommodate copied binaries.

New game_output_wire.h/writer.h reserve576B at11MiB+128KiB (above raw-owner store,
below12MiB source timing),2GPU slots,explicit full source session/sequence/hash,
content identity and fixed world offset. Never overwrite acquired slots. x86
receiver27wire+18timing+21new pool checks PASS;direct64andmain add-on builds PASS.
Game-mode receiver disables continuous readback/private verification staging;
producer also omits unused staging in timing/live mode to respect128MiB GPU cap.
Raw source/frame/pose is unchanged;separate diagnostic parent offsets model X.

normal_coverage.h derives opaque isolated-owner coverage ONLY from qualified
finite0..1depth against negative background sentinel,not RGB or ordinary picking.
Needs actual pixel qualification. Existing SDK compositor defaults unchanged;
new native-screen option maps1:1pixels and scissors to native tactical viewport.
d3d9_game_receiver.h imports GPU handles on owned worker,checks GPU/resource/
source identity,draws only matching current publication and retains each lease
until nonblocking GPU query completes. No stale-image hold. Resizes/device loss
conservatively stop/hide this generation;automatic recovery is not yet qualified.

LiveOwnerRelay optional additive branch prepares frozen current material/image/
quality settings,live native light adapter(no replay fallback),actual output pool
and offset from captured mesh bounds. Offline-only replay remains explicitly
separate. run_return_fixture additive path is WIP:source must publish before known
8xMS depth draw;new pool telemetry/failure and original-state checks must pass.
Actual SFC runner/start wrapper/qualification still to finish. Do not launch SFC.

## Final authoritative execution result — 2026-10-20

READY FOR SPONSOR OFFSET-SHIP TEST, not gameplay PASS. All earlier WIP/no-launcher
statements in this record are historical. No SFC launched by Codex this run.
Authority remains approved additive execution plan; original ship NOT suppressed.
M1 CONTINUES; no requirements amendment, architecture change or maturity claim.

### Additional evidence and corrections

CONFIRMED, pinned source plus independent runtime texture captures: tightly packed
single-mip BGRA rows already satisfy four-byte pitch alignment. All56 FCA textures,
including8/32-wide images, exactly match saved runtime DDS pixel identities. All5
KFF matches remain valid. Rejecting width%64 was an erroneous conservative guard,
not a native-format limitation. Batch hash helper avoids one process per image.
Typed `uchar inputs:filter_mode`/wrap settings replace ignored unprefixed fields.

CONFIRMED offline: ordinary D3D9 material-only USDA binds existing texture policy.
No USD geometry, SDK mesh registration, offline OBJ or Toolkit ingestion in live
path. Secondary contribution remains provisional primary-weighted emission, not
newly proved native glow fidelity. Negative native-USD anisotropy remains rejected;
current sponsor setting+.5 accepted. Same-primary/conflicting-pair cases explicit.

Final actual full-event-proxy fixture:
`artifacts/remix-runtime/runs/20261020-222142-946534-return-fixture`.
Runtime/fixture exits0, owned GPU job exit0, API shutdown0, no remaining processes.
Fresh replayed FCA owner3/revision3; asset SHA256
`3aa4a80fa4eadfdabee6632e0c8fd05476e3b2c3787e25cbc271c4dd95863a36`.
World offset[-23.8465843,0,0], computed as-1.5 times captured maximum axis span.
120 exact-current backbuffer image submissions; independent one-shot readback
18,596 changed pixels, original border untouched. State errors0, resize and device
recreation exercised.1,206 source records/603 exact Present-overlay pairs, no
invalid/dropped/wrong-thread events.435 completed output transfers, one mismatched
light frame omitted.254 pool publications,21 unclaimed replacements,110 stale
image rejections,0 acquired-slot saturation/invalid/resource/depth errors.120
nonready GPU-query polls are counters, not waits. Source preparation17.985s in this
fixture; not actual game preparation latency. Source lead deliberately synthetic
~16ms. Replayed lights are explicitly NOT live-game lighting evidence.

Earlier partial fixtures retained:214708 wrong pitch guard;214948 erroneous shared
32MiB image/log cap;215153 limited-event proxy lacked depth observations;215916
actual pixels but a newer-light/older-owner join aborted the host. Corrected by
using existing qualified full-event proxy in test copy, separate128MiB image and
32MiB log budgets, and skipping mismatched light frames rather than aborting or
inventing correspondence. Output sequence now counts actual transfers separately.
220203 was an earlier successful combined fixture; final222142 additionally tests
current raw-source-stopped guard, cleanup RAII and watchdog build.

### Contract, controls and limits

See [contract](../reconnaissance/d3d9-additive-output-contract.md) and
[probe](../reconnaissance/probes/D3D9-ADDITIVE-001.md). No game callback allocations,
file IO, CPU screenshots, explicit waits or worker calls. Importing resources is
worker-owned; leases released only after nonblocking GPU completion. Exact session,
owner epoch/revision/frame/source hash/sequence required. Retired/invalid/stale
source hides output. Isolated-owner coverage comes from qualified depth/sentinel,
not black-key/picking0. Native viewport scissor and scene depth remain required.
Resize/device recreation hides this generation; automatic recovery not claimed.

90s formal tactical window starts after first actual matching image, with up to30s
preparation. Internal source/controller watchdog120s, input110s, GPU job120s,
receiver130s allow that preparation and normal teardown; outer prepared workflow
still<=285s/five minutes. This does NOT authorize a120s formal capture. One owner,
asset revision; no original suppression, stale-image hold or buffering. Settings
are frozen snapshots, not a tuning session. Existing four sponsor TOMLs untouched.
Two receiver surface triplets plus producer/grade~82,944,000B, below128MiB output
budget; semantic mapping16MiB, new pool576B. Images128MiB; logs32MiB, warning16MiB.

### Files created/modified in this increment

New `tools/d3d9_proof/`: `texture_hash.cpp`, `build_material_binding.ps1`,
`material_binding.py`, `qualify_material_binding.py`, `archive_material_fixture.ps1`,
`visual_controls.h`, `direct_lights.h`, `light_fixture.py`, `live_light_binding.py`,
`game_output_wire.h`, `game_output_writer.h`, `normal_coverage.h`,
`start_d3d9_offset_ship_session.ps1`.
Modified there: `d3d9_direct_host.cpp`, `build_direct64.ps1`, `output_receiver.cpp`,
`output_channel.h`, `build_receiver.ps1`, `live_owner_input.h`.
New `tools/remix_runtime/`: `d3d9_game_receiver.h`, `additive_qualification.py`;
modified `live_owner_timing.py`, `run_return_fixture.py`, `return_fixture.cpp`,
`return_addon.cpp`, `ship_triplet_compositor.h`, `run_return_game.py`,
`start_return_image_session.ps1`, `archive_fixture_binaries.ps1`.
New tests:`test_normal_material_binding.py`, `d3d9_game_output_tests.cpp`;
updated `d3d9_output_wire_tests.cpp`, `test_remix_visibility_cli.py`.
Docs:this record, HANDOFF, additive plan status, new output contract/probe and
curated preparation receipt. Earlier dirty Run69–80 files preserved, not claimed
as newly reviewed implementation. Proprietary/runtime images and vendor caches
remain ignored. No helper project changes.

### Validation and reproducibility

- `build_material_binding.ps1`, `build_receiver.ps1`, `build_direct64.ps1`,
  `build_return_probe.ps1`, `build_light_discovery.ps1` PASS.29 output-wire,
  18 timing,21 pool checks;37 return,13 expanded,14 broad,22 calibration checks;
  native light core9 and observer13 on bothx86/x64, actual observer qualification.
- `python -m unittest discover -s tests -p test_*.py`:353 PASS. First sandbox
  attempt failed181 tests on sandbox Temp PermissionError; rerun outside that
  broken temporary-folder restriction passes. Not a product test failure hidden.
- `python tools/remix_runtime/run_return_fixture.py --d3d9-additive`:PASS above.
- `additive_qualification.qualify(final_fixture)` creates ignored source/binary/
  config receipt; result OFFLINE_ADDITIVE_PREPARED_NOT_SFC_PASS. Changing covered
  source, binary or TOMLs invalidates launch. No rebuild during sponsor setup.
- `start_d3d9_offset_ship_session.ps1 -CheckOnly`:read-only preflight PASS, no
  renderer/game started. Parser checks and `git diff --check` PASS.
- Accepted and copied clients unchanged SHA256
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.

### Recoverable storage and remaining uncertainty

Final fixture generated binary/image inputs archived to
`artifacts/remix-runtime/archives/20261020-222142-946534-return-fixture-binaries.zip`,
SHA256 `5C1539A712E37E1B4D4403539C5B77BFF242D0641FD44931CDFE34CFA38DE604`,
199 entries/6,859,515B. Every decompressed file hash verified before deleting exact
generated copies. Same treatment for214948/215153/215916/220203; partial receipts
explicitly do not promote failed results. Logs, manifests, original packet evidence
remain. Four material A/B payload sets and three finished historical private
fixture texture sets020900/021656/022244 similarly compacted; source game assets
untouched. Earlier transient aggregate10,130,110,217B was observed after fixtures;
no cap increase authorized. Compaction restores9,667,896,417B and a192MiB next-run
reservation; new additive fixture preflight now enforces that aggregate reservation.

Vendor warning40 persists; no leak-free claim. Gate3 stable live delivery remains
unresolved: rejected stale output can cause gaps/flicker. This prepared extra-ship
diagnostic measures simultaneous real-game delivery, not a waiver for replacement.
Native light join/current depth/UI behavior need actual runtime corroboration.
No new baseline ZIP was required/requested for this increment; recoverable evidence
ZIPs are not represented as a full repository backup.

Final Git:HEADd29111f7, index empty, all implementation/evidence docs unstaged and
uncommitted, prior dirty files preserved. No SFC/owned GPU processes or persistent
tool sessions left active. No stage/commit/push. Exact next action: sponsor runs
the prepared offset-ship launcher and Codex reviews its new bounded evidence.
