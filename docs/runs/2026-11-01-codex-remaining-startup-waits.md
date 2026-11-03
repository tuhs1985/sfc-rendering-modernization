# Run255 — Remaining startup-wait characterization

## Findings

**Slow native asset preparation is narrowed to a generated geometry-file open.** A new delayed-start observation reproduced 4.075 seconds of native preparation for the F-CA. Six samples of that preparation worker, spread over 3.375 seconds, show the same `NtCreateFile → CreateFileW` stack and exact `gpu/assets/2/scene.bin` filename. The file is 689,144 bytes and is not compressed. This is a file-opening stall, not ordinary model conversion or the normal cost of copying its textures.

This reproduces the same preparation-delay family as Run254's unsplit 6.721-second interval; it does not retroactively identify the precise operation in that older event. The Windows component responsible for the new file-open wait is not established. Do not label it a proved Defender callback merely because other file/process operations were attributed to Defender earlier.

**The five-second rendering-completion timeout remains unattributed.** Three new observed delayed-start fixtures completed all 600 measurement frames and native pixel/depth/text checks without that timeout. They therefore cannot establish the cause of the two preserved Run254 failures. No timeout was increased or bypassed to obtain these results.

## Why “GPU completion” is not a complete diagnosis

The existing host's `wait9` includes `IDirect3DQuery9::GetData`, implicit flushing, optional asset-service work and short polling waits. Its five-second exception labels the whole completion stage. It does not independently measure five seconds of GPU execution.

NVIDIA's source at the pinned runtime commit shows `GetQueryData` returning `S_FALSE` while the query's command-stream reset counter is nonzero, as well as when the GPU event is unsignalled. Thus queued CPU work can also prevent completion. The command-stream implementation executes queued commands on its own `dxvk-cs` thread. Sources:

- [Pinned D3D9 query implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/d3d9/d3d9_query.cpp#L119)
- [Pinned command-stream worker](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/dxvk_cs.cpp#L157)
- [Pinned asynchronous USD load/rebuild path](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_mod_usd.cpp)

The observations also caught short `NtCreateFile` samples on generated DDS textures in `rtx-usd-mod-rebuild`. Those samples establish that file opens remain in Remix's own material loading. Each filename appeared in only one sample: there is no measured multisecond DDS wait and no direct causal link to the earlier completion timeout. Do not claim texture streaming, shader compilation or GPU saturation as the root cause from these samples.

## Controlled work

All probes are under `artifacts/player-replacement/run255`; no production implementation was edited.

### CPU-only preparation replay

`prepare_probe.cpp` reuses the existing neutral scene parser, file reader and actual shared-memory texture consumer. The supervisor provides the accepted F-CA catalog packet, 12 fresh geometry-file copies and the exact existing converted image packets. No GPU or Remix runtime starts.

- 12 cases passed.
- Complete preparation: 29.944–33.942 ms.
- 689,144 geometry bytes; 20,583,296 texture bytes.
- File metadata: 24–103 microseconds; scene read plus identity check: 4.360–8.339 ms; scene load: 1.063–1.282 ms; memory texture delivery: 24.144–24.768 ms.
- This control shows ordinary work is tens of milliseconds. It does not rule out intermittent file filtering, storage or scheduling delays under other conditions.

### Bounded worker observation

The observer accepts only this project's pinned standalone renderer executable and explicit startup session. It uses cached local symbols, waits for startup-ticket acceptance and samples for at most eight seconds. Each sampled thread is resumed immediately after collecting its context/stack. File paths are read only when a valid object-attributes structure is present. No kernel trace, public symbol download, game hook, security exclusion or screenshots were added.

Observations briefly suspend threads and consequently are **not performance qualifications**. Suspension durations and counts are recorded. Nearest exported names inside the stripped runtime/driver are not reliable function identities; use module offsets and thread descriptions instead.

| Standalone run | Outcome | Native preparation | Relevant observation |
|---|---|---|---|
| `20261101-153634-551487-return-fixture` | Completed | 1.917 ms / 32.211 ms | No slow file open sampled. Initial observer covered first 96 threads only; that limit was corrected for later observations. |
| `20261101-154208-149209-return-fixture` | Completed | 1.690 ms / 4,075.406 ms | Rotating coverage caught six `scene.bin` open samples on worker 50612 across 3.3747921 seconds. Also one DDS-open sample on the USD rebuild worker. |
| `20261101-154700-954907-return-fixture` | Completed | 2.124 ms / 6,370.014 ms | Final observer focused on runtime/render threads. It did not sample the unnamed preparation worker, so the operation responsible for this outlier is not directly attributed. Two individual DDS-open samples were caught. |

The first cohort's measured D3D9 query waits were approximately 7.9, 7.0 and 6.8 ms respectively. The original five-second failure did not recur in these observed runs. The first/all-ship display timing is not inferred from a completed fixture alone.

## State preserved

- Normal host remains SHA256 `48eea81bb1a731e8296ac5f78a5fd251b787ba0e5c4fc0ea9a1a75a3cacdd726`.
- Existing memory texture delivery, geometry, material/light/image configuration, output limits, query deadline, GPU ownership and native fallback are unchanged.
- All three fixtures exited normally, retained independent returned-pixel checks and left no owned renderer/receiver processes. No SFC gameplay was launched.
- Evidence, analysis and observer sources/binaries are local artifacts. The earlier rotation observer is preserved separately; earlier samples were not overwritten.
- No staging, commit or push.

## Smallest next actions

1. **Geometry handoff:** extend the already-existing session-owned asset-memory delivery to include the finalized neutral scene packet. Parse the same bytes in memory for bootstrap and later assets, retaining existing identity, bounds and ownership checks. Remove both generated `scene.bin` rereads from the active path. This targets an observed delay without changing rendering or geometry.
2. **Completion-stage timeout:** keep the two failed Run254 trials authoritative. If it recurs, collect a trigger-bounded record of time inside `GetData`, time inside the asset-service callback and runtime worker state while that exact query is pending. Avoid assuming the earlier file-open mechanism explains it. Further broad system tracing or repeated sponsor gameplay is not justified by the present evidence.

Step 2's asset-delay investigation has an actionable result. Step 1's completion-timeout cause remains explicitly unresolved; there is no safe evidence-backed renderer-setting change to prescribe yet.
