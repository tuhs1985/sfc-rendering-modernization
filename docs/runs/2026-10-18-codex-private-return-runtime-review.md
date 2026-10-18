# Codex run — fresh private return runtime review

Run SFC-RETURN-20261018-24;reviewed 2026-10-18 (America/New_York).
Active approved return-path investigation / REMIX-LIVE-RETURN-001.
Result: **PARTIAL — current-frame private admissions demonstrated; sustained operation unresolved.**
No on-screen ship return, suppression, replacement or milestone PASS.

## Baseline and execution

HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d;existing large dirty worktree,
empty index. Run23 prepared tooling and qualification unchanged. Sponsor ran
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\remix_runtime\start_return_image_session.ps1" -PrivateShip`
and reports: "done, no issues noted on my side". This review did not launch SFC,
change implementation, invoke a helper, stage or commit. FuelGuard attached;
advisory allowance warnings did not block authorized evidence review.

Sources reviewed: Run23, HANDOFF, private-return probe/contract/readiness,
run_return_game.py, ship_live_host.cpp:79–90, ship_triplet_wire.h:64–68,
ship_live_receiver.h, return_addon.cpp; runtime directory
`artifacts/remix-runtime/runs/20261018-043335-298481-in-game`.
Read manifest/result/host/controller/component logs, worker summary and fresh
asset manifest. Runtime tools, exact dependency/build pins and configuration
are preserved in that manifest and Run23; unchanged for this test.

## Direct evidence — CONFIRMED

- Verified test PID3420. 90-second tactical observation;128.235-second runner.
- Fresh FCA `assets/models/fca/fca.mod`,owner epoch2/revision2;19110 expanded
  vertices (6370 triangles). No saved template. Owner1 was explicitly refused
  as too small for the diagnostic return;no substitute displayed.
- 203 offers;202 published triplets;68 acquired/private draw attempts;
  134 late/mismatching rejections;0 private invalid records;0 private failures;
  1 cancelled publication. Sequence/ACK202 at exit. These draw counters prove
  admission/submission,not nonempty pixels or faithful moving-pose pixels.
- First sampled accepted counter at0.86s;68 reached by9.72s. At9.99s cancelled=1,
  lease=Rendering(1),sequence=ACK202. All return counters then remain unchanged
  through89.86s. OFF30–45 / ON45–60 / stop60–90 phases therefore do NOT establish
  successful recovery or continued operation. No frame-equality relaxation used.
- First100 detailed GPU request/completion durations:median6.1006ms,
  minimum4.0215ms,maximum97.4813ms(first request),QPC10MHz. These exclude
  pre-request asset preparation and are NOT full end-to-end latency or all202.
- Controller0,renderer0,normal SFC exit;hook restoration and component unload
  explicitly logged. Worker4648 records/2995447 bytes,3 transfers,0 dropped,
  invalid,capture failures or saturation. Geometry hook stayed OFF.
- Both installations' seven critical files matched before/after and were
  independently rehashed in review. Client SHA256
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
  Launcher settings unchanged. No SFC/host/controller process remained;no
  transient SFCRemix/m1_/winmm/component.ini files found in test root.
- Sponsor reports normal gameplay. No visible effect was expected:private
  target only;backbuffer_ship_drawing=false,original_ship_suppressed=false.

## Defect adjudication

**STRONG HYPOTHESIS:** publication try-lock contention strands the Rendering
lease. `publish` returns false immediately when the guard is unavailable without
changing that lease. Host clears `inflight` unconditionally after the call,then
requires Idle to proceed. Observed cancelled=1/lease1/ACK202 and permanent freeze
match this path. Static code establishes the defect is possible;runtime lacks a
dedicated lock-contention reason counter,so the exact triggering cause is not
CONFIRMED. This is not evidence the semantic seam failed or GPU took90seconds.
Do not fix by waiting on the game thread,overwriting an in-use surface,or accepting
old-frame output. Next fix must retain completed producer work on transient
publication contention and explicitly terminate/recover genuine cancellation.

Persistent Remix shutdown warning `[40] common device objects were not disposed
of.` remains unresolved despite normal exit. Component summary also reports52
semantic rejections/two diagnostic buckets,1 owner retirement and finite known
00509843 exception5405;these are distinct from private invalid=0 and must not be
reported as globally zero semantic rejections. No causality established here.
Motion/camera phases after10s were not validated by successful return admission.

## Bounds, preservation and validation

Existing probe limits retained:30Hz maximum,one in-flight triplet,private256²
target,32MiB log cap/16MiB warning,285-second prepared budget;no screenshots,
image dumps,geometry transcripts or appearance tuning. Raw runtime7794792bytes.
Archive `artifacts/remix-runtime/archives/20261018-fresh-private-runtime.zip`:
1630171bytes,SHA256
`FEDB370D13394EB6A367A631A2E7E122D3FF9B191744D60C410666E6799655E9`.
Raw evidence retained;compression bounds storage without discarding failures.
Archive CRC validation,JSON parsing,documentation reference checks and
`git diff --check` performed. No rebuild needed for documentation-only review;
Run23 offline qualification remains historical,not proof of sustained runtime.

Changed only this run record,new curated runtime evidence,and newest sections
of HANDOFF/readiness/probe. Existing evidence/raw result (including pending
sponsor field) not overwritten;this record supplies sponsor disposition.
Final repository remains dirty from prior work plus these docs;index empty,
no staging/commit. No active transient session needed for resumption.

**Exact next action:**add a deterministic busy-publication regression and fix
the host's completed-output retry/cancellation handling,then requalify offline
before another private runtime test. Do not expose/suppress ships yet.
