# UE world-space foundation — packaged qualification

November 18, 2026. `codex/expand-rendering-interface`, parent `27f4638`.
The sponsor authorized execution of `ue-native-insertion`. Changes are
unstaged/uncommitted. The separately published alpha and prior UE proof are
preserved. PR #5 subsequently merged release documentation into remote master
at `e01cd90`; this UE branch has not been rebased or merged onto that commit.

## Scope and current result

Implemented `src/ue_wrapper`, separate from the successful `src/ue5_proof`.
The project plugin has runtime and editor modules. A game-instance subsystem
owns source data, transient textures/materials and a runtime StaticMesh; a world
subsystem owns actor instances, capture target and source camera. World teardown
removes those instances; session teardown drops retained assets. There are no
receipt workers yet: this stage uses the existing checked offline scene JSON,
not a new live wire. Live threading and source receipt remain stage 3.

The F-FF Development and Shipping packages rendered and exited normally. Its 8,762
interior source pixels matched 99.50% within three colour levels. All static
mesh triangle positions, UVs, normals and group/material assignments passed
readback against source arrays. The compact procedural comparison matched
98.28%. The final configurations have matching source-hash manifests. Stage 1
is qualified within the recorded offline/standalone scope. No SFC game was
launched and GPU exchange to another process is not yet implemented.

## Source and transform conventions

Original scene arrays, group associations and image identities remain upstream.
The input is the prior inspector's `sfc.ue5.offline-proof.v1` file with original
top-row-first BGRA images. It is an offline qualification facade, not the stable
DLL ABI or a saved ship template used for live integration. It contains no
Remix UV correction, generated roughness, exposure or material settings.

The source uses column vectors: `p_camera = V * M * p_local`. Native units are
retained. UE-local points use `B p = (-z,x,y)`. UE row-vector matrices are
`transpose(B * M * inverse(B))`; camera world pose is
`transpose(B * inverse(V) * inverse(B))`. The capture projection retains the
earlier independently qualified axis/projection conversion, including reversed
depth. The original tactical viewport (200,30,1720,1020) is displayed at its
recorded offset, not stretched to the full window. Geometry is never rewritten
when model/camera state changes. Nonrepresentable affine/sheared poses are
rejected rather than silently baked into geometry.

`SFCSourceMath.h` is UE-adapter math, not an extension of the neutral wire.
Its standalone x86 and x64 fixtures each pass 1,016 checks: independent model
and camera rotations/translations, relative view, viewport projection, reversed
depth, constant local data and invalid matrices. The three existing independent
pixel-comparison Python tests also pass.

## Runtime geometry and diagnostics

Runtime `UStaticMesh::BuildFromMeshDescriptions` uses the fast path with no
collision or editor dependency. One source corner becomes one local vertex
instance; groups retain their own material slot and original indices. Multiple
actors can refer to the same mesh. A compact procedural path is available only
for comparison. The old proof's F-FF stored 11,511 vertices in each of 35 sections
(402,885 entries); the new mesh has 11,511 render vertices.

Required file reads and admission checks execute normally, not inside `check`.
Normal mode does not scan constructed arrays, read back images or emit receipts.
`-SFCDiagnostics -SFCOutput=<directory>` enables those bounded offline checks;
`-SFCExit` requests normal exit after its one readback. The inspection window
has an Exit button, Escape and ordinary Windows close. The package is not
connected to SFC or authorized to suppress original drawing.

## Failures found during qualification

- The first package rejected startup because UE hardware ray tracing requires
  compiled skin-cache support. Added `r.SkinCache.CompileShaders=True` alongside
  `r.RayTracing=True`, following Epic's requirement. No engine modification.
- The first diagnostic image used UE's numbered bitmap filename while the
  comparator expected an exact filename. The writer now requests `ship.bmp`.
- The legacy per-LOD ray-tracing pointer can be null in this engine's on-demand
  mode. The receipt now checks `RenderData->RayTracingProxy->LODs` instead.
  Presence of this representation is not a claim of verified ray-traced shadows.
- The shared-owner case exposed UE's material UV-streaming metadata ensure.
  Runtime fast build requires explicit initialization. Original transient images
  are resident (`NeverStream`); slots now initialize zero streaming densities,
  without changing source UVs. Its failing process/log was retained, and only
  the two owned stalled fixture processes were stopped. Shared-owner
  requalification passed afterward.
- The build commandlet ignores the percentage-based shader worker setting.
  The recipe now sets the actual unused-thread keys read by the pinned compiler.
  This affects build resource use, not game/renderer timing.

Early F-FF preparation measured 0.471 seconds (cold) and 100 transform-only
updates totalled 0.000118 seconds. First RT-process shutdown also waited about
33 seconds for pending PSO creation; it then exited normally. These are separate
measurements and do not establish live insertion/startup performance.

## Reproducibility and next gate

`tools/ue_wrapper/build.ps1` pins UE 5.8.4 CL 58902052, uses separate editor
content generation, builds packages and records source hashes. A source change
during a build invalidates that qualification. Outputs stay in
`artifacts/ue-foundation`; generated project caches/content are locally ignored.
No full game copy was created. `qualify.py` uses serial standalone processes,
source-derived pixel references and normal close tests. Logs/receipts are local.

Development qualification now passes shared ownership, all four recorded break
pieces, two poses for piece 1, malformed/missing input, normal close and immediate
relaunch. Final independent pixel fractions: F-FF 99.50%, compact procedural
F-FF 98.28%, K-FF 100%, pieces 0/1/2/3 99.03%/99.53%/98.88%/99.09%; piece 1
pose 7 is 100%. The second shared owner references the same StaticMesh and
11,511 render vertices. Forty-two focused existing Python regressions pass in
the desktop environment (the native debris IPC fixture cannot start inside the
restricted execution environment). No baseline transport source changed.

The synthetic paired shadow fixture initially failed for both mesh paths. Bias
and culling controls, and an explicitly lit, unclipped receiver, did not resolve
it. Setting the manually driven capture's public
`bAlwaysPersistRenderingState=true` produced **5,797 darkened shadow pixels**
with hardware ray tracing enabled. Keep this view-state setting in the adapter;
it does not alter original source geometry or the normal scene's transforms.
The diagnostic fixture is explicitly synthetic and does not claim a captured
SFC camera/light relationship. Its image and the original pixel-reference
captures serve different qualifications.

Frame owner/revision admission was also exercised RED-to-GREEN against a
deliberately mismatched file. Indices, matrix types, revisions, missing image
bytes and escaping image filenames all yield explicit rejection receipts
without producing a successful asset receipt. The engine can exit normally
with code 0 after a graceful runtime rejection, so tests check the rejection
receipt and absence of a success receipt rather than treating exit code alone
as proof. Normal-close and immediate-relaunch outputs contained zero diagnostic
files. Shipping also passed these cases, plus normal Escape exit and relocation
of the whole package to a path containing spaces and Omega, then restoration to
its original location. No duplicate game copy was made. GPU return is not wired.

Shipping exposed a separate readiness defect: a fixed 30-tick warm-up could
emit a completely black image while source arrays/identities were correct.
The adapter now uses UE's public PSO/scene-proxy readiness. Capture continues
while readiness is pending; readiness gates the receipt, not the rendering work
needed to become ready. The corrected Shipping F-FF is 99.50%, with preparation
0.111 s and renderer readiness 0.230 s in the measured sample. This is not a
live SFC source-to-display timing claim.

An intermediate Development shared-owner run timed out before its receipt.
Its exact engine-side cause was not established from that run. State-change-only
diagnostic readiness messages were added, and five serial shared-owner runs
with continued capture passed (readiness 0.258–0.297 s, process lifetime
2.69–3.04 s). Keep the timeout as a qualification limitation rather than claiming
the diagnostic instrumentation itself fixed it.

Actual world recreation passes in both configurations: **two world activations,
one asset build**, still 99.50% F-FF source pixels. The immutable admitted source
definition survives world changes; no disk reload is used as a world-lifetime
signal. Session/epoch and available fragment visual/index identity key instances.
The second shared-owner fixture is explicitly synthetic, not a newly observed
SFC ship. A centered synthetic close-camera fixture (source frame/sequence null)
also passes 99.11% across 267,283 interior pixels; it is not gameplay evidence.

Select runtime StaticMesh fast build for the next gate: qualified source
attributes/pixels, one reusable GPU mesh and actual ray-traced shadows. The
procedural path remains a comparison, not an automatic fallback. Nanite and
Lumen surface-card support are not established by these tests.

Exact build receipts and source hashes are in
`artifacts/ue-foundation/{Development,Shipping}/build-receipt.json`.
Final smoke receipts are `qualify/wrap-{fff,shared,world-restart,shadow}`;
the five-repeat set is `qualify/shared-progress-*`. All remain private local
evidence. Normal mode has no comparisons/readback/receipt capture. The
readiness transition log and synthetic fixtures are diagnostics only. The
repeatable recipe also caught and rejected a source edit during build; repeated
editor content generation exposed a missing FullyLoad on the lit fixture package,
which was corrected and rebuilt successfully.

An installed-engine search found Epic's SDK and D3D11/D3D12 samples under
`Engine/Extras/VirtualProduction/TextureShare`, including native SDK DLL/lib.
The earlier absence at the documented ThirdParty location does not mean the
SDK is missing. Inspect and test these before custom sharing work. No Texture
Share runtime integration has been implemented yet. Its public
`Blueprints/TextureShareBlueprintContainers.h` exposes `UTextureShare` and
`UTextureShareObject` with named send textures and custom data. The world
subsystem's public Blueprint getter is reflected, although its C++ class header
is private. Evaluate this supported route and SDK receiver before private engine
interfaces or a custom RHI transfer. Check GPU completion and timeout semantics;
a Texture Share frame barrier must not be assumed to be GPU completion.

Sponsor requested a short continuation and wrap-up for credits. Stop at this
foundation checkpoint; next work is task 2.1, not a new gameplay discovery run.

Sources: [Epic fast-build parameters](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/UStaticMesh/FBuildMeshDescriptionsParams),
[hardware ray tracing requirements](https://dev.epicgames.com/documentation/unreal-engine/hardware-ray-tracing-in-unreal-engine).
Pinned implementation inspected: `StaticMesh.cpp` fast build and
`InitializeRayTracingRepresentationFromRenderingLODs`, `MeshUVChannelInfo.h`,
and `ShaderCompiler.cpp` commandlet worker selection.
