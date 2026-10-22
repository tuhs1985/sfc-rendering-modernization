# Run77 — actual SFC source timing adjudication

Date:2026-10-20 America/New_York. Result:CONFIRMED source timing observation;
Gate3 CONTINUES,not live D3D9 delivery or formal milestone PASS.
Authority:approved additive execution plan,Run76 prepared probe and sponsor
continuation. Sponsor completed the prepared run and reports "done, no issues
noted". This confirms reported normal behavior,not unreported cue details.

## Starting state and exact run

HEAD d29111f7a513c4510c4d33aeeda2c355d98443a5,branch codex/github-sanitized.
18modified tracked/78untracked individual files,index0 at prior checkpoint;
all Run65–76 dirty work preserved. No helper,agents,commit,push or installation
changes in this adjudication. Fuel Guard already attached;credits authority active.

Prepared command:tools/d3d9_proof/start_source_timing_session.ps1 from established
elevated parent. Actual evidence:
artifacts/remix-runtime/runs/20261020-051149-684568-in-game.
Probe D3D9-SOURCE-TIMING-001,game PID48208,render thread43020,QPC10MHz.
Exact dependencies/configuration and binary hashes in run manifest.json and
Run76 qualification. Runtime154.407s total,90s tactical;no image/Remix load,
original suppression or backbuffer ship drawing. Geometry firehose OFF.

## Direct evidence — CONFIRMED

- 14,832metadata records,7,416exact frame/owner/revision pairs across5,398observed
  frames. No repeated/unpaired groups,pose/camera changes between Present and
  overlay,wrong-thread,invalid,missing timestamp,ambiguous,overflow or drop.
- 10,796callbacks;32snapshot misses remain explicit. These are failed/empty
  mailbox reads,not32proven missing tactical frames. Their phase/cause is not
  established by this metadata. Do not silently erase them.
- Owner/revision1/1:1,585frames2–1586,KFF;2/2:5,397frames3–5399,FCA;
  3/3:434frames1693–2126,KFF. Same KFF model/source labels recur with a NEW epoch;
  do not merge those epochs or infer physical ship destruction from retirement.
- Observed frames contain one owner3,380times,two owners2,018times. No conflicting
  camera hashes within an observed frame. Complete scene/category coverage is
  NOT established. Matching callbacks do not prove a source publication seal.
- Median adjacent-frame source interval~16.98ms for each epoch,roughly59Hz,
  independently of legacy30Hz diagnostic publication. Captured pose hashes change
  1,521/1,718/433times;camera hashes0/1,985/76times respectively. These are state
  changes,not a claim of sponsor-controlled enemy movement or physical displacement.
- Last semantic offer to Present,per-owner min/p05/median/p95/max milliseconds:

|Epoch/revision|Min|p05|Median|p95|Max|
|---|---:|---:|---:|---:|---:|
|1/1|6.9380|13.9329|15.6530|17.4364|22.9379|
|2/2|9.5804|13.9470|15.5679|17.1699|22.8495|
|3/3|9.6657|13.7662|15.6079|17.5127|18.8041|

First/last offer timestamps are identical in retained rows. Latest actually
observed owner to first Present per frame:min6.938,p0513.946,median15.5679ms.
Overlay follows Present median0.1438ms,max0.4824ms;it does not provide a useful
extra full-frame budget. These are callback timings,not physical display timing.
Under12ms windows:8/1,585,20/5,397,2/434owner observations. Do NOT convert those
counts into a predicted live delivery percentage.

All hooks restored,component unloaded,controller0/host0,normal game exit,
no controller left running. Worker:2,565legacy records,3asset transfers,
capture failures/dropped/invalid/overflow/unsent0,stopped=true,io_failed=false.
Accepted/copied critical hashes match their manifests;launcher settings unchanged.
Both client SHA256:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Capture23files/5,273,063bytes before derived adjudication;metadata raw1,186,688bytes.
No continuous images or geometry transcripts. Original raw evidence retained;
no generated bulk input copies needing deletion were made in this adjudication.

## Engineering decision / unresolved fact

STRONG HYPOTHESIS:early nonblocking publication can overlap ordinary-D3D9/Remix
work with SFC's remaining frame. Typical15.6ms source window versus separate
Run75~11.98ms p95 cost supports investigating this,not guaranteed delivery.
CONFIRMED:narrower windows exist than both that p95 and14.04ms offline maximum.
Separate runs do NOT measure simultaneous GPU contention or combine into a
joint latency distribution. No relaxed identity,stale-pose display,prediction,
whole-frame buffering,original suppression or forced render-thread waits adopted.

Next smallest action:implement and offline-test bounded immutable owner/frame
publication plus conflict/retirement invalidation and exact output matching,
then measure the actual renderer with SFC without drawing the extra ship first.
Establish the source completion/seal relationship before claiming coherent
scene publication. Reuse qualified GPU transport;do not repeat startup/OBJ/UV
work or ask for another identical timing-only gameplay run. If simultaneous
delivery cannot fit,obtain a scheduling/architecture decision rather than hide
gaps behind the original ship. Gates4–5 remain unexecuted.

Small metadata deficiency:manifest's inherited scene description says "early
depth-binding observation";probe ID,source_timing block,result and host log
unambiguously establish semantic timing mode. Preserve raw manifest;correct
that description when next modifying/preparing the runner,not retroactively.

## Validation and changed files

Added tools/d3d9_proof/analyze_source_lead.py and
tests/test_d3d9_source_lead.py:exact frame/owner/revision pairing only,exclude
changed/repeated states,report observed-owner windows,adjacent-frame cadence,
state transitions and cross-owner camera disagreement. No nearest-time joins,
runtime/proxy/native changes,or source qualification invalidation.
Derived source-lead.adjudication.json generated in run directory;source packet
SHA256 a4beb18afcf5a7ddceef1256dd80b44527c96bcb695157259366df67997d37ff.
Reproduce with bundled Python:

```powershell
python tools/d3d9_proof/analyze_source_lead.py artifacts/remix-runtime/runs/20261020-051149-684568-in-game
python -m unittest discover -s tests -p "test_*.py"
git diff --check
```

334Python tests PASS4.747s,including4new adjudication tests. Initial sandbox run
had179temporary-file permission errors;approved unsandboxed rerun passes. This
is environment setup evidence,not179semantic regressions;no checks weakened.
Pillow deprecation warnings remain historical. No native rebuild needed because
only offline analysis/docs changed. Diff whitespace check PASS. No owned game,
controller,host or fixture process remains. Historical Run76/native results
retained,not claimed rerun. Updated run record,curated receipt,probe progress,
approved execution progress and HANDOFF;earlier checkpoints preserved.

Final state:18modified tracked/82untracked individual files,index0,HEAD unchanged;
all implementation/evidence unstaged/uncommitted,no push. Exact next action is
the bounded immutable publication/offline matching unit above;no sponsor action
needed for that unit. Intentionally disabled features remain disabled.
