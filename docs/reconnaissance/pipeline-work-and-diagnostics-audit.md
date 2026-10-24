# Live pipeline work, safeguards and diagnostics audit

Status: current-source audit, 2026-10-23, Run127. Documentation only; **no switches, limits or runtime behavior changed**.

Run128 follow-through: [implemented performance/test policies](pipeline-modes.md)
now supersede the baseline table's “no independent switch” and historical scan
placement statements where specified. Baseline findings remain as history.
Correction: native live CSV streams already used DeferredDiagnostics buffers;
D07's original “writes directly” description missed those buffers. Performance
mode now disables CSV formatting/collection, not merely file flushes.

Run130 follow-through: native VB/IB/texture upload readback comparisons are now
Test-only as well. The real renderer/device/shared outputs initialize at verified
copied-game launch and idle without rendering; asset-dependent bootstrap still
follows complete material-library activation. See [current policy](pipeline-modes.md).
This does not remove content identity, schema/bounds or GPU synchronization and
does not establish the sub2s target. Historical audit rows are not current switches.

Scope: `tools/d3d9_proof/start_d3d9_multiship_session.ps1` and its actual ordinary-D3D9/Remix multi-ship dependencies. Legacy Toolkit, SDK and standalone experiments are considered only for leakage into this path. This is an implementation inventory, not a CDD amendment, milestone PASS or new capability requirement. Audit IDs below are inventory labels, not requirement IDs.

## Findings and classification

- **Essential (E):** produces, transports or displays the current supported scene. Some implementation steps are replaceable, but cannot simply be removed today.
- **Safeguard (S):** protects correctness, original gameplay, resource bounds or recoverability. Preserve the protection; optimize its implementation rather than blindly disable it.
- **Diagnostic (D):** observes or verifies behavior without being needed to produce the image. It should be independently selectable, but many current diagnostics are not.
- **Test policy (T):** fixture layout, duration or approval conditions. Not a shipping renderer dependency; not all can be removed under current approved test authority.
- **Mixed (M):** an essential or safety mechanism is coupled to evidence collection. Splitting it requires code plus validation, not deletion of an output file or environment flag.

CONFIRMED means directly supported by inspected source or measured replay. Costs marked unmeasured are not assumed free or asserted bottlenecks. All proposed controls below are **not implemented**.

### Immediate conclusions

1. CONFIRMED: whole-history budget inventory is the dominant measured asset-preparation delay. Four concurrent assets invoke eight full inventories. Reservation entry holds a common lock while scanning; release needs that same lock. Historical capture accumulation therefore affects current loading time.
2. CONFIRMED: several diagnostic streams are compulsory in the current multi-ship workflow. There is no independent low-evidence/performance preset. Calling this mode “timing only” does **not** mean diagnostic logging is disabled; it primarily disables CPU image readback.
3. CONFIRMED: current packet files, ordinary texture uploads, Remix material DDS files and the aggregate material library are functional inputs, not merely optional exports.
4. CONFIRMED: source/latest-state and lifecycle/identity safeguards share flags and storage with audit records. Turning off timing/persistence flags to suppress logs can disable the live connection itself.
5. CONFIRMED: broad geometry transcripts, continuous image readbacks, historical Toolkit startup, synthetic replay pacing and repeated magenta/on-off demonstrations are not required by the active multi-ship path. Important exceptions and existing flags are listed below.
6. Unresolved: the sponsor reports this pattern has occurred about four times. This audit does not establish an exact incident count or retroactively attribute every earlier stall to diagnostics.

## Essentials and selected appearance features

| ID | Work and source | Execution location / current state | Disable disposition |
|---|---|---|---|
| E01 | Semantic owner/model/source capture; `tools/m1_component/m1_component.cpp`, `m1_live_scene.h` | Game callbacks; fixed capture storage, original control flow retained. Fresh mainline assets, not native MOD-file geometry imports. | Required. Do not remove hooks merely to reduce diagnostic detail. ABI/state-preservation protection remains. |
| E02 | Persistent simulation registry, epochs, world transforms and camera; `m1_live_scene.h`, persistent scene headers | Game update/render flow, independently of camera visibility. | Required for retained living ships. The evidence sampling rate is not the scene-update rate. |
| E03 | Bounded asset transfer/latest owner tables and worker serialization; `m1_live_scene.h`, bridge/channel modules | Preallocated game-side capture plus off-callback worker and current-user transport. | Required. Shared memory is functional; the current collector also depends on serialized asset files. |
| E04 | Four-worker preparation/content coalescing; `tools/remix_runtime/asset_preparation.py`, `multi_scene_relay.py` | External worker threads; coordinator owns catalog changes. | Required current implementation; four is concurrency, not owner capacity. Asset/owner identities cannot be dropped. |
| E05 | Decode geometry, retain corner normals/UVs/groups, build ordinary-D3D9 buffers; `tools/scene_bridge/scene_bundle.py`, `tools/d3d9_proof/multi_scene_runtime.h` | External preparation then native CPU future/device-owning thread. | Required current adapter boundary. Repeated decode/serialization can be optimized, not silently bypassed. |
| E06 | Original images -> ordinary BGRA uploads and Remix replacement DDS/material bindings; `tools/d3d9_proof/material_binding.py` | External asset worker, then normal runtime material ingestion. | Required for current textured output. The Remix-only DDS row flip is essential backend conversion; do not apply it to generic captured UVs. |
| E07 | Initial catalog/material batch and native readiness mask; `multi_scene_relay.py`, `multi_scene_runtime.h` | Initial discovery/seal/preparation before host launch, then native admission. | Mixed functional/startup policy. Current batch seals after 750ms + 200ms quiet, or 2s maximum; not early loading discovery. Do not confuse with a fixed render refresh limit. |
| E08 | Native ordinary D3D9 submission -> pinned Remix runtime -> GPU output sharing -> in-game ReShade compositor; `d3d9_direct_host.cpp`, `output_receiver.cpp`, `game_output_writer.h`, `tools/remix_runtime/return_addon.cpp` | Separate 64-bit renderer/32-bit receiver and game presentation callbacks. | Required current return path. No continuous CPU screenshots, Toolkit, OBJ or per-frame USD geometry ingestion. ReShade remains the current compositor, not original-renderer replacement. |
| E09 | Color/depth/coverage output, synchronization and source correspondence | GPU/native worker and game compositor. | Required selected composition contract. Coverage is the qualified tracked-set union, not a proven native per-pixel owner map. Do not disable fences/coverage as “telemetry.” |
| E10 | Native lights, accepted light/image/quality controls; `tools/d3d9_proof/live_light_binding.py`, native light transport, `tools/remix_runtime/config/*.toml` | Native capture/shared-memory light bank; external binding; GPU processing. | Functional appearance policy, independent of evidence. Current multi-ship light/image/material configuration is frozen at startup; do not promise tuning-mode hot reload here. |
| E11 | Generated roughness/emission and grading/AA/filtering choices | External material preparation and runtime GPU processing. | Optional appearance FEATURES, not diagnostics. Roughness map has its existing `roughness_map_enabled` control in materials.toml; changing it changes appearance and comparison baseline. Do not disable sponsor settings during performance work without recording it. |

## Safeguards: retain protection, review placement and cost

| ID | Protection / source | Current placement | Cost / disposition |
|---|---|---|---|
| S01 | Exact client/copy/proxy/runtime, process path and launcher/config checks; `tools/remix_runtime/run_return_game.py`, launcher/qualification modules | Before launch, startup verification, after exit | Required for governed testing. Primarily setup/teardown; no new timing claim. Offline qualification/builds are not frame production. Do not falsify receipts or weaken process-path checks. |
| S02 | Original assets untouched, transactional proxy/config backup, interrupted-session recovery | Before installation and after normal game exit | Required. Restore only owned/verified targets, never overwrite an active game's loaded setup. |
| S03 | Current-user/session ownership, stable owner epoch/revision/content hashes, packet guard/checksum/length/index/finite checks | Capture/transport/admission/composition | Required. Native pointers/resource IDs alone cannot qualify content or reappearance. Small checks are not equivalent to repeated historical scans. |
| S04 | 32 owners, 64 asset revisions, four 2MiB transfer slots; per-asset 128MiB decoded-image budget, 256 resources/4096², 256MiB conservative retained backing | Fixed capture/transport and external/native admission | Supported-capacity safeguards, not promises of arbitrary mission scale. Four workers != four ships. Old scene-wide 128MiB/256-image export caps are removed in multi mode; legacy workflows differ. |
| S05 | Aggregate 20,000,000,000-byte output budget, free space, 32MiB reserve and four 256MiB temporary disk reservations; `multi_scene_resources.py` | Entry scan under reservation lock + exit scan per asset | **CONFIRMED expensive implementation of a necessary disk safeguard.** Two inventories per unique preparation; workers wait entering and releasing the common lock. No safe disable switch. Proposed: pre-run inventory plus bounded session accounting/reservations/reconciliation off the loading critical path. Preserve concurrent-output accounting and free-space protection. |
| S06 | Current-run output watchdog; `run_return_game.py::enforce` | Supervisor nominal ~50ms gameplay loop; repeated recursive walks of current run (total, non-broad, images) | CONFIRMED repeated walks; their isolated cost is **unmeasured**. Separate from whole-history S05. Proposed: maintained counters/throttled reconciliation; retain bounded logs and fail-safe stop. |
| S07 | Owned-process guard and scratch/runtime caps; `tools/remix_ingest/bounded_job.cpp` | External supervisor/job | Required owned cleanup and resource backstop. Current scratch scanning may add load; not measured here. Do not remove ownership or terminate unrelated processes. |
| S08 | Actual frame/sequence/session/camera/cohort matching, closed-frame watermark, 50ms history-age guard; `input_admission.h`, synchronized compositor/buffer headers | Native renderer and game presentation | Required against stale/wrong-owner pictures. 50ms is a maximum history guard, not artificial 20Hz rendering. Do not fix flicker by blindly keeping old pixels. |
| S09 | GPU query/fence and resource ownership/readiness, device/resize handling | GPU/native worker/compositor | Required. WorkerPoll supports `SFC_D3D9_POLL_US=250` (default) or `0` (Sleep(1), NOT no wait). Poll scheduling is implementation policy; fence completion is not optional. |
| S10 | Callback drain, worker joins/cancellation, mapping/resource release, hook restore/unload | Shutdown | Required. Performance changes must retain failure/disconnect/shutdown tests. |

## Diagnostics and test-only work

“No independent switch” means there is no supported way to disable just that item in the active launcher today. Editing an output file, inherited environment variable or test receipt is not an acceptable substitute.

| ID | Work / actual output | Active mode and placement | Existing control / lost evidence / next disposition |
|---|---|---|---|
| D01 | Semantic event detail and rejection records (`M1-A-events.csv` and summary) | Component detail capped at 120 frames/10,000 events; counters/other streams continue separately | Generated component.ini supplies caps, but launcher exposes no independent evidence preset. Reducing logs must not reduce owner/transform capture. Loss: early seam/exception detail. |
| D02 | Identity census of callers/context/chosen owners | Full-run multi-ship callback path; fixed 256 entries/128KiB output; includes owner-table searches | **Always on when multi-scene is active; no independent switch.** No isolated cost measured. Important regression evidence for shared-model ownership, but not actual owner selection. Proposed default-off detailed census with minimal error counters retained. `enabled` in its summary is a recorded state, not a user switch. |
| D03 | `LIVE-SCENE-001-updates.jsonl` detailed 96-word rows | Same native worker as asset transfer/latest-state/light publication; lifecycle mode limits detail to ~20Hz, 2,700 rows/owner, 16MiB | No independent switch in active workflow. Essential latest state is published BEFORE detail sampling. However `scene_bundle.prepare` hashes this journal into provenance, so merely suppressing/deleting it breaks preparation. Must separate provenance contract before disabling. |
| D04 | `LIFECYCLE-001-events.jsonl`, associated analysis | Lifecycle event queue and off-callback serialization; 1MiB event journal | `SFC_LIFECYCLE_CAPTURE` exists but `--multi-ship` implies persistent -> camera_recovery -> lifecycle_capture. No independent active-launcher switch. Retain actual registry/lifetime correctness without requiring its diagnostic journal. Loss: detailed retirement/camera-gap investigation. |
| D05 | Source timing/audit records and post-exit `.bin`/analysis JSON | Source/Present/overlay timing stores, native counters; Python exports/analyzes after stop | `--multi-ship` forces source/live timing. **Mixed flags/storage:** latest frame/owner handoff is functional. Removing `SFC_D3D9_SOURCE_TIMING` or `SFC_D3D9_LIVE_TIMING` is NOT a safe logs-only toggle. Split detailed audit recording from protocol state first. |
| D06 | `D3D9-MULTISCENE-001.frames.bin` sampled cohort packets | External recovery service; at most 120 detailed samples, roughly each 60 source frames | No independent switch. Final shared-store snapshot/catalog ACKs also exported at exit. Loss: cohort membership correlation. Proposed separate sampled-evidence option, summary counters retained. |
| D07 | `frame-timing.csv`, `live-input.csv` | Native render loop formats CSV into live DeferredDiagnostics buffers, flushed at teardown; stream checks remain | Baseline had no independent diagnostics switch. `SFC_DIRECT64_TIMING_ONLY=1` does NOT stop these. Cost unmeasured. Run128 adds independent evidence policy; retain required control/transport failures. |
| D08 | RETURNED/cohort/owner console diagnostics | Renderer std::cout buffered by DeferredDiagnostics in live mode, fixed default 1MiB, flushed at teardown; vendor logging separate | Already mitigates per-frame pipe/file IO for std::cout only. It does NOT buffer CSV streams or all vendor logs. Disabling `SFC_D3D9_LIVE_TIMING` to change buffering breaks live mode. Loss: detailed native stage reasons. |
| D09 | Native light latest-file mirrors and discovery journal | Native worker publishes shared light bank, also writes/renames `native-light-latest-<owner>.bin`; final `native-lights.bin`/summary | Current persistent binding reads shared memory, not these latest mirrors. Producer has no separate shared-only/no-mirror option. Do not disable native light capture/shared flags: those supply lighting. Split duplicate file evidence from shared publication. No isolated file-mirror cost measured. |
| D10 | Supervisor history snapshots, manifest/config copies, post-exit analyses | Supervisor periodically appends bounded history; exports provenance and test conclusions | Useful audit trail, not pixel production. Mixed startup/qualification consumers still require some manifests. Propose minimal run identity/config hashes/counters by default and detailed history by explicit choice; don't remove required inputs. |
| D11 | Repeated source-image/packed-upload comparison and extra decoding | `material_binding.prepare` rereads/decode originals per group and compares against `texture-N.bin`; source packet/reference SHA checks too | No independent switch. Identity/source safety and full pixel-comparison evidence are currently coupled. Prefer reuse of already decoded immutable data and its identity; do not discard content/session correctness. FCA material preparation measured ~1.39s in a separate profiled replay, including one unusually slower helper call; not a universal constant. |
| D12 | Full generated-DDS pixel readback/roundtrip | **Already removed** from active per-load material path; only cheap header/layout/size checks remain | Offline tests retain conversion correctness checks. Do not reintroduce runtime roundtrips as a silent prerequisite. |
| D13 | Continuous CPU output readback/staging and raw image files | **OFF** in game path: host and receiver use `SFC_DIRECT64_TIMING_ONLY=1`; game output requires that state | Do not set this to 0 during live performance tests. Offline replay may enable sampled verification; `--capture-ship-image` is a separate legacy one-image workflow, not active multi-ship. |
| D14 | High-volume 0x006AB410 geometry tracing; broad ReShade resource/draw tracing; depth snapshots | **OFF / separate modes**; generated component.ini explicitly `EnableGeometryHook=0` | Broad/depth options are not the multi-ship performance path. Essential bounded mesh capture at the semantic source is NOT this diagnostic geometry hook. |
| D15 | Synthetic rows, injected lag, paced frames, raster backbuffer screenshots | Offline fixtures only; normal launch sets paced/latest/lag flags to zero and removes named fixture/backbuffer flags | Keep offline. Fixture negative tests/qualification should not be rerun or leak into gameplay. No proven exhaustive sanitation of every future environment variable is claimed. |
| T01 | Camera-left copies; original ships ON | `tools/d3d9_proof/multi_ship.toml`, compositor/host placement | Deliberate test policy, not replacement. The placement config exists; zero offset is not a no-cost way to validate replacement (overlap/z-fighting). Remove only under a separately qualified composition/suppression step. |
| T02 | 120s menu entry, 90s tactical window, 285s total workflow, 25s initial preparation watchdog, 30s first-image watchdog | Launcher/supervisor/controller | Current approved test bounds, not required future play duration. Do not silently lengthen or remove. Timing `.preparation_seconds` from parent creation includes menu/setup and is NOT isolated conversion time. |
| T03 | Builds, deterministic replay, native/Python regressions, exact-source qualification | Offline; current multi launcher uses existing qualified binaries and does not rebuild each gameplay launch | Necessary release/test qualification, not runtime image production. Avoid adding full rebuilds/fixture runs into the tactical path. |

## Why apparently optional files cannot all be deleted today

| File family | Current role |
|---|---|
| `gate/LIVE-SCENE-001-asset-*.bin/.json` | Fresh captured input used by the external preparer, in addition to transport slots; currently essential. |
| `gate/run-metadata.json` | Immutable session provenance consumed by preparation; currently required. |
| `gate/LIVE-SCENE-001-updates.jsonl` | Detailed diagnostic journal, but startup exporter currently hashes it; mixed dependency. |
| `gpu/assets/*/scene.bin`, `texture-*.bin` | Actual ordinary-D3D9 consumer input, not optional OBJ/test exports. |
| `gpu/assets/*/scene.json`, `material-binding.json` | Provenance plus runtime preparation/admission inputs; mixed. |
| `gpu/assets/*/rtx-remix/.../*.dds`, `mod.usda`, aggregate library | Actual normal Remix material resources; no USD geometry ingestion. Late library rewrite still causes a separate known runtime pause. |
| Native/CSV/detail snapshots | Evidence, but current post-run qualification/parsers require several of them. A low-evidence preset must update those readers to label absent evidence accurately, not fabricate PASS. |

## Measured root cause and limits of inference

Actual Run125 game record: `artifacts/remix-runtime/runs/20261023-205121-223108-in-game/result.json`. Four initial identifications took 0.278–0.443s; concurrent full preparation took 9.412–12.269s. Initial discovery -> host launch 12.866s; host launch -> first logged GPU output-ready query 2.780s; sum 15.646s. This is not physical display timing or all-six-owner first appearance. Later owners were first discovered at 14.307s and 25.133s; discovery timing is separate from preparation.

Read-only diagnosis (preceding turn) used those four captured assets, production preparation functions, frozen captured material config, external disposable output, no SFC/Remix execution. Only output-path guards were relocated in memory to the diagnostic scratch root. No repository source was changed.

- Real capacity checks: batch16.264s, eight full inventories. Reservation entry waits2.261/5.319/8.524/12.178s. Geometry/primary-image stages0.051–0.301s, material stages0.150–1.296s, native catalog proof0.019–0.045s. Concurrent timings overlap and must NOT be summed as sequential elapsed time.
- Diagnostic A/B replaced only repeated `storage()` enumeration with one immutable snapshot inside the isolated process; safety arithmetic/reservations retained. Three fresh-output batches2.148/2.100/2.057s. One-time inventory2.362s measured separately. All499 corresponding geometry/upload/DDS files per batch byte-identical to accepted outputs; ~192.1MB output per batch. Snapshot accounting was a causal experiment, NOT an implemented or production-safe concurrent-writer ledger.
- A separately profiled whole-history walk made ~2.02million calls, including108,399 stat calls, and took2.908s. Subsequent native helper-only measurements were ~37–53ms texture identity and44–46ms catalog proof. Helpers/GPU effects are not the measured ten-second culprit.
- CONFIRMED causal bottleneck: repeated historical enumeration + reservation-lock contention. Expensive preparation is not automatically an RTX4070 limitation. More workers or NTFS compression is not the root-cause fix.
- STRONG HYPOTHESIS: reusing immutable decoded image data and reducing per-group readback comparison can reduce the remaining ~2.1s preparation. No implemented speedup or end-to-end sub2s PASS is claimed.
- Unmeasured: cold-cache behavior, security-scanner contribution, individual current-run watchdog cost, individual census/CSV/light-mirror cost, larger mission scaling and shipping behavior. Do not label them confirmed causes.

## Prioritized disposition — documentation, not execution authorization

1. **First:** replace S05's historical scans on the asset critical path with correct concurrent session accounting; retain reservation/free-space/budget safeguards. User target: fresh availability to textured readiness <2s, with complete initial batch measured. Earlier asset discovery is explicitly deferred.
2. Measure S06/S07/D02/D07/D09 before attributing stalls. Make evidence-only census, lifecycle/detail journals, cohort snapshots and CSV collection independently selectable. Do not repurpose core live-mode flags as diagnostic switches.
3. Split M dependencies: packet/provenance inputs vs optional full evidence, shared lights vs file mirrors, minimal summaries vs post-run full analysis. Keep evidence absence explicit and qualification appropriate to the chosen preset.
4. Preserve authored appearance baseline, client hashes, source/camera/epoch validity, bounds, GPU sync and orderly cleanup. Separate remaining host startup and late-material reload from preparation cost.
5. Proposed future conventions (not implemented): minimal `performance` evidence, bounded `diagnostic` evidence and standalone `offline-verification`. Every diagnostic must state enabled state, cap, thread, saturation/failure policy, disable control and lost evidence. Never silently make an optional log failure stop rendering.

No new rendering architecture, vendor patch, earlier loading hook, appearance change, replacement, requirement waiver or aggregate milestone claim follows from this audit.
