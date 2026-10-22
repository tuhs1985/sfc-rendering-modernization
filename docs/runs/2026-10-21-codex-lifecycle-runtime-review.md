# Run95 — lifecycle runtime review: fresh return confirmed, unload timing defect

2026-10-21 America/New_York. Sponsor reports "done" after dedicated lifecycle
runner. Reviewed newest HANDOFF/Run94/probe, actual053837run, raw JSONL and fresh
packets, native controller wait and Python cleanup logic. HEADd29111f7,index empty,
existing dirty work preserved. Fuel Guard recent-hook receipt confirmed, no daemon.
Read-only runtime review plus durable evidence/handoff; no implementation change,
game launch, helper, agents, stage, commit or push. Sponsor action/behavior report
requested asynchronously; not inferred from "done". Subsequent sponsor answer
"yes" confirms the requested alive camera-away/return and own-ship destruction
sequence. This is human observation,not a native death signal or exact timestamp.

## Direct runtime evidence — CONFIRMED

Run: artifacts/remix-runtime/runs/20261021-053837-052998-in-game, PID41176.
All four requested cues issued at formal seconds15.031,25.015,40.031,60.000.
These are cue times,not verified gameplay action times. Component elapsed time
below has a DIFFERENT origin; do not equate it with formal cue seconds.

Raw state JSONL:1829valid96word records,1180251bytes,all lines complete.
Transition journal:6valid records,2394bytes,all lines complete. Actual visibility
epochs retained far beyond the old~5second cutoff:

| Owner/revision | Model | Observation interval, component ms | Retirement frame/ms |
| --- | --- | --- | --- |
| 1/1 | KFF enemy | 0..97031;953rows | 5223 /97031 |
| 2/2 | FCA selected player fixture | 47..33094;369rows | 1987 /33094 |
| 3/3 | FCA fresh returning epoch | 36703..82985;507rows | 4980 /82985 |

Returning FCA geometry equals initial FCA:positions,corners,polygons,groups and
used points all equal,geometry SHA256
16981bd6f5b84f8d9f17f1395a92b34011387ddba5e1a64fbff4b21bd81e65a5.
Resource records,group assignments and secondary-role evidence also exactly equal.
Packet hashes differ because epoch/frame provenance differs;expected,not geometry
corruption. Same native model/source addresses are corroboration only,not identity
authority. KFF did not get silently substituted for player.

Renderer remains pinned2/2,last displayed source frame1984. It does not rebind3/3.
1661draws,21stale;zero invalid/resource/depth failures. Received1693valid owner
inputs;3238ineligible audits after disappearance. One source rejection remains
reported;do not claim every channel zero. Source timing counters separately all
zero anomalies over10442callbacks;renderer exit0,normal owned exit,completion
invalid0/audit drops0. No death-state/destructor instrumentation was added.

## Interpretation

CONFIRMED:content-identical player ship returned under a fresh epoch while renderer
stayed pinned to the old one. This independently repeats Run92 and supports
content-qualified epoch rebind,NOT removing retirement or accepting pointer reuse.
CONFIRMED:later FCA observation retirement exists and no later FCA return is
recorded. That is render-observation absence only. Sponsor subsequently confirms
actual destruction and alive camera return. A native death discriminator
remains UNQUALIFIED. No conversion of cue timing/absence into verified death.

## Cleanup deficiency — separate from useful data

Result PARTIAL: `Semantic component removal/unload not confirmed; exit normally`.
Normal game exit true,controller8,renderer0. No worker summary exists,therefore
final loss/queue/drain counters cannot be checked. Six retained complete events
are useful direct evidence,NOT a complete lossless lifetime trace.

CONFIRMED static timing defect:controller waits120seconds AFTER tactical gate
before attempting stop. Python completes <=30seconds prep plus90seconds formal,
then waits only15seconds for controller. Actual first-image preparation4.625s;
roughly94.625+15seconds from gate is too early for120second controller stop
(allowing small initialization differences). Runner can request exit on its own
cleanup error before controller reaches its removal time. Controller log says
target exited before removal,not failed hook restoration. No evidence here that
the semantic seam itself cannot unload. Exact stop scheduling needs correction;
do not loosen cleanup criteria or repeat gameplay merely to work around timing.

Original critical files unchanged,launcher settings unchanged,test proxy restored;
copied critical hashes equal accepted baseline. Both client SHA256 remain
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
No active SFC/owned worker process at check. Existing vendor warning40 persists.
Logs/CSV/JSONL2087600bytes,total run88690172bytes including generated copies;
comfortably within existing caps. Raw partial game evidence retained;clean-game
archive guard not bypassed. No image dumps or new captures created.

## Validation and final state

Parsed every retained state/event row and native-decoded both FCA packets;compared
geometry/resource fields and hashes. Reviewed source counters,normal exit and
rollback receipts. git diff --check PASS;no rebuild required for evidence-only
review. New evidence JSON and this record plus HANDOFF are this run's only edits.
All prior implementation/evidence work remains unstaged/uncommitted,index empty.
No M1/TRL gate advancement or lossless capture/controlled-unload PASS claimed.

Next smallest action:correct controller/runner stop synchronization offline so
worker drains and hook removal precede exit request. Preserve new lifetime data;
then use fresh-content-qualified rebind for returning epochs rather than doing
another broad capture. Sponsor confirms the requested action sequence;the terse
"yes" does not separately describe rendering/control anomalies or their absence.
