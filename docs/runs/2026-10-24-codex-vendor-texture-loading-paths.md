# Run138 — NVIDIA loading paths tested; internal profiling next

## Outcome and authority

PARTIAL startup investigation, no speed fix promoted. Sponsor: “Go, be sure to reference Nvidia documentation, avoid making new when the pipe exists.” Read current handoff, Run137, approved M1 plan and existing performance/test policy; no gate or architecture revision. Fuel Guard attached using the actual thread; no daemon, helper or agent started.

Normal runtime, shader/material/light/image/quality defaults, original game behavior and all client assets remain unchanged. No SFC launched. No SDK geometry, new loader, vendor patch, Toolkit startup or new rendering-thread work. HEAD unchanged `d40f8f230fc7504023e4a052c99a81b5a08ce6b4`; prior dirty work preserved; index empty; no commit/push.

## NVIDIA references and findings

All runtime findings refer to pinned Remix1.5.2/source `b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4`, not newer upstream defaults.

- [NVIDIA pinned runtime profiling instructions](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/README.md#profiling-remix): Tracy0.8 support requires `enable_tracy=true` and a rebuild. This run did NOT rebuild/replace the pinned runtime. Scanning its DLL found no Tracy/TracyProf/tracy::/TRACY_ENABLE strings; this is supporting inspection, not alone proof of every compiler option. Vulkan SDK, Meson, Tracy and Nsight CLI were not found in normal environment checks. Toolkit/Kit profiler instructions are not the profiling entry point for this standalone runtime host.
- [Pinned material loader](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_mod_usd.cpp): material `inputs:preload_textures` controls force-preload. Our ordinary generated stages explicitly set true. The implementation has opening/material/mesh/light/loaded progress states, but no corresponding public readiness query was found in our pinned SDK interface. Existing stock log messages are not precise completion fences for those stages.
- [Pinned texture manager](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_texture_manager.cpp): disabling force-preload makes textures demotable and requests one mip; the initial preload still calls scheduling with async=false. Our generated DDS is single-mip. Therefore changing that boolean does NOT prove all first-load work moved to a background thread. Subsequent managed streaming and initial staging are different operations. Device upload occurs separately from staging. Do not mislabel the experiment as a new asynchronous loader or assert texture residency from its flags.
- [Pinned NVIDIA option reference](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/RtxOptions.md): `rtx.io.enabled` selects the existing RTX IO backend; `rtx.io.useAsyncQueue` is supported. The package already contains `rtxio.dll`. `alwaysWaitForAsyncTextures` remains inherited/defaultfalse; no forced waiting introduced.
- [Pinned RTX IO definitions](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_io.h) and [implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_io.cpp): the backend has internal completion/counter facilities, but this is not a public Remix material-residency API for our host. No private pointer extraction or replacement loader was added.

## Narrow offline experiments

Existing standalone fixture extended, not the gameplay launcher:

1. `--material-texture-loading stream` (normal default `preload`): requires startup profiling, layered material publication and no API-preload experiment. Writes a sibling `streamed.usda` for each generated stage; only `bool inputs:preload_textures = true` changes to false. Original stage preserved; relative image references, map roles, all shading values and all image bytes unchanged. Master layer references these siblings only in the experimental session. Bounded1–64layers,1–256preload declarations/stage,16MiB stage limit; unexpected declarations/path escape/symlink output refused. No substantial work is added to the normal default branch.
2. `--loading-policy rtxio`: uses documented `rtx.io.enabled=True`, `rtx.io.useAsyncQueue=True`, and matching `DXVK_USE_RTXIO=1`, leaving unrelated loading/shader settings untouched. Existing receipt records native inputs. Runtime log recognizes values and registers RTX IO provider; no RTX IO-specific failure reported. No per-resource backend counters captured, so not proof of a specific transfer's hardware schedule.

Both are offline-only, defaultOFF, and explicitly refused by normal qualification. Source captures, image/resource associations, ordinary-D3D9 geometry, owner/frame synchronization and source-client hashes unchanged. No additional runtime snapshots beyond existing early/late pair.

## Results (no SFC)

Same three historical captured contents/four synthetic owners including shared geometry;0s optional menu idle. Logs/results/BMPs under `artifacts/remix-runtime/runs/<folder>`. First-match clocks are provenance-valid images, NOT independently material-resident/final-correct-pixel clocks. Single samples, different cache conditions; no statistical speed claim.

| Folder (20261024-…-return-fixture) | Mode / loading | Discovery→matching | Activation→matching | Largest bootstrap Present | Steady draws/600 |
| --- | --- | --- | --- | --- | --- |
| 144854-230825 | Performance / original preload | 5.453448s | 2.943074s | 2.207995s | 600 |
| 144935-036157 | Performance / streaming eligibility | 3.186382s | 0.710255s | 0.060496s | 596 |
| 145124-177894 | Performance / RTX IO, original preload | 5.422399s | 3.075348s | 0.093160s | 593 |
| 145322-155590 | final-source normal Test / original preload | 5.772099s | 3.037866s | 0.062015s | 593 |

All four cases:4independent admitted/acknowledged/drawn owners,3reused content assets, no asset partials or source-state errors, preserved native HUD/border/state, resize/recreation passed, normal native/API exit and owned children0. Draws per owner839/800/785/783 respectively. Existing vendor common-object shutdown warning remains known; no claim all vendor internals are leak-free.

Important separation: final normal Test spends3.038s after activation despite its longest measured bootstrap Present only62ms. RTX IO has the same pattern (3.075s/93ms). Thus neither “largest bootstrap Present” nor total bootstrap wall time explains every remaining delay. Do NOT attribute the whole gap to GPU rendering/texture copy. Material-watch/replacement activation, first useful cohort delivery and synchronization remain possible components requiring a timeline.

Discovery→activation alone:2.510374s original Performance,2.476128s stream,2.347050s RTX IO,2.734233s finalnormal. Even instant post-activation output would miss2s in these samples. This is a measured lower bound for these runs, not a universal hardware limit; preparation and internal runtime work must be optimized separately.

### Pixel/content checks

All432generated native-image/DDS files have equal SHA256 multisets across the first three cases. No missing diffuse/emission/roughness files, map substitution, UV/orientation/normal or material-value repair. The streaming sidecar modifies loading policy only. Late snapshots visually inspected: recognizable ship layouts/textures retained. Cross-run pixel identity is NOT asserted.

Mean absolute early→late RGB difference over31315covered pixels: original2.3537,stream9.6824,RTX IO13.6682 (0–255scale). Late stream vs original covered mean2.1045,7219pixels above3in any channel; late RTX IO vs original2.1481,7421pixels above3. This again shows frame identity/geometry readiness is not settled-pixel readiness. It does NOT by itself identify which maps were unavailable: path-tracing/temporal convergence remains an alternative to texture-stage completion. Do not invent a readiness latch from image brightness or suppress original ships based on this evidence.

## Validation, storage and remaining dependency

-488 Python tests PASS, including derivative-only preload change, immutable originals, malformed declarations/bounds, gameplay/qualification rejection and RTX IO isolation of unrelated options.
-Native renderer/fixture binaries unchanged from Run137's builds; no native source edited this run. Current-source normal Test145322 passes existing native collector/worker qualification; native light discovery qualification PASS through approved outside-sandbox mapping execution. Both read-only Performance/Test game preflights PASS. No new native build needed or claimed.
-Client hashes unchanged for accepted/copy `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`; copied proxy unchanged `E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7`.
-Recoverably compacted five completed generated-image sets: Run137143326/143542 and this run144854/144935/145124. Each432files162,619,600bytes→10,051,597byteZIP; ALL entries decompressed/SHAchecked before exact generated originals removed. Saved762,840,015bytes total. Per-run `generated-images-archive.json` records files/archive SHA; ZIPs in existing archive directory, restore entries relative to run root. Packets, original capture dependencies, material manifests/stages, logs/results and comparisonBMPs preserved. Latest normal145322 intact. Governed artifacts18,960,507,810bytes<20GB before small curated documentation; no allowance raised.

Files modified this run (preserving prior edits): `tools/remix_runtime/material_library.py`, `tools/remix_runtime/loading_policy.py`, `tools/remix_runtime/multi_scene_relay.py`, `tools/remix_runtime/run_return_fixture.py`, `tools/remix_runtime/qualify_multiship.py`, `tests/test_material_library.py`, `tests/test_loading_policy.py`, `docs/HANDOFF.md`, `docs/reconnaissance/pipeline-modes.md`; added this record and `docs/reconnaissance/evidence/20261024-vendor-texture-loading-paths.json`. Ignored one-off archive script updated for exact completed folders. No controls promoted to normal gameplay, no staging/commit/push, no active owned session left.

## Exact next action — use NVIDIA's existing profiler

Prefer [NVIDIA Nsight Systems](https://developer.nvidia.com/nsight-systems/get-started), not a custom loader or rebuilding Remix merely to obtain Tracy. [NVIDIA's CLI guide](https://docs.nvidia.com/nsight-systems/UserGuide/index.html) documents Windows Vulkan tracing and process-tree launches; Windows CLI requires administrator context. Nsight was not found on PATH, standard NVIDIA installation directories or installed-program records. Installation is the consequential next setup action and has NOT been performed.

After sponsor approves tool installation: install official Nsight Systems, then validate its local help/version and prepare ONE bounded process-tree-only capture of the existing standalone fixture, including the native Remix host. Do not use system-wide injection, capture unrelated apps, modify driver/security policy or change the pinned runtime. Reserve trace storage within20GB and fixed duration before capture; profile overhead makes its timings diagnostic, not acceptance measurements. Attribute CPU wait/queue submission/texture transfer/first useful return on that timeline. Vendor internal material zones may still require a separately approved Tracy-enabled same-commit build if Nsight cannot expose them.

No sponsor gameplay needed. Two-second target and exact material-residency boundary remain unresolved; a faster single streaming sample is not sufficient reason to enable it or start replacement.
