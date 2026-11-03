# Run245 — receiver-process creation stalls five seconds

## Finding

The remaining interval is not model conversion, texture preparation, scene hashing or the startup profiler. Two standalone reproductions spend **5001.997ms and 5002.367ms inside OutputPeer.start's CreateProcessW**, launching the existing x86 output_receiver.exe.

Unsampled ExtraFrame: `20261101-030626-629019-return-fixture`. Sampled Strict: `20261101-030936-850550-return-fixture`. Both use the current pinned runtime, performance/async-material path,60-second synthetic menu idle and600frames. No SFC gameplay launched;not an identical gameplay/FPS comparison.

In the unsampled run, scene reread takes0.0751ms and hash0.0569ms;private output channel setup is also sub-millisecond. Maximum combined memory-statistics diagnostic cost across the run is0.588ms (0.278ms sampled). The old coarse materials_enabled marker included memory queries;narrow markers now exclude and independently measure those queries. Diagnostics did not cause this reproduced wait.

Thirty bounded local host-thread samples show29inside ntdll!NtCreateUserProcess, reached through KERNELBASE!CreateProcessInternalW/CreateProcessW and the host. One initial sample catches mapping teardown before that call. First stack walk suspended the standalone host52.425ms;later captures approximately0.3ms. Sampled timings are diagnostic,not an unperturbed benchmark. Symbols came from the previously approved local cache;no new downloads or broad kernel trace.

Four plain-Python-parent controls launch the exact receiver executable in1.656–3.198ms. No arguments deliberately produce input rejection(exit1)before D3D device/channel creation. These differ from real sessions;they establish only that this executable does not universally need five seconds to launch.

## Limits of attribution

- Established: Windows process creation blocks the renderer startup thread after activation. Receiver launch is currently serial and late,on the first-ship critical path.
- No explicit five-second sleep exists in OutputPeer.start. Its five-second waits belong to shutdown/error cleanup. GPU effects/render throughput cannot explain this measured interval.
- Unresolved: which internal kernel operation/process-creation callback causes the wait. User-mode stacks do not establish Defender,NVIDIA or a specific security rule/driver as the cause. Run243's Defender file-open finding does not prove the cause of this distinct operation.
- Shared-memory activation remains fixed. Neither timing policy resolves this later operation.

## Changes and verification

Added only opt-in bounded startup QPC markers around scene read/hash,GUID/security/mapping/events,process creation and console announcement. StartupProfile separately records its own process/system memory-query cost. Normal profiling stays disabled;no per-frame instrumentation,appearance,renderer policy,security or startup-order changes. Other OutputPeer callers retain the default signature.

Ten focused analysis tests and /W4 /WX candidate-host build pass. Both600-frame GPU fixtures pass two independent pixel/depth/native-text checks,three-owner replacement,zero graphics-state errors and normal child/host exit. Qualification refreshed;sampled fixture establishes correctness only. Normal all-ship launcher read-only preflight passes,no game started.

Evidence: artifacts/player-replacement/run245/summary.json,per-run .startup.json,receiver-launch-stacks.txt,plain-process-controls.json,sample-result.json and executed diagnostic sources. Initial sampler attempt stopped before launch on stale build receipt after a test update;host rebuilt and retry passed. No checks bypassed.

Four closed successful runs' converted texture packet sets archived losslessly with per-file hashes checked before loose-copy removal:163MiB reclaimed,176.7MiB original. Original captures,geometry,logs and game assets preserved. Receipt:run245/texture-archive-receipt.json. Restored normal544MiB reservation within existing20GB evidence allowance.

## Next

Prepare the existing receiver/channel during launch alongside the prewarmed renderer. Keep it passive until activation;start active-work timeout at activation,preserve process-death/cancel cleanup and outer workflow limit. OutputPeer.start needs no mesh,texture or rendered surface,so asset readiness does not require its late ordering. **Recommended,not implemented here.** This moves/overlaps the wait rather than proving it eliminated. Exact kernel attribution would need a narrow process-creation trace;the old file-filter observer cannot establish it.

Changes unstaged/uncommitted. No Defender exclusions,protection,original-client or appearance changes.
