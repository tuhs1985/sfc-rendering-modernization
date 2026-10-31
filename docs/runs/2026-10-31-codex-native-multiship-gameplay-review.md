# Run229 — multi-ship replacement gameplay review

Sponsor ran the prepared launcher twice: two initial ships, then six. Sponsor reports replacement worked, with more visible native fallbacks on camera changes; appearance differences make those transitions more apparent on some ships. Sponsor subsequently identified the un-replaced ship as the cloaked Romulan. This is a review only: no renderer/configuration changes, new gameplay, staging or commits.

## Results

Both used **Strict**, with no fixture-only artificial delays.

| | Two initial ships | Six initial ships |
|---|---:|---:|
| Run folder, under `artifacts/remix-runtime/runs/` | `20261031-170501-648831-in-game` | `20261031-170825-272571-in-game` |
| Recorded requests after first successful insertion | 5,006 | 4,433 |
| Successful recorded request frames | 5,006 | 4,343 |
| Missed admission deadlines in that interval | 0 | 90 (2.03%) |
| Additional misses before first successful insertion | 10 | 2 |
| Distinct owners with actual insertion/suppression receipts | 4, including two later KFT instances | 5 |
| Median / p95 presentation interval | 16.65 / 17.47 ms | 16.68 / 17.67 ms |
| Median coordination wait | 12.53 ms | 12.56 ms |

Counters are different measures: the native gate ring records a scene frame, while the cohort sidecar counts owner insertions and suppressed mesh lists. The smaller run has 12,132 owner insertions and 16,447 suppressed lists, including primary/secondary KFT paths. The larger run has 10,036 insertions and 10,036 suppressed lists. They are not insertion success denominators.

The smaller run also has eight projection rejections in the renderer; the larger has six. The larger records six limited membership-unavailable events on the LFF owner. These are separate from missed output deadlines. They can leave individual owners native despite another owner being inserted in the same frame. Aggregate logs do not prove the exact per-frame/per-owner relationship between these counters. Zero steady gate timeouts does not prove zero individual native fallback.

Both: normal game exit, controller/renderer exit zero, hooks restored/component unloaded, copied proxy/settings restored and accepted critical client files unchanged. Native gate error/invalid/partial/ring drops are zero; active requests drain to zero; maximum active request and occupied output slots are one. Receiver resource/depth/handle errors and source expiration/rejection counters are zero. Persistent scene reports two registry retirements in the smaller run and none in the larger, with no failed pose updates in either. Registry retirement alone is not proof of a particular destruction event. No accumulating output queue is evident. These findings support functional supported-owner replacement, not seamless universal replacement or alpha completion.

## Camera-transition fallbacks

The larger run has genuine steady-state misses: 90 of 4,433 recorded requests, all timeout outcomes. Several are consecutive rather than isolated:

- 29 consecutive recorded frames, approximately 78.65 seconds into the observation: about **612 ms** from the first frame start through the last presentation.
- 13-frame bursts around 34.76 and 77.73 seconds: about 288 and 285 ms respectively.
- Additional 11- and 9-frame bursts occur around 71.40 and 73.83 seconds.

There are also 537 no-request records between the first and last successful insertion in the larger run. These are not automatically deadline failures: no eligible native submission, offscreen views, or qualification rejection can prevent a gate request. The evidence does not identify each such interval as either harmless invisibility or visible fallback. Do not report the 2.03% admission rate as a complete visible-fallback rate.

Median completed-output readiness is around 12.4 ms into the native frame, against Strict's 16.67 ms admission deadline. Several missed frames have same-frame readiness recorded only by presentation; others have no completed output recorded there. This supports intermittent delivery/qualification timing pressure, not memory exhaustion or steady geometry rebuilds. All five preparation jobs in the larger run finish once; there is no recorded repeated asset preparation during the late timeout bursts. Retained geometry remains in use.

Camera correlation is bounded: the smaller callback probe contains 31,748 records without drops. The larger reaches its 32,768-record cap around frame 3,603 and omits 14,108 later diagnostic records. Only 20 of the 90 steady timeout frames have retained camera-hash evidence; 19 show a change from the previous observed frame. Hash changes also include ordinary camera motion and are not explicit camera-switch events. Sponsor observations associate the visible transitions with camera changes; the data does not prove the exact CPU/GPU operation responsible. The callback-probe cap did not drop the native gate ring or asset transport.

## Cloaked Romulan: upstream exclusion, not a demonstrated Remix failure

Fresh packets include `assets/models/rde/rde.mod`, owner epoch 11/revision 6, but its capture is at source frame **6,377**. The active replacement recording ends at frame **5,382**. The native observer continues during controlled teardown; therefore a packet present in the final folder is not proof it existed while the replacement service was active.

The runtime catalog contains only FFF, KFF, FDD, FCA and LFF. There is no RDE preparation job, asset registration, renderer draw or suppression receipt. Thus **five ships were demonstrated in this six-ship mission**; the Romulan was never submitted to Remix during the measured window. No failed RDE texture upload, Remix material rejection or renderer crash was observed.

Sponsor's cloak observation is consistent with an unqualified alternate visibility/transparency path upstream. The collector discovers assets from qualified owner rows; that path requires established status/transform qualification. Existing packets/logs do not establish exactly which cloak-specific call/state prevents earlier qualification. The late RDE packet itself has ordinary-looking captured groups, but does not reveal its earlier cloaked draw state. Do not call this a proven Remix transparency defect, or suppress the original cloak effect using an opaque hull replacement.

## Recommended next action

1. Compare the same heavier mission under the existing **ExtraFrame** policy before changing buffering or rebuilding assets. It gives completed output more admission time; it may reduce deadline fallbacks but does not solve a rejected projection/member. Preserve timing measurements and distinguish those outcomes.
2. Inspect the separate projection/qualification rejection path at camera changes. Existing counts show this is distinct from output timing. Do not remove exact owner/frame matching or pass stale poses to hide it.
3. Track cloak admission/transparency as a separate compatibility gap. Trace its native draw/visibility state and preserve native cloak behavior until qualified; the present run does not require a new broad payload capture to establish that RDE never reached Remix.

No fix is claimed by this review. Prior supported geometry sharing, fresh textures, native shield/text ordering and clean cleanup remain demonstrated within their test conditions.

Local reproducible analysis: `artifacts/player-replacement/run229/analyze.py` and `review.json`, including raw-input SHA-256 hashes, deadline bursts, catalog/capture comparisons and bounded diagnostic coverage. Original runtime evidence is unchanged. Combined run folders were approximately 309 MB at review; this is actual retained output, not an unbounded-rate estimate. Implementation remains unstaged/uncommitted.
