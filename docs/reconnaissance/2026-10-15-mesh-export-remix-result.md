# MESH-EXPORT-001 — real capture and Remix geometry ingestion

## 2026-10-16 current addendum — visible preview recognized

The previously pending recognizable-preview observation is now CONFIRMED through
a separate diagnostic viewer using installed Kit/HdRemix and this exact saved USD.
Sponsor recognized the ship and corrected the camera labels (Front+X/Side+Z);
only cameras changed. [Preview run](../runs/2026-10-16-codex-mesh-preview-launcher.md)
pins actual images, runtime failure/correction, final settings and clean exit.
Captured geometry/derived attributes/provenance unchanged. Basic external mesh
consumption/visible-recognition proof established, **not** faithful materials,
face shading/handedness, world units, live game rendering or TRL advancement.
Original capture/import records and provisional status strings below are historical
and deliberately preserved rather than rewritten as original runtime conclusions.

## 2026-10-15 original adjudication

2026-10-15 America/New_York. **Capture/OBJ PASS; actual Toolkit geometry accepted,
preview pending.** Not full Stage B PASS, live Remix integration, ray tracing in
SFC, recovered materials or a TRL promotion. Sponsor: "done, no issues noted".
[Probe A](probes/MESH-EXPORT-001.md), [Probe B](probes/MESH-EXPORT-001-remix-ingestion.md),
[execution record](../runs/2026-10-15-codex-mesh-export-remix-runtime.md).

## Direct runtime evidence — CONFIRMED

- Game run `artifacts/m1/runs/20261015-190310-enabled`, component0.14,
  automatic tactical gate;90s neutral/mesh-export/wrapper observation, geometry
  hook and visual modifications disabled.5337frames observed,1180 detailed events,
  log339509bytes; configured120frame detail envelope saturated normally, summary
  continued. No log truncation/warning, rejected semantics or owner/thread overflow.
- Two semantic owner epochs in retained sequence. Selected owner1, ship
  `0x1065AD88`, visual`0x0EC8ACD0`, Model0`0x17B0C518`, source`0x04A9365C`,
  selected child0. Owner-scoped primary wrapper`0x006AC5A0`, caller`0x0042E55D`.
  Exact additional provenance/header/transforms remain in packet/analyzer.
- First attempt accepted at elapsed78ms/frame3:254positions,240referenced,
  **452triangles/1356corners**,5source groups (109/239/54/46/4triangles).
  Raw packet57744bytes, no degenerate triangles/zero vectors, checksum valid.
  Copy/checksum QPC time0.0859ms, **not** a frame-time/performance guarantee.
  Packet SHA256 `D6A397215B7788A0D5ABF3A6130CBD5E13EE233B17350CE2CB279B383219F103`.
- Raw vectors predominantly nonunit (935corners), opposed geometric winding
  alignment approximately-1; this is preserved evidence, not auto-repaired.
  OBJ normalizes derived vectors only; native meaning/handedness not reclassified.
- Receipt: complete/file_write_ok/hooks_restored=true, one attempt; selected owner
  retired later, no retarget. Summary counts one retirement; early detailed packet
  contains none because detail ended earlier. Do not mistake that for contradiction.
- Controller/component hooks restored, normal process exit; current reference and
  installed client SHA256 unchanged. No owned proxy/config/component DLL leftovers
  found in game directory. Sponsor reports no visible/gameplay issues. No new
  `0x006AB410` transcript: hook deliberately off, historical downstream proof stands.
  Generic M1 analyzer PARTIAL_OR_REVIEW_REQUIRED reflects absent geometry samples,
  not a failed mesh-export receipt or a new whole-milestone verdict.

## Actual Remix ingestion — CONFIRMED, limited scope

One job `C:\Project\RemixJobs\20261015-231057Z-19b131ce`, pinned Toolkit
1.6.0-dev+main.30229.3f23f80a.gl, official schema/plugin pipeline, no vendor edits.
Input copied from accepted run; real-run normal-exit/client-hash gate enforced,
**no --fixture bypass**. Vendor validation_passed=true, own inspection INSPECTED.

- **452triangles matched**, zero missing/extra or reversed faces, local positions
  preserved. Toolkit splits source runs into11mesh prims, not11ships. Bound
  neutral-grey source labels remain5groups; not recovered SFC materials/textures.
- Corner comparison cyclically matches position+UV+derived unit direction+source
  binding, absolute tolerance1e-6:all452matched. Maximum deltas position4.98e-9,
  UV1.91e-9, normal2.98e-8. Initial five-decimal-bin comparison flagged5triangles
  solely at rounding thresholds; retained report superseded by numeric comparison.
  No input, face, vector or UV altered to obtain the match.
- All inspected normals/UVs faceVarying; orientation rightHanded. USD stageY-up,
  metersPerUnit1, **100x uniform parent transform on all11meshes**, as in synthetic
  preflight. World-unit/axes interpretation not qualified, not silently rescaled.
- Job11.781s, exit0/stop_reason0, zero remaining owned processes; console107545bytes,
  polled peak scratch1177187bytes. All far below180s/256MiB/8MiB limits. No new
  gameplay or user Toolkit-window operation. USD157648bytes, SHA256
  `59B9C57ADAD61BEF4244F34B631B833BD6C34416791D3108ADE0537A64592696`.

## Decision / remaining uncertainty

**Real SFC semantic mesh data has reached the standalone Remix Toolkit as mesh
geometry, with its derived corner attributes and semantic provenance retained.**
This is more than seeing textures or a fullscreen render target; it is still an
offline selected-primary-mesh export, not a full physical ship/all LODs/passes or
real-time route back to the game. Other observed owner has6370primary polygons,
outside this probe's512admission cap; no expansion or prefix capture attempted.

Next smallest action: visually inspect this existing `output/ship.usda` in Remix
to recognize the selected mesh and assess face visibility/orientation/scale. Do
not capture again merely to preview. Actual textures/material recovery, faithful
camera/world contract, lighting and live renderer bridge remain deferred. No
modernization technology/gate decision follows automatically from this test.
