# Run256 — In-memory geometry and targeted completion diagnostics

## Delivered

The current progressive D3D9 path now transfers finalized geometry and textures together through the existing session-owned memory connection. Bootstrap and later asset admission no longer reopen generated `scene.bin` files. The same neutral packet is still written as evidence, and the same parser validates its bytes. Positions, indices, corner normals, UVs, groups, initial frame and subsequent live state remain unchanged.

A default-off slow-completion recorder is available through `-CompletionDiagnostics` on the existing native multi-ship launcher. It retains only unusually slow or failed completion waits, bounded to 64 records and a dropped counter. The original five-second guard remains intact. There are no new game callbacks, continuous captures or normal-mode per-poll diagnostic clock samples.

See the updated [asset-memory contract](../reconnaissance/texture-memory-contract.md) for protocol 2, byte bounds, publication, acknowledgement, shutdown and recorder fields.

## Implementation details

- The preparation coordinator reserves actual geometry bytes alongside image packets before scheduling assembly. Size comes from already prepared vertices/indices, nonempty groups and one existing frame record. The worker copies the unchanged finalized scene bytes through `geometry_sink` and seals only when geometry and every image have been written.
- Mapping version is now 2. Geometry occupies the catalog's exact byte count starting at offset 2176; textures follow. Catalog identity, geometry FNV, texture aggregate FNV, counts/dimensions and the immutable seal remain checked. Version 1, missing geometry and corrupted geometry reject explicitly.
- The 256 MiB plus four-header pending-map budget is unchanged and now includes geometry. Individual geometry remains capped at 2 MiB and image payloads at 128 MiB. Busy storage postpones assembly outside SFC callbacks; acknowledgement and drained shutdown retain the existing ownership rules.
- `load_bytes` is the existing neutral scene parser split from its file-opening wrapper. All original schema, finite-value, index and group checks remain. The historical disk diagnostic still uses `load(path)`; active memory mode has no payload-file fallback and requires the existing prewarm handshake.
- Initial activation resolves the session's bootstrap catalog entry before parsing. It receives geometry and textures together and uses those same geometry bytes for output provenance. M1's original disk `LiveChannel` bootstrap is unchanged; no circular startup dependency was added.
- The optional recorder separates query-call time, asset-service time and polling-pause time, including maximum individual call durations, source frame and QPC identity. A caught exception retains a failure record even below 100 ms. Records flush to the existing host log before runtime shutdown. Normal launch explicitly disables an inherited diagnostic flag.

## Validation

- 68 focused Python checks passed: asset memory, parallel preparation, async materials, existing asset preparation, warm startup, timing and native cohort handling.
- 21 real native consumer cases passed with no scene/texture payload files: exact transport, geometry corruption, old mapping version, stale/wrong identities, incomplete publication, malformed image bounds and lifecycle cases.
- 10 native recorder checks passed: default-off behavior, threshold, bounded storage/drops, serialization, a deliberate 110 ms service delay and exception retention.
- The pinned 1.6.1 host built with warnings treated as errors. Final SHA256: `b0a157de420975e7c199dc440e51204c797a7a7aea44e20cf446f8a8a0e16d3c`.
- The older pinned diagnostic SDK also compiled this host source successfully, compile-only. The parked API host's existing compatibility issue remains parked; no API qualification is claimed.
- Strict immediate `20261101-181058-963490-return-fixture` and ExtraFrame 60-second delayed `20261101-181356-161923-return-fixture` both completed 600 measurement frames, independent returned pixels, native depth/text, graphics-state checks, three owners, two unique assets and a shared instance. Both exited normally. No asset rejection or preparation partial was reported. All asset mappings were released.
- A third, sampled diagnostic fixture `20261101-181757-556694-return-fixture` also completed correctly. Sampling perturbs timing, so it is evidence for wait attribution rather than a performance qualification.
- Cohort/light preparation receipts were refreshed. Read-only launcher preflight passed with diagnostic arguments. No SFC gameplay was launched. Defender service, antivirus, real-time and behaviour protections remained enabled.
- Accepted image, quality, material and light configuration files and `rtx.conf` exactly match the prior sponsor baseline. No appearance settings changed.

## Timing and newly attributed remaining wait

Large F-CA native preparation took **35.208 / 30.488 / 26.296 ms** across the three trials. Small bootstrap asset preparation took **2.768 / 1.627 / 1.912 ms**. The generated-geometry-file dependency caught in Run255 is structurally absent from active native preparation.

These are asset-preparation timings, not complete appearance times. The immediate fixture begins cold renderer preparation at discovery and first inserted at 3.907 s. The prepared delayed fixture still first inserted at 3.210 s because of a later completion-stage wait. No consistent sub-two-second loading claim is made.

The existing startup profile's `materials_enabled → renderer_assets_started` interval was 0.70–1.42 ms. Its coverage has changed: geometry and texture receipt now happen before `scene_loaded`. Do not compare that shorter interval alone with older setup markers to claim an equal end-to-end gain. Whole activation/output/insertion times and per-asset preparation remain in `summary.json`.

The new recorder caught the delayed trial's first cohort waiting **2.625 s**, of which query calls used only 2.858 ms and service callbacks 47.383 ms; 2.574 s was polling-pause time. A targeted worker observation then reproduced **3.354 s** of completion waiting, with just 2.716 ms in query calls and 58.112 ms in service callbacks.

During that latter wait, **13 samples** show the runtime's **`dxvk-cs` command worker** in `NtCreateFile → CreateFileW`, opening:

`gpu/textures/f5d105dd91e20553315a24d5ea412d94a0560a58f5fd8d230a6ae04cd7d1e062.dds`

Those samples span **2.9231832 s** and fall inside the same recorded pending-query interval. `light-fixture.json` and SHA256 identify the file as the configured dome light's **generated uniform white 4 × 2 environment**, just **160 bytes**. It is not a ship's diffuse, roughness or illumination image. No sample changes its pixels or lighting contribution.

This attributes the new reproduced completion delay to CPU-side runtime file opening on its command worker, rather than three seconds of GPU scene execution or our asset-service callback. The exact Windows/filter component holding this file open is not established; do not claim Defender kernel attribution from user-mode stacks. The old Run254 five-second failures lack their own worker snapshots; treat the new event as an evidenced mechanism in the same stage, not retrospective proof of the identical file in those older failures.

## Evidence and operating state

`artifacts/player-replacement/run256/summary.json` records timings, source/settings hashes, transport bounds and the dome-file samples. `asset-memory-native.json` records consumer cases. `worker-check/` holds the bounded observer run. Its source/executable are the existing local Run255 observer; no permanent thread sampler was added to normal launches.

Closed successful generated DDS evidence was losslessly archived with per-file and archive verification and restoration receipts to maintain the unchanged 20 GB evidence allowance. Original assets, captured geometry, logs and failures remain preserved. Source changes are unstaged and uncommitted; earlier working-tree changes are preserved.

## Launcher and next action

The existing launcher is prepared:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\native_insertion\start_native_multiship_session.ps1" -CompletionDiagnostics
```

It retains the usual 90-second tactical test and normal exit cue. Remove `-CompletionDiagnostics` for normal performance-mode logging. Existing timing-policy options and visual configuration remain unchanged.

**Next startup fix:** qualify preparing and retaining the required dome environment through supported Remix facilities during existing renderer preparation, before the first live frame needs it. Its image is known from configuration and does not require ship movement data. Preserve exact texture/light/config identity and lifetime; do not disable the dome, change illumination, extend timeouts or add security exclusions. Evaluate existing public runtime resource/preparation mechanisms before custom loading. This light-resource preparation is identified but **not implemented** in Run256.
