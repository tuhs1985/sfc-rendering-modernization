# Run118 — repaired multi-ship delivery, first actual SFC review

2026-10-22 America/New_York;UTCfolder20261023. Sponsor reports no noticed flicker
despite aggressive testing and announces a second run with more than two ships.
Scope:read-only evidence review and durable records;no implementation or gameplay
launch by Codex. Reviewed authoritative HANDOFF,Run117 and fresh completed run
`artifacts/remix-runtime/runs/20261023-034547-144070-in-game`.
HEADd40f8f230fc7504023e4a052c99a81b5a08ce6b4,indexempty,prior work already
unstaged/untracked. FuelGuard trusted-hook confirmed;no helper/agent.

## Confirmed first-run result

- KFF owner1/revision1 and FCA owner2/revision2 freshly captured and acknowledged.
  Retained draws5403/5401;two asset loads,zero asset rejections. No saved template
  or original-model suppression. Source poses/camera and previousleftoffset retained.
- **Zero incomplete cohort lookups,zero input admission rejections**,both checks
  exercised5404times. No unqualified anchor input or rebind. One individual
  projection rejection and three unprepared-instance omissions remain;not a
  zero-rejection claim. Geometry/asset scope unchanged.
- Raw synchronized audit independently decoded:5410records,5392paired images,
  16missing,onewarmup/onereset,zero audit failures/drops. First match atindex7.
  After first match:11missing/5403records(0.204%);ten of those atsourceframes
  331–340 and345 during early settling,one isolated later miss at4383. After
  sourceframe600:5132paired/5133records. Sponsor saw no flicker;do not translate
  that into literally zero missing returned frames.
- Compare Run116 after-first-match692/5405(12.803%),including65-frame gap.
  Both old lookup/admission defects are absent in current counters. Different
  runs are not controlled GPU benchmarks;this is direct actual delivery evidence,
  not a claim that all future scenes are fixed.
- Output GPU stage wall-time:p50 9.344ms,p9513.229,p9916.015,max27.491.
  Draw/Present CPU submission:p500.299ms,p950.388,max2.110. Peer stage:p500.759,
  p952.477,max5.246. No>50ms output waits in this run. This does NOT overturn the
  isolated late-material reload stall from offline tests;no mid-session new asset
  was admitted here. Prepared material caching remains deferred by sponsor.
- Persistent registry14394pose publications,7196offscreenupdates,zero failed
  updates/destruction/rejections;7198sourceframes. Geometry hookOFF,zero semantic
  rejections. Known0x00509843count7204,finite and non-invalidating in this run.
- Published output5403,composited5392,seven stale packets,zero invalid output,
  overwrites,resource failures,GPU-busy imports or missing depth. One union image
  represents the cohort;anchor owner1 in buffer audit is NOT proof of player-only
  output or native per-pixel owner classification.

## Bounds,cleanup and validation

Images91,506,338bytes(<128MiB,above64MiBwarning),91fullcohort samples(<120cap).
Resident conservative CPU+GPU backing45,261,744bytes. Supervisor152seconds.
Final runtime records confirm normal game exit,controller0,hook restoration and
component unload,renderer0,proxy and launcher settings restored,original/copy
critical hashes unchanged. Client SHA256:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Pinned runtime still reports40undisposed common objects atshutdown;unresolved.

Validation:decoded raw synchronized header/session/process and records with
`synchronized_buffer.decode`,crosschecked saved counters,enumerated missing frame
numbers,read final native/backend summaries,computed CSV timing quantiles excluding
bootstrap output and compared Run116. Curated raw hashes in
[evidence](../reconnaissance/evidence/20261022-d3d9-multiship-delivery-runtime.json).
No rebuild,new tests,config edits or repeat gameplay needed for review.

Second folder`20261023-034948-568962-in-game`exists but its result explicitly says
`IN_PROGRESS`,stage`prepared`,final_report_complete=false at inspection. Mere
existence of result.json does NOT establish completion. No adjudication,cleanup,
capture modification or source change to that active run. Do not archive binaries
while its owned processes are active. Next test's larger scope remains separate.

Only this record,curated evidence and newest HANDOFF changed. Prior source work
preserved;HEAD/index unchanged,no staging/commit/push. No new session spawned.
Exact next action:after sponsor finishes the larger run and its final report is
complete,review per-owner/asset delivery,bounds/stalls and cleanup separately;
do not implement material caching or original replacement during that review.
