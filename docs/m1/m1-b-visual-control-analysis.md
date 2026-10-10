# M1 bounded visual-control analysis — 2026-09-19

Historical status (2026-09-19): **ADDITIONAL BOUNDED ANALYSIS REQUIRED**. The sponsor's 2026-09-19
instruction authorizes investigation of one reversible, object-specific visual
intervention. It does not change the CDD, select a renderer, or establish formal
TRL 4 completion. No intervention was installed in this run.

## Available state and examined candidates

| Candidate | Evidence | Adjudication |
|---|---|---|
| Semantic targeting | The existing component validates `tEntityShip` at `0x004162B9`, its `+0x88` visual, `t3DVisual_Model` at `0x0042FD3F`, and mainline `tModel0` at `0x0042E4B2` with return `0x0042FDD5`. Two distinct chains were observed in M1-A-RT-001/003. | **CONFIRMED** owner/model/mesh identity; suitable targeting predicate. |
| Material/tint | `tModel0` reads fields `+0x10/+0x14/+0x18` and calls manager vtable `+0x140` at `0x0042E557` and `0x0042E620`. The ownership map explicitly leaves exact material layout open. | **SPECULATIVE** as a tint control. No field-to-visible-color relationship is proved. |
| Manager mode | Exact-build vtable `0x007B8D4C` slot `+0x50` resolves to `0x006A96E0`. `tModel0` calls it at `0x0042E4D4/0x0042E4DF`, supplying either `tModel0+0x1C` with the high bit cleared or default value `5`. It stores only values `3..5` at manager `+0x1ECC`; `0x006AC16C` and `0x006AC909` read that state to alter polygon-processing flags. | **STRONG HYPOTHESIS** that changing the mode changes the rendered image. The exact visual effect, batch timing, and state-restoration boundary are not proved. Manager state is shared; an override could bleed into another object. |
| Manager slots `+0x48/+0x58` | Resolved to `0x006A9670/0x006A9620`. They set manager fields `+0x1EC4/+0x1EC8` and `+0x1EBC/+0x1EC0`, respectively, from values chosen by `tModel0` flags. | **CONFIRMED** state setters, **SPECULATIVE** visual control and object isolation. |
| LOD override | Visual `+0x120` and selected child `+0x160+LOD*4` are known. | A per-visual LOD change might be reversible but would not guarantee an unmistakable effect or preserve the intended mesh; not selected. |
| Transform handoff | Ship render obtains a matrix-like object through virtual `+0x6C` and hands it to manager virtual `+0xE4` at `0x00416323`. | Changing it might move a ship visually, but the pointer's ownership/copy lifetime and render-only isolation are unproved; not selected. |
| Generic geometry | `0x006AB410` can correlate downstream activity, but routine interception processed 32.4 million calls and coincided with a 3–5-second stutter in M1-A-RT-002. | Keep this diagnostic hook **disabled**. It is too late for semantic targeting and too costly for the proposed intervention. |

The most promising *candidate* is a bounded manager-mode change during one
validated `tModel0` owner scope. It is **not selected for implementation yet**:
the original `tModel0` method does not visibly restore manager `+0x1ECC` before
its `ret 10h` at `0x0042E64D`. A shared cached value could affect subsequent
polygons, other owners, or UI. Likewise, a changed value may be visually
subtle or invisible in the chosen fixture. These are risks, not observed defects.

## One missing relationship and next action

Determine whether manager `+0x1ECC` has a bounded owner-local lifetime from
the `tModel0` `+0x50` call to polygon consumption, and where the original value
is safely restored or overwritten before another owner's rendering. First do
a narrowly scoped static trace of the existing `+0x1ECC` read sites
(`0x006AC16C`, `0x006AC909`, `0x006AD169`, `0x006AD266`) and the `tModel0`
call/return. If static evidence remains ambiguous, define a read-only,
scene-gated, per-owner sampled probe before runtime: capture manager value at
the `+0x50` call and at visual exit, plus the next owner's entry, with a small
frame/hit/file envelope. Do not change a mode value until visual effect and
cross-owner isolation can be defended. No raw polygon firehose is needed.

Success for that investigation is a specific candidate override and restore
point with an explicit per-owner correlation rule; failure means consider one
other bounded visual-state candidate or report BLOCKED. This record does not
claim an on-screen effect, object-specific visual modification, or sponsor
runtime readiness.

## 2026-10-10 continuation — selected copy-only RGB intervention

The sponsor directed continuation. The mode candidate is rejected for this
first intervention: `0x006AC909` reads the shared mode during a deferred path,
and the setter does not flush or restore it. A mode override would need more
state/batch isolation work than this proof requires.

The mainline polygon path exposes a simpler data control. Exact instructions:

- `0x0042E529..0x0042E534` passes Model0 argument 2 to manager slot `+0x13C`.
  `0x006ABFB0` stores that pointer at manager `+0x558`.
- `0x0042E546..0x0042E557` passes count `Model0+0x10` and pointer list
  `Model0+0x14` into slot `+0x140` (`0x006AC5A0`). This forwards them to
  polygon preparation `0x006ABFC0` through slot `+0x180`.
- `0x006AC028..0x006AC03F` reads each polygon's DWORD `+0x04` index and forms
  `source + index*36`. `0x006AC105`, `0x006AC112`, and `0x006AC121` read
  bytes `+0x06/+0x05/+0x04` from that entry and normalize them into color
  channels. Lighting may multiply them; the unlit path copies them directly
  to prepared vertices at `0x006AC3D6..0x006AC3E8`.
- `0x006AC4FD/0x006AC51A/0x006AC53A` calls the established `+0x184` anchor.
  `0x006AB535..0x006AB598` packs those float channels into vertex diffuse
  color; `0x006AB5E0..0x006AB5EC` copies vertex data into the batch. The
  batch therefore retains vertex values rather than the source-array pointer.
- `0x006ABF9F` clears prepared-vertex flags on every Model0 source init,
  preventing a previous owner's prepared color cache from being reused.

These byte/field/call relationships are **CONFIRMED static observations**.
Their live interpretation as a useful visible tint is a **STRONG HYPOTHESIS**
until a sponsor-operated runtime test. No full material layout is claimed.

Selected implementation: copy the source entries referenced by one validated
owner's primary polygon list into fixed component storage, change only RGB
bytes `+4/+5/+6` to `255/0/255`, and substitute only that Model0 invocation's
source argument. Preserve flags, alpha, textures, geometry, transforms, modes,
and original control flow. Magenta is symmetric under red/blue ordering and
provides a strong visual contrast without needing to classify channel order.
Only the first validated mainline owner epoch is selected; retirement must not
retarget another epoch. The effect uses a short baseline/on/off time window.

Bounds: at most 4,096 primary polygons and 256 source entries (9,216 bytes per
thread buffer). Guard every source/list read and reject out-of-range indices or
arithmetic overflow. Keep the original source pointer as semantic evidence;
record the effective copy pointer, entry count, original sample RGB, applied
RGB, and override/restore result. Fail open on rejected data or saturation.
Do not enable the geometry hook.

At visual exit, restore manager `+0x558` only if it still points to the copy.
The original Model0 damage pass can install its own temporary source; preserve
that renderer-authored state if present. Stop must drain live tinted scopes
through the still-installed visual-exit hook before removing hooks. The copy
storage/DLL remains valid until process exit. Offline tests must cover this
drain behavior and failed restoration as well as snapshot boundaries.

Unknowns retained for runtime: model flags/lighting/texture interaction may
weaken the visible tint, not every ship surface need use the primary source,
and the first render-owner epoch is not labeled as player versus opponent.
The proposed effect is diagnostic and does not meet visual-quality or formal
TRL 4 requirements.

## Runtime adjudication — 2026-10-10

Live-tint uncertainty is superseded for the tested fixture by
[M1-B-RT-001 evidence](evidence/M1-B-RT-001-20261010-visual-tint.md): 1,179
target-owner substitutions/restores, two coherent owners, sponsor observed
Klingon enemy magenta then normal and functional play. Hooks restored, normal
exit, unchanged client hashes. **CONFIRMED** bounded visible-control proof,
not broad coverage, new downstream capture or formal TRL 4 completion.
