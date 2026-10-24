# Run119 — six-ship fixture:three returned,coverage PARTIAL

2026-10-22 America/New_York. Completed UTCfolder
`artifacts/remix-runtime/runs/20261023-034948-568962-in-game`.
Sponsor reports three of six ships displayed,initial flicker that quickly settled.
Sponsor manually cycled ships not initially in view and confirms three identical
Klingon enemies. Do not dismiss missing objects as simply never observed by user.
Read-only review;HEADd40f8f2,indexempty,prior work already unstaged/untracked.
FuelGuard trusted-hook attached;no source/config/build/game launch/helper/agent.

## Confirmed findings

Four native captured owners/revisions,each with a different captured model:

| Owner | Model | Backend disposition |
| --- | --- | --- |
| 1 | Federation FDD | admitted,5251draws |
| 2 | Federation FCA | blocked by conservative aggregate image-output budget |
| 3 | Federation FFF | admitted,5248draws |
| 4 | Klingon KFF | admitted,5076draws |

Native persistent registry admitted FOUR owners,not six;four captures,zero capture
failures/owner overflow/unsent assets. Thus there are TWO DIFFERENT deficiencies:
one captured ship withheld downstream by budget,and two identical Klingon instances
not represented as separate captured/registered owners. Asset deduplication alone
does not explain or qualify their absence. The instance limit is32 and no overflow
occurred;this is not a three-owner limit.

Image accounting127,424,806bytes of128MiB(134,217,728bytes),105unique original
images of256allowed;remaining6,792,922bytes. FCA explicitly reported
`Cohort conservative image budget;asset postponed as partial`. This is our
original/derived image-output accounting guard,NOT measured GPU-memory exhaustion.
Conservative resident CPU+GPU backing60,669,336bytes below256MiB. Do not equate
the sponsor's20GB artifact allowance with authority to silently change this cap.
Existing identical-content sharing should permit independently qualified repeated
instances without reloading their geometry;actual repeated-owner qualification is
not demonstrated by this run.

Raw synchronized audit5405records:5227paired,176missing,onewarmup/onereset.
Afterfirstmatch:173/5400missing;long initial clusters82frames338–419 and69frames
594–662. Output GPU waits1287.807ms at338 and1107.872ms at594,consistent with the
already isolated late-material reload problem. After sourceframe1000:4707paired
of4711,only missing4547–4550. No claim of perfect steady delivery.
Zero cohort lookup,decode,projection or input admission rejections;repair holds
at those stages.5253accepted inputs,5251published outputs,20stale images,
zero invalid output,overwrites,resource failures or missing depth. GPUstage p50
9.350ms,p9512.618,p9916.533,max1287.807;median is not the cold-arrival cost.

## Narrow capture-identity hypothesis

Read existing `m1_contract.h::OwnerTable` and `m1_component.cpp::record`:
owner admission uses native ship identity,but model-stage ownership is reassigned
through `g_owners.find_by_visual(event.visual)`. That function returns the FIRST
active matching visual. If multiple native ships share that visual,model
observation can collapse onto the first owner despite separate ship callbacks.

CONFIRMED static ambiguity;STRONG HYPOTHESIS for the missing repeated Klingons.
This run lacks retained unsaturated per-ship/visual tuples proving actual sharing.
Do not claim that model sharing itself is confirmed or that every shared visual
is one ship. Current shared-geometry backend acts AFTER owner qualification and
cannot recover instances that never reached it. Exact next investigation is the
native owner/visual/model association for repeated ships,not broad renderer RE.

Semantic diagnostics5454rejections:2727visual-stage reason2(ship-vtable guard),
2727model-stage reason12(no active visual-owner match). First bucket observations
start78.906seconds;they do not by themselves identify the initially absent ships.
Summary also records10render-owner retirements and7destroy-hook invocations while
persistent registry recordszero destroyed tracked owners. Do not reinterpret
hook counts as seven confirmed tracked-ship deaths. Need per-context correlation;
do not weaken identity guards merely to admit unknown objects.

## Validation,cleanup and final state

Reviewed final report (`PARTIAL`,errornull,final_report_complete=true),capture
association JSONs,raw synchronized audit,backend timing/stage summaries,lifecycle
worker and native rejection diagnostics,existing owner lookup and content-sharing
code. Current configured MaxOwners32,geometry hookOFF;no capacity overflow.
Native detailed event CSV saturates early and is NOT a complete owner census.
Persistent28235pose publications/21037offscreenupdates,zero failed pose updates.
Native worker one diagnostic drop,zero invalid/IOfailure;3,562,892evidencebytes,
91cohort samples. APIshutdown0;40undisposed runtime objects remain unresolved.
Normal game exit,controller/component cleanup,proxy/launcher restoration and
unchanged original/copied client hashes confirmed;supervisor176.172seconds.

Only this record,curated evidence and HANDOFF changed. No cap increase,source
changes,rebuild,archive,staging,commit or push. All prior work preserved;HEAD/index
unchanged. No live session needed to resume. Next exact action:qualify repeated
ship-owner association at the existing semantic boundary using current context
and bounded identity evidence;then review image dedup/accounting separately.
Material caching remains deferred;original replacement remains separate.

## 2026-10-23 follow-up — what the existing run can actually prove

Sponsor asks whether existing data should resolve ownership. Exhausted retained
identity sources before proposing another run:full detailed event CSV,all four
raw capture headers and association JSONs,lifecycle/movement streams,summary
rejection buckets and component log. No implementation or runtime work.

CONFIRMED detailed native tuple window contains1678records,frames0–119,
elapsed0–2015ms. Its360ship-entry events represent only Federation owners1/2/3,
each with distinct native ship and visual pointers. The first captured Klingon
appears atframe555/9265ms,AFTER this detailed window. Its raw packet records one
ship/visual pair (`0x195C9100`,`0x19230108`),model`0x191302CC`,source`0x04F33440`.
The raw captured tuples are richer than association JSON alone,but still describe
only the four successfully captured owners. Continuous movement/lifecycle/cohort
records are downstream of ownership assignment;they cannot reconstruct a native
identity that may have been collapsed before publication. Summary counters lack
the two missing ship/visual tuples;late rejection examples begin78.906s and have
different visual identities,not evidence of the hypothesized shared Klingon tuple.

Conclusion:existing run proves the budget rejection,missing-instance symptom and
timing improvement,NOT shared-visual causation. That remains STRONG HYPOTHESIS,
not a confirmed fix target. Do not guess a correction from model-name coincidence.
If static caller/context review cannot settle it,the missing observation is a tiny
first-seen/changed native ship→visual→model association list retained throughout
the tactical window,including comparison with the chosen owner. No exhaustive
geometry log/full-rate transcript is needed. This follow-up creates no probe and
requests no new gameplay. Only this record/HANDOFF modified;HEAD/index unchanged,
all work unstaged/uncommitted. Exact next action:review native caller ownership
context against this precise evidence gap before implementing any identity fix.
