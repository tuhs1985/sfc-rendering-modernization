# Expand the SFC rendering interface

## Why

The alpha proves live ship replacement, but ordinary D3D9 draws expose only part of the information we already recover from SFC. A future UE5 adapter needs the same source assets, frame state and effects without reconstructing them from D3D9 or depending on Remix-specific conventions.

## What Changes

- Reuse the existing scene decoder and asset representation to expose a renderer-neutral view of qualified source data. D3D9 remains the submission path for Remix.
- Inventory usable data across ships, debris, lights, damage, transient effects, shields, backgrounds, tactical overlays and UI. Identify which data is live, which is observed in surveys, and which still needs a source-to-draw join.
- Prove an independent consumer can use the existing scene data before expanding capture. Then qualify one bounded transient effect end to end.
- Keep the tested alpha and the current native drawing and fallback paths available throughout development. A full UE5 renderer, broad replacement and a public SDK stability promise are outside this increment.

## Capabilities

### New Capabilities

- `render-scene-consumption` — Reusable SFC scene and effect data with explicit identity, frame provenance, and support reporting.

### Modified Capabilities

None.

## Impact

The existing source capture, scene transport and D3D9 adapter provide the starting points. The initial consumer runs offline using existing replay or captured evidence. Expansion of live capture requires a qualified source and bounded tests. The alpha ZIP and tester workflow stay on the merged release baseline during this work.
