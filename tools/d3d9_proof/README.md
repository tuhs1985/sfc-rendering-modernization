# Plain D3D9 offline proof

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
