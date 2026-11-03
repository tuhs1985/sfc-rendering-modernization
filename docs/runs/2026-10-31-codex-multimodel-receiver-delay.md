# Run247 — receiver startup stall reproduced in gameplay

Reviewed `20261101-032801-609261-in-game`. Sponsor confirms normal replacement ships,cameras,HUD and controls after initial loading delay. No new execution or implementation edits in this review.

## Startup

First committed replacement enters the native game targets **6059.772ms after first recorded tactical frame**,or5794.556ms after first asset discovery. Of that critical path,**5001.1004ms is inside CreateProcessW for the receiver**. This reproduces Run245's specific standalone stall in actual gameplay;not merely an inferred aggregate delay.

Scene reread0.0846ms,hash0.0449ms;maximum combined memory-query diagnostic cost0.4007ms. Shared startup ticket publish-to-accept10.168ms. Renderer warm-up was complete56.511s before discovery. This is neither late device creation nor five seconds of model/material conversion.

Run246's fast two-ship gameplay checkout used the **same renderer executable hash** and launched the receiver in3.891ms. No code change occurred between the two sponsor runs. Thus the delay is intermittent in the same build. This does not establish whether an earlier cleanup changed susceptibility,and does not identify the kernel cause. Run245's local samples place the wait in NtCreateUserProcess;Defender attribution remains unproven for this distinct process-creation wait. No new trace is necessary to establish its location.

## Model delivery and runtime

22tracked identities all have delivered assets and nonzero native insertion receipts;five unique GPU asset loads(KDD,FCV,KCA,FFT,KFT),17reuses. This is a session total,not proof22simultaneously visible. No partial assets,rejected assets or unfinished jobs. Initial base preparation for unique KDD176.623ms,FCV511.083ms,KCA636.946ms,FFT1265.922ms,KFT749.150ms from respective discovery;queued preparation extends some jobs,but cannot explain the separate measured five-second process launch. FCV renderer-side CPU admission451.327ms is another measurable cost,not this OS wait.

After first insertion:4721requested frames,4717commits,4requested fallbacks. Owner receipts:32047insertions,74621suppressed submissions,17owner-unavailable observations,zero omitted. Suppression counts include repeated native mesh submissions;not one-to-one with frame/owner insertion counts. Fighter1–4display multiplicity remains deferred SFC-22;no new mechanism claim from these counts. Before first success,normal initial preparation remains visible in native-frame evidence.

Registry102328pose updates,95462offscreen,zero failed/rejected updates,10retirements. Three diagnostic calibration misses are not failed functional publications. Frame-period median17.659ms,p99 20.726ms,max28.636ms. This busy battle differs from Run246's workload;do not infer cleanup-induced FPS regression from unlike missions.

Normal game exit,renderer0,controlled unload,proxy restoration,unchanged accepted-client/launcher checks all pass. Sponsor reports normal operation after loading. Recorded tactical window90seconds;total workflow197.203seconds. No per-object exact first-pixel timings or universal-model support claim.

Evidence: `artifacts/player-replacement/run247/multimodel-review.json`,original result/native-gate binary/startup logs retained in source session. No staging/commit or source edits.

## Next

The five-second launch is now confirmed as a real-game startup blocker,not an artifact unique to standalone fixtures or a requirement to process many models. Same-call/same-build fast-versus-slow evidence supports reviewing launch ordering and OS context. Moving receiver creation into passive launch preparation would take this operation off first-ship readiness;still only a proposed mitigation. Exact Windows-internal cause remains unknown. Preserve Defender protection and avoid unrelated asset/material changes.
