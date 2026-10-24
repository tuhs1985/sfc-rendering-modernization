# Run157 — two live runs reviewed before sponsor visual feedback

## Scope and verdict

Read authoritative Run156/handoff, attached existing Fuel Guard hook, then
reviewed both completed sponsor runs without requesting or incorporating visual
feedback. Analysis only; no implementation, tuning, dependency, client, staging,
commit or push changes. No further gameplay requested yet.

**All observed objects admitted and submitted; delivery is not seamless and the
two-second startup target remains unmet.** Sponsor visual assessment is pending.
No replacement, visual parity, universal asset coverage or milestone PASS claim.

Curated bounded evidence and result hashes:
`docs/reconnaissance/evidence/20261024-two-live-regressions.json`.
Inputs under `artifacts/remix-runtime/runs/`:

| Run | Sponsor fixture | Objects admitted | Initial preparation | First matching game output |
| --- | --- | ---: | ---: | ---: |
| 20261024-211419-661828-in-game | two ships + shuttle | 3 | 1.357s | 4.237s |
| 20261024-211721-889006-in-game | six ships + late shuttle | 7 | 2.080s | 5.694s |

Times start at the first captured asset discovery, not scenario selection or
mission start. First game output is an actual matching adjacent-frame compositor
audit, not physical scanout or evidence that every individual ship was visible.

## Coverage and arrivals

First run: KFF, FCA, FMS. All three acknowledged, no rejected/partial assets.
Main ships each submitted 5,296 times; shuttle 3,172 times. Shuttle discovered
39.535s after first asset, prepared in 127ms, native-admitted in 134ms.

Second run: KFF, FDD, FFF, FCA, KDD, RDE, FMS. All seven acknowledged, no
rejected/partial assets. Four initial assets prepared concurrently (peak four
workers). KDD/RDE first captured around 11.55s, prepared in 157–175ms,
native-admitted around 203–205ms after their own discoveries. No evidence here
that these assets existed in the capture earlier; do not call all this delay
conversion time. Shuttle first captured at 91.413s, prepared in 133ms,
native-admitted in 158ms; submitted 182 times despite short remaining window.
Other six objects submitted 4,888–5,258 times. These are native draw submissions,
not individual-object pixel confirmations.

## Startup and presentation

First cohort GPU outputs at 4.208s and 5.553s. Initial CPU preparation ends at
1.357s/2.080s. Bootstrap wall time is 2.503s/2.997s; slowest individual Present
boundaries about 1.75s/2.36s. Final first-cohort copy boundary only 16.8/19.4ms.
Thus current live startup cost is not principally raw native mesh admission:
individual native CPU admission is ~1.5–33.2ms, GPU admission ~0.006–3.676ms.
These inclusive stages must not be added across overlapping workers.

Actual buffered delivery after first successful pair:

- First: 5,278 paired of 5,402 records (97.705%); 124 without Remix layer.
  Largest consecutive gap 65 frames, 1.069s first-to-last timestamps (roughly
  1.08s including the final frame interval).
- Second: 5,233 paired of 5,402 (96.872%); 169 without Remix layer.
  Largest gap 77 frames, 1.268s first-to-last timestamps; another 65-frame gap
  spans 1.068s near the late shuttle arrival.
- Buffer provenance failures zero; maximum retained frame ages 24.645/18.108ms.
  No malformed mixed-frame output, missing depth, resource-failed or GPU-busy
  compositor counters. Output stale counters 14/22 are separate from buffer
  omission totals; do not add them as independent missing-frame populations.

CONFIRMED temporal association: the first run's shuttle library publication at
39.665s precedes a 65-frame gap beginning 39.784s. Second run publications at
11.724/11.740s precede a 77-frame gap beginning 12.191s; shuttle publication at
91.548s precedes a 65-frame gap beginning 92.438s.

STRONG HYPOTHESIS: late material-library consumption/first use is stalling the
retained rendering path. Current coordinator atomically republishes the root
USD sublayer list (`multi_scene_relay.py::commit_layers`). CPU preparation itself
is much shorter than the long gaps. Exact Remix-internal allocation/upload/
compilation attribution is not proven; temporal correlation is not a causal
profiler trace. Original SFC drawing remains present, so these records alone
do NOT establish that the original game or HUD flickered.

## Evidence limitations and safety

Performance mode retains counters, not a complete per-owner frame journal.
No independent before/after screenshots supplied. Appearance parity cannot be
adjudicated from these counters. Source-lead diagnostic is PARTIAL: both source
recorders count two invalid observations; first also two snapshot misses;
second exhausts its fixed record capacity (33,892 detailed records dropped).
This is not 33,892 lost render frames. The separate buffered presentation audit
has zero dropped records in both runs and remains usable for gap measurements.
Some projection omissions (0/33) are recorded; not silently treated as zero.

Both runs: error null, normal SFC exit, gate cleanly unloaded, controller and
renderer exit 0, no controller left running. Both owned GPU jobs exit 0,
stop reason 0, remaining processes 0. Accepted installation hashes unchanged;
copied critical files match pre-run hashes; launcher configuration restored.

Evidence footprints ~102.5MB and 223.6MB. Combined conservative M1/runtime/
ingest/D3D9 artifact inventory 19,461,200,284 bytes before final tiny doc overhead,
under 20GB. No evidence deleted this review. Before another larger run, compact
completed generated-image sets with verified recovery archives: four concurrent
256MiB worker reservations will not fit comfortably in remaining headroom.

## Next exact action

### Sponsor clarification and full-timeline recheck

Sponsor reports separate hiccups NOT associated with shuttle additions. Earlier
conversation incorrectly answered that observation using only the largest
asset-adjacent gaps. Rechecked ALL buffered records, grouped omissions across
at most 0.35s of successful delivery, and separately checked callback pacing.
Evidence: `reconnaissance/evidence/20261024-live-hiccup-recheck.json`.

CONFIRMED independent non-arrival omissions, seconds from first asset discovery:

- Two-ship run: 69.317–69.785s, 17 missed Remix outputs interspersed with
  successful outputs; 88.332–88.817s, 24 misses. These clusters span 0.468s
  and 0.485s, NOT uninterrupted freezes of that duration. They begin 29.65s
  and 48.67s after the shuttle material publication. Also one isolated miss
  at 23.835s, well before shuttle arrival.
- Six-ship run: two consecutive misses at 21.957–21.975s; three scattered
  misses at 30.674–30.941s; four consecutive at 37.441–37.491s. These are
  about 10.22,18.93,25.70s from the nearest material publication, all long
  before the shuttle near 91.55s. These are distinct from arrival stalls.
- Neither run has an interval above 30ms between consecutive buffered
  presentation-audit callbacks. Thus this retained audit shows missing Remix
  images while callbacks continue, not a proven whole-game render freeze.
  Physical display pacing and exact sponsor-event matching remain unproven.

Correction: material-arrival stalls are ONE issue, not a sufficient explanation
for all sponsor hiccups. Independent steady-state delivery misses are a SECOND
issue. Their specific cause (render deadline, input availability, camera-related
handoff, etc.) is unresolved; do not attribute them to shuttle/material reload
or assume a cause from the sponsor observation alone. No implementation changed.

Receive sponsor's already-offered independent observations and compare with the
recorded startup and late-arrival gaps. Then target material publication/
consumption stalls using the existing documented NVIDIA mechanisms; retain
geometry, image content, normal 1.5.2 pin and output provenance. No new broad
discovery run is justified by this review alone. Do not begin another test or
change implementation before incorporating that feedback.

HEAD fe2eaf7; index empty; all earlier uncommitted work preserved. This review
adds only the run record, curated JSON and newest handoff checkpoint.
