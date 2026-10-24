# Run154 — useful NVIDIA trace; profiled teardown incomplete

## Sponsor run disposition

**The NVIDIA trace was captured successfully and is readable. The overall
profiled workflow is PARTIAL, not a clean runtime/shutdown PASS. No repeat is
needed merely to establish that tracing works.** User reported launcher error;
read actual receipts rather than infer trace failure from exit status.

Trace folder artifacts/d3d9-proof/nsight-candidate-20261024-195309-6113982;
standard candidate fixture20261024-195312-767178-return-fixture. Same isolated
1.6.1 synchronous-initialization policy, no SFC or accepted-install modification.
Fuel Guard attached existing hook, no daemon/helper/agent. Normal1.5.2 unchanged.

## Evidence and useful findings

[Curated report](../reconnaissance/evidence/20261024-nsight-first-trace.json).
Actual candidate-startup.nsys-rep7,273,057bytes; NVIDIA installed CLI successfully
exported367,367events to candidate-startup.sqlite18,927,616bytes. SQLite opened
read-only for queries. Report and SQL SHA hashes recorded. No new capture was
started during export/analysis and no registry settings manually changed.

-357,128Vulkan API events;4,628GPU workload rows;113pipeline-creation metadata
  events. All Vulkan API records identify only our renderer PID24076, matching
  renderer-ready.bin; no SFC or unrelated renderer in this API trace.
-111vkCreateComputePipelines calls, largest482.5ms, aggregate threaded time
 10,996.8ms. Their calls occupy trace-relative1.747–3.797seconds and overlap
  across worker threads. **This is NOT11seconds elapsed loading.**
- Two vkCreateRayTracingPipelinesKHR calls total543.0ms threaded time, largest
 272.2ms, within2.672–2.945seconds. Two graphics pipeline calls3.774–3.857s.
- Native renderer-ready receipt maps to3.6559seconds on the trace clock using
  QPC and exported session systemClockNs; initial shader work largely precedes
  it. This supports genuine startup pipeline-creation work, not a conclusion
  that all later bootstrap delay is compilation.
- Fifteen-second capture stops before source/native final shutdown. Deferred
  native stdout was not preserved in report (empty stdout stream), so direct
  bootstrap STARTUP_PROFILE timestamp correlation is missing for THIS run.
  Renderer stderr and pipeline/API activity exist. Do not transplant old run
  bootstrap timings onto this trace as if captured together.
- Batch GPU workload rows may duplicate/overlap intervals. In particular the
  apparent2.046second workloads later in capture cannot be summed or assumed
  to explain the earlier startup stall. CPU scheduling/sampling deliberately
  disabled, so exact CPU loader/wait attribution remains unresolved.

Use installed NVIDIA export/schema/help and the existing
[Nsight guide](https://docs.nvidia.com/nsight-systems/UserGuide/index.html).
No vendor patch, new loader, shader-cache claim, runtime promotion or sub2s result.

## What failed and what passed

Actual fixture child exited0. Log confirms source/HUD pixels exact, border
untouched, state_errors0, resize+device recreation1,595/600paired steady frames,
and expected disabled/reenabled samples. Useful visual/transport fixture evidence
survives despite later harness failure.

Supervisor error verbatim:

```
Live fixture: Owned live GPU workflow failed to retire normally
```

`live_owner_timing.stop()` allows10s to wait for its owned guard. During profiling
that guard owns NVIDIA's wrapper as well as the renderer. After10s it terminated
the guard; inner gpu/job-result.json is absent and final native audit report was
not completed. The outer guarded job recorded exit1, stop_reason0,36.765s,
remaining_owned_processes0. Independent final inventory found no owned GPU
fixture/renderer/receiver/job process. No evidence cap/time cap was exceeded.

**Confirmed harness10s timeout; exporter/wrapper finalization is the leading
explanation, not a proven clean native teardown.** Missing inner receipt means
do NOT claim clean unload or mark this an overall runtime pass. Trace analysis
and passed fixture checks remain valid within their documented scope.

## Narrow diagnostic-only launcher correction prepared

Changed only ignored artifacts/profile_candidate_nsight.py: --wait=primary
avoids waiting for reparented helpers; --show-output=true preserves forwarded
native output when available; only the profiled guard's10s wait receives60s for
NVIDIA finalization, still under existing outer180s/1GiB/2MiB bounds. Normal game
and relay10s behavior untouched. Python parser validation only; **not rerun or
claimed verified**. Fifteen-second capture still does not guarantee late deferred
stdout in its archived stream; forwarded console is intended to retain it.

## State and next action

Only new versionable changes this run: this record, curated JSON and HANDOFF.
No normal code/native/settings/client/dependency/source-lock changes; prior dirty
work preserved, HEADfe2eaf7/indexempty/unstaged/uncommitted/nopush. Raw report,
SQLite, fixture images/captures/logs/receipts retained. Nothing deleted. No new
full regression required for read-only analysis; old499passes remain historical.
JSON/reference/diff validation performed at closeout. No active tracing session
or hidden application state is needed to resume analysis.

Exact next action: continue read-only timeline analysis of this report around
renderer readiness/first-use using its actual API/GPU events and stderr. If
missing application timing prevents attribution, use the corrected bounded
launcher for a specifically justified correlation repeat, not another discovery
run. Do not call this capture failure, native clean-unload pass, all-GPU bottleneck
or11s serial shader time. No immediate sponsor action needed.
