# Run189 — live owned-upload checkout active; arrival time not meaningfully improved

Reviewed `artifacts/remix-runtime/runs/20261025-222203-640797-in-game` after sponsor
report: **“ran, didn't see a change in appearance time.”** This is an arrival-time
observation, not an explicit report that every gameplay/control behavior was
normal. Preserve that distinction; raw result's pending sponsor-behavior field
was not rewritten. No new game launch, implementation edit or benchmark in this
review. Fuel Guard attached; credits remain authorized.

## Activation and actual timing

Experimental/parallel/progressive checkout flags are true. Native admission service
and initial-pixel upload flags are actually active. KFF5+FCA56textures report
**61initial uploads,0staged,0unsupported**. Both distinct owners/assets acknowledged,
no rejected/partial assets and5410draws per owner. Current KFF/FCA content signatures
match Run185204448, and frozen light/material/image/quality files are byte-identical.

| Recorded milestone | Latest222203 |
| --- | ---: |
| KFF original-textured base, from its discovery | 236.519ms |
| FCA original-textured base, from its discovery | 399.181ms |
| KFF enhancements, from its discovery | 704.066ms |
| FCA enhancements, from its discovery | 1010.250ms |
| Renderer activation, from first discovery | 264.651ms |
| KFF native catalog admission, from first discovery | 453.871ms |
| FCA native catalog admission, from first discovery | 2929.244ms |
| First matching returned frame, from first discovery | **3683.827ms** |

Run185's first matching returned frame was3890.227ms; difference206.400ms is not
a demonstrated meaningful arrival improvement, consistent with sponsor feedback.
These sessions are not a controlled timing pair or physical display timestamps.
First matching output is not proof of complete final-material appearance.

FCA native resource construction/admission was**8.965ms**; the rejected old staging
lock is not silently running. Native CPU preparation was828.820ms and overlaps
other startup work. Asset conversion is not being blamed for the entire interval.

## Remaining startup wait — stronger existing evidence

Latest bounded startup timing: bootstrap draw/present**2838.088ms**, copy submission
0.004ms, GPU query24.407ms, postprocess1.488ms, first receiver startup/ACK215.771ms.
Cumulative admission-service callback time by that point was9.470ms. First real
cohort draw/present0.641ms, query17.271ms, postprocess1.179ms, peer3.422ms.

The bootstrap aggregate includes24draw/Present iterations,10ms sleeps, light
submission and asset-service calls. This is our existing consumer policy, not a
stated NVIDIA requirement. Live timing does not distinguish its individual
Presents. Do not describe all2838ms as pure GPU work, shader compilation, or an
intentional sleep.

Read-only follow-up of already-retained Run188 standalone startup marks splits
this further, without another run:

- Staged control220718:24draws total1.834ms; Present+service total2841.822ms;
  largest individual Present+service, index21,**2238.987ms**. All admission callback
  work through bootstrap/output totaled15.587ms.
- Initial-data220919:24draws total1.788ms; Present+service total3130.390ms;
  largest individual Present+service, index17,**2397.617ms**. All admission callback
  work through bootstrap/output totaled8.607ms.

Thus the long Present-side interval is confirmed in existing matched-build controls;
small asset-admission callbacks cannot account for its full duration. Which internal
runtime/material/shader/upload work holds it remains unassigned. Correlation to
material publication is a question to test, not a proven cause. Historical single-
Present controls lacked the accepted enhanced appearance: do not blindly remove
the24-Present policy and count incomplete material output as the same result.

## Delivery, cleanup and bounds

5393matching buffered outputs; no provenance failures/audit drops.12post-start
omitted returned layers, longest4records spanning51.010ms. The prior run had96
post-start omissions and late fighters; latest captured only KFF/FCA. Do not claim
a controlled stability improvement from different activity, or invent a sponsor
no-flicker report. No late-arrival integration proof from this game session.

One input failed the existing combined identity/decode/thread/projection qualification
and was skipped. Its counter does not divide the reason or time; do not label it
startup or camera-related. Source-rejected/completion-invalid/input-invalid and
cohort lookup/decode/projection rejection counters are0; no old epoch/age rejection.
It is finite, with no asset rejection or cross-owner evidence.

Normal game exit, gate unload, controller0/renderer0, no leftover controller,
proxy restoration, original critical hashes, launcher settings and complete final
report all PASS. No owned process/channel remains. Total workflow147.063s remains
within its prepared limit. Run folder93,447,824B including image/derived assets;
reported image ledger91,506,178B, text logs122,010B. Existing bounds retained.
Latest fresh capture and its generated assets remain available for the next bounded
offline startup investigation; no bulk cleanup needed in this review.

## Checkpoint and exact next action

Curated evidence: `docs/reconnaissance/evidence/20261025-live-owned-upload-result.json`.
Full comparative timing analysis: `artifacts/staging-integration/live-checkout-analysis.json`.
No new tests were necessary for this read-only adjudication; evidence structure,
referenced paths and `git diff --check` verified. HANDOFF/STATUS/Obsidian updated.
HEAD9ff2d3d; prior implementation remains unstaged/uncommitted, no push. No normal
policy promotion or formal milestone claim.

**Exact next action:** attribute the long startup Present interval using the pinned
runtime's supported profiling/source and existing standalone controls, preserving
final material/lighting output. No repeat gameplay is needed to verify activation
or rediscover the upload lock. Native CPU-preparation828.8ms is a separate remaining
cost; do not add overlapping durations or remove integrity checks blindly.
