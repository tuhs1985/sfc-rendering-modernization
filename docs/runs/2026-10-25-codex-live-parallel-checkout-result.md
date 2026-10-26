# Run183 — first live parallel/progressive checkout successful within fixture

Reviewed `artifacts/remix-runtime/runs/20261025-192053-388603-in-game`.
Sponsor: about3seconds initial loading, estimated2seconds faster; follow-up
explicitly confirms **no flicker or other issues noticed**, including SFC itself.
No game/renderer launch or source/settings change during review.

## Confirmed activation and comparison

Manifest/result experimental_parallel_assets=true, preparation parallel_parts=true,
experimental_live_checkout=true, performance mode/detailed evidence=false. This
actually exercised the Run180 dependency graph, ready-ship admission and per-group
material publication. It was not the stable launcher used for Run181.

Prior stable run190849 and current run192053 have exactly equal KFF/FCA content
signatures and geometry hashes. Different live sessions are not a randomized
benchmark; visual estimates also have no common manually supplied start timestamp.
Comparisons below use first captured asset discovery on the shared QPC clock:

| Recorded milestone | Stable190849 | Experimental192053 |
| --- | ---: | ---: |
| Renderer activation | 1.500115s | 0.355788s |
| KFF native admission | 4.355950s | 1.227371s |
| FCA native admission | 4.398148s | 3.368412s |
| First audited matching game/returned frame | 4.491866s | 3.488309s |

About1.00s improvement to the first audited matching frame; sponsor's approximate
2s visual improvement is preserved separately, not converted to measured timing.
Native admission is not first physical display. Full loading below2seconds is
not achieved. New KFF diffuse prep292.33ms/enhanced420.06ms from its discovery;
FCA diffuse1153.53ms/enhanced1780.55ms from its own discovery139.18ms later.
Last enhanced stage published1.92928s after first discovery, ahead of FCA admission
3.36841s and first paired output3.48831s. Remaining post-preparation delay is not
yet attributed to one vendor/internal operation.

## Delivery, lifetime and cleanup

Both owners admitted/acknowledged, no rejected assets or preparation partials.
KFF5410/FCA5408draws.100bounded progressive events include individual material
completion and atomic stage publication. CPU stage readiness is not a measured
per-group GPU-consumption time. Peak accounted working images5,909,020B/81,592,248B.

Buffered audit5540records/zero audit drops/zero failed provenance checks:
5399paired,139without ship,1warmup,1reset,max paired audit age18.356ms. Of139without
ship,134preceded first paired output; **five occurred afterward**, in four gaps,
longest2records (~17.5ms between those two records). At discovery-relative3.7544s,
13.8542–13.8717s,14.0043s and66.0017s. Do not claim perfect delivery or infer visible
flicker from every omitted extra-ship output. Sponsor observed none. Prior stable
run had22post-start omissions versus five here; full-session counts do not replace
the separate fixed-window offline gate.

Original critical hashes, copied/accepted baseline checks, launcher settings and
proxy restoration passed. Normal game exit, gate unloaded/controller0/not left
running, renderer0, normal owned exit, final report complete, error null. No
original suppression, protocol/native/runtime/SDK/settings changes, process or
channel remaining from analysis. No staging/commit/push; HEAD9ff2d3d.

## Adjudication

**Successful first sponsor-operated experimental checkout of parallel preparation
and progressive materials, with faster observed/recorded arrival and no noticed
gameplay regression.** Limited to this two-content fixture. Run180's deliberately
delayed-material stress gate remains unresolved; this run completes material
publication before the first paired frame and does not prove interruption-free
late changes. Stable default remains unchanged; experimental opt-in remains
available. No formal milestone/sub-two-second/universal scene claim.

Exact next action: attribute enhanced-stage-ready→FCA-admission/first-paired output
using retained runtime evidence, preserving the successful experimental path;
keep non-disruptive genuinely late material consumption as a separate open gate.
No repeat same-fixture gameplay required to confirm activation.
