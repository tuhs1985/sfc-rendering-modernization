# Native foreground preservation — shield-first interface increment

## Current direction — Run221,2026-10-29

Actual SFC ordering failed:shield captured0/replayed0;ship also covers pause text.
Shield replay is PARKED. Offline proofs below are historical mechanism evidence,
not an in-game repair. Target returned colour+physical depth insertion into the
native scene before effects/text,with exact-frame readiness and qualified batch
ownership. [Run221](../runs/2026-10-29-codex-native-insertion-reassessment.md). No new sponsor launcher ready.


Current:2026-10-28 Run219 **PAUSED / NOT READY FOR GAMEPLAY**. Draft native
capture/assembly/hook connection exists and focused builds/tests pass; full
Runtime/Remix foreground fixture is not run. See [Run219](../runs/2026-10-28-codex-native-shield-connection.md)
and the authoritative handoff. Remaining MSAA compatibility review precedes
standalone qualification. The sequence below remains implementation requirements,
not a claim that every gate has passed.
Keep the Run215 solid-hull repair and source-frame transaction. No height shift,
depth bias,forced shield depth writes,black key or whole-scene Remix conversion.

## Established connection points

- Existing tEntityShip render routine uses the primary visual at owner+0x88.
  Mainline visual render call0x0041655A is followed by helper0x004103E2 and,
  conditionally, shield state at owner+0x1BC.
- Shield call0x004165AA ->0x00426563, return0x004165AF. This provides an
  owner-relative native span, not a new arbitrary global rendering phase.
- Known manager shield path selects the shields.bmp ID and requests additive
  blending/depth writes off. Historical translated draw-context evidence matches
  that behavior in303samples;one other flush-state sample is explicitly excluded.
- Opaque depth-writing work can follow these shield contexts before Present.
  A single global opaque-then-transparent cut has NOT been established.

## Required small extension

The existing transaction retains a complete, already flattened native colour
image plus depth. It needs a way to preserve the selected ship's foreground
contributions and apply them AFTER matched replacement colour. Keep native
shield appearance; do not make Remix interpret its material or light it anew.
An additive contribution can be isolated/replayed, but ownership, state and
occlusion must be retained, not inferred from ONE/ONE blending alone.

Keep this interface separate from the renderer: source session/frame, owner
epoch, asset revision, viewport/camera signature, native pass identity and GPU
resource lifetime accompany the foreground work. The current returned colour
and physical hull-depth contract remain renderer outputs. Foreground remains
native SFC work. Source-frame pairing must include all three.

## Implementation sequence and unresolved facts

1. In an isolated fixture, qualify bounded retention of the exact native draw
   resources/state (or a genuine independently captured foreground layer).
   Prefer supported D3D11/ReShade operations. No unqualified recreation of the
   shader, blend math, native UVs or vertex format. Metadata-only survey records
   do NOT contain enough data to replay an arbitrary draw.
2. Associate the selected owner+0x1BC span with its native resource selection,
   translated draw(s), pipeline and resource epochs. The entry state-change
   flush can include earlier queued geometry: do not label every flush inside
   the span as exclusively shield-produced. Filter with qualified state/resource
   and producer information, preserving unknown work unchanged.
3. Retain required dynamic buffer contents for the SAME source frame before
   native reuse. Holding a buffer COM pointer alone does not freeze its contents.
   Preserve immutable shader/state/texture interfaces by owned lifetime. Fixed
   GPU buffers/slots must be prepared outside SFC callbacks; callback work has
   no allocations, CPU readback, waits, image conversion or file access.
4. In a focused fixture, prove native background + replacement + retained
   foreground assembly. Apply shield only where late hull composition overwrote
   native pixels, otherwise effects outside the hull would be doubled. Respect
   front/back shield visibility and occluding retained objects; using a saved
   flat shield rectangle is insufficient. Do not blindly reuse native depth
   from a suppressed hull as though it still contains that hull.
5. Fit any capture/stencil/depth resources into the existing128MiB controlled
   output budget: Run215 already uses126.5625MiB conservatively. Another fullHD
   texture cannot simply be added. Qualify reuse/reduction of existing resources
   before allocating additional planes; do not silently raise the cap. Snapshot
   geometry/buffer storage has its own explicit bounded accounting.
6. Only then connect the default-off shield-first path and prepare one sponsor
   checkout. Missing/stale foreground data must participate in the same
   replacement readiness/recovery transaction; do not present a knowingly
   incomplete suppressed frame or force permanent disable on a routine gap.

No supported earlier insertion point is assumed merely because the native
span is known. The asynchronous Remix output is currently qualified against a
closed source frame at Present. Moving that operation earlier without changing
how the native passes are retained would mix frames or miss output deadlines.

## Rejected shortcuts

- Shift ship height/bias: changes valid geometry placement without preserving FX.
- Force depth writes on shields: changes native rendering and does not preserve
  partial additive colour over the replacement.
- Recover alpha/additive colour from final native RGB: saturation loses data.
  Two different shield contributions over a bright native background can both
  clamp to white but require different output over a dark replacement. Run217
  includes an explicit counterexample; a colour-difference patch is not general.
- Replay all later draws or use a detached overlay: provenance, mutable resource
  versions, UI, depth and frame correspondence remain unsatisfied.

## Proportional validation

Use one focused resource-lifetime/foreground-composition fixture first. Test
front/back overlap, unchanged pixels outside the hull, frame/owner mismatch,
retirement and resource reuse. Broad regression renewal is justified only when
shared presentation/suppression code changes. A formatting-only source change
with identical executable must not by itself cause another GPU campaign; any
qualification-process adjustment needs explicit equivalence evidence and must
not amount to editing old receipts to claim unrun tests.

No further general combat survey is needed to identify this shield context.
If a native producer-to-resource join remains missing during implementation,
observe only this span/resource/state and its draw descriptors under a small
fixed cap; no ship payloads,continuous screenshots or broad2GiB recapture.

## Run220 connection result

The bounded original-shader shield retention and same-frame masked assembly are
now offline qualified. [Run220](../runs/2026-10-28-codex-native-shield-connected.md)
records actual Remix pixels, native front/back/occluder tests, source/output faults,
resource recreation and clean hook ACK. D24S8 reuses the existing history planes;
no extra full-size output surface. Unknown/sample-frequency/coverage-dependent
shaders, partial sample masks and unsupported contexts reject. Single-sample
foreground replay is not a claim of exact native8MSAA edge matching. Actual SFC
shield appearance/unload remains the next sponsor checkout. The earlier plan
above is historical rationale, not a request to redo discovery.
