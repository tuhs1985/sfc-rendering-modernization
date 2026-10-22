# Run87 — fast-camera flicker deadline attribution

Local2026-10-20;UTC evidence20261021. Sponsor asks investigate cause,not implement
new synchronization. Read HANDOFF/Run86 and Run84 retained runtime receipts.
Fuel Guard attached through trusted-hook receipt;no daemon launched. HEADd29111f7,
index empty,prior dirty work preserved. No SFC/Remix launch,helper,agents,commit/push.

## Method

New offline tools/d3d9_proof/analyze_delivery.py joins validated native observer
audits,source stage1camera hashes,host live-input.csv and frame-timing.csv from
artifacts/remix-runtime/runs/20261021-024303-198180-in-game. It makes no runtime
changes. Source identity/session/PID/order validation reused from existing parsers.
Join input by source sequence/owner/revision/frame. Timing CSV sequence is loop
index,NOT output sequence(light omissions skip outputs):join unique source frames
and explicitly skip ambiguous repeats instead of misassociating samples.

Reproduce using bundled Python:

```powershell
python tools/d3d9_proof/analyze_delivery.py artifacts/remix-runtime/runs/20261021-024303-198180-in-game
python -m unittest discover -s tests -p "test_d3d9_delivery_analysis.py"
python -m unittest discover -s tests -p "test_*.py"
git diff --check
```

## Findings and confidence

CONFIRMED code:game_output::matches requires exact session,source sequence,owner,
revision,frame and state hash. d3d9_game::Receiver::step releases unmatched output
without drawing. It does not hold the previous picture. This converts missed
delivery windows into omitted additive-ship frames,not stale camera placement.
No evidence that this is a UV/material reload problem or insufficient model data.

Observer4956matched,474old/different,1no completion,1ineligible.475eligible misses:
457expected outputs taken before observer but completion after it;2not taken until
after observer;16have no retained expected output. Completion<=observer but not
matched:ZERO. Absence of retained output is not evidence of GPU failure;existing
light omissions/source skipping need separate treatment. No false match assertion.

For459misses with output timings,346have pre-peer work definitely unfinished at
observer time,even allowing microsecond timing quantization.113sit at transfer/
publication/ACK boundary:host timestamp is AFTER ACK,so cannot prove pool image
was unavailable at observer for every such case. Native compositor executes at a
different callback:475observer misses are NOT431stale-image rejections or a perfect
per-image audit. No independent physical-display capture.

Matched vs missed median milliseconds:

| Quantity | Matched | Missed |
| --- | ---: | ---: |
| Source offer to observer budget |15.435|14.628|
| Source offer to completed/ACK |12.469|15.873|
| Queue before worker takes input |0.879|1.467|
| Render-ready GPU wait |9.691|13.053|
| Postprocess |0.571|0.550|
| Peer transfer/ACK |0.774|0.749|
| Light update |0.0042|0.0042|

Misses finish median1.195ms late,p95lateness7.847ms,max20.769ms. GPU wait covers
rendering/scheduling/queued work/output completion,NOT independently measured
ray-tracing shader duration. Cannot prove GPU contention or temporal history
invalidation specifically. Current light update is not the observed dominant delay.

Camera hash changed since previous adjacent source frame:401misses/3043checks
(13.18%);unchanged:74/2388(3.10%). CONFIRMED state-change association,not speed
measurement or proof that rotation alone caused every missed frame. Hash includes
captured camera state;no user input timestamps/magnitude. Combined with sponsor's
direct fast-camera observation,STRONG HYPOTHESIS:camera-dependent workload and/or
shorter source window pushes an already marginal same-frame chain over deadline.

First observer match frame1216;initial30-frame unmatched streak includes warm-up,
not steady-state fast-camera failure. After first match:4956matched/445missed.
Overall streak histogram includes326single misses,27two-frame,7three-frame,
2four-frame,one each5/6/11/14/30. No exact action timestamp to label long streaks.
Do not blame6000record cap or intentional disabled teardown for these earlier misses.

## Disposition / next smallest action

Delivery remains OPEN,M1 CONTINUES. Runtime texture-preparation improvement from
Run86 is independent and retained. No rendering implementation,quality reduction,
30Hz cap change,stale hold,whole-frame buffering,original suppression or replacement.
Most concretely supported bottleneck is render-ready wait plus a tight same-frame
window,not texture loading or final transfer as the sole cause.

Next smallest action:bounded offline critical-path experiment to separate worker
wakeup/queue overhead from render-ready work under camera-changing input. Compare
event-notified input with current Sleep(1) polling only if reviewed;preserve source
identity/deadlines/current effects. This may recover margin but must not be promised
to eliminate worst-case tails. If same-frame completion still cannot be reliable,
seek explicit synchronized whole-frame pacing/buffering decision rather than using
stale ship pixels or merely loosening identity checks. No gameplay action needed now.

Files:analyzer,tests/test_d3d9_delivery_analysis.py,curated JSON,this record,HANDOFF.
Validation:six focused synthetic tests and370total Python tests PASS;git diff
--check PASS,index empty. Checks
cover missing source,identity mismatch,late queue/render,ACK ambiguity,camera hash
change,streak gaps and ineligible exclusion. No native rebuild;runtime unchanged.
No bulk outputs generated/raw captures modified. Index empty,changes unstaged/
uncommitted,client files untouched,no active runtime sessions. Launcher qualification
still stale;NO NEW LAUNCHER READY.
