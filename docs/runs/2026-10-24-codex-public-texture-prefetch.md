# Run137 — public Remix texture-cache preload qualification

## Disposition

PARTIAL texture-preload qualification; NO production speed fix promoted. Sub-two-second discovery-to-correct-image target remains OPEN. No SFC gameplay launched, suppression/replacement, appearance tuning, milestone claim, staging, commit or push. HEAD remains `d40f8f230fc7504023e4a052c99a81b5a08ce6b4`; existing dirty work preserved.

Authority: sponsor's instruction to investigate existing pinned-runtime loading facilities and test solutions, followed by “Go”; Run136's exact next action. Fuel Guard attached without starting a daemon. No helper or agent used.

## Supported relationship and its limits

Pinned Remix 1.5.2/source `b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4` retained. Source inspection confirms public `CreateMaterial` queues finalized material/texture work. It copies path values into the queued work; API return is NOT texture-residency completion. Its external-material registry is distinct from ordinary-D3D9 replacement materials, but both reach the texture manager's asset cache.

The DDS asset identity includes its resolved filename, not only its content. Observed USD-resolved paths normalize the Windows drive letter to lowercase. The experimental API requests use that same spelling; this is a Remix boundary convention, not a change to captured data or a future D3D adapter contract.

The texture cache returns an existing matching entry before handling `forceLoad`. Public API preloads use false; USD's force-load request uses true. That difference affects demotion/loading policy even where our DDS has one mip. Do not assume the two entry paths are interchangeable simply because the source bytes match. The public API exposes no residency-completion query used here. A D3D9 event query drains ordered command work, NOT independently the texture manager's asynchronous GPU upload queue.

Primary references:

- [Pinned public API implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_remix_api.cpp)
- [Pinned texture manager](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_texture_manager.cpp)
- [Pinned asset manager](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_asset_data_manager.cpp)
- [Pinned USD material loader](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_mod_usd.cpp)

## Experimental probe and implementation

Default-OFF, standalone-only flags: `--api-texture-prefetch`, optionally `--overlap-texture-prefetch`; both require startup profiling/prewarm/multiship. Normal qualification refuses these fixtures. Normal gameplay does not expose these flags; inherited experimental environment is stripped. Ordinary-D3D9 mesh submission remains unchanged; zero SDK mesh/instance submissions.

- Python builds immutable, session/PID/checksum-bound requests from finalized worker material manifests. Header32 bytes, 1–1024 paths of256 bytes, trailing FNV64; at most64 incremental requests. Exact generated DDS paths must remain within the owned GPU directory. Full union request is published before activation.
- In overlap mode, coordinator publishes each completed worker's resource list while remaining preparation runs. External host consumes sequential immutable requests during its existing activation wait, deduplicates paths, and queues private, never-drawn opaque API materials to preload textures. No SFC callback/thread changes or custom vendor loader.
- At most1024 retained preload-only handles. Explicit `DestroyMaterial` and command drain before shutdown. Exceptional cleanup also queues destruction. Successful fixtures report API shutdown0 and zero owned child processes. Existing vendor teardown warning about40 common objects also occurs without this experiment; internal leak-free vendor teardown is NOT established.
- Source/generated images, accepted material/light/image/quality policies, UVs and geometry are unchanged. No images converted a second time for this probe.
- Optional profiled standalone fixture now saves TWO bounded actual-compositor BMPs: existing settled-cohort sample and one sample at the end of its existing600-frame window, if a matching frame is available. No continuous screenshots or gameplay readback. Two1920x1080 BMPs fit the existing32MiB non-image fixture allowance.

Files added: `tools/remix_runtime/texture_prefetch.py`, `tools/d3d9_proof/texture_prefetch.h`, `tests/test_texture_prefetch.py`, this record and curated JSON. Modified preserving prior changes: `tools/d3d9_proof/d3d9_direct_host.cpp`, `tools/d3d9_proof/warm_start.h`, `tools/remix_runtime/multi_scene_relay.py`, `tools/remix_runtime/run_return_fixture.py`, `tools/remix_runtime/qualify_multiship.py`, `tools/remix_runtime/return_fixture.cpp`, `docs/HANDOFF.md`, `docs/reconnaissance/pipeline-modes.md`. Ignored one-off archive script/receipts are evidence maintenance, not shipped pipeline tooling.

## Actual offline GPU results

Same three historical captured asset contents/FCA/RCA/FDD and four synthetic owners including shared FCA. No current game pointer/resource identity reused. Each successful case admits/draws all four owners, with no asset partials, and passes native HUD/border/state preservation, resize/recreation, normal exit and owned-process cleanup. These are isolated samples, not controlled statistical performance claims; cache/system conditions vary.

| Fixture suffix (all 20261024, return-fixture) | Mode | Idle | Discovery→matching output | Activation→matching output | Largest bootstrap Present |
| --- | --- | --- | --- | --- | --- |
| 141601-646642 | Performance, batch API | 60s | 5.259074s | 3.130923s | 0.856114s |
| 141805-721638 | normal Test | 60s | 3.338041s | 0.894233s | 0.070632s |
| 142246-433034 | Performance, overlap API | 60s | 5.252438s | 3.001686s | 0.946595s |
| 143326-727766 | final-source normal Test | 0s | 5.817374s | 3.098359s | 0.066682s |
| 143542-442532 | final-source Performance, overlap API | 0s | 5.161898s | 2.721528s | 0.853933s |

Batch API queued268 exact paths in0.044724s; command drain1.461278s, total1.506002s. Overlap60s case published3 requests, first native preload began1.452528s before activation; subsequent calls reached cumulative15/129/268 textures. Thus actual overlap is CONFIRMED, but no sub2s result or dependable improvement follows. All268 API paths queued;28 eligible large-single-mip warning paths appeared once each in the first batch log, supporting cache reuse for that observed subset, not a residency/cache-hit counter for all resources.

Final-source normal:783 draws per owner,594 paired audit records,593/600 steady-window draws. Final-source overlap:841 per owner,654 paired,595/600 steady. Intentional disabled interval remains part of standalone fixture; ordinary game's established no-on/off policy is unchanged. Guard exits0/stop_reason0/owned0. Peak scratch165,488,089 /165,284,413 bytes, console147,178 /90,387 bytes respectively.

### Pixel readiness finding

Initial60s normal-vs-batch samples differed in brightness despite identical accepted policies and original/derived image bytes. Do NOT declare appearance equivalence from covered pixels alone.

The new0s pair saved early and late snapshots, each covering31315 rendered pixels. Normal early→late mean absolute RGB difference over covered pixels was21.4293/255; preload early→late2.3432/255. Cross-run late images were visually inspected: recognizable textured geometry/placement, much closer appearance. Nonidentical cross-run late pixels still remain (mean2.5023 over differing pixels;7461pixels have a channel difference>3). This is NOT a zero-difference appearance acceptance test. All432 generated native-image/DDS files have identical SHA256 multisets between the final pair. The private request `texture-prefetch.bin` is NOT an image; image inventory must use exact `texture-[0-9]+.bin`, not a broad filename prefix.

CONFIRMED: first matching geometry/frame provenance does not guarantee settled material pixels; even the normal case changes substantially later. STRONG HYPOTHESIS: material-stage ingestion and/or texture residency occurs after first matching output. SPECULATIVE: the public API's different force-load/demotion behavior contributes to remaining color differences. Temporal convergence remains another possibility. Do not blame color conversion or change material defaults without isolation. Reported timings above are matching-output clocks, NOT proven first fully correct-material clocks.

### Incomplete cases and safety accounting

142745-117623 and143128-048012 hit existing fixture time/output cap;143403-077273 ended with native fixture failure before cohort/resize completion. Their reports explicitly show asset refusal: `Authorized20GB project output allowance;asset postponed`. The incomplete cohort then prevented success; these are NOT shader/preload performance observations. No allowance was raised, no partial promoted. Native job receipts show exit0/owned0 for completed bounded host cleanup, separately from failed overall fixture adjudication.

Recovered completed-fixture image bulk for141601/141805/142246 and historical044102/044404/050416/053427: each432 exact generated image files162,619,600 bytes became10,051,597-byte ZIP; every entry fully decompressed/SHA256 checked before exact generated files removed. Total1,067,976,021 bytes recovered. Original captures, native packets, manifests, logs/results and BMPs preserved. Archive receipts in each run contain paths/hash/entry inventory; ZIPs in `artifacts/remix-runtime/archives`, restore entries relative to owning run. Latest normal143326 and final overlap143542 remain intact. Final governed artifact inventory18,960,723,811 bytes<20,000,000,000; this established budget scope excludes unrelated dependency/source trees, not confused with total disk use.

## Validation and final state

-485 Python tests PASS, including session/checksum/path/dedup/image immutability and experimental-qualification rejection.
-Native64 build/regressions PASS: light11 and combined post/GPU65; fixture build/regressions PASS: wire37, expanded13, broad14, presentation22.
-Final-source normal143326 qualifies through existing native collector/worker tests; no experimental flags can qualify normal startup. Native light discovery qualification PASS. Mapping tests initially denied inside sandbox, then PASS through approved bounded outside-sandbox execution; no security-policy changes.
-Both Performance/Test read-only game preflights PASS. No `--execute` or gameplay launch.
-Accepted/copy client SHA256 unchanged `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`; copied proxy unchanged `E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7`.
-No normal startup/appearance setting changed. No provider/runtime block; no sponsor interaction required for this offline investigation. Repository remains dirty/unstaged, index empty; no commit/push.

Exact next smallest action: instrument or use supported pinned-runtime profiling to distinguish replacement-material stage activation from texture-upload/first-use completion on the SAME unchanged library. Establish a material-ready boundary, not just first matching geometry, before attempting another production startup optimization. Keep API preload experimental OFF; do not repeat dummy warmups, drop maps, change translators, request another broad game capture or claim the two-second goal achieved.
