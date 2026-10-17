# RT-005 — zero exclusions; retired epoch successfully reobserved

**M1 CONTINUES — additional bounded evidence required.** No classification
exclusions reproduced. Read-only sampling dynamically resumes on a fresh epoch;
34 valid snapshots through85s support transform/input qualification. Neither
zero exclusions nor sample count alone establishes full normal-space/TRL4 PASS.

## Runtime and sponsor evidence

Run artifacts/m1/runs/20261012-010503-enabled, PID37852, component0.8;
started2026-10-12T01:05:03.6282463-04:00, normal exit01:07:42.1096324-04:00.
[Definition](../probes/M1-C01-RT-005.md):90s/two raw interest filters/36 maximum
snapshots/18 five-second windows/64 polygons x8 corners/3MiB; semantic120 epochs/
10k events/eight owners/16–32MiB, diagnostic32 signatures/64 examples/64KiB.
Geometry/tint/shading disabled. No source/model writes or fresh downstream proof.

Sponsor confirms target tracking off, briefly slewed to bring enemy into view,
ship moved/turned after third cue, no rendering/control issues. No precise slew
timestamp is available/needed; initial visibility/setup is not a pure stationary
baseline. View loss is compatible with observed render gap, but not proven the
sole cause. Do not equate on-screen visibility with render-owner lifetime.

| Epoch | Ship | Visual | Model0 | Source | Samples |
| --- | --- | --- | --- | --- | --- |
|1|0A4586C0|0A450E48|1DA1C20C|0FFBA9C0|18,78ms–85,015ms|
|2|0FFB6EA8|1C56EA40|1DA1C518|048D365C|2,3,469–5,000ms|
|3|0FFB6EA8|1C56EA40|1DA1C518|048D365C|14,20,687–85,015ms|

Epoch2 retired6,094ms; same raw(ship,visual) filter reobserved20,687ms with literal
fresh ID3. No merging of IDs/identity continuity claim from raw address reuse.
Filter1 windows2/3 (10–20s) have no observed mainline events, not unreadable
captures. Filter0 all18; filter1 total16. Transition ledger complete, dropped0,
outside-filter0, thread/visual mismatch0; no stale epoch2 used for later captures.
Thus bounded fresh-epoch reobservation is **CONFIRMED**, corroborating existing
lifetime policy/static sampler and observed transition/new-ID records. Previous
RT-003 gap explanation remains hypothesis, not retroactively proved.

## Numeric observations

All34 snapshots status0/no nonfinite data. Corner vectors/indexed positions
remain bitwise fixed **within each literal epoch/model/source**, comparisons
reset on fresh ID3. Epoch1 supplied basis10 unique patterns; epochs2/3 respectively
2/5. Epoch1 basis stays fixed through30s then changes from35s, while composed
transform changes earlier. This is consistent with camera influence on composition
and commanded object turn affecting supplied basis, corroborated by tracking-off
sponsor report, but no exhaustive causal isolation/player-owner assignment.
Maximum supplied basis Gram errors1.075315e-7/6.760673e-8/1.211220e-7;
approximately orthonormal over these sampled poses. Epoch1 vector magnitudes
0.9999493..1.0000554; epochs2/3 0.6761773..1.0000000. Don't normalize game data
or treat one source index as one normal. Model-local interpretation strengthened
(STRONG HYPOTHESIS); exact scale/handedness/inverse-light contract still pending
lead adjudication against existing static transform/light evidence.

## Rejections, safety and bounds

Diagnostic total0 reconciles with aggregate0; all pre-gate/tactical kind/reason
counters0, no buckets/examples/overflow/omission. This is **CONFIRMED non-reproduction**,
not identification/fix of RT-004's2,658 cause. Don't attribute the difference to
target tracking without paired control. Retain prior finding as non-reproduced;
no automatic repeat solely to provoke an exclusion. Diagnostic mechanical tests
remain offline evidence, not runtime coverage of failed reads.

5,391 gated epochs/15,095 Model0 calls; known00509843 count5,395 finite/unassigned.
No owner/thread overflow, interventions/leases or hook-state failure. Component/
controller restored bytes, duration stop/removed, normal exit; no remaining game/
controller observed, temporary proxy/config absent. Client SHA256 independently
unchanged4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29,
MD52BE8F713F81B1C68D50EAD6088C32886. Startup succeeded, prior error cause unresolved.

CSV203,104/packet606,954/summary2,470 bytes. Detail saturated120 epochs/709events,
full counters continued. All16 files879,094 bytes; well below all caps/10GB ceiling.
Verified archive artifacts/m1/archives/M1-C01-RT-005-20261012-010503.zip109,867 bytes,
SHA256DBD5EC7701D26335950835ECCCAE93478416DAD97009FA21B3568FBEF6270786;
all16 archived entry hashes match raw. Small raw retained/ignored, none deleted.
RuntimeDLL F5354324485F365738D7A1027441D5C678CB984AC7CDB8E8AA9CC9C01EF9F7CC;
controllerCBC3FCCE973DEBEDBA4ACADFED3BA6781718087B9EA8C408886B89FA2BE1B879.

Next smallest action: adjudicate the corner-vector/transform mathematical contract
using retained RT-004/005 numeric evidence and existing scalar transform/light
byte anchors. Do not request another run just to fill two genuinely absent
windows or chase an unreproduced aggregate; no C-02 implementation authorized.
