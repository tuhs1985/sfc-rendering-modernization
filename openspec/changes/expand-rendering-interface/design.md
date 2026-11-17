# Rendering interface design

## Boundary

Expose SFC's qualified source data after the existing scene decoder and before adapter-specific conversion. Reuse the [scene view](../../../docs/reconnaissance/scene-contract-v1.md), current frame and asset transport, and existing identity and lifetime rules. Start with an offline consumer of the same data. Introduce wire changes only for newly qualified data that the existing transport cannot carry.

The Remix adapter continues using ordinary D3D9 meshes plus its material, light and output interfaces. A future UE5 adapter can ingest the same assets and instances, apply its own coordinate and material conversions and update runtime meshes. Its rendering and GPU return path require separate qualification. [NVIDIA fixed-function compatibility](https://docs.omniverse.nvidia.com/kit/docs/rtx_remix/latest/docs/introduction/intro-compatibility.html) · [Epic runtime mesh component](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/GeometryFramework/UDynamicMeshComponent)

## Coverage at the merged alpha

| Family | Current exposure | Next usable evidence |
| --- | --- | --- |
| Ships, supported fighters and break fragments | Fresh geometry, source UVs/normals, image associations, camera and instance state. Supported break fragments have independent poses. | Exercise asset sharing, offscreen updates, retirement and fragment motion in the independent reader. Keep unsupported LODs and fighter formations explicit. |
| Materials and damage | Source images and group bindings. Live damage selector/family with separate mapping. Remix-specific material derivation and decal application. | Expose source bindings and reversible damage through the reader. Preserve primary and secondary image-role evidence. |
| Scene lights and weapon lights | Scene state and a frame-keyed native effect-light bank. Remix applies its own radiance, shape and gain. | Retain the source values and distinguish persistent scene state from transient banks. An exact weapon owner remains optional pending evidence. |
| Phasers, other beams, projectiles, explosions and sprites | Surveyed effect classes, quad submissions, resources and partial atlas/state joins. A renderer cannot replay every effect from this evidence. | Start with one verified quad path and prove producer, exact geometry/UVs, texture revision, effective draw state, frame and order. Keep beam endpoints, widths and ownership optional until observed. |
| Shields and cloak | Shield draw context and additive depth-tested state are observed. Native insertion preserves shields. Cloak and exact shield batch ownership remain open. | Verify batch-exclusive data before attempting a portable rendering contract for either family. |
| Sky, stars/dust, grid, targeting, tactical UI and cursor | Native drawing remains active. The sponsor identifies `space##.mod` as the skybox background, and earlier capture confirms loads of several numbered space models. | Trace a selected space model to its draw and texture bindings, then establish camera coupling and depth/order. Qualify the other world and screen passes separately. Treat any external cursor as a distinct presentation capability. |

Use the [family map](../../../docs/reconnaissance/rendering-family-map.md), [interface audit](../../../docs/reconnaissance/2026-11-03-renderer-interface-exposure-audit.md) and [frame provenance audit](../../../docs/runs/2026-11-12-codex-frame-provenance-audit.md) as evidence. The latest implementation and run results take precedence over older inventory rows.

## First extension

Candidate is the already observed `fx0.bmp` four-corner path from Run169. Check the archived evidence for the exact producer and texture version at submission. A shared flush, class name, or atlas filename alone cannot establish a draw association. Carry the proved primitive, indices or topology, vertex colour, UVs, coordinate space, blend/depth/cull state and order only where the fixture can verify them. Start with offline replay and compare against the captured event. If the evidence is missing a field that affects rendering, isolate that join in a narrow observation before adding a live channel.

Asset bytes publish on identity/revision change. Frame-local records carry the exact frame and ordering and use bounded storage. Slow consumers drop obsolete frame data and report gaps. Live production keeps its current rendering-thread allocation, wait and I/O constraints. Native drawing continues for unsupported or incomplete effects. The first consumer uses no GPU output-return interface. Any future insertion still requires proven colour/depth/coverage provenance and exact frame matching.
