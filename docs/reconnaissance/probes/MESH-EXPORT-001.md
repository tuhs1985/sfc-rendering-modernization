# MESH-EXPORT-001 — complete selected primary mesh, read only

Status2026-10-15: **Capture/OBJ PASS**, actual bounded Toolkit geometry ingestion
accepted, recognizable viewport preview pending. [Real result](../2026-10-15-mesh-export-remix-result.md)
supersedes preparation-only statements below. Sponsor no issues, normal exit,
hooks restored/client hashes unchanged; one57744byte packet/452triangles.
Sponsor-authorized read-only export, not live renderer work.
[Input contract](../2026-10-14-single-ship-export-contract.md).

## Current sponsor-approved first test — capture AND Remix Toolkit ingestion

Sponsor approved adding Toolkit ingestion to this same first test. Stage A is the
unchanged read-only 90-second SFC capture plus validation and automatic OBJ/MTL
conversion. Stage B is the separate Toolkit import described in
[Remix ingestion procedure](MESH-EXPORT-001-remix-ingestion.md). Both stages need
their own outcome; an OBJ on disk does not demonstrate Remix consumption. No new
live runtime shim, game DLL, renderer connection or asset replacement is added.

## Question / hypothesis

Can one owner-scoped selected primary mesh be saved as complete, independently
readable positions, ordered polygon corners, raw vectors/UVs and source groups?
STRONG HYPOTHESIS: existing primary wrapper has sufficient inputs. Existing M0/M1
owner chain and RT-010 graph usage are CONFIRMED; complete portable export is not.
No external renderer, recovered textures, faithful camera or visual improvement
claim follows from a valid packet.

## Implementation / configuration

- Component **0.14**, x86, from `tools/m1_component/m1_component.cpp` and
  `m1_mesh_export.h`; analyzer `analyze_mesh_export.py`, schema `sfc.mesh.v1`.
  Existing hook thunks/trampolines and register/flags/FX-state preservation remain
  unchanged. Collector uses integer/raw-byte copies and checksum, not native edits.
- Build: Visual Studio 2026 Community x86 environment, Developer Prompt 18.7.3,
  preparation MSVC 14.51.36231, `/std:c++17 /EHsc /W4 /WX /O2 /MT /arch:SSE2`.
  Preparation binary hash is in the run record; runtime hashes in run metadata.
  Record a changed tool revision before future use; compiler is not bundled
  into source control. Python 3.12.14; bundled PowerShell 7.6.5. Entry supports
  Windows PowerShell 5.1 by re-executing the known bundled PowerShell 7 path.
- Offline build: `tools/m1_component/build_m1_component.ps1`. It builds the
  component/proxy/gate/controller plus existing and new native tests. Generated
  files remain under ignored `artifacts/m1/bin` and `artifacts/m1/test-temp`.
- Live configuration: enabled neutral mode, `EnableMeshExport=1`,
  `EnableWrapperObservation=1`, `EnableGeometryHook=0`; `EnableCornerSnapshot=0`,
  all tint/shading/private-copy/repeated-copy/epoch-requalification/surface-lighting
  modes off. MaxFrames=120, MaxEvents=10000, MaxOwners=8, ContinueAfterBurst,
  MaxSeconds=90, GateTimeoutSeconds=600. Component and runners reject incompatible
  modes. No legacy action-phase/camera cues in this workflow.
- Reuse existing automatic tactical gate, launcher/client hash checks,
  process discovery, controller load/unload, safe hook restoration, normal-exit
  observation and temporary proxy cleanup. Accepted Community Edition stack
  remains untouched except existing workflow's documented temporary proxy.

## Launch method / privileges

Only after runtime is requested, from the existing appropriately elevated parent:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\m1_component\start_mesh_export_session.ps1"
```

This entry builds/tests then uses `start_m1_enabled_session.ps1` with explicit
mesh/wrapper/geometry-off/90s/ContinueAfterBurst/AutomaticArm options. It inherits
elevation; `Test-ProbeElevation` refuses an unelevated parent rather than spawning
UAC. No execution-policy registry or Windows security setting changes. `Bypass`
is process-scoped. Do not launch the entry as an offline test.

Sponsor action: enter the usual two-ship skirmish, keep both visible initially,
then play normally. Expect **normal appearance**, no magenta/lighting change and
no special camera or ship maneuvers. Two beeps and the console request mean exit
normally, about 90 seconds after tactical rendering begins. Audio is best-effort;
if inaudible, check the console. No timestamp/pointer analysis.

## Start/stop / filters / bounds

- Hook acquisition only through owner-scoped primary wrapper `006AC5A0`, caller
  `0042E55D`, matched model/list/count/manager/source, depth=1/pending=1 and live
  owner epoch/vtable/ship->visual relationship. Capture after native source and
  position setup. Reject secondary `0042E626`, unowned/exception `00509843`,
  nesting and mismatches. Do not turn on `006AB410` diagnostic geometry hook.
- First count-admissible validated primary owner becomes the immutable target;
  this need not be the player ship. Actual selected child checked against visual
  LOD count/override/selection. Do not pick a stale cached LOD alone. Maximum
  admitted LOD count 64 is tooling policy, not engine-capacity discovery.
- At most two attempts on different rendered frames, one accepted packet,
  <=90,000ms from tactical gate. No target epoch reuse/retarget after retirement;
  record later retirement separately. No per-frame whole-mesh logging.
- All primary polygons, 1..512; 3..8 corners each; 1..65,536 positions; source
  indices <256. These are admission limits, not requirements/native allocation
  lengths. Unsupported large meshes fail open, not prefix-exported as complete.
- Preallocated packet storage **930,052 bytes** measured with x86 `sizeof`,
  <1 MiB static assertion. Worst synthetic 65,536 positions/512 eight-corner
  polygons/one source wrote **919,848 bytes**. The full 256-source schema maximum
  is **930,048 serialized bytes**, calculated; not an observed game capture.
- Packet hard cap 2 MiB; receipt/analysis <=64 KiB. Existing semantic event log
  warning 16 MiB/hard stop 32 MiB, bounded event/owner/thread storage unchanged.
  Native capture occurs at most twice; file serialization occurs on controller
  stop after recorder drain and hook restoration, not on the render thread.
- Full second-pass byte/identity comparison before publication; failure leaves
  no accepted packet and never alters render arguments. Bounded comparison is
  mutation detection, not a universal atomicity proof. Saturation/file failure
  never blocks original rendering. Timing uses QPC per attempt; receipt records
  raw ticks/frequency, analyzer converts to milliseconds when available.

## Outputs / analysis / cleanup

Unique ignored `artifacts/m1/runs/<timestamp>-enabled/` contains existing metadata,
INI, component/semantic/wrapper logs, hashes, controller and exit results plus:

- `MESH-EXPORT-001.bin`: raw little-endian packet, only if complete.
- `MESH-EXPORT-001-receipt.json`: status/attempts, owner, checksum/size, timing,
  retirement and hook-restoration/file-write receipt.
- `MESH-EXPORT-001-analysis.json`: bounded pointer-independent validation.
- `MESH-EXPORT-001.obj`, `.mtl`, `.obj-manifest.json`: automatic diagnostic
  derivatives from validated packet/receipt, triangle-only, <=2 MiB OBJ and
  <=64 KiB each sidecar. Preserve raw packet; separate toolkit-ingestion evidence
  is still required. Converter `export_mesh_obj.py` normalizes vectors only in
  derived OBJ, preserves position/UV/winding, and uses neutral grey source labels,
  not recovered game materials. No inferred world transform/axes/units applied.

Runner invokes analyzer with `--receipt` and `--output`. On packet rejection,
warn, still request normal game exit and preserve exit/hash evidence, then report
failure. Do not classify a missing/invalid packet as successful capture.
Conversion failure is recorded separately from raw packet validation failure in
`run-result.json`; both preserve normal exit/hash evidence. Existing derived
files are never overwritten automatically. A manifest written last identifies a
complete derivative set; partial files after I/O error are not ready for import.

Packet layout: 64 DWORD header; `vertex_count*12` position bytes;
`polygon_count*36` records (seven header DWORDs plus native header/corner addresses
as provenance); `corner_count*28` bytes; `source_count*40` sparse indexed source
records. Header magic=0x314D4653, version=1, byte size, whole-packet FNV-1a with
checksum word zeroed. Header words 4..23 carry owner/thread/frame/time, native
identity, caller/list/base, counts and LOD evidence; 24..26 dispatch words;
27..29 reserved; 30..46 supplied and 47..63 composed raw transforms. Polygon
word6 is a portable **corner ordinal**. Native provenance values and opaque
source words are never consumer pointers. Analyzer additionally reports SHA256.

Acceptance: checksum/exact lengths, full coverage, in-range indices, finite
referenced positions/vectors/UVs, source membership and selected-child consistency.
Report bounding box, UV ranges, vector lengths, winding/face alignment and
degeneracy without repair. Preserve nontriangle polygons raw; report topology
conversion unqualified, never assume a triangle fan. External camera/material/
lighting/composition are explicitly absent. Ground-truth semantic targeting
comes from existing owner provenance, not whether a future preview looks plausible.

Normal stop restores hooks and unloads the read-only component under existing
controller policy; no pointer lease/native graph substitution or DLL pin is
introduced. Normal process exit and entry's finally block remove owned temporary
proxy/config artifacts. Verify `run-result.json`, logs, client hashes and absence
of game-directory test leftovers before another run. If interrupted, use existing
documented controller cleanup; never overwrite a loaded proxy or start a second
controller. One activation per fresh game process; no same-process rearm assumed.

Historical preparation predicted fixed output bounds; actual first capture and
consumer sizes/results now recorded in the linked real result. These fixed caps cannot
produce a mesh firehose; unsafe unbounded apitrace/shim transcripts are not used.
Retain/verify a ZIP of useful evidence after adjudication before optional raw
cleanup; never delete originals/reference assets. No raw files deleted in prep.
Potential one-time hitch from full copying/checksum is still a runtime risk;
QPC duration is capture time, not a full presentation-latency measurement.

Offline validation: build's mesh unit/production tests; Python unit suite;
`tests/test_mesh_export_workflow.ps1`; Windows PowerShell runtime shim fixture
with `-EntryName start_mesh_export_session.ps1`; independent Python parsing of
both native-generated packets. Preparation-time NOT EXECUTED is historical;
actual runtime adjudication is in the linked result above.
