# Run246 — gameplay functional checkout after memory-ticket change

Reviewed sponsor run `20261101-031833-357227-in-game`. Sponsor confirms ships,lighting,shields,pause text,controls and camera switches all looked normal. No offset/manual timing required. No implementation changes or new game launch in this review.

## Startup measured in the game

- First recorded tactical/native frame to first committed insertion: **695.092ms**;its Present callback at699.383ms. That first ship is KFF,owner1. From CPU asset discovery to insertion:553.703ms.
- F-CA,owner2,is independently proven inserted **by1645.211ms** from first native frame,or1499.162ms from its asset discovery. This is the first owner-labelled committed gate record,an upper bound on earliest F-CA appearance:the shared cohort may already have included it before it became the gate's representative owner. Do not label this as its exact first visible pixel time.
- CPU base readiness:KFF96.491ms,FCA378.283ms;enhanced derivative readiness429.342/752.593ms. Derivative completion is not runtime consumption/visible enhancement proof.
- The receiver CreateProcessW call is3.891ms this run,not the5.002s measured in Run245's two standalone fixtures. No launch-order fix was applied. This establishes the delay is not universal;does not prove why it happens or whether earlier cleanup introduced it.
- Shared startup ticket published-to-accepted6.075ms. Host warm-up was already complete approximately35.5s before discovery. Startup memory profiling was enabled in this actual process (retained receipts);maximum diagnostic cost is separately available. Do not call the run diagnostic-free or a controlled comparison with prior fixtures.

Timings share the existing QPC clock. Native insertion/Present callbacks establish return into the game,not physical monitor scanout. The normal tactical recording is90seconds;total workflow176.156seconds,normal game exit afterward.

## Function and continuity

Both qualified assets delivered with no partial assets/rejections/unfinished jobs. Native owner receipts show5335insertions and5335suppressed submissions (KFF2569,FCA2766),zero owner unavailable/omitted. These owner operations differ from per-frame gate records;do not compare as one-to-one counters.

Across5372recorded native frames,4327gate records commit. After first successful insertion:4370requests,4327commits,43requested fallbacks (~0.98%);962other frames have no gate request. No-request frames are not evidence of a missing replacement. Header totals include47deadline misses and36stale observations;stale is not an additional independent failed-frame count. Longest requested-fallback sequence11;not necessarily11consecutive display frames. No gate errors,invalid commits,partial commits or dropped evidence. Sponsor reported no visible swaps/problems. Do not claim zero fallback or universally seamless scheduling.

Frame-period median16.693ms,p9517.935ms,p9921.016ms,max26.918ms. Persistent registry:12387pose updates,6192offscreen,zero failed updates/rejections/calibration misses. This confirms tracking continued independently of camera visibility in this run.

Renderer/controller exit0,normal game exit,controlled unload,proxy restoration,unchanged accepted client and launcher settings all pass. No cleanup regression evident in this run. Existing vendor teardown warning about common device objects remains recorded;do not turn it into a clean-runtime-internals claim.

Evidence summary:`artifacts/player-replacement/run246/functional-review.json`;source native gate binary/result/startup QPC logs retained with original session. Changes remain unstaged/uncommitted.

## Next

Functional checkout accepted with sponsor confirmation. Investigate intermittent receiver launch delay against earlier working/current ordering before changing scheduling;this run's3.891ms launch is a useful same-host counterexample to Run245's slow launches. Preparing receiver earlier remains a possible mitigation,not an implemented fix or proof of root cause. No immediate repeat gameplay test necessary.
