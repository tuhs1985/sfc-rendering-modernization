# SFC Watch claims — applicable Remix capabilities and next actions

Date: 2026-10-24. Research only; no runtime, settings, implementation or installed
application changed. Builds on Run140's API review, Run138's loading experiments
and Run143's post-cleanup regression. Source statements are not binary/runtime
qualification. No new game or GPU test, download, dependency switch or commit.

## What is actually installed versus used

CONFIRMED locally:

- Managed Toolkit VERSION: `1.6.1-0+1-6-1-0.30549.7d65b007.gl`.
- Managed bundled x64 runtime exists at
  `C:\Program Files\NVIDIA Corporation\RTX Remix\deps\remix_runtime\runtime\.trex\d3d9.dll`
  (282,883,696 bytes). Presence is not a qualified standalone SDK package.
- Actual game relay `tools/remix_runtime/live_owner_timing.py` still selects
  `artifacts/d3d9-intercept/deps/remix-1.5.2/.trex/d3d9.dll`.
- Existing return dependency manifest pins 1.5.2/source
  `b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4`.
- Current host uses ordinary D3D9 meshes/draws, with supported Remix API output,
  configuration and lighting facilities. Historical direct API ship/triangle
  hosts already exist. Neither path implies all newer capabilities are enabled.
- `nvidia-smi` NOW reports RTX4070Ti / driver621.01. Earlier records617.42 are
  historical; no driver change performed here. Use this current environment for
  both sides of any new A/B, not old timings as a controlled comparison.

Installing the Toolkit does not update the pinned game runtime. Toolkit controls
also do not automatically control our separate native renderer process.

## Claim adjudication

### Release, memory and driver claims: CONFIRMED as vendor capabilities

[NVIDIA release notes](https://github.com/NVIDIAGameWorks/rtx-remix/releases/tag/remix-1.6.1)
confirm the October23 release, Minecraft API demonstration, neural rendering,
sparse/compact-buffer rendering, driver616.92 floor and material-reload changes.
Sparse rendering trades sampling quality against GPU cost; it is not a model
loading accelerator. Less memory for one feature does not promise lower total
process memory. Toolkit startup/DDS-export improvements do not automatically
accelerate our own Python asset preparation. None is an SFC performance result.

### Material reload: the strongest immediate fit — CONFIRMED SOURCE CHANGE

Release-linked runtime source
[`rtx_mod_usd.cpp` at0a6cd5b](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_mod_usd.cpp)
has `rebuildWorkerEntry`, its own upload context, dirty mesh/material/light sets,
and `applyPendingRebuild` merging changed entries into the live replacement
table. Abort handling retains the previous scene; shutdown joins the worker.
This is materially different from our pinned older reload path. It is NOT proof
that our particular master-layer edits will be incremental, textures instantly
resident or the first rendered image correct. STRONG HYPOTHESIS: using this
supported implementation could reduce current activation and late-asset stalls.
This finding elevates isolated runtime qualification ahead of custom warmup work.

### Existing async machinery: real, but not an untried magic switch

Our [Run136](../runs/2026-10-24-codex-built-in-loading-investigation.md),
[Run137](../runs/2026-10-24-codex-public-texture-prefetch.md) and
[Run138](../runs/2026-10-24-codex-vendor-texture-loading-paths.md) already tested
explicit upstream async settings, library layouts, API texture prefetch,
streaming eligibility and RTX IO. No normal-path speed fix was promoted.
The pinned renderer was not accidentally forced into synchronous compilation
by the wrapper's separate environment dictionary. Initial staging, subsequent
streaming and hot reload must remain distinct.

Reference: [pinned initializer](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_initializer.h).
Reuse these supported mechanisms/experimental flags; do not recreate a loader or
rerun identical switch tests without a new runtime/path hypothesis. Preserve all
material/map content when comparing output readiness.

### Minecraft API: supported example, separately paired package

The [release-linked header](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/public/include/remix/remix_c.h)
declares API0.6.5; the inspected
[Minecraft header](https://github.com/NVIDIAGameWorks/rtx-remix-minecraft/blob/f2c6fdaa763f45676f1576e63f8e054bf4ef16af/rtxremix-java/native/include/remix_c.h)
declares0.16.0 and exposes memory texture operations, retained instances,
material updates and separate Submit/output interop. The
[package pin](https://github.com/NVIDIAGameWorks/rtx-remix-minecraft/blob/f2c6fdaa763f45676f1576e63f8e054bf4ef16af/packman/remix-sdk.packman.xml)
is `minecraft-rtx2-71a581da-win64-release`, not the ordinary Toolkit version.
NVIDIA's [bridge instructions](https://github.com/NVIDIAGameWorks/rtx-remix-minecraft/blob/f2c6fdaa763f45676f1576e63f8e054bf4ef16af/rtxremix-java/README.md)
require paired headers/binaries and warn its header can lead main.

CONFIRMED useful example, NOT D3D7 translation, guaranteed startup improvement,
an automatic D3D12 interface, or a reason to discard D3D9. Its
[OpenGL output integration](https://github.com/NVIDIAGameWorks/rtx-remix-minecraft/blob/f2c6fdaa763f45676f1576e63f8e054bf4ef16af/src/main/java/com/nvidia/rtxremix/minecraft/gl/GlInterop.java)
imports memory and synchronizes access; this does not qualify our separate
D3D11 consumer, coverage/depth or reset behavior. Its own
[playing guide](https://github.com/NVIDIAGameWorks/rtx-remix-minecraft/blob/f2c6fdaa763f45676f1576e63f8e054bf4ef16af/docs/PLAYING.md)
warns about initial shader compilation/unfinished scenes. Direct API is not
evidence of instant first-load completion.

### Neural rendering: feature exists; hardware and composition gate remain

[NVIDIA's announcement](https://www.nvidia.com/en-gb/geforce/news/dlss-5-faster-ai-model-hogwarts-legacy-rtx-spark-laptops/)
confirms Remix's new integration and artistic controls. Do not infer every DLSS
feature works on the4070Ti: advertised DLSS5 targets include RTX50/RTX Spark;
actual per-feature support needs capability verification. DLSS Super Resolution,
Ray Reconstruction, Frame Generation and neural rendering are different options.
Generating frames inside our ship-only renderer does not generate matching
frames of the retained SFC background, weapons and UI. It cannot fix scene
synchronization or load missing materials. Do not enable it globally as a cure.

## Recommended work, in order

1. **Qualify stock1.6.1 in isolation using the existing D3D9 fixture.** Resolve
   a matching standalone package/header/dependency manifest, verify its binary
   capabilities and output interfaces. Keep1.5.2 selectable and unchanged.
   Do not run directly from the managed install or let future app updates mutate
   the test dependency. Never copy only one DLL from a bundled dependency tree.
2. **A/B the actual material path on that runtime.** Same captured assets,
   original/derived images, material settings, renderer startup policy and driver.
   Measure initial discovery, worker preparation, library activation, fully
   usable texture/material output and composition separately. Add one late asset
   to exercise incremental reload while existing ships continue. Use installed
   Nsight for a bounded owned-process timeline if attribution remains unclear.
   Verify final pixels/maps/orientation, frame correspondence, memory, device
   recreation and cleanup; first geometry arrival is not material readiness.
   Keep profiling time separate from unprofiled timing. Promote only measured
   improvement without content/appearance loss;2s remains a target, not a promise.
3. **Qualify the newer direct resource API as a backend experiment.** Obtain
   its exact paired runtime first. Feed existing neutral packets into memory
   textures/materials/retained instances; test two different owners sharing one
   asset plus an asset update. Reuse capture/registry/camera/lights/settings.
   Compare the same workload with D3D9; prove GPU color/depth/coverage return and
   explicit synchronization before any game-path adoption. No Java/Minecraft
   port, vendor patch, ABI mixing or replacement of the backend-neutral contract.
4. **Use Toolkit packaging for prepared-resource fast paths.** Qualify stable
   identity-to-prepared PBR assets and NVIDIA's packaging/RTXIO support for those
   assets. Keep fresh unknown ships supported. An RTXIO switch alone does not
   turn loose generated single-mip images into an optimized packaged asset set.
5. **Qualify image-quality features individually.** Start with native-resolution
   denoising/Ray Reconstruction comparisons, then real higher-resolution render
   plus filtered downsample. Current `quality_controls.py` explicitly rejects
   supersampling>1 because the output-copy path lacks a qualified filtered
   resolve. Do not merely unlock the number. Test sparse rendering separately
   for memory/performance/clarity, with existing crisp baseline retained.
6. **Use the Toolkit for what it contributes, not a second game renderer.**
   Create/export selected PBR materials, texture maps and prepared replacements
   through supported workflows, then load via our qualified runtime path. Its
   artist controls are useful authoring tools; keep live TOML controls independent
   unless an explicit transfer is implemented. ComfyUI/AI asset generation and
   optional headless services are later authoring work, not startup requirements.
7. **Return to owner-specific replacement after delivery qualifies.** Preserve
   synchronized depth/coverage, lifetime and failure handling; test overlap with
   grid, other ships, shields and weapons. Newer rendering features do not remove
   these SFC-specific composition obligations. Full-scene features come later.

Not recommended: install every optional service, enable every feature at once,
repeat legacy Toolkit ingestion tests, revive deleted portable installation,
remove safeguards, swap translators, or build a custom material loader before
testing the vendor's revised implementation. D3D9 remains the agnostic interface
baseline; D3D12 remains a separate future adapter gate, not provided by this SDK.

Exact next smallest action: pin/qualify a separate stock1.6.1 runtime/header pair
against the current deterministic D3D9/output fixture, WITHOUT changing normal
SFC launcher or appearance defaults. This is the recommended next increment,
not an implementation or upgrade performed during this investigation.
