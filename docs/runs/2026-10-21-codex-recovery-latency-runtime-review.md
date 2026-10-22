# Run97 — reconnection works;visible delay NOT accepted

2026-10-21 America/New_York. Sponsor reports copy works but slight delay when a
camera loses visual contact;explicitly unacceptable. Read current HANDOFF/Run96
and actual062533run. Fuel Guard trusted recent hook,10%advisory with credits;
bounded analysis completed. HEADd29111f7,index empty,prior dirty work preserved.
This run analysis/docs only;no code change,launch,helper,agents,stage/commit/push.

## CONFIRMED runtime findings

artifacts/remix-runtime/runs/20261021-062533-368618-in-game. One actual FCA rebind
observed,2/2->3/3,ACKgeneration2/rejected0,same resident content signature
60db5ad77a07374cf83a0997c09d889ffbd27740c306b31c382f5920f8342eda.
Two camera cycles were cued,NOT two proven FCA epoch changes;other new epochs
were KFF1->4->5. Do not inflate this into repeated generic-player-lifetime PASS.
Fresh native light packets for new epoch3were supplied;no renderer/asset restart.
Initial preparation16.640s remains separate,also not acceptable as eventual baseline.

5328inputs,invalid0,unqualified1;5192draws,96stale. Source rejected0,audit drops0,
completion invalid0. Source timing separately invalid2 over11364callbacks;other
source counters0. No blanket zero-anomaly claim. Original rendering never suppressed.
Sponsor confirms functional recovery but rejects visible latency;no independent
new blanket HUD/control checklist confirmation inferred from this statement.

## Measured return delay,not camera-switch timestamp guesses

Joined raw SOURCE-TIMING records with live-input.csv and immutable presentation
audits on owner/revision/frame/QPC. Start is first semantic observation of fresh
FCA3/3(frame2613),NOT sponsor camera action or physical screen-photon time.

| Endpoint | Delta from first fresh semantic observation |
| --- | --- |
| First offered packet that eventually produced returned output(frame2635) |365.0606ms |
| First returned output completion(frame2635) |381.3986ms |
| First strict matching Present audit(frame2647) |580.3088ms |

Rebind request refers to frame2619;ACK was observed63ms after request. This
coarse Python ACK measurement excludes earlier packet capture/requalification and
later lighting/GPU/presentation work. It is NOT total recovery latency. Native
first source records for owner3exist before source selection changes. Light
omission logs cover source frames2627..2634. Therefore available semantic state
was not immediately delivered as a usable image;this is our pipeline deficiency,
not merely SFC withholding an offscreen object.

First output completion missed its same-frame Present by0.369ms;following
frames2636..2642missed by2.426,4.978,7.288,9.856,11.566,16.033,18.157ms. Frame2647
completed1.029ms before Present and first strict matching audit appears there.
This corroborates an additional re-entry frame-budget/backlog problem after the
initial control/light wait. Exact compositor-draw onset/physical display time is
not recorded,so0.580s is a strict-receipt latency,not exact visible-pixel timestamp.

CONFIRMED:requalification/ACK/light publication and missed deadlines lie on return
critical path. STRONG HYPOTHESIS:serial Python polling/file-mediated lighting and
transient re-entry render workload are material contributors. Exact per-stage
share and vendor-side cause remain unresolved;do not assert shader compile/GPU
resource reload without evidence. Resident resources were retained.

## Cleanup / evidence integrity

Overall PARTIAL:Semantic component removal/unload not confirmed;controller8,
no worker summary. Normal game exit true,renderer0;target exited before controlled
removal. New deadline logic exists,so do NOT simply repeat Run95's old15s-timeout
attribution. Actual cause/timing of exit relative to requested cue not established.
Keep controlled-unload verification OPEN,not a hook-restoration failure claim.
No active game/owned renderer remains. Original/copy critical hashes equal,
original critical files/launcher settings unchanged,proxy restored. Supported
client4D65761D...20C29unchanged. Total evidence90650137B,under established caps;
raw partial run retained,no clean-game archive bypass. Vendor warning40open.

Validation:parsed runtime result/journal,raw native timing/audit records,CSV;
cross-joined exact identities and QPC frequency10MHz. git diff --check PASS.
No build necessary for analysis-only change. New curated evidence,this record
and HANDOFF only;prior/new work unstaged/uncommitted,index empty.

## Disposition / exact next action

Functional fresh-epoch reconnection demonstrated for this fixture,performance
deficiency OPEN and sponsor explicitly rejects it as baseline. No formal gate
advancement. Do not ask another gameplay run to rediscover this delay.

Next:bounded offline profiling/change to remove serial recovery/light handoffs
from first usable-frame path and eliminate the measured re-entry deadline misses,
while retaining fresh semantic qualification,identity,lighting provenance and
exact-frame rejection. Reuse resident resources;do not display stale pixels,
weaken retirement or turn on exhaustive geometry tracing. No implementation
authorized/inferred solely from this feedback during this analysis turn.
