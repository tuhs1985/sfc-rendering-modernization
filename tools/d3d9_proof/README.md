# Plain D3D9 offline proof

## Optional asynchronous-material checkout (Run194)

The normal command keeps its existing1.5.2 runtime. Add `-AsyncMaterialCheckout`
to `start_d3d9_multiship_session.ps1` for the separately qualified1.6.1 host/header,
parallel base-first assets and completed single-file material publication. Do not
combine it with `-ExperimentalParallelAssets` or Test mode. Settings and original
ship drawing stay unchanged; this is an additive gameplay checkout, not replacement.
The separate `qualify_async_material.py --initial <fixture> --late <fixture>` gate
requires the normal qualification plus actual integrated candidate fixtures, exact
captured content matching, paired output, full-interval delivery and cleanup. It
does not overwrite the normal receipt. Diagnostics from Run193 cannot certify it.

Use the usual two-ship skirmish, briefly keep both ships visible, switch cameras,
move/turn, optionally launch a shuttle/fighter, and exit on the existing request.
No magenta/on-off cycle or manual timestamps. The unchanged90-second tactical and
285-second total workflow limits apply. Omit the flag to return to the normal path.
No Toolkit startup, imported template or SDK mesh submission is used.
See [Run194](../../docs/runs/2026-10-25-codex-async-material-checkout.md) and the
[probe definition](../../docs/reconnaissance/probes/D3D9-ASYNC-MATERIAL-001.md).
Offline initial600/600 and late596/600 are not a live-game or sub-two-second PASS.

## Owned initial-pixel upload (Run188)

The shared Renderer can create documented single-mip SYSTEMMEM staging textures
from prepared BGRA pixels. InitialData moves the source vectors into renderer
ownership, destroyed after its COM references. UpdateTexture/geometry/material
identities are unchanged. A classic-device D3DERR_INVALIDCALL uses the old staging
method once per Renderer; other errors propagate. Native x86/x64 classic/Ex,
reset/recreation, exact pixels and source ownership are tested.

Normal policy stays old staging. The existing explicit
`-ExperimentalParallelAssets` checkout selects initial data for bootstrap and later
assets. Native console/report counters prove actual acceptance/fallback. Offline
`--texture-upload staged-lock|initial-data` supports a matched comparison; there is
no new gameplay switch. Run188 Remix controls report107fast uploads,0fallback.
Startup and late-material returned-image gaps remain; do not claim seamless/sub2s.
See [Run188](../../docs/runs/2026-10-25-codex-owned-initial-textures.md).

## Renderer-thread admission during waits (Run186)

The experimental parallel relay services ready assets on the existing renderer
thread between bootstrap Presents and during query/fence/output-ACK waits. Real
completion, ownership and deadlines remain. Normal policy explicitly disables it.
Offline controls can select `--asset-admission-service on|off` with
`--parallel-assets`; actual activation and two bounded startup timing records are
retained. Native23state/pixel/thread checks pass. Material-file sharing conflicts
retry on a later coordinator cycle with a five-second bound.

This removes an admission dependency, but first matching output did **not** improve
in the measured pair:5.33s off/5.67s on. Late-material returned-image gaps remain.
An admission can still block in resource creation/upload: one closing run measured
1.48s there. First matching output does not imply every pending ship is ready.
The pre-existing shared diagnostic validation counter is now thread-local.
No new sponsor run is required merely to verify this change. See
[Run186](../../docs/runs/2026-10-25-codex-renderer-admission-service.md).

## Base/enhancement phases (Run184)

The explicit experimental parallel path now admits the original-textured base
without waiting for enhanced images; enhanced pixel generation starts independently
of bundle completion. Ready bases publish before enhancement filesystem work.
Missing secondary inputs report an enhancement partial while base remains eligible.
Same existing worker checksum DLL now supplies the exact catalog FNV64 and pinned
Remix XXH3 in memory; rebuild with `build_mesh_checksum.ps1` after preparing the
existing pinned xxhash.h dependency. No producer helper launch/repeated file hash,
and consumer integrity checks/wire format unchanged. This adds no DLL to SFC.

Full streaming tests still show returned-layer gaps during late updates, even when
the subsequent600frame window passes. Normal default is unchanged. Sponsor's
`-ExperimentalParallelAssets` opt-in remains available; it is not a seamless
enhancement-streaming qualification. See Run184 in the newest handoff.

## Isolated parallel preparation / progressive materials

Run180 adds dependency-driven geometry/image tasks and individual material-group
publication to the existing ordinary-D3D9 standalone fixture. Append
`--parallel-assets` to the performance multi-ship/prewarm/startup-profile fixture.
Add `--parallel-material-delay-ms 5000` to qualify delayed consumption. This mode
rejects other candidate/API/loading-policy experiments. Actual gameplay requires
the separate explicit sponsor-checkout option described below.
Geometry/image inputs are prepared once; final texture/material bytes match the
accepted reference. CPU publication does not establish GPU consumption.

**Not gameplay-promoted:** delayed material application yielded538/600 delivery,
below the existing540 minimum. The existing gameplay path remains qualified.
Sponsor subsequently authorized an experimental checkout: use the normal
`start_d3d9_multiship_session.ps1` with `-ExperimentalParallelAssets`. It must print
`EXPERIMENTAL PARALLEL ASSETS ENABLED`. Manifest/result record the option; absence
of the switch keeps stable behavior. This opt-in is not default promotion or a
claim that the known late-update delivery gate passed. See Run182 for test actions.
See [Run180](../../docs/runs/2026-10-25-codex-parallel-progressive-assets.md)
for implementation, bounds, timings, archive recovery and exact next action.

## Performance baseline

SFC's freshly captured mesh/resource associations are the source of truth. The
normal multi-ship launcher, direct gameplay CLI and live relay default to
performance mode. Use launcher `-Mode Test` for diagnostic source/pixel comparisons.
Offline exporter/material helper defaults remain test mode for deliberate evidence
work; the live relay passes performance explicitly.

Performance material preparation does not rehash/recompare the already consumed
mesh packet and references or compare primary images against the intermediate
manifest. Test mode retains these checks and upload-pixel comparisons. Required
Remix texture hashes and content-addressed output names are identities, not checks
against a prepared ship; they remain. Bounds, packet/owner identity, paths, output
synchronization, material-identity conflicts and cleanup checks remain in both.

Decoded original images are reused within one performance preparation with a
32MiB LRU per worker (four workers,128MiB total cache allowance). Derivative keys
include image content, role and applicable settings; reuse occurs before encoding.
Caches expire at preparation completion. No persistent cross-run trust/cache.
This is not a sub-two-second startup claim; see Run179 in the handoff.

## Isolated stock1.6.1 initialization qualification

The normal gameplay runtime is still1.5.2. The standalone return fixture accepts
`--runtime-candidate 1.6.1 --candidate-asset-loading synchronous` with
`--multi-ship --prewarm`. This changes only NVIDIA's
`rtx.initializer.asyncAssetLoading=False` (matching child environment0); it does
not disable preparation workers, shader async or texture streaming, and is not a
GPU-residency readiness signal. Defaults remain `inherit`; the switch is rejected
without the candidate and cannot combine with `--loading-policy` overrides.

Use the verified isolated candidate host built by `build_candidate_runtime.ps1`.
For the standard larger offline fixture, run the project Python with:

```
tools/remix_runtime/run_return_fixture.py --multi-ship --multi-ship-resources
--prewarm --startup-profile --pipeline-mode performance
--runtime-candidate 1.6.1 --candidate-asset-loading synchronous
```

Add `--multi-ship-late-asset` for incremental publication. Omit both candidate
options for the unchanged1.5.2 control. Keep lines on one invocation. Neither
mode launches SFC. Result runtime_candidate.asset_loading plus
gpu/loading-inputs.json and the runtime log record requested/effective policy.
Candidate results cannot certify the normal gameplay pin. See
[Run150](../../docs/runs/2026-10-24-codex-initial-loading-material-workaround.md)
and current handoff for qualification outcome and packaged-source caveat.

**Retired dependency (2026-10-24):** historical `inspect_intercept.py` uses USD
libraries from the retired portable Toolkit. Restore the verified old Toolkit
before replaying that inspection, or separately qualify a managed-library
migration. The current D3D9 gameplay path does not use that parser or Toolkit.
See [rollback record](../../docs/runs/2026-10-24-codex-toolkit-cleanup.md).

**Current path:** the live in-game experiment now uses this D3D9 adapter with
persistent FCA tracking and a synchronized GPU return buffer. See the
[project pipeline overview](../../README.md#how-it-fits-together) and newest
[handoff](../../docs/HANDOFF.md). The sections below preserve the individual
offline/interception gates and their then-current limitations; do not treat
their original unlit/offline-only scope as the latest integrated status.

No SFC launch,game modification,Remix DLL/SDK,Toolkit,USD ingestion or live bridge.
See [contract](../../docs/reconnaissance/scene-contract-v1.md) and current HANDOFF.
Source assets are bounded historical runtime captures;model filenames are labels,
not geometry loaded from installed MOD files. Original image files alone are read
from the preserved copied test installation. No appearance parity claim.

Build with modern PowerShell and installed VS2026 x86 tools:

```powershell
pwsh -NoProfile -File tools/d3d9_proof/build.ps1
```

Explicit bounded execution with the project's Python3.12/Pillow/NumPy environment:

```powershell
python tools/d3d9_proof/run_offline.py --execute
```

The runner has an explicit local capture fixture path;new checkouts need the
ignored original evidence and owned test textures. Missing evidence is a blocker,
not permission to reconstruct geometry from MOD files. Native executable accepts
one derived replay directory. It creates only an owned hidden window and ends.
Native cases45s timeout;complete proof180s;logs2MiB/case;outputs128MiB/run;128MiB
aggregate reservation inside sponsor20GB ceiling including existing return outputs
(raised by sponsor2026-10-20;per-run bounds unchanged).
Reserve includes no new whole-game copy or runtime download. These are offline
limits,not claims of real-time performance. Tests read back GPU images deliberately.

The build also produces`d3d9_startup_probe.exe`. `python tools/d3d9_proof/startup.py
--execute` records adapter/monitor/session/windowed format checks without loading
assets or changing Windows state. The ordinary proof automatically runs this
20s/1MiB admission first. An active input desktop different from the thread's
desktop yields`BLOCKED_INACTIVE_INPUT_DESKTOP`:wake/unlock Windows normally and
retest;do not disable security or switch desktops. Device availability alone does
not pass the reference render/texture/reset tests. See Run71 and approved gated
execution plan before progressing to normal Remix output or SFC integration.

Outputs under ignored`artifacts/d3d9-proof/`:source-hashed result,scene manifests,
native logs and diagnostic PNGs. Do not publish captured geometry/images/binaries.
After analysis,`archive_offline.ps1 -RunDirectory <exact-completed-run>` recoverably
compacts generated binary fixtures/readbacks after decompressed SHA256 verification;
metadata/logs/PNGs remain. `-AllowPartial` required for a completed failed run.
Restore a named generated ZIP into its corresponding exact run before reanalysis;
never overwrite newer files. Original captures remain untouched.

Expected success:`OFFLINE_PLAIN_D3D9_TWO_ASSET_PASS`,not normal Remix interception,
live integration or renderer-independent gate closure. Known synthetic controls
are distinguished from captured Klingon/Federation assets. Original shader-based
replacement experiment remains parked,unchanged and uncommitted.

## Normal Remix interception — separate offline gate

`build_intercept.ps1` compiles the SAME renderer with `SFC_D3D9_REMIX_PROOF`.
`python tools/d3d9_proof/run_intercept.py --execute --asset 4` uses the pinned
1.5.2 x86 client/x64 bridge from the SHA-verified local release ZIP. Asset3 is
the cruiser;`--capture-frame 96` captures its later coherent source snapshot.
This is ordinary D3D9 interception,NOT public SDK mesh registration. No game,
Toolkit ingestion,proxy installation or sponsor appearance settings are used.

The existing owned-process guard limits the whole bridge tree to90s,128MiB
scratch and2MiB console. Private runtime generated extras64MiB/logs32MiB;
source release binaries are frozen inputs. Combined outputs retain sponsor20GB
ceiling with128MiB reservation;finished outputs are compacted before more work.
The native replay draws at least120 and at most600 bounded presents,waiting
for the runtime's `End USD export` marker before closing. These are offline
test limits,NOT real-time performance results. Missing marker is failure.

`python tools/d3d9_proof/inspect_intercept.py <run> --source-index 0` compares
actual captured meshes/materials/images/camera with the original replay.
Use index2 for capture96. The installed Toolkit's USD Python libraries are used
READ-ONLY as a parser;the Toolkit application is never launched. See Run70 for
its exact local dependency path. All positions/normals/corner UVs/groups and
decoded primary images must match. USD export V/winding conventions are handled
only by analysis;source UVs and D3D9 uploads remain untouched.

Current camera result is PARTIAL:the runtime USD exporter omits verticalAperture.
The report separately records raw error and an analysis-only reconstruction from
the source viewport aspect. This does NOT fix the actual runtime or establish
complete independent camera/presentation parity. `NORMAL_D3D9_REMIX_CAPTURE_MATCH`
is scoped evidence,not overall gate PASS. Runtime common-device disposal warnings
also remain unresolved despite zero client refs and normal process-tree exit.

`archive_intercept.ps1 -RunDirectory <exact-run>` preserves logs/manifests/results
and ZIP-compacts generated replay binaries,capture assets and single screenshots
only after SHA256/decompressed-byte verification. Restore the exact named ZIP
to its corresponding run for reanalysis;never overwrite newer source captures.
Generated proprietary assets must remain ignored/unpublished.

Run72 clears native startup/reference:awake Default desktop restores hardware
capabilities;final native023149-082425 PASS. Old inactive-desktop failures remain
historical,not a reason to change driver/geometry or bypass admission.

`build_capabilities.ps1` verifies pinned header and compiles x86 interface probe;
`python tools/d3d9_proof/probe_bridge_api.py --execute` owns/bounds the bridge tree,
enables API only in private effective`.trex/bridge.conf`,records capabilities and
restores prior config. No SDK mesh calls. Current initialized shipped interface
has no output-copy/external-image/picking entrypoints:Run72 Gate2 was BLOCKED.
Subsequent sponsor approval of the64bit alternative is recorded below;this does
not bypass the remaining output/timing gates or authorize immediate gameplay.

## Approved direct64 ordinary D3D9 alternative — Run73

Run74 adds standalone x86 output receiver:build_receiver.ps1 then build_direct64.ps1.
Use run_direct64.py --execute --asset 4 --receiver normal (or asset3for FCA).
Fault modes:slow,disconnect,exit-acquired,stale-ack,invalid. Logs/byte comparisons
stay in exact run directory. All are OFFLINE held snapshots,not live delivery.
Source-state/scene hashes and generation/ACK wire in output_channel.h;no geometry
registration through SDK. archive_intercept.ps1 also compacts receiver raw32data
after hash verification. Original captures unchanged. See Run74for limitations.

Sponsor approved the64bit helper. Build`build_direct64.ps1`,then
`python tools/d3d9_proof/run_direct64.py --execute --asset 4` (or3).
`--synthetic` selects independent known controls,NOT a game asset.
Optional`--diagnostic-capture` saves one capture/screenshot;
`--backbuffer-diagnostic` adds offline ordinary backbuffer checks. Both defaultOFF.
Host uses SAME parser/Renderer via types-only compile guard,no SDK mesh calls.
Output API initializes/registers ordinary device,copies shared GPU textures and
owns final registered-device shutdown;never duplicate that teardown via COM aliases.

`analyze_direct64.py <case>` checks actual returned color/depth/picking against
independent native oracle. Actual full-frustum/.5sample convention is explicit,
not a captured matrix/UV change. Picking0 is not sufficient coverage;isolated
depth/sentinel coverage only. See experimental output contract and HANDOFF.
Run74/75 independently qualify a separate x86 receiver for bounded offline cases;
these proofs do NOT qualify live scheduling,lifetime or appearance. Never copy offline sleeps/waits/readbacks
into SFC. `archive_intercept.ps1` now accepts only exact owned direct64-runs as
well as legacy runs and archives generated payloads with decompressed hashes.

Run75 options:--single-present retains24startup presents,then only1per changed
snapshot. --paced-frames120or300 cycles recorded snapshots under artificial60Hz
demand;NOT original recorded timing. QPC frame-timing.csv includes all steady
rows,including diagnostic stalls. --timing-only requires paced mode and saves NO
pixels;result labelled TIMING_RECEIPTS_ONLY. analyze_schedule.py reports deadline
misses independently of sampled pixel analysis. --output-size WIDTH HEIGHT changes
only consumer target extent;large all-frame readbacks rejected by scratch budget.
Wide/tall camera controls remain independent. All modes are standalone/offline;
do not run SFC or treat ordinary offline waits as production callback code.

## Read-only source lead check — Run76

Prepared source_timing.h/add-on observes validated first/last source QPC versus
Present/overlay,not a new rendering backend. Build/requalify OFFLINE with
python tools/remix_runtime/qualify_source_timing.py --execute after native builds.
Source/binary receipt is exact;do not rebuild during gameplay setup.
Sponsor entry:start_source_timing_session.ps1 from existing elevated parent.
Normal-looking two-ship90second fixture,no pause,both ships visible;beeps provide
settling/prep/camera/movement/exit instructions. No Remix runtime or image display.
See docs/reconnaissance/probes/D3D9-SOURCE-TIMING-001.md and Run76. Source lead
remains UNKNOWN until actual game data;no live additive delivery claim yet.

## Current corrective additive test — Run82

Historical sections above are superseded by docs/HANDOFF.md and Run82. First
actual additive run was mostly absent due missed source-frame deadlines. Current
worker-completion correction passed588/600 offline frames;not yet gameplay PASS.
start_d3d9_offset_ship_session.ps1 uses existing elevated parent/test copy. No
original suppression,SDK geometry,stale-image hold or Toolkit. Current fixture
explicitly selects Federation FCA in offset_ship.toml,not first enemy/native player
flag;missing/duplicate configured owners reject. Keep the same player cruiser.
Four appearance TOMLs remain frozen. Source/binary/config changes invalidate the
qualification;no rebuild during sponsor setup. See probe D3D9-ADDITIVE-001.

### Remix base-image mapping (Run197)

The progressive fallback now applies `remix_coordinates` when deriving its first
BGRA texture upload, before admission. Enhanced color/emission/roughness DDS use
the same backend image-origin policy. Material hashes are computed from the
actual adapted base bytes. Captured positions, normals, UVs, triangle/group order,
original images and their provenance hashes remain canonical. Neutral scene
export/plain D3D9 replay do not implicitly apply this Remix conversion; a future
D3D12 backend must define its own requirements. No geometry-axis/face repair.

Base-first appearance is independent of enhanced-material installation. The live
Run196 missed-update case remains open; file publication, returned-frame counters
and native asset ACKs are not material-ready acknowledgements. Do not restore the
rejected metadata-touch workarounds or enable private renderer warm-up in normal
launchers without separately demonstrated correctness and performance.

### One-time material startup priming (Run199 checkout)

`-AsyncMaterialCheckout` now exercises the existing private renderer startup once
before declaring renderer readiness. It then waits without further private draws.
Enhanced-library publication cannot race this preparation; base asset delivery is
independent. No fixed material grace window or notification retries. The normal
runtime without the opt-in remains separately qualified.

Test with the familiar two ships first; inspect material appearance before adding
a shuttle, then exit on the usual request. Original ships remain visible and the
same corrected camera-left copies/settings are used. This is a priming experiment,
not a live fix claim. Existing menu/workflow time bounds remain. Idle tests found
stable private allocations/handles but roughly two cores of pre-existing renderer
CPU use with and without priming; see Run199 for memory/cleanup limitations.

### Material revision compatibility (Run200 checkout)

Live startup priming did not fix late roughness. Standalone NVIDIA roughness views
and the packaged OpenUSD25.11 library confirmed whole-second Windows timestamp
precision: two fast USD revisions can appear unchanged despite OS notification.
The opt-in checkout assigns distinct revision timestamps BEFORE atomic exchange.
No sleep, repeated touch or base-display barrier. Logical file time may lead
wallclock; performance measurements still use QPC.

Only the Remix/USD publisher applies this policy. Canonical data, initial mapping,
material values, normal1.5.2 and future adapters stay independent. Read Run200
before changing this again; rejected timer/touch experiments are not the fix.
The same `-AsyncMaterialCheckout` launcher is ready for gameplay confirmation
without requiring a shuttle to activate enhanced maps.
