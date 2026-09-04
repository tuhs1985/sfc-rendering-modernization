# SFC Rendering Modernization — M0 / TRL 3 Critical Function Proof

## 1. Executive result

**PASS.**

M0 demonstrated a stable semantic rendering ownership chain from two distinct
runtime `tEntityShip` instances through `t3DVisual_Model` and `tModel0` into
the previously confirmed graphics-manager, batch, native D3D3 draw, and
presentation path. Ship-owner, visual-model, selected mesh/LOD, source, and
transform-handoff identity remain identifiable before collapsing into generic
polygons and cached state.

Static RTTI, vtable, field, and call reconstruction corroborate bounded runtime
pointer correlation. The client remained responsive, accepted normal tactical
control, and exited normally. Client files and hashes were unchanged. The
result establishes a defensible upstream semantic seam while retaining
`0x006AB410` as a confirmed downstream validation anchor.

## 2. Rendering path map

```text
tEntityShip owner — 0x004162B9
  [ship identity; visual +0x88; transform handoff]
  -> t3DVisual_Model render/LOD owner — 0x0042FD3F
     [model/source/LOD identity; child array +0x160]
    -> selected-child call — 0x0042FDD2
      -> tModel0 mesh owner — 0x0042E4B2
         [mesh/LOD identity; source/count/group fields]
        -> manager source — 0x006ABF80 / 0x006ABFB0
          -> polygon preparation — 0x006ABFC0
            -> generic accumulation — 0x006AB410
              -> batch flush — 0x006AB380
                -> IDirect3DDevice3::DrawIndexedPrimitive — 0x006AB3C0
                  -> scene end/presentation — 0x0069E3D0 / 0x0069EB90 / 0x006A84B0
```

See the [semantic ownership map](m0-semantic-ownership-map.md) and curated
[semantic function map](m0-semantic-function-map.csv) for exact identities,
fields, links, and confidence classifications.

## 3. Candidate rendering boundary

The defensible modernization seam is a cooperating chain:

- primary ship owner: `tEntityShip` method `0x004162B9`;
- model/LOD owner: `t3DVisual_Model` method `0x0042FD3F`;
- mesh/source owner: `tModel0` method `0x0042E4B2`;
- downstream correlation anchor: manager source/polygon path through
  `0x006AB410`.

The chain retains stable ship, model, selected mesh/LOD, source, and
transform-handoff identity. At the manager source handoff the parent
relationship ceases to be explicit; by polygon preparation it has collapsed to
source/polygon lists, counts, flags, and cached manager state. Confidence is
**CONFIRMED** for RTTI identities, stable runtime objects, call relationships,
source identity, and downstream convergence.

Known exceptions and breaks:

- a third `tModel0` owner returned to `0x00509843` without the captured
  visual-model parent; it is a finite, confirmed, unclassified exception;
- the two ship owners were not labeled player versus target;
- exact material/texture-owner fields and hardpoint/effect ownership remain open;
- UI, sprites, and tactical effects may use cooperating owner paths;
- the launcher-selected downstream wrapper is an observation point, not an
  architecture selection.

## 4. Dynamic proof

### Hypothesis

Distinct engine-side ship owners remain identifiable through visual-model and
mesh/LOD selection and converge only after entering the shared manager
source/polygon path.

### Probe

M0-RT-001 first established the low-level path using probe version 0.2. The
continuation used bounded probe version 0.4 profiles M0-RT-002 and M0-RT-003.
All profiles used exact-address temporary breakpoints, independent hit caps,
duration and output safeguards, launcher-aware waiting, and elevation. Full
configuration, launch, cleanup, and evidence fields are in the
[capture runbook](probes/m0-probe-capture-runbook.md).

### Initial low-level proof

Run `20260904-100033` produced 18,017 samples in 51.766 seconds:

- scene_begin, scene_end, engine_present, surface_present: 4,000 each;
- batch_flush: 1,000;
- draw_indexed_call: 1,000;
- model_parse: 17;
- `scene_end -> engine_present`: 4,000;
- `engine_present -> surface_present`: 4,000;
- `batch_flush -> draw_indexed_call`: 976;
- scene and indexed draws used the same Device3 pointer,
  `0x127E8B38`;
- the stable batch owner was `0x04A00038`.

Run `20260904-100901` added the higher boundary and produced 16,276 samples
in 40.094 seconds:

- geometry_submit: 1,500;
- batch_flush and draw_indexed_call: 1,000 each;
- model_parse: 16;
- geometry manager `0x04980038`, Device3 `0x127E7F70`, and batch
  `0x04981F84` were stable for all 1,500 submissions;
- geometry callers were `0x006AC503` (1,238), `0x006AC520` (258), and
  `0x006AC8EB` (4);
- captured geometry arguments were generic values dominated by vertex count
  3, zero, an integer selector, and flag 1.

The client remained responsive during each capture and exited normally.
`stop_reason=process_exit` was recorded. Temporary breakpoint bytes were
restored or discarded with process exit.

### M0-RT-002 mesh/source owner

The owner profile was limited to 5,212 accepted samples, 180 seconds, exact
address filters, independent caps, and a 2 MB safeguard. Run
`20260904-103417` recorded exactly 5,212 samples in 84.734 seconds, stopped on
process exit, and produced a 1,155,344-byte CSV. Three stable `tModel0`-like
owners reached manager source calls at `0x0042E527/0x0042E534`, polygon calls
through `0x006AC6D6/0x006AC71F`, and stable manager `0x04950038`.

Static follow-up identified `tModel0` and parent `t3DVisual_Model` RTTI,
vtables, fields, and the selected-child call at `0x0042FDD2`.

### M0-RT-003 ship/model/mesh correlation

The discriminating profile added only `0x0042FD3F`, `0x0042FDD2`, and
`0x0042E4B2`. It was limited to 6,364 accepted samples, 120 seconds, and the
same 2 MB safeguard. Run `20260904-104217` recorded exactly 6,364 samples in
64.718 seconds, stopped on process exit, and produced a 1,412,572-byte CSV.

| `tEntityShip` | `t3DVisual_Model` | `tModel0` | Source | Hits |
|---|---|---|---|---:|
| `0x1CC1A1D8` | `0x1CC11808` | `0x1CA3C3EC` | `0x0492365C` | 194 |
| `0x1CAE86C0` | `0x1CAE0E48` | `0x1CA3C0E0` | `0x1C9BB7F0` | 190 |

Both chains used manager `0x04980038` and converged into 1,500 generic
submissions, 1,000 batch flushes, and 1,000 native indexed-draw call sites.
Static reconstruction independently identified `tEntityShip` RTTI, vtable
`0x00796F0C`, visual pointer `[this+0x88]`, and a matrix-like transform
handoff before the visual-model call.

### Conclusion

The hypothesis is **CONFIRMED**. Two ship owners remained distinct through
visual-model and mesh/LOD selection and converged only in the shared manager
path. Normal tactical operation was not destroyed. This is the required
critical-function proof of an observable, useful semantic rendering seam.

## 5. Information-loss map

| Boundary | Before | After | Confidence |
|---|---|---|---|
| `tEntityShip` to `t3DVisual_Model` | stable ship, visual pointer, transform handoff | stable model/source/LOD owner; ship recoverable by parent | CONFIRMED |
| `t3DVisual_Model` to `tModel0` | model/source identity, LOD fields and selected child | stable mesh/LOD owner and source/group fields | CONFIRMED |
| `tModel0` to manager source | parent ship/model recoverable in call chain | source pointer/counts; no explicit parent argument | CONFIRMED |
| Manager source to polygon preparation | source identity and manager state | polygon-list/source identity, counts and flags | CONFIRMED |
| `0x006AB410` to manager batch | generic polygons and cached manager state | FVF `0x1C4`, vertex/index buffers and counts, primitive mode | CONFIRMED |
| State change or capacity transition to `0x006AB380` | pending batch plus cached texture/render state | one or more generic D3D3 draw submissions | CONFIRMED |
| `0x006AB3C0` native indexed draw | Device3, primitive type, FVF, vertices, indices, counts, flags | generic legacy graphics command; no gameplay/model/material owner | CONFIRMED |
| `0x006A84B0` presentation | primary/back/render-target surfaces and flip/blit selection | presented surface/image | CONFIRMED |

Ship identity ceases to be explicit at the `tModel0` to manager-source
handoff. Model/selected-mesh identity collapses to source/count representation
there. Material intent becomes cached texture/render state before
`0x006AB410`; its exact object layout remains open. Object transform intent is
handed to the manager above the visual call and becomes generic manager/matrix
state before polygon submission. Hardpoint, effect, shield/damage, and UI
ownership were not adjudicated.

## 6. Evidence table

| Reference | Evidence | Classification |
|---|---|---|
| `0x004162B9`, vtable `0x00796F0C`, COL `0x007BF2A8` | `tEntityShip` RTTI; visual `+0x88`; transform handoff; two runtime owners | CONFIRMED |
| `0x0042FD3F`, vtable `0x007985A4`, COL `0x007C0938` | `t3DVisual_Model`; source `+0x158`; LOD fields and child array | CONFIRMED |
| `0x0042FDD2` | selected visual-model child call into `tModel0` | CONFIRMED |
| `0x0042E4B2`, vtable `0x007983E8`, COL `0x007C07C0` | `tModel0`; stable mesh/source owner and group fields | CONFIRMED |
| `0x006ABF80 / 0x006ABFB0 / 0x006ABFC0` | manager source count/pointer and polygon preparation | CONFIRMED |
| IID data `0x007BB198..0x007BB1D8` | IDirect3D3, Surface4, Surface3, DirectDraw4, DirectDraw2 GUIDs | CONFIRMED |
| Wrapper `+0x30,+0x34,+0x38,+0x3C` | primary, back, target, z-buffer Surface4 pointers; z attach at `0x006A848C` | CONFIRMED |
| Wrapper `+0x40,+0x44,+0x48,+0x4C` | Device3, Viewport3, DirectDraw4, Direct3D3 | CONFIRMED |
| `0x0069E300/0x0069E36A` | engine scene begin / Device3 BeginScene | CONFIRMED |
| `0x0069E3D0/0x0069E41B` | engine scene end / Device3 EndScene | CONFIRMED |
| `0x006AB410` | concrete manager virtual `+0x184` geometry accumulation entry | CONFIRMED |
| `0x006AB380/0x006AB3C0` | batch flush / Device3 DrawIndexedPrimitive | CONFIRMED |
| `0x0069EB90/0x006A84B0` | engine present / Surface4 Flip-or-Blt wrapper | CONFIRMED |
| Run `20260904-100033` | 18,017 samples; same `0x127E8B38` Device3 in scene and draw | CONFIRMED |
| Run `20260904-100901` | 1,500 submissions from three callers; stable manager/device/batch identities | CONFIRMED |
| M0-RT-002 `20260904-103417` | 5,212 samples; stable mesh/source paths; 1,155,344-byte output | CONFIRMED |
| M0-RT-003 `20260904-104217` | two ship/model/mesh chains; downstream convergence; 1,412,572-byte output | CONFIRMED |
| Third `tModel0` `0x18422324`, return `0x00509843` | finite non-captured-parent path, 131 hits | CONFIRMED path; SPECULATIVE role |
| `0x0042FEF9` | 17 and 16 model-parser hits preceding tactical geometry | CONFIRMED execution; STRONG HYPOTHESIS role |
| `0x0041C271` | zero hits in both bounded runs | INCONCLUSIVE |
| Client hashes after testing | MD5 and SHA-256 match the approved original | CONFIRMED |
| Direct native disposable run | window creation succeeded; Device3 path failed at `0x0069D782` | CONFIRMED negative observation |

Raw logs are generated and ignored under the four referenced run directories.
The analyzer generates JSON summaries and evidence packets beside each log.
Curated maps, probes, analyzer, report, and run records are versionable. The
executed M0-RT-003 probe SHA-256 was
`AB1E590C3256C0C19875EF4527888D56CE48F790E30235E2F60511BA805135AC`.

## 7. Open technical questions

1. What exact `tModel0` fields own material groups and texture resources
   before manager state binding?
2. Which bounded owner paths cover the observed non-ship `tModel0` entry,
   tactical effects/sprites, and UI?
3. Which observed `tEntityShip` is player versus target, and can a unique
   model/texture label it directly?
4. What is the exact transform structure, and at which state call does
   per-object transform identity cease to be recoverable?

These define integrated validation coverage and exceptions; they do not
undermine the demonstrated ship/model/mesh seam.

## 8. M1 implications

**M1 JUSTIFIED — TRL 3 semantic seam proven sufficiently to plan integrated
validation.**

Future TRL 4 planning is justified around observation/tag propagation across
the composite `tEntityShip -> t3DVisual_Model -> tModel0` seam, using
`0x006AB410 -> 0x006AB380 -> 0x006AB3C0` as the downstream validation anchor.
Integrated validation must bound material/texture recovery and the finite
non-ship/effect/UI exception set.

This result selects no final renderer architecture and performs no M1 work.
