# Live break pieces — implementation prepared, November 7, 2026

## Result and next action

The default-off destruction path now connects fresh indexed debris geometry,
independent simulation poses and child lifetimes to the existing retained scene,
ordinary D3D9 renderer, Remix output and synchronized native insertion. **Live
gameplay is not yet verified.** No game was launched during this implementation.
Changes remain unstaged and uncommitted; existing work is preserved.

Run the focused checkout:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\native_insertion\start_native_break_session.ps1"
```

Use the established F-CA with a surviving wingman. Let its enhanced hull appear,
destroy that ship while visible, watch the fragments, then switch cameras away
and back. Exit normally at the cue. The checkout uses ExtraFrame, zero offset,
current appearance, weapon lights and damage, a 90-second tactical window and
the existing 285-second prepared-workflow bound. The normal untimed launcher
and tuning workflow are unchanged; `-BreakModels` is opt-in.

## Source and lifetime contract

The existing [simulation review](2026-11-07-codex-break-simulation-review.md)
qualifies the FCA factory, indexed child construction, simulation arithmetic and
retirement. The [standalone replay](2026-11-07-codex-break-d3d9-replay.md)
qualifies its four captured textured meshes. No additional discovery run was
needed. Existing capture `break-20261107-050659-161275` remains authoritative.

Four optional hooks observe factory `0x41455B`, child constructor `0x41B657`,
child drawing `0x41B900` and destructor `0x41B8B4`. Only the qualified factory
caller (`0x416754`) and constructor caller (`0x41BAFB`) admit children of an
already tracked parent. Each child receives an independent high-bit render
epoch; native pointers alone cannot reconnect it. The intact render instance
retires at the qualified handoff; the simulation ship is untouched. Children
continue receiving fresh simulation transforms independently of visibility and
remain until native retirement. Camera switches reuse geometry.

Fresh primary/secondary indexed slices are captured at the existing polygon
wrapper, returns `0x42EA92` and `0x42EB34`. Source count/list, cumulative ends,
visual/model/source and piece index must agree. Capture occurs before
suppression. Both submissions use the existing source-frame insertion decision;
zero count is authorized only after the matching output insertion commits.
Unknown callers, ambiguity, changed source identity, unavailable output or
capacity exhaustion preserve native drawing. Shared flush is never used to
suppress an owner.

The existing current-user mapping, owner table, four acknowledged asset slots,
worker and output lease are reused. Preallocated child state is prefaulted
before hooks. No callback disk access, conversion, allocation or extra wait is
added. Asset capture remains at most once per source frame; functional pose and
cohort publication follows native frames without a new refresh cap. First asset
discovery is published immediately; the existing 34-ms diagnostic/discovery
mirror does not throttle functional scene updates.

The optional `sfc.break.piece.v1` association metadata carries child/parent
epochs, piece count/index, first/count/total triangles and original list identity.
The ordinary decoder stays closed to indexed origins unless break mode is
explicitly enabled. Original geometry, images, normals and UVs stay unchanged;
existing Remix-specific conversion remains in its adapter. The manifest retains
piece provenance. Output owner/depth identifiers preserve high-bit epochs.

Fragments use their original break textures and ordinary material preparation.
They deliberately have no inferred intact-hull damage UVs or inherited damage
scalar. Mixed intact/debris scenes skip optional damage geometry only for pieces
with no such channel; intact damage qualification remains enforced.

## Verification

- Focused native fixtures exercise actual x86 hook forwarding, stack/register
  conventions, LastError, callback accounting and decrement/return inside the
  unload-protected instruction range. Scene/worker tests cross the actual
  shared-memory boundary, checking independent epochs, capture limits, offscreen
  transforms, cached geometry, retirement, pointer reuse and clean shutdown.
- Component coordinator fixture: **99 checks PASS**, including child primary
  and secondary suppression after commit, unchanged captured arrays, timeout
  and stale-epoch native retention. Batch-flush qualification: **12,300 PASS**.
- Native gate: **1,216 checks per architecture PASS**; cohort wire: **193 per
  architecture PASS**. Physical hull/depth: **801 PASS**, including high-bit
  child owner identifiers and existing 256-owner coverage.
- **90 targeted Python tests PASS** across break transport/output, parallel
  assets, damage materials/mapping, resources, startup safety, cohort, gate and
  insertion. Real current-user native/Python mapping transfer and acknowledgement
  were exercised in the desktop session.
- M1, direct D3D9 and pinned candidate builds PASS. Native light/queue/worker
  regressions PASS. Candidate dependency pins remain Remix 1.6.1 / API 0.6.5.
- Both full standalone native-insertion regressions PASS: **600 measured frames
  each**, changing poses, three owners/two assets, actual transport and GPU
  completion, native depth/text and graphics-state restoration. No SFC involved.

| Fixture | Strict | ExtraFrame |
| --- | ---: | ---: |
| Local run | `20261107-164601-601458-return-fixture` | `20261107-164951-909697-return-fixture` |
| Owner commits | 1,617 | 1,752 |
| Pixel mismatches / state errors | 0 / 0 | 0 / 0 |
| Header misses / stale | 62 / 46 | 17 / 17 |
| Invalid / dropped / partial / active at stop | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| Fixture / renderer exit | 0 / 0 | 0 / 0 |

These regressions deliberately inject delays and overruns. Their misses are not
live gameplay measurements, nor simultaneous debris acceptance. Local logs and
test outputs are in `artifacts/break-live`; raw fixture evidence remains under
`artifacts/remix-runtime/runs`. Cohort qualification was refreshed from these
runs. Read-only ExtraFrame/all-ships/break preflight PASS; damage remains ON.

## Limits and unresolved items

Only the established rigid triangular indexed path is admitted. The verified
FCA is the first gameplay fixture, not universal `_brk.mod` coverage. Unobserved
in-place deformation is unqualified. Existing 256-owner/1,024-revision and image,
output, log and aggregate evidence budgets apply; unsupported pieces stay native.
Only bounded counters are added, not continuous images or exhaustive draw logs.

The earlier short one-Present standalone teardown limitation remains recorded.
Its blocking shader-compilation and 24-Present diagnostic startup controls are
**not enabled for gameplay**. Live pieces share the already-prewarmed retained
host/receiver; neither is recreated per fragment. Both 600-frame fixtures exit
normally. Appearance, light, synchronization policy and runtime pins are intact.

Next accept or diagnose the sponsor's live destruction checkout: four textured
fragments, continued motion across camera changes, no doubled original debris,
normal shields/UI/gameplay, normal cleanup and protected-client checks. Do not
claim alpha completion or broaden rollout before reviewing that evidence.
