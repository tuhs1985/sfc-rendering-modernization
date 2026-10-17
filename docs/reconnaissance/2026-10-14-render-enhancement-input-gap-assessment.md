---
status: research-complete-initial-assessment
date: 2026-10-14
scope: input-contract-and-bridge-feasibility
---

# Enhancement integration — what to capture and what to generate

## Result

The proven semantic seam is a credible source for a modern rendering consumer,
but a newer DirectX call stream alone is not the required contract. Three routes
remain distinct: repair translated D3D9 capture for Remix; explicitly submit scene
data to Remix's SDK; or build an independent renderer with optional Streamline
features. None is selected/implemented by this research.

**New CONFIRMED documentation finding:** Remix has explicit scene-submission and
output interfaces, not only automatic D3D9 interception. Its SDK may avoid relying
solely on translated draws to recover missing semantics. **STRONG HYPOTHESIS for
investigation:** our upstream data could feed this route. SFC compatibility is
unproven; no runtime claim follows from finding API declarations. [S1][S2][S3]

DLSS is a rendered-image consumer, not a mesh renderer or a replacement for
lighting/material generation. Separate ray-traced scene integration from later
Super Resolution, Ray Reconstruction and Frame Generation input contracts.
Old shim reconstruction is not prerequisite to identifying these contracts.

## Consumer requirements — documented, not SFC capabilities

| Consumer | Minimum contract to investigate | What it does not solve |
| --- | --- | --- |
| Remix automatic capture | Compatible fixed-function scene submissions, useful geometry/transforms/material state and classification | A translated API does not guarantee recoverable scene identity or capture. Historical material visibility does not establish geometry sufficiency. [S8] |
| Remix explicit API | Register triangle meshes and surfaces/materials; submit instances/transforms, camera and lights each frame; manage resource lifetime | In-game replacement, UI/depth composition and SFC-to-SDK bridge still require proof. [S1][S2] |
| DLSS Super Resolution | Input/output color, depth, motion vectors, dimensions and frame/camera constants; jitter/history/reset handling and exposure policy | Does not reconstruct missing mesh/material/lighting information. Auto-exposure can replace a supplied exposure texture. [S4][S7] |
| DLSS Ray Reconstruction | Ray-traced noisy color, diffuse/specular albedo, normalized shading normals, roughness, depth, dense motion; reflection motion or hit-distance/matrix alternative | Cannot produce a ray-traced scene from native color alone. Current guide accepts view-space or hardware depth; do not universalize older linear-depth-only advice. [S5] |
| DLSS Frame Generation | Depth/motion and HUD-less scene data, frame-consistent constants/presentation and Streamline Reflex; separate UI representation for quality | Not an initial lighting improvement; original UI and simulation timing must remain trustworthy. [S6] |

Current sources are moving upstream main documentation inspected2026-10-14.
Streamline guides identify2.14.1; inspected Remix API header identifies0.6.5.
These are research references, **not pinned runtime/build selections** or proof
of compatibility with the historical Remix1.3.6 experiment. Validate feature/API/
driver support for an eventual pinned build, not a generic 'latest DLSS' label.

## Local seam input map

Confidence labels refer to evidence, while action classes distinguish capture
from generation. UNKNOWN means not established, not proven unavailable.

| Information | Existing SFC evidence | Action / gap |
| --- | --- | --- |
| Owner/model/mesh/source identity | CONFIRMED M0/M1 mainline and two-owner tests; opaque epochs remain separate | Already proven association. Capture a bounded export identity/version; never treat recycled pointers as durable IDs. |
| Full geometry/topology | Model0+8 vertex count,+C position base,+10 primary polygon count,+14 list; indexed positions/corners read live; whole452-polygon private graph used in RT-010 | Additional capture/qualification. Existing corner packet is only64 polygons/8 corners and omits UV values; full graph-copy success is not complete external mesh export. Validate all selected indices, polygon winding/triangulation and per-corner splits before rendering. |
| Surface directions | CONFIRMED sampled normal-like geometric alignment and native lighting use; model-local interpretation STRONG HYPOTHESIS | Capture raw floats; qualify normal space/sign/magnitude. Native vectors are sometimes non-unit. External normalization must be a documented derived copy, not a write to game data. |
| UV/material grouping | Corner+10/+14 UV accesses and polygon source index known statically; original corner payload copied by diagnostic | Capture/decode UVs and polygon-to-source grouping. Do not infer source index equals complete material/texture ownership. |
| Texture/material resources | Individual materials visible in historical utility: CONFIRMED sponsor attestation, missing original artifacts | Additional targeted resource association needed. File/pixel ownership, channel/color-space/blend semantics unknown. A controlled constant material can qualify geometry but is not faithful material reconstruction. |
| Object placement | Supplied transform at manager+6F4, composed position transform+6B0 sampled; source setter006AA550/static compositions known | Qualify coordinate system, layout and numerical mapping for a consumer.17DWORD native payload is not automatically an external4x4 matrix. |
| Camera/projection/viewport | Static manager+628/+5E4 compositions; camera influence inferred from controlled changes | Missing qualified view/projection, clip/depth conventions, viewport and camera resets. Restrict investigation to necessary setters/hand-off; no general camera-system reconstruction. |
| Lights | Native transform/light-slot accesses mapped, lighting control observed | Capture only if native light fidelity needed; types/intensity/space unqualified. One explicit controlled light can isolate renderer integration first. |
| Previous-frame identity/poses | Epoch-aware observation confirmed, no dense history export | Derived state requiring validated current/previous camera and object transforms, timestamps, LOD/discontinuity/reset policy. Sparse5s snapshots cannot serve as per-frame motion. |
| Depth/motion/albedo/roughness buffers | No validated modern, sampleable versions established by M1 | Generate in a scene renderer, or qualify an existing compatible source. Do not relabel object matrices as per-pixel motion, source RGB as albedo, or a bound depth surface as usable depth data. |
| HUD/scene separation and final composition | Original UI preserved by neutral/diagnostic tests; no replacement compositor | Additional capture/integration contract: distinguish tactical3D from overlays, align output/depth/occlusion, suppress duplicate native ship safely, retain unrelated effects/UI. Whole-image overwrite is not sufficient. |

Local evidence: [readiness review](../decisions/2026-10-14-integration-readiness-assessment.md),
[numeric proof](../m1/evidence/M1-C01-MATH-001-20261012.md),
[field map](../m1/m1-c01-corner-transform-qualification.md),
[RT-010](../m1/evidence/M1-C01-RT-010-20261013-surface-lighting.md),
[actual sampler](../../tools/m1_component/m1_corner_snapshot.h),
[historical Remix intake](2026-10-14-external-remix-handoff-intake.md).
Earlier preparation findings in source documents do not override later runtime
evidence; no critical semantic naming promoted solely from decompilation.

## Bridge feasibility and constraints

**Explicit Remix:** SDK docs distinguish the32-bit D3D9 bridge from its64-bit
renderer. Header defaults reject non64-bit ray-tracing use, with an x86 opt-in
macro; that macro is not proof of full32-bit scene-API support. A validated
bridge/serialization or64-bit consumer boundary is an investigation item, not a
drop-in DLL assumption. Native addresses cannot be copied as valid foreign-process
pointers. SDK version/header/runtime must match. [S1][S2]

SDK offers external image/output-copy facilities; availability does not prove
zero-copy, synchronization, format or interoperability with existing CE output.
Current texture APIs use resource paths and need mapping from original assets;
existing device texture handles cannot simply be passed across boundaries. [S2]

**Translated capture:** if old shim source reappears, first audit actual vertex
format/transforms and all relevant target/blit edges. Up-converting UP calls or
changing the last render target alone does not restore lost3D semantics. Offscreen
routing remains a hypothesis, not established sole failure cause. Do not recreate
unsafe COM/cache abandonment merely to match reported logs.

**Independent renderer/Streamline:** documented integrations use modern D3D/Vulkan
device/resource lifecycles; query each feature's actual requirements. The default
Windows SDK artifact/build path is64-bit. SFC isx86: bitness, synchronization and
presentation ownership must be explicit before linking any SDK into the process.
Neither modern-API translation nor visible ReShade/DXGI establishes those feature
inputs. No DirectX12/Vulkan/backend selected here. [S7][S9]

## Smallest next investigation (proposal, not implementation)

1. Qualify a **consumer-neutral single-small-ship packet** using the proven owner
   scope: complete positions, topology/per-corner vectors/UVs, source-group labels,
   transform bytes and snapshot epoch/frame/version. One owner/model first;
   preserve original data and fail open. Capture bounds must be documented before
   a new probe, not relaxed to export every frame/every object.
2. Separately resolve game-camera/coordinate mapping needed for in-game alignment.
   An independent fixed-camera mesh check can show usable geometry, but cannot
   substitute for the eventual live camera/composition proof.
3. Investigate explicit Remix SDK bridge/version/bitness feasibility against that
   packet before assuming old D3D9 proxy reconstruction is the best route.
   If rejected, retain the same packet contract for another consumer.
4. Only then propose one real light/material enhancement and reversible output
   integration. Motion/depth and other DLSS-specific buffers belong to the chosen
   renderer contract, not a broad hunt for every SFC internal field.

Success of this research is the map above and a discriminating next question,
not another color test or a claim of path tracing. No new probe/build/code,
runtime/installer/dependency update or M2 implementation authorized/performed.
Community Edition setup and approved requirements stay untouched. M1 closure
recommendation remains awaiting sponsor acceptance; research does not advance TRL.

## Primary references (accessed2026-10-14)

- S1: [Remix SDK](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/main/documentation/RemixSDK.md), components, setup/versioning/resources.
- S2: [Remix C API header](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/main/public/include/remix/remix_c.h), inspected version0.6.5; mesh/camera/instance/light/output declarations and architecture guard.
- S3: [Runtime README, Remix API](https://github.com/NVIDIAGameWorks/dxvk-remix#remix-api), explicit submission alongside/instead of Direct3D.
- S4: [DLSS Super Resolution guide](https://github.com/NVIDIA-RTX/Streamline/blob/main/docs/ProgrammingGuideDLSS.md), resources/constants.
- S5: [DLSS Ray Reconstruction guide](https://github.com/NVIDIA-RTX/Streamline/blob/main/docs/ProgrammingGuideDLSS_RR.md), required/conditional buffers.
- S6: [DLSS Frame Generation guide](https://github.com/NVIDIA-RTX/Streamline/blob/main/docs/ProgrammingGuideDLSS_G.md), input/UI/Reflex lifecycle.
- S7: [Streamline integration guide](https://github.com/NVIDIA-RTX/Streamline/blob/main/docs/ProgrammingGuide.md), feature requirements/device lifecycle/security.
- S8: [Remix compatibility FAQ](https://docs.omniverse.nvidia.com/kit/docs/rtx_remix/latest/docs/remix-faq.html), capture suitability is conditional.
- S9: [Streamline README](https://github.com/NVIDIA-RTX/Streamline#readme), current platform/build artifacts.
- S10: [Streamline constants](https://github.com/NVIDIA-RTX/Streamline/blob/main/include/sl_consts.h), temporal camera/motion convention fields; does not validate SFC conventions.
