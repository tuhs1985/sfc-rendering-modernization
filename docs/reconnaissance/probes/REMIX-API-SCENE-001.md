# REMIX-API-SCENE-001 — Run164 isolated direct API material/mesh submission

Sponsor authorized API-path experiment after Run163. Keep accepted ordinary D3D9
gameplay host/settings/runtime1.5.2 unchanged. Do not silently promote this as a
D3D9 indexed-draw proof: experimental backend submits SDK meshes/instances.
Engine-side scene/camera/identity and existing GPU output/ACK/compositor remain.

Use existing pinned API0.6.4 header/runtime. Follow NVIDIA's exact-source
[SDK instructions](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/documentation/RemixSDK.md)
and [implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_remix_api.cpp).
CreateMaterial queues registration/preload, CreateMesh copies surface arrays and
queues registration, SetupCamera/DrawInstance enqueue scene state. Success is
NOT inferred from a handle: verify actual first/settled returned pixels and GPU
completion. Destroy meshes before materials; drain queued retirement before SDK
Shutdown owns registered-device teardown.

## Implementation boundaries

- Separate tools/remix_api_proof host/build/fixture, explicitly offline-only.
- Reuse existing replay parser, raw transforms and multi-scene retained registry.
  No source model conversion from game-folder models and no saved ship template.
- Register group-matched accepted DDS color/emission/roughness with current
  material scalars. No recompression, appearance tuning or duplicate UV flip.
- Copy native per-corner position/normal/UV exactly into HardcodedVertex; rebase
  each group's indices, preserving triangle order and assignments.
- Explicitly transpose camera matrices to vendor column-major storage. Fold the
  captured viewport into projection so full output retains source screen-space
  placement; verify algebra offline. Model3x4 remains native row-major arithmetic.
- Reuse image/quality controls and light adapter, same surface pools/fences and
  first-frame fixture. No file-watched USD material publication on this route.
- Native mock tests validate actual passed SDK arrays, values, transforms,
  lifecycle/failures. Actual GPU tests must follow; mocks are not renderer proof.

## Controls, bounds and acceptance

First compare four-owner/three-content captured fixture with Run163 first-image
control; same432images and settings. One startup Present, no fixed warm-up count.
Require per-owner drawing, matching projection/coverage, material response in the
FIRST output and stable delivery, clean leases/exit. Negative emission/material
control distinguishes loaded maps from ordinary diffuse fallback. Retain both
first/settled images and provenance. Measure initial-ready output, do not promise2s.

Keep existing32owners/64asset revisions, packet/image dimensions/byte budgets,
90s intended runtime window/5min workflow,32MiB supervisor log envelope and20GB
aggregate. No live SFC launch, public issue posting, runtime upgrade, replacement
suppression, full-scene migration or final architecture selection in this proof.
Stop at isolated qualified result or a concrete supported-API incompatibility.

## Run164 disposition

See [run record](../../runs/2026-10-24-codex-api-scene-proof.md). Explicit SDK
mesh/material delivery, first-output emission response, sharing and late assets
demonstrated offline. Four current-route controls exit cleanly using registered
Device9Ex PresentEx, not the SDK Present wrapper used by the first two failed
teardown attempts. Vendor warning remains, as on the normal reference.

Overall PARTIAL: full initial cohort4.217–4.244s, not sub2s; camera placement/scale
differs from intercepted route despite algebraically verified viewport folding.
No cross-route pixel parity or gameplay readiness claim. Next smallest action is
projection-oracle qualification offline; do not silently promote this backend.
