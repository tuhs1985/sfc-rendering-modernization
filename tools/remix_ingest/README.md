# Bounded standalone Remix ingestion

## Current live entry: follow SFC camera (prepared, runtime unverified)

Same start_live_bridge_session.ps1 now builds0.19/protocol2. Separate window uses
live game view/projection/tactical viewport, showing ONLY selected Klingon. Angle,
zoom and placement should agree in that viewport; it does not copy HUD/background/
other ships or reproduce original lighting exactly. Separate view/Frame buttons
are disabled so they cannot override the camera. Keep Klingon visible in SFC,
move camera/zoom, then play normally; exit on two cues. Expect90s tactical recording.
No game appearance changes. [Probe](../../docs/reconnaissance/probes/LIVE-CAMERA-001.md).
--fixed-camera on run_live_bridge.py explicitly selects previous diagnostic; default
is now aligned. Offline launchers unchanged. Numerical checks are NOT a claim
that actual game pixels have already been matched.

## Opt-in live bridge (experimental, not runtime-qualified)

From the established elevated PowerShell parent, use
`tools/m1_component/start_live_bridge_session.ps1`. It builds/tests first, preloads
the separate resident-texture/provisional-lighting viewer, then starts the known
SFC workflow. No new UAC, global graphics changes or picture replacement.
The supported kff ship may be the enemy. Window stays empty until fresh geometry,
five image pairs and owner epoch verify; then follows supplied ship transform.
Camera is fixed, Frame ship is manual; hidden/disconnected is explicit, not an
invitation to reuse old pointers. Play normally, initially hold still, observe
ship movement/turn and briefly move the game camera; exit at two exit cues.

See [probe](../../docs/reconnaissance/probes/LIVE-BRIDGE-001.md) and
[wire/lifecycle contract](../../docs/reconnaissance/live-bridge-contract.md) for
exact2MiB/30Hz/2700update/twoepoch/90s/300s limits and safe cleanup. Defaults and
offline launchers remain unchanged. No model/UV/normal/winding/brightness tuning.
`python tools/remix_ingest/run_live_bridge.py --replay` tests the actual viewer
with saved assets and synthetic movement/retirement/reappearance, NEVER SFC;
replay success is not runtime integration proof. Owner-local channel tests must
run outside restricted sandbox tokens; do not weaken the user-only DACL.

## One-click saved-mesh preview

Double-click `start_mesh_preview.cmd` in this directory. It uses the existing
installed Kit/Remix renderer to open a **separate diagnostic viewer**, not the
normal mod-project workspace. Buttons Angled/Front/Side/Above fit the selected
mesh; Front=+X and Side=+Z were sponsor-qualified for this capture. Above uses+X
as camera-up; no mesh rotated. Close preview button or automatic120s ready/180s
total limit exits only this owned process tree. No SFC launch, new conversion,
on-disk asset edit or routine administrator/PowerShell-policy prompt required.

Reads the exact accepted capture only; fresh scratch copy/anonymous camera+light
session. NRC disabled through process-local environment after a default-mode GPU
fault; job-local bloom off for clear inspection. No settings/renderer selection
for the game. [Probe definition](../../docs/reconnaissance/probes/MESH-PREVIEW-001.md)
records controls, hazards and limitations. `run_mesh_preview.py --smoke` performs
bounded no-window render checks. A successful process/PNG alone is not recognition
or fidelity evidence. Do not silently reverse normals/faces to make a prettier view.

## Asset ingestion

This is an offline asset-consumer test, not a renderer DLL, SFC launcher, or
live integration. Follow the [probe definition](../../docs/reconnaissance/probes/MESH-EXPORT-001-remix-ingestion.md).
The installed vendor package is read-only input. Scratch copies are disposable;
original packets and game directories are never outputs.

With the repository's configured Python 3.12 and PowerShell 7 executables:

```powershell
pwsh -NoProfile -File tools/remix_ingest/build_remix_job.ps1
python -m unittest discover -s tools/remix_ingest -p 'test_*.py' -v
python tools/remix_ingest/run_remix_ingest.py <accepted-capture-directory>
python tools/remix_ingest/run_remix_ingest.py <accepted-capture-directory> --execute
```

The first runner invocation only prepares a fresh job. The second prepares and
executes another fresh job; it does not resume or overwrite the first. Default
Toolkit `C:\Project\RTXRemix`; jobs `C:\Project\RemixJobs`. Those two roots must
have no whitespace because the installed Kit/vendor CLI script parsing is
space-sensitive. The SFC repository/capture path may contain spaces.

`--fixture` is explicitly synthetic-only qualification, bypassing the real-run
normal-exit/client-hash gate. Never use it to qualify an actual capture. Successful
synthetic conversion is not SFC compatibility or a visually recognized ship.

The native guard atomically assigns the child to its own unnamed Windows Job
Object at process creation. It terminates only that owned tree, never processes
by name. Bounds: 180-second complete job, vendor conversion timeout 120 seconds,
console file hard cap 8 MiB, scratch warning 128 MiB, stop threshold 256 MiB polled
every 25 ms. Polling is not a filesystem quota: fast writers may overshoot the
scratch threshold before termination. Portable cache/data/log roots are inside
scratch; shared GPU/driver/system caches are not wholly isolated or size-bounded
by this mechanism. Do not delete global caches or weaken Windows controls.

The copied vendor model schema retains all checks/resultors; only input/output
context changes. Vendor affirmative `validation_passed` metadata, mesh inspection,
clean process-tree exit, and position/topology/winding comparison are all required.
Normals, UVs, bindings, stage units/axes and transforms are recorded, not yet fully
qualified against source. No silent scale/axis/winding repairs. Actual mesh success
remains `GEOMETRY_INGESTED_PREVIEW_PENDING` until preview/attribute adjudication.

Additional bounded offline corner check (no Toolkit/game launch):
`python tools/remix_ingest/compare_obj_attributes.py <job>/input/ship.obj <job>/geometry.json --output <job>/corner-comparison-numeric.json`.
It matches position/UV/derived unit direction/source binding per triangle corner,
allowing cyclic order with absolute tolerance1e-6; records maximum differences.
This avoids decimal-bin threshold artifacts without altering geometry. Only
faceVarying UV/normal interpolation currently admitted; unsupported forms require
adjudication. Does not qualify raw vector meaning, world scale or original assets.

Each job records config/command/revisions, raw packet/receipt copies, derived OBJ/
MTL/manifest, console and portable log, owned-job result, inspection and final
result. Retain a verified evidence ZIP excluding caches after analysis; cleanup
is optional and confined to that exact job folder. Never remove reference/source
captures or vendor installation. No automatic cleanup and no elevation required
by design; a sandbox execution-policy issue is distinct from asset rejection.

## Same-run texture recovery (explicit opt-in)

See [TEXTURE-EXPORT-001](../../docs/reconnaissance/probes/TEXTURE-EXPORT-001.md).
The separate 90-second prepared game entry is
`tools/m1_component/start_texture_export_session.ps1`. Game appearance stays normal.
After normal exit it resolves only fresh registry-named original images and writes
`<capture>/textured/association-manifest.json`, original copies, lossless PNGs and
`ship.obj/ship.mtl`. It never uses old process IDs to find textures. No image or
filename guessing, UV flip, face/normal repair or automatic glow assumption.

Codex-operated follow-up, **after reviewing the real association manifest**:

```text
python tools/remix_ingest/run_remix_ingest.py <capture> --textures --execute
python tools/remix_ingest/run_mesh_preview.py --job <new-ingestion-job> --textures --smoke
python tools/remix_ingest/run_mesh_preview.py --job <new-ingestion-job> --textures
```

Use the bundled Python from the existing entry scripts. Actual Kit ingestion and
the textured viewer still require fresh runtime evidence; unit/preparation tests
are not a rendered texture PASS. `--textures` is never implicit; the original
grey CMD/accepted asset remain unchanged. New textured import requires unchanged
geometry plus corner UV/normal/group comparison before preview. Existing child-only
NRC-off settings and 120s view/180s job, 256MiB scratch/8MiB console limits remain.
Ten unique images, <=4096², 128MiB original+derived image budget/warn64MiB. Secondary
images are preserved separately but not bound as emission until their role is proven;
the association manifest therefore deliberately remains PARTIAL pending adjudication.
New preview PNGs belong to that preview job; compare against sponsor SFC observations.
Archive useful packets/manifests/images/logs after review without caches. Nothing is
automatically deleted, staged or committed.

## Fresh live multi-ship scene — default OFF

Prepared entry:tools/m1_component/start_live_scene_session.ps1,from established
elevated parent. Protocol3/component0.20 builds an EMPTY session scene directly
from fresh mesh/resource packets;no imported Klingon required. Both ships in
first different-class fixture should follow SFC camera. Original images loaded
once from proven filenames,lossless DDS for renderer;primary-only provisional
materials,unknown secondary/alpha roles retained as limitations. No image return.

Offline rehearsal only:python tools/remix_ingest/run_live_bridge.py --fresh-scene
--replay. This never launches SFC and uses explicitly synthetic motion/shape
variants. Actual two-class gameplay still required. Old start_live_bridge_session
single-ship path and offline grey/textured import workflows remain intact.
See docs/reconnaissance/probes/LIVE-SCENE-001.md and live-scene-contract.md for
layout,bounds,privileges,outputs,safe cleanup and acceptance;do not mix protocols.
