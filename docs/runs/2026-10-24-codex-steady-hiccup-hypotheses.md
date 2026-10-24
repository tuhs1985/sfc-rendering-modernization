# Run158 — steady-state hiccup diagnosis, no implementation changes

## Evidence

Reviewed Run157 full-timeline correction and actual source, including
`tools/remix_runtime/d3d9_game_receiver.h`, `scene_frame_buffer.h`,
`tools/d3d9_proof/live_owner_input.h`, `live_owner_wire.h`,
`worker_poll.h`, `output_receiver.cpp` and `d3d9_direct_host.cpp`.
Fuel Guard attached existing trusted hook. No game, profiler, helper or agent
started. No implementation/tuning/staging/commit/push changes.

Curated report `docs/reconnaissance/evidence/20261024-hiccup-cause-review.json`
joins retained source-camera hashes, completion observer receipts and the separate
actual buffered compositor audit for NON-arrival windows in both sponsor runs.

CONFIRMED:

- Two-ship 68.8–70.3s window: 17 omitted buffered outputs; latest completion
  observed up to nine source frames behind and ~157ms old. At 87.8–89.3s:
  24 omitted buffered outputs, completion up to thirteen frames behind/~215ms.
  These are observer completion lags, not physical display latency or proof of
  a continuous freeze of those lengths.
- Six-ship independent windows at ~22,31,37s: two,three,four omitted outputs;
  latest completion sometimes two source frames behind. Thus both a larger
  intermittent backlog and smaller deadline misses exist.
- Both actual compositor histories continue recording at intervals <30ms.
  Reset/warm-up occur only at startup, not in these status2 omission windows.
  No malformed output/depth/resource failures, zero old-epoch/expired/age/closed
  input rejections. Thus owner retirement, buffer reset and the 50ms age guard
  are not supported explanations for these particular omissions.
- Native input loop records 36 unqualified packets in the first run, four in
  the second. This counter combines owner/source/thread/decode/projection
  qualification checks; it does NOT localize their timing or specific reason.
  First run's accepted5334 minus received5298 equals36. Multiscene per-instance
  projection omissions separately count0/33. Do not confuse the two counters.
- Camera and pose hashes change in every retained joined row of all reviewed
  windows, including successful deliveries. This does NOT prove a camera switch,
  fast movement, or camera-caused misses; binary hash change is not motion speed.

## Ranked hypotheses

1. **STRONG HYPOTHESIS: exact-frame deadline shortfall.** The compositor restores
   only adjacent N-1 and requires matching frame/sequence/cohort hash; no matching
   ready output means omit the Remix layer. The completion stream demonstrably
   falls behind during these windows. This explains the visible mechanism, NOT
   which upstream operation caused delay. Do not solve by showing old ship
   pixels with a new game camera/scene.
2. **PLAUSIBLE upstream trigger: transient qualification skips.** Verified native
   unqualified counters and combined validation branch can interrupt fresh work;
   this deserves timing/reason attribution, especially the first run's36. No
   per-rejection receipt exists in Performance mode, so camera/projection cause
   is not proven and the validation must not simply be disabled.
3. **PLAUSIBLE upstream trigger: transient render/transfer scheduling delay.**
   Renderer waits for output completion/peer ACK before progressing; receiver
   copies, waits for a fence and publishes through a bounded pool; GPU leases
   retire on an import worker with Sleep(1), while native input uses250us private
   waits. A briefly delayed stage can exceed the one-frame budget even when
   average rendering is fast. GPU execution, queueing, OS wake latency and ACK
   boundaries are not individually timed in retained Performance evidence.
   Zero gpu_busy compositor counter does not prove no upstream GPU stall.

Not supported: these non-arrival hiccups are all shuttle reloads; objects were
retired/rebuilt; two-second startup target was met; larger scene complexity alone
explains them (larger delays occur in the two-ship run).

## Next smallest engineering action

Add bounded in-memory aggregate/tail-event timing and explicit qualification
rejection reasons at the existing external-worker boundaries, flushed on exit.
Attribute first stalled input/qualification/render/transfer/pool publication
versus actual N-1 consumption. Keep it low overhead and fixed capacity; no full
frame/image logging or global tracing. Test offline first. This is a recommended
next change, NOT implemented or a request for another gameplay run in this review.

HEADfe2eaf7, index empty, all prior work preserved. New outputs are this record,
curated cause review JSON and handoff addendum only. No new runtime state.
