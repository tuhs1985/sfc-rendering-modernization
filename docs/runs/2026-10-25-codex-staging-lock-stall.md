# Run187 — resource stall isolated to staging texture LockRect

## Decision

**The call site is CONFIRMED.** A fresh16KiB SYSTEMMEM staging texture's first
`LockRect(0,...,0)` consumed1839.4133ms and1476.4589ms in two separate standalone
controls. Its renderer construction totaled1850.4404ms/1483.1906ms. Thus over99%
of this measured admission stall was inside that lock, before copying its pixels.
GetThreadTimes recorded no CPU-time increment during either lock; this coarse
counter supports waiting, not a claim of literally zero instructions.

**A supported avoidance mechanism works in an isolated control.** Supplying
already-prepared pixels when creating SYSTEMMEM staging textures avoids the
lock/copy/unlock sequence. Same affected renderer construction measured3.9863ms
and3.8469ms for initial/late cases, retaining the normal UpdateTexture submission.
No vendor patch, new loader, graphics thread, resource format, dimensions or
material-setting change. **Not yet integrated or promoted to gameplay.**

This resolves attribution of the1.48s admission block; it does not establish
sub-two-second loading or uninterrupted material consumption. Underlying queued
render work still causes other waits. No new sponsor game run is needed yet.

## Documentation-backed explanation

All NVIDIA references are the actual1.5.2 pin/source
`b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4`.

- [NVIDIA device implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/d3d9/d3d9_device.cpp#L4215):
  SYSTEMMEM LockImage can enter WaitForResource even with a fresh CPU backing
  buffer. That helper synchronizes the command-processing thread before deciding
  resource usage. This makes earlier queued work a possible dependency of this
  small lock. CreateTexture already allocates/initializes SYSTEMMEM backing, so
  its first lock is not necessarily the lazy-allocation branch that skips waiting.
- **STRONG HYPOTHESIS, not an internal stack trace:** that command-thread join
  explains the reproduced lock delay. Host call timing and control establish the
  boundary; they do not name the shader/material/GPU activity occupying the queue.
- [Microsoft CreateTexture](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-createtexture#remarks)
  documents SYSTEMMEM creation from existing memory, with one mip, tightly packed
  pitch and a pointer supplied through pSharedHandle. Our existing one-mip BGRA
  packets satisfy those shape requirements. This parameter is a CPU memory pointer
  in this specific contract, not a new cross-process GPU sharing mechanism.
- [NVIDIA initializer](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/d3d9/d3d9_initializer.cpp#L126)
  copies supplied pixels into its backing buffer. Its [CreateTexture implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/d3d9/d3d9_device.cpp#L444)
  accepts this case; [SetupForRtxFrom](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/d3d9/d3d9_common_texture.cpp#L593)
  hashes CPU backing during UpdateTexture. Avoiding LockRect therefore need not
  lose the ordinary material identity. This was tested, not assumed from headers.
- [Microsoft UpdateTexture](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-updatetexture)
  still requires SYSTEMMEM source and DEFAULT destination. The diagnostic control
  retains that path and all real GPU/output completion checks.

## Probe definition and limits

No tracked production implementation changed in this run. The existing dirty tree
and HEAD9ff2d3d remain intact. An isolated derivative under
`artifacts/resource-stall/` copies the current host and instruments only Renderer
construction. Original source SHA256s and actual diagnostic executable/runtime
hashes are retained in each fixture's `resource-probe.json`. The normal executable
hash is checked before/after each run. No binary was replaced in the game or
qualified renderer folder.

Versioned probe: `docs/reconnaissance/probes/20261025_staging_lock_probe.py`;
versioned analyzer: `20261025_staging_lock_analysis.py` in the same folder.
Original executed script copies remain in `artifacts/resource-stall/`.
The versioned probe also checks generated-source hashes/build freshness before
running and creates its output directory if absent.

`20261025_staging_lock_probe.py prepare` creates the timing derivative;
`prepare --initial-data` creates the single supported-path control. Build x64 with
the same MSVC `/O2 /W4 /WX /fp:precise /Brepro`, existing header/library include
paths, and libraries from build_direct64.ps1, output `profile_host.exe` in this
isolated folder. `20261025_staging_lock_probe.py run [--late]` overrides only this standalone
supervisor's renderer path. It never selects a different runtime or launches SFC.
The accepted golden capture remains the source of geometry/textures.

Measured operations: VB/IB create/lock/unlock, DEFAULT/staging texture creation,
staging lock, CPU row copy, unlock, UpdateTexture, staging Release and total
construction. Explicit Release is at the same original scope-end position.
QPC and current-thread CPU time are recorded into8192fixed records; output flushes
at thread exit, not during admission.770records per lock control,449per alternative,
zero drops. No image streams or model recapture. Existing100s fixture hard bound,
32MiB log policy, owned-process cleanup and20GB aggregate policy remain.

Diagnostic results remove `multi_ship_build_locks` and carry
`production_qualification_eligible=false`; original reference locks are preserved
under a diagnostic-specific field. They are not normal gameplay qualification.
Use `20261025_staging_lock_analysis.py` to reproduce the read-only analysis,
including archive access; that version was rerun successfully after archival.

## Four standalone outcomes

| Fixture suffix | Staging path | Affected construction | Settled output | All post-start omissions |
| --- | --- | ---: | ---: | ---: |
| 213454-340621 | Lock control,initial | 1850.4404ms | 595/600 | 2 |
| 213559-910384 | Lock control,late | 1483.1906ms | 595/600 | 154 |
| 213854-971322 | Initial pixels,initial | 3.9863ms | **491/600** | 109 |
| 214030-845021 | Initial pixels,late | 3.8469ms | 595/600 | 91 |

All named folders are `artifacts/remix-runtime/runs/20261025-...-return-fixture`.
All4owners acknowledged,0invalid/rejected/partial, normal owned process exits,
native HUD/scene unchanged, resize/recreation and state checks passed. Both
diagnostic variants compile warning-as-error. The491/600 window fails the existing
delivery threshold; do not hide it behind the successful late run.

The first lock control had anomalous first matching output22.386s, compared with
3.219s in its late control. Alternatives were4.686s/4.968s. The initially small
post-start omission count excludes that long startup. These are not controlled
whole-pipeline speedup numbers. Do not report the local construction improvement
as an equivalent first-picture speedup. The initial-data control still measured
1411ms first-cohort GPU-readiness wait; a queue wait is not necessarily eliminated
from the whole renderer merely because admission no longer joins it.

Material transitions remain interrupted: alternative initial longest gap106records
(1.762s QPC span); late88records(1.520s). These are missing returned layers,
not measured SFC freezes. No gameplay/sponsor observation is invented.

## Content and pixel checks

Initial pair:381scene/texture/DDS/material files have identical hashes. Late pair:
all geometry/normals/UVs/indices/groups, texture images and material stages exact;
one scene.bin differs only in captured frame number200366→200406. That provenance
is preserved and explicitly reported, not normalized away in saved evidence.

Inspected the final alternative BMP: all three textured ship contents visible.
Final ship-region comparison against controls has mean absolute RGB error around
0.25/255(initial) and0.21/255(late), with932/532pixels exceeding10in a273600pixel
region. **Not bit-exact rendered pixels**, and this does not qualify early-stage
material readiness. Asset bytes/material identities are exact; the image evidence
supports retained final appearance, not a universal graphics fidelity claim.

## Evidence and final state

- Curated: `docs/reconnaissance/evidence/20261025-staging-lock-stall.json`.
- Full calls, bounded timings and comparison: `artifacts/resource-stall/analysis.json`
  and each fixture's `resource-calls.json`, raw console/audits/results and BMPs.
- Both generated asset sets archived after per-file SHA256 verification:
  `artifacts/remix-runtime/archives/run187-lock-controls-assets.zip`
  (287313297→17815927B) and `run187-initial-data-assets.zip`
  (287313291→17816001B). Restoration paths/hashes in the two receipts under
  `artifacts/resource-stall/`. Raw diagnostic evidence remains loose. No golden
  input, normal qualification fixture or original game file removed.
- Existing aggregate ledger18,846,873,115B plus isolated probe tree5,792,388B:
  combined18,852,665,503B<20GB. Four console logs combined598967B.
  Budget preflight once deferred a control until completed duplicates were archived;
  the budget was not bypassed. No policy/permissions change.
- Normal experimental read-only preflight still PASS against unchanged production
  sources/binaries/qualification. Prior613Python/native checks were not relabeled
  as new executions; this run adds four actual diagnostic graphics controls.
- New repository files are this run record, curated JSON and the two versioned
  probe/analysis scripts; HANDOFF/STATUS updated,
  including the requested Obsidian tracker. No staging/commit/push. No active owned
  renderer/fixture/game process or shared-memory session remains.

**Exact next action:** integrate the documented initial-data staging path into the
ordinary-D3D9 consumer as a small separately validated change: explicitly retain
source-memory lifetime, verify native D3D9/Ex pixels/state and Remix material
identity, then repeat full-interval delivery checks. Preserve normal defaults until
qualification; do not claim material-streaming or total startup solved by this call fix.
