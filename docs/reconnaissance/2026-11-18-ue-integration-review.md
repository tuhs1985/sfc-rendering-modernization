# UE integration review before live scene updates

November 18, 2026. Read-only engineering review of the local UE 5.8.4 proof
and the existing SFC interface. No renderer, settings, capture, game files or
package were changed. Findings are source observations and recommendations,
not newly qualified runtime behavior.

## Decision and scope

Keep the successful offline proof and its independent pixel reference as the
comparison baseline. Do not extend `AProofGameMode` directly into the live
wrapper. First qualify a small runtime adapter with reusable local geometry,
separate world transforms/camera and explicit resource ownership in a packaged
replay. This preserves the value of the proof without making its diagnostic
shortcuts the production architecture.

The project still has two separate deliverables: a renderer-independent DLL
interface and necessary support, and a UE wrapper consuming it. UE types,
object lifetimes, render resources and engine-version dependencies belong in
the UE adapter. They must not become requirements of the neutral DLL.
[Delivery direction](../decisions/2026-11-17-project-deliverables.md).

The [packaged proof](../runs/2026-11-18-codex-ue5-packaged-proof.md) established
geometry, original image sampling and recorded camera projection. It did not
establish a live scene, production material model, lighting features, shared
GPU output or end-to-end frame latency. The sponsor launched it and reported
that closing the window was not discoverable. This is not evidence of a
complete live-wrapper checkout.

## Evidence and source policy

Review target: `codex/expand-rendering-interface`, parent `e07a025`, including
the current uncommitted proof source. Engine: installed 5.8.4, changelist
58902052. Code references below name the actual repository functions and the
matching installed Epic sources. Web guidance was checked November 18.
Epic's unversioned pages sometimes default to 5.9 and some 5.8 API links return
empty pages. Version-sensitive conclusions therefore require the local 5.8
implementation or a packaged experiment. No 5.9 feature is assumed available.

Primary references:

| Reference | Use in this review |
| --- | --- |
| [Epic subsystems](https://dev.epicgames.com/documentation/en-us/unreal-engine/programming-subsystems-in-unreal-engine) | Managed session/world ownership. Local confirmation: `Engine/Source/Runtime/Engine/Public/Subsystems/{GameInstanceSubsystem,WorldSubsystem}.h`. |
| [Epic plugins](https://dev.epicgames.com/documentation/en-us/unreal-engine/plugins-in-unreal-engine) | Runtime/editor module separation and a reusable UE adapter. |
| [Epic threaded rendering](https://dev.epicgames.com/documentation/en-us/unreal-engine/threaded-rendering-in-unreal-engine) | Game-thread object ownership, render-resource handoff and asynchronous release. Use current local APIs, not legacy macros shown in examples. |
| [Epic assertions](https://dev.epicgames.com/documentation/en-us/unreal-engine/asserts-in-unreal-engine) | Required operations must survive disabled diagnostics. Local confirmation: `Core/Public/Misc/AssertionMacros.h`, `DO_CHECK` disabled branch. |
| [Procedural mesh API](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/ProceduralMeshComponent/UProceduralMeshComponent?application_version=5.8) | Current mesh component, documented experimental status. Local `ProceduralMeshComponent.cpp` defines copying and ray-tracing implementation. |
| [Geometry scripting guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/geometry-scripting-users-guide-in-unreal-engine) | DynamicMesh ownership and rendering-feature limitations. Its GeometryFramework types do not require the whole Geometry Scripting plugin. |
| [Dynamic mesh API](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/GeometryFramework/UDynamicMeshComponent?application_version=5.8) | Runtime editing candidate, not an automatic replacement. Local `Components/BaseDynamicMeshComponent.h` documents ray-tracing reconfiguration costs. |
| [RDG](https://dev.epicgames.com/documentation/en-us/unreal-engine/render-dependency-graph-in-unreal-engine), [readback API](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/RenderCore/AddEnqueueCopyPass) | Existing render-pass and optional diagnostic readback mechanisms. Neither proves cross-process output transfer. |
| [Timing Insights](https://dev.epicgames.com/documentation/unreal-engine/timing-insights-in-unreal-engine?application_version=5.8) | Optional CPU/GPU timing qualification rather than another bespoke trace system. |

## Findings and disposition

### UE-R01 — Scene ownership is concentrated in GameMode

**Observed:** [ProofGameMode](../../src/ue5_proof/Source/SFCSceneProof/ProofGameMode.cpp)
loads input/images, owns visible geometry, the capture camera, output texture,
Slate brush, comparisons and shutdown request. The earlier hidden-actor failure
came from its `AInfo` inheritance. This is valid as a small test application but
does not provide session/world separation or live disconnect/mission cleanup.

**Recommendation:** a UE runtime plugin owns the adapter. A game-instance
subsystem owns the external session, immutable asset catalog and worker
lifetime. A world subsystem owns world-specific ship actors and camera
participation. GameMode remains thin. This is our proposed responsibility
split using Epic facilities, not an Epic mandate for this particular project.
World changes remove scene instances without accidentally killing an active
session. New sessions revoke old instance/asset associations.

### UE-R02 — Camera and pose are baked into geometry

**Observed:** `BeginPlay` evaluates `View * Model * Position` and stores
`(-z,x,y)` as every procedural vertex. Normals receive the same rigid rotation.
The capture camera remains at the origin. A live camera update would otherwise
require rebuilding vertices or leave the ship attached to the old view.

**Before live:** keep asset vertices in local space, use separate owner
transforms and a real view transform. Define a common source-world-to-UE basis
and its inverse, then convert model and camera consistently. The current
camera-space mapping is a verified endpoint reference, not a complete choice
of world basis. Preserve native units in the interface. Document any UE scale
in the adapter and apply it to positions, camera, lights and depth together.
Test translation, rotation, nonidentity camera and two independent owners.
If scale is nonuniform, normals require the appropriate inverse-transpose.
Two-sided proof materials must not hide an unqualified winding conversion.

### UE-R03 — Required file loading is inside a diagnostic assertion

**Observed:** the texture load is the expression in
`check(FFileHelper::LoadFileToArray(...))`. With ordinary Shipping checks
disabled, that expression is not a dependable operation. The code can then
reach a copy without loaded pixels. This is a concrete source defect in the
proof's suitability for Shipping, not evidence that its Development runs failed.

**Before a production-oriented package:** execute required I/O explicitly and
handle failure. Simply changing `check` to `verify` would preserve the side
effect but would not provide recoverable Shipping error handling. Keep cheap
count/index/finite-value and checked-byte-size admission at the external input
boundary. Qualify immutable assets once and reuse the result. Array comparisons,
source-file rehashing and pixel comparisons stay optional diagnostics, not
per-frame prerequisites. Do not copy JSON `check` assumptions into a live or
untrusted public parser.

The receipt's `constructed_arrays_checked=true` is currently unconditional.
When comparisons become optional, that receipt must report whether they
actually ran. A diagnostic-off package must not claim a comparison it skipped.

### UE-R04 — Vertex storage is duplicated for every material group

**Observed:** every `CreateMeshSection_LinearColor` receives the complete
`Vertices`, `Normals` and `UVs` arrays, even for one group's indices. Installed
`ProceduralMeshComponent.cpp::CreateMeshSection` copies `Vertices.Num()` into
each section. The F-FF fixture therefore creates 11,511 × 35 = **402,885**
vertex entries from 11,511 original corners. The effect is structural; no GPU
memory or timing estimate is claimed from this arithmetic.

**Before fleet scaling:** retain one asset per content/revision, images per
image content/interpretation, and instances per session/owner epoch. Compact
section-local vertices if the procedural fallback remains. For rigid assets,
qualify shared runtime `UStaticMesh` resources with independent component
transforms. Material/damage updates should not rebuild geometry. Sharing the
same CPU source object alone does not prove shared GPU geometry. Do not add a
new four-ship/32-owner limit or hide transport capacity behind a silent clamp.

### UE-R05 — Select the mesh path by demonstrated capabilities

| Candidate | Useful property | Limit or qualification needed | Disposition |
| --- | --- | --- | --- |
| Current ProceduralMeshComponent | Already passed packaged source-pixel checks, accepts original triangle lists | Epic API calls it experimental. Per-component sections own copied geometry. Current proof has ray tracing and shadows disabled, although local component code has a ray-tracing path. | Preserve as reference and a bounded fallback candidate. Do not claim it cannot ray trace. |
| GeometryFramework DynamicMeshComponent | Runtime topology/attribute editing | Epic describes ray tracing but not Nanite/Lumen support, and component-owned mesh data rather than ordinary static-mesh instancing. Local ray-tracing toggle can flush/rebuild the scene proxy. Per-corner expansion is needed for the retained non-manifold fragment case. | Consider for actual deformation needs, not a presumed universal upgrade. |
| Runtime UStaticMesh + components | Natural sharing for mostly rigid ships/fragments | Installed `Engine/Private/StaticMesh.cpp::BuildFromMeshDescriptions` supports non-editor fast builds and initializes ray-tracing representation when allowed. Rebuilding an initialized asset releases resources and waits. Editor import/cook features are not thereby available at runtime. | Preferred candidate to qualify for rigid assets. Build a new immutable revision once. Do not rebuild the active asset on every pose/material change. |
| Prepared cooked StaticMesh | Normal UE asset/cooking path | Requires prepared replacement content and versioned packaging | Optional later mod path. It cannot replace the captured-data fallback or make tester-owned game assets distributable. |

The static-mesh preference is an engineering recommendation, not a completed
benchmark. Packaged qualification must check preserved corner attributes,
material groups and fragment topology, cold admission time, shared memory and
required lighting/shadow behavior. Neither runtime fast building nor a
ray-tracing flag establishes Nanite, distance-field generation or full Lumen
support. Those remain separate tests. No custom scene proxy or third-party
mesh plugin is justified before the built-in candidates have been evaluated.

### UE-R06 — Inspection rendering must not become default overhead

**Observed:** the proof manually calls `CaptureScene` each tick until its
30-frame readback, uses `ReadPixels`, and writes a BMP/receipt. It also has a
normal viewport rendering a world plus a Slate image of the capture. The source
does not disable the viewport's world rendering. The extra work has not been
profiled. Readback timing is not first displayed-frame latency.

**Recommendation:** choose one primary render view for the next replay. A
single SceneCapture displayed in Slate is acceptable for the recorded custom
projection/viewport, provided the default world view is disabled and verified.
The installed `GameViewportClient.h` exposes `bDisableWorldRendering`. A direct
viewport-camera path is another option if it preserves the exact projection.
Do not add a custom render graph merely to display a ship.

Normal mode must not perform CPU image readback, array equality scans,
continuous file output or automatic trace recording. Optional screenshot
diagnostics can use existing UE readback facilities where appropriate. Later
game return must stay GPU-side. An asynchronous CPU readback API is not a GPU
return mechanism and a scene-capture component is not inherently a diagnostic.

### UE-R07 — Source-colour parity is not production material qualification

**Observed:** the proof deliberately uses unlit, two-sided materials,
`SRGB=false`, nearest sampling, no generated mip chain, no supplied tangents
and no shadows. It samples only primary images. This reproduces original
source colour for comparison and says nothing about a physically lit surface.

**Recommendation:** preserve original images/UVs and carry colour-space,
sampler, opacity and secondary-image role as adapter interpretation. Do not
infer a verified colour space or glow role from a BMP filename. Qualify colour
ramps/asymmetric textures, culling, normals and tangents before enabling lit
materials. Separate source emission from global bloom/tone mapping. Use UE
material instances and texture parameter updates for late enhancements and
reversible damage. Missing enhanced resources must not delay a ready base
model. Shader preparation/cooked base materials should use Epic's facilities.
No appearance retuning is authorized by this review.

### UE-R08 — Live snapshots and render completion need explicit ownership

**Current interface:** [scene receipt](../../src/transport/scene_receiver.py)
owns asset acknowledgements. The versioned retained-frame
[wire](../../tools/d3d9_proof/multi_scene_wire.h) represents a qualified registry
snapshot, not every engine draw or a completed GPU frame. Some production
prepared images already include Remix-specific conversion. Reusing that output
directly would violate the neutral-source boundary.

**Recommended flow:**

```text
unchanged x86 SFC capture and bounded session IPC
    -> neutral asset/frame reader in the x64 consumer
       -> immutable source assets + coherent frame snapshots
          -> UE adapter session owner
             -> game-thread world instances and camera
                -> UE-owned rendering resources
                   -> local view
                   -> later: separately qualified GPU output adapter
```

Reuse existing capture, identity, acknowledgements and cancellation. Qualify
the reader boundary for original data before attaching UE. Do not route through
Remix-oriented asset preparation or expose UE objects in the shared ABI.
The x86 hook DLL cannot simply be loaded into the x64 UE process. Stable public
ABI packaging is still unfinished and must not be implied by this diagram.

Workers may read IPC, decode bytes and prepare ordinary immutable CPU arrays.
Game-thread code owns UObject creation and scene mutation. Render resources
follow UE's queued ownership/release mechanisms. A render-command fence only
proves render-thread progress; it does not by itself prove the GPU finished.
Do not mutate a mesh/texture still in use or recycle a source packet merely
because its CPU work was queued.

Commit camera and instance state from one identified source snapshot. Preserve
session, owner epoch, asset revision, source frame/sequence and resource
generation. Asset-arrival work and newest eligible transform updates can advance
independently, with no extra 30 Hz cap. Discard obsolete work without blocking
SFC, and do not display old pixels under a new pose identity. UE's internal
pipeline can queue frames, so actual completed-image provenance needs its own
qualification. Do not add a new fixed frame delay or disable all engine
threading based on a documentation example.

During stop/disconnect/world change, stop admission, cancel/wake receipt work,
finish owned CPU work, detach instances/widgets, and retire rendering resources
through the engine's completion mechanisms. Remove Slate content before
releasing its brush/render target. The static proof's process-exit success
does not establish these repeated-session lifetimes.

### UE-R09 — Production packaging and window controls need their own boundary

The current material-generation commandlet is editor-gated inside the runtime
module. That built successfully, but a reusable plugin should put editor-only
generation in a separate editor module or development tool. Keep cooked base
materials explicit, engine pin/build receipts reproducible, and assets/caches
outside source control. Project-authored interface packaging must not depend
on UE or redistribute tester-owned assets.

The staged `DefaultEngine.ini` also contains an Android File Server settings
section added during the earlier editor run, including a generated token.
That section is absent from the authored config. The nine other authored
project/build files match the last-built stage. This is a reproducibility and
package-hygiene finding, not evidence that a network server is running. Do not
publish the token. Qualify an explicit plugin/config allowlist and a full engine
build pin before treating this proof recipe as a release build procedure.

Before the next interactive package, add a visible Exit action and Escape-key
support, normal window-close handling and explicit widget/resource cleanup.
Alt+F4 remains the current operating-system close method. Confirm package
relocation and early exit/relaunch without an installed editor. Runtime loading
must handle missing input/materials and failed allocations with a useful
message, rather than an assertion crash or silent blank window.

## Smallest follow-up increments

These are recommendations for separate implementation. This review does not
perform or claim any of them.

1. **Packaged world-space replay foundation.** Separate session/world ownership,
   use original local meshes with independent transforms/camera, make required
   loads independent of diagnostics, separate editor generation, and add Exit.
   Keep the current package as the comparator. Qualify the runtime StaticMesh
   candidate before choosing it for the wrapper. Keep an explicit fallback
   candidate if it fails, not a silently substituted model.
2. **Packaged retained-scene and performance qualification.** Replay captured and
   deterministic frames through the candidate. Verify two different assets,
   shared geometry under different owners, offscreen persistence, revision and
   material arrival, fragment retirement, pointer reuse, disconnect, world
   recreation and source shutdown. Keep data/session identity exact. Measure
   cold/warm asset admission, transform-only CPU cost, render/GPU time and
   memory for 1, 6 and 100+ representative owners within declared budgets.
3. **Live read-only UE scene delivery.** Only after the above passes, attach the
   existing neutral session input. Begin with retained ships and the SFC camera.
   Keep native SFC drawing and all unsupported families unchanged. Do not
   reopen SFC-07 discovery without a specific missing relationship.
4. **GPU output and native insertion.** Separately prove same-adapter GPU
   colour/depth/owner transfer, resource generations, actual completion, leases
   and changing-image provenance against the existing standalone consumer.
   Then qualify suppression through the existing game-side gate. This review
   does not choose a DX12/D3D11 sharing implementation or bypass ReShade.

## Gates before live updates

- Package runs and exits in both the intended Development and Shipping
  configurations. Missing/bad input does not depend on enabled checks.
- Local vertices, UVs and indices remain constant across camera/object motion.
  World-space projection matches the existing source-space reference, including
  captured viewport offsets, winding and near/far ordering.
- Shared asset owners reuse qualified geometry/images. Transform updates do
  not rebuild geometry, reload textures or regenerate materials. Source
  visibility does not destroy a living owner.
- Receiver work does not touch game-thread objects. Delayed/reordered assets,
  stale snapshots and a new session cannot revive an old instance. Teardown
  works during load and during pending rendering.
- Required runtime work and optional diagnostics have explicit, separate
  switches. A no-recording run emits no captures/traces, and diagnostics
  storage limits do not stop normal play. Keep mandatory memory/bounds checks.
- Use optional bounded Insights captures to separate decode, resource creation,
  shader/texture readiness, first completed render and presentation. Do not
  reuse the proof's actor-to-30th-frame number as startup or SFC replacement
  latency. Report observed tails and pressure without promising an unmeasured
  sub-second fleet load or inventing a new timing policy.

## Review completion and next action

The review examined authored proof source, build/module/config boundaries,
existing neutral/retained transport contracts, official Epic guidance and the
pinned installed engine implementation. No additional game or GPU run was
needed to establish these source findings. No renderer behavior was changed
or newly qualified. The prior proof's four packaged runs and 12 focused checks
remain their own evidence, not tests of this proposed architecture.

Review verification checked 1,000 local documentation links, OpenSpec strict
validation and Git whitespace. The packaged executable still matched its
recorded hash. Nine authored source/build/config files matched the last-built
stage, with the earlier editor-generated config append accounted for above.
No new gameplay or performance experiment was run for this documentation-only
increment. Handoff, status, interface guidance and Obsidian were updated and
read back.

Next create the scoped **packaged world-space replay foundation** change with
these gates and the retained proof fixtures. Do not wire live input first.
Update the renderer interface document with the implemented connection only
when that implementation is qualified. The separate SFC-07 transient/native
pixel gaps and the accepted Remix alpha remain unchanged.
