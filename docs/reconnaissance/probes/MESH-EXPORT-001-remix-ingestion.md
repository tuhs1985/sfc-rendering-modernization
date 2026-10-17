# MESH-EXPORT-001 — Stage B: Remix Toolkit asset ingestion

Updated2026-10-16. Sponsor-approved extension of the first mesh test. **Real
capture/OBJ PASS; geometry accepted and saved mesh visibly recognized.** Surface/
world/material fidelity remains unqualified. No runtime rendering bridge,
SFC configuration change, mod installation, or game asset replacement.

## Current execution status / implemented runner

[Preview procedure](MESH-PREVIEW-001.md) and
[2026-10-16 run](../../runs/2026-10-16-codex-mesh-preview-launcher.md) supersede
preview-pending statements in original import evidence. Separate own Kit/HdRemix
viewer rendered the exact saved mesh; sponsor recognized it. No conversion replay,
asset/normal/winding repair, live game connection or formal gate promotion. Initial
default NRC GPU fault avoided in corrected process-only reference-mode preview.

[Real result](../2026-10-15-mesh-export-remix-result.md) supersedes synthetic-only
preflight: job`20261015-231057Z-19b131ce` ingested452real triangles into11mesh prims,
retaining local geometry/corner attributes/source-neutral bindings.11.781s,
~1.18MB scratch,clean owned exit.100x parent scale still unqualified; preview
required before full Stage B PASS. No actual SFC textures recovered.

[2026-10-15 preflight record](../../runs/2026-10-15-codex-remix-ingestion-preflight.md)
supersedes preparation-only/driver-blocked claims below. Driver617.42 and latest
GUI log confirm renderer loading. Installed Toolkit remains the pinned development
package below. Its official model pipeline successfully processed one synthetic
triangle into one USD mesh; vendor validation affirmative, native local position/
winding match, clean owned-process exit. **Not a real ship or full ingestion PASS.**
It authored a100x uniform parent transform, metersPerUnit1/Y-up; recorded, not
silently undone. Actual ship attributes/world alignment and preview remain open.

Runner/source/tests: [tools/remix_ingest](../../../tools/remix_ingest/README.md).
Use configured Python3.12.14/PowerShell7.6.5; build x86 guard with VS2026/MSVC14.51
as documented there. No routine UAC requirement by design; restricted-sandbox
startup stalled while the same owned workflow progressed outside sandbox. This
environment dependency is distinct from importer rejection. Do not weaken UAC,
change drivers or modify installed Toolkit to run an asset job.

```powershell
pwsh -NoProfile -File tools/remix_ingest/build_remix_job.ps1
python -m unittest discover -s tools/remix_ingest -p 'test_*.py' -v
python tools/remix_ingest/run_remix_ingest.py <accepted-capture-directory> --execute
```

Default work root **`C:\Project\RemixJobs`**, outside game/vendor/repo, supersedes
the earlier suggested artifact-root location (Kit script parsing is space-sensitive).
Fresh timestamp/UUID per job; do not overwrite/retry an existing output. Captured
packet/receipt are copied, then revalidated/converted. Nonfixture execution requires
run-result normal exit, unchanged client and expected SHA256. `--fixture` is only
for synthetic data; never use it to bypass an unqualified actual game run.

Actual launch bypasses the vendor's whitespace-sensitive outer Python/bootstrap,
not its ingestion engine: runs installed Kit CLI app with vendor merged settings,
explicitly enables the five plugins declared by that settings app, then executes
our copied `kit_ingest.py` calling installed `vendor_cli.run` asynchronously.
Plugin names/full argv/schema are preserved in job-metadata.json/schema.json.
Installed schema SHA256 pinned; no checks removed. Only input/output fields change.

Start: explicit runner `--execute`, no automatic game/session trigger. Stop: vendor
job/inspection completes,120s conversion limit or180s total time, log saturation,
scratch threshold or I/O failure. Native owned Job Object assignment is atomic at
child creation; descendants inherit ownership; KILL_ON_JOB_CLOSE protects launcher
failure. Never kill all Kit processes or disturb the sponsor's GUI.8MiB console
cap is enforced before writes;128MiB scratch warning/256MiB stop polled every25ms
can overshoot (not a disk quota). Kit portable logs/cache/data inside job; shared
driver/system caches are outside that size control. Avoid repeated large captures;
do not delete global caches. No shader warm-up or video capture requested.

Expected output: job metadata/config/schema, input packet/receipt/OBJ/MTL/manifest,
output ship.usda/.meta, console/portable logs, job-result.json, inspection.json,
geometry.json and result.json. Raw packet<=2MiB, OBJ<=2MiB, metadata<=64KiB,
geometry inspection<=2MiB. Synthetic success measured522255bytes total, console
89717bytes, USD3608bytes,4.047s. Real ship volume remains unmeasured; stop limits
apply regardless. Toolkit can produce much larger cache/log data in general;
these controls prevent an unlimited job, not every external global-cache write.

Analysis requires owned exit0/no remaining children, affirmative vendor metadata,
mesh topology/local position/winding comparison. Arrays/transforms/materials are
recorded, not automatically qualified; no coordinate or face repair. Final real
status remains GEOMETRY_INGESTED_PREVIEW_PENDING until attributes/recognizable ship
preview are adjudicated. One configuration retry was used in synthetic preflight
after exact missing-plugin diagnosis, separately from one sandbox-environment retry.
Do not blindly repeat import or gameplay after failure.

Cleanup: first verify a ZIP of useful inputs/config/logs/outputs/source revisions;
exclude caches if material. Delete only the exact adjudicated scratch directory
if needed, never source captures, reference assets or installed Toolkit. No game
DLLs deployed, so no game-side cleanup. Current small jobs retained; verified ZIP
and exact sizes/hashes recorded in run record. No transient shell history needed.

## Historical preparation baseline — standalone acquired

Sponsor requested standalone after NVIDIA-app installation failure. Official
GitHub development package **1.6.0-dev+main.3f23f80a** extracted to
`C:\Project\RTXRemix`, GUI `lightspeed.app.trex.bat`, ingestion CLI
`lightspeed.app.trex.ingestcraft.cli.bat`; model schema at the relative path below.
App manifest confirms1.6.0-dev; included Kit has valid NVIDIA Authenticode.
[Acquisition record](../../runs/2026-10-14-codex-remix-standalone-package.md) pins
artifact11921797093/run38619866886, ZIP hash/size and launcher/schema hashes.
This is a **development build**, not the stable NVIDIA-app channel. At acquisition
no scripts were launched; that statement is historical, superseded above.

## Purpose and decision

Can Remix Toolkit ingest the validated selected ship mesh as usable geometry?
Stage A validates native packet/provenance and creates portable input; Stage B
must actually process that input in the Toolkit. Neither proves live SFC-to-Remix
integration, correct game camera/lighting, recovered textures, ray tracing in SFC,
or formal TRL promotion. Blender is optional, not a prerequisite.

CONFIRMED documentation: current NVIDIA ingestion guide accepts OBJ models and
produces USD-family assets. Tool-specific SFC compatibility remains unproven.
[NVIDIA ingestion guide](https://docs.omniverse.nvidia.com/kit/docs/rtx_remix/latest/docs/howto/learning-ingestion.html),
sections UI ingestion, CLI ingestion and file-format compatibility, checked
2026-10-14. This moving documentation does not identify the installed version.

## Stage A handoff / conversion definition

Use [MESH-EXPORT-001](MESH-EXPORT-001.md) entry once sponsor is ready. No additional
gameplay/camera phases. The existing runner automatically validates the binary
packet with its stop/cleanup receipt, then runs:

```powershell
python tools/m1_component/export_mesh_obj.py <run>/MESH-EXPORT-001.bin --receipt <run>/MESH-EXPORT-001-receipt.json --output <run>/MESH-EXPORT-001.obj
```

Use the configured bundled Python 3.12.14, not an assumed PATH installation.
Converter schema `sfc.mesh.obj.v1`; preserve script revision and run metadata.
No elevation needed for conversion or normal Toolkit processing; gameplay entry
continues inheriting the validated elevated parent without routine UAC prompts.

Outputs in that ignored unique run directory:

- OBJ: all primary triangles, one independent position/UV/normal per corner;
  no welding, triangulation guessing, position scaling, axis/V flip or transform
  application. Float32 attributes printed at nine significant decimal digits.
- Adjacent MTL: neutral grey diagnostic materials named by source group. This is
  **not** recovered material or texture data. No textures/fonts/scripts/resources
  loaded from opaque native pointer values.
- `.obj-manifest.json`: input SHA256, owner/Model0/source identity, selected child,
  output hashes/bytes/counts, polygon/source/face mapping, normalization policy.
  Normal vectors normalized in the derived OBJ only; raw magnitudes/signs remain
  in packet. No auto face/vector reversal or normal repair.

Triangle-only derivation refuses nontriangle topology, zero vectors or degenerate
triangles. That is conversion BLOCKED, not invalidation of an otherwise complete
raw packet. Inspect available evidence before any repeat capture or scope change.
All existing derived paths are protected against overwrite; new manifest written
last. If interrupted before manifest exists, treat derivatives as incomplete.

Bounds: existing packet/log caps unchanged; derived OBJ hard cap **2 MiB**, MTL
and manifest each **64 KiB**, all checked before file creation. Input <=2 MiB.
One output set per capture; no streaming/repeated export. Known bounded worst
counts 4,096 corners/512 triangles (triangular accepted packet is <=1,536 corners);
no unbounded mesh/firehose. Actual sizes recorded in run evidence after testing.

## Toolkit readiness and execution controls

- Historical preparation: installation/version/path was **not yet confirmed**. Narrow preparation checks
  of NVIDIA Program Files and local NVIDIA/legacy `ov/pkg` roots found no obvious
  Toolkit folder; this is not a whole-machine absence claim. Sponsor asked for
  shortcut/install location. Do not install/rebuild the old D3D9 shim or mix game
  DLLs while looking for Toolkit. Resolve actual version before processing.
- Operate an isolated scratch project/work area under
  `artifacts/remix-ingest/<capture-run-id>/`, never the SFC game directory or a
  working mod project. Record any sample/base stage needed by the installed
  Toolkit project workflow; no authentic SFC capture is assumed available.
- Prefer automation with the installed Toolkit ingestion CLI once its schema and
  version are verified. Do **not** edit the vendor's installed schema: copy its
  model-ingestion configuration into the scratch area and record the full config.
  Current docs locate it under
  `exts/lightspeed.trex.app.resources/data/validation_schema/model_ingestion.json`
  and document `lightspeed.app.trex.ingestcraft.cli.bat -s <config> -ex 1` plus
  `-t` timeout. Check actual local CLI/schema/help before constructing commands;
  these are upstream references, not a tested local launch command.
- Equivalent UI path, if automation is unavailable: Ingest/Ingestion -> Models
  -> Add the OBJ (with adjacent MTL) -> choose isolated output -> USDA -> Add to
  Queue -> inspect validation report. Developer handles configuration/analysis;
  sponsor involvement is limited to recognizing the displayed ship if necessary.
  Exact UI may differ with installed version; do not fabricate a successful import.
- First conversion uses identity scale/no guessed axis changes. Preserve settings
  and generated metadata. Use a generic preview camera/light if needed and label
  them synthetic. Do not compensate for camera/material gaps by editing SFC data.

Historical proposed controls (now implemented with caveats above): one asset/job, 120-second conversion timeout after tool initialization, one
diagnostic retry only for a materially explained configuration issue. Scratch
output warning **128 MiB**, hard stop **256 MiB** including logs/generated copies;
log transcript <=8 MiB with bounded tail if needed. These are proposed first-job
controls, not an implemented wrapper or measured Toolkit output. **Before CLI
execution**, prepare/validate a runner that enforces these limits and owns only
its spawned job; the packet runner does not enforce external Toolkit output.
Record installation launch time separately; never kill unrelated user Toolkit
sessions. No unbounded screen/video capture. If UI cannot be bounded safely,
prepare bounded CLI execution before relying on repeated jobs.

## Evidence and outcomes

Retain Toolkit version/configuration, exact invocation, ingest job result and
validation report, produced USD/USDA and hashes/size, packet/OBJ manifest linkage
and one useful viewport screenshot. Verify mesh geometry (not just textures or a
flat image): expected triangles, corresponding bounds/shape and usable attributes.
Toolkit may legitimately merge identical vertices; compare faces/positions and
corner attributes rather than requiring unchanged point count. Document any
axis/unit transform applied by the importer and any normals/group reconstruction.
Do not silently fix winding/smoothing to obtain a prettier screenshot.

Separate outcomes:

1. **Capture/OBJ PASS:** complete raw packet, cleanup and validated derivatives.
2. **Toolkit ingestion PASS:** actual job creates usable mesh data; preview is
   recognizable as the selected ship mesh and correlates to counts/provenance.
   This is asset ingestion only, not the live SDK/renderer bridge.
3. **PARTIAL/BLOCKED:** record packet, conversion or consumer stage independently.
   Tool missing/setup failure is not proof of bad geometry or incompatible seam.
   An importer rejection is not permission to repeat gameplay without analysis.

After adjudication, preserve a verified ZIP of useful input/config/report/output
evidence before optional raw cleanup. Do not delete original capture/reference
assets or vendor installation. Historical preparation had no Toolkit output;
current small synthetic jobs/verified archive are recorded in the run record.

**Exact next action:** use the prepared preview CMD for further visual inspection
if desired. Remaining engineering work must separately qualify surface orientation/
normals and units, not repeat gameplay or ingestion just to view the saved mesh.
