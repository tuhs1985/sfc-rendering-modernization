# Renderer boundary audit — 2026-10-27

Scope: read-only source review after Run209, before sponsor player-replacement
checkout. Sponsor then authorized documenting, committing and pushing the
accumulated work. No runtime refactor, build, gameplay or change to the prepared
test was part of the audit. The
[renderer-independent boundary gate](../decisions/2026-10-18-renderer-independent-boundary-gate.md)
remains **OPEN**. No new capability requirement or renderer architecture chosen.

## Assessment

**Partially separated; not yet interchangeable.** A future renderer can reuse
SFC ownership/geometry/camera work. Today it would also require changes in shared
startup and asset preparation, beyond implementing its own graphics adapter.
ReShade event handling is separated from the compositor; the latter still
requires today's D3D11 resource and synchronization interfaces.

| Boundary | Confirmed current implementation | Implication |
| --- | --- | --- |
| Captured scene | Native mesh/images/state preserved; `scene_bundle.py` has no renderer/SDK imports and `live_owner_decode.h` qualifies native arithmetic independently. Plain system-D3D9 proof exists. | Reusable source foundation, not proof that all live backends consume one common interface. The live wire still carries SFC-specific96word rows. |
| Texture conventions | `remix_coordinates.py` explicitly changes only derived Remix image bytes; original images/UVs stay unchanged. | Correct backend ownership of the conversion. However `parallel_assets.py` invokes it unconditionally and includes its policy in the derived base-asset key. Canonical content identity and backend-resource identity must stay distinct. |
| Materials/startup | `multi_scene_relay.py` constructs Remix configuration and USD paths; catalog preparation reads `remix_hash`. `async_material_checkout.py` selects pinned Remix releases and publication behavior. | A `renderer_backend` executable/runtime dictionary is not a general backend interface. Asset preparation/publication/startup still assume Remix. |
| Renderer | `d3d9_direct_host.cpp` submits ordinary D3D9 geometry, registers its device and retrieves final color/depth through supported Remix output APIs. Light/image controls also use Remix APIs. | Keep these dependencies inside the Remix backend; ordinary D3D9 geometry submission alone does not make this output host renderer-independent. |
| Return transport | `output_channel.h` / `game_output_wire.h` carry source identity, sessions, sequences and handles without SDK objects. Producer/consumer use fixed BGRA8/R32F surfaces, classic shared handles and D3D11 leases/fences. | Useful versioned transport, with API-specific sharing. D3D12 handles/resources cannot be substituted without a qualified transfer adapter. |
| Presentation | `return_addon.cpp` obtains ReShade callbacks/native D3D11 targets and calls `d3d9_game::Receiver`. The receiver/compositor do not take ReShade API objects. | ReShade can be replaced at that callback/target/depth boundary; a new presentation adapter still has to establish equivalent ordering, state restoration and synchronization. |
| Replacement coordination | `replacement_transaction.h` contains session/owner/revision/frame/generation receipts, no graphics SDK objects. `replacementStep` applies that policy alongside D3D11 imports/depth/copy/composition. | Retain common transaction meanings; separate policy and native-resource operations incrementally rather than replacing the capture architecture. |

## Important output semantics

The third returned surface is **union coverage carrying the scene anchor label**,
not independently identified per-ship picking. `normal_coverage.h` derives it from
qualified depth; `game_output_writer.h` explicitly records union coverage. This
supports the current player-only replacement and the whole rendered cohort in
additive tests. Selective multi-ship replacement must define the batch owner set
or qualified per-owner masks; it cannot infer pixel ownership from that label.

Color, depth and coverage shapes/meanings are currently established by code and
qualification. Packet version checks are not a general negotiation of color
space, HDR, depth convention, mask meaning, synchronization method or supported
formats. Fixed1920x1080 and eight-sample native scene-depth assumptions belong to
the qualified presentation implementation, not universal scene requirements.

CONFIRMED source evidence:

- [Neutral preparation](../../tools/scene_bridge/scene_bundle.py),
  [native state decoder](../../tools/d3d9_proof/live_owner_decode.h),
  [plain D3D9 consumer](../../tools/d3d9_proof/d3d9_replay.cpp).
- [Remix correction](../../tools/d3d9_proof/remix_coordinates.py),
  [parallel preparation](../../tools/remix_runtime/parallel_assets.py),
  [live coordinator](../../tools/remix_runtime/multi_scene_relay.py),
  [candidate backend](../../tools/remix_runtime/async_material_checkout.py).
- [Renderer/output host](../../tools/d3d9_proof/d3d9_direct_host.cpp),
  [output wire](../../tools/d3d9_proof/output_channel.h),
  [game-output writer](../../tools/d3d9_proof/game_output_writer.h),
  [coverage](../../tools/d3d9_proof/normal_coverage.h).
- [ReShade entry](../../tools/remix_runtime/return_addon.cpp),
  [receiver](../../tools/remix_runtime/d3d9_game_receiver.h),
  [compositor](../../tools/remix_runtime/ship_triplet_compositor.h),
  [replacement transaction](../../tools/d3d9_proof/replacement_transaction.h).

## Smallest recommended follow-up — not implemented

After the player-replacement checkout, formalize two existing boundaries:

1. Renderer operations: prepare/cache assets, update scene state, provide completed
   output and release resources. Wrap existing functions; keep Remix conversion,
   material libraries, settings and startup behind that adapter. Retain canonical
   data and content identity separately from backend-derived cache keys.
2. Completed-frame description: explicit source/batch identity, color encoding,
   depth convention, coverage meaning, extent, resource ownership and GPU readiness.
   Presentation/transfer adapters interpret their own native resources. Reject
   unsupported combinations; do not guess compatibility from a handle or API name.

No new general-purpose engine, automatic renderer discovery, redundant scene
format or full renderer rewrite is justified by this audit. Windows-specific
sharing is acceptable inside its adapter. Further backend independence requires
a second qualified consumer/output implementation; the existing portable-looking
headers alone do not close the gate. Keep the prepared runtime checkout unchanged.
