# Run116 — diagnose multi-ship offset flicker, no implementation

2026-10-22 America/New_York. Runtime folder uses UTC20261023:
`artifacts/remix-runtime/runs/20261023-024532-240443-in-game`.
Sponsor reports frequent flicker, occasional disappearance, all ships and a newly
appearing fighter delivered. Request is diagnosis, not implementation approval.
HEAD `d40f8f230fc7504023e4a052c99a81b5a08ce6b4`; Run113–115 work already
unstaged/untracked; index empty. Fuel Guard trusted-hook attachment confirmed.
No helper/subagent, rebuild, new gameplay, source/config change or cleanup.

Reviewed authoritative HANDOFF, approved M1 disposition, Run114/115, retained
multi-ship contract, current collector, wire, host, asset admission, receiver,
one-frame history, input admission and existing analysis decoders. User-supplied
AGENTS instructions govern; no repository-root AGENTS.md exists.

## Confirmed runtime result

- Fresh KFF owner1/revision1 (452 triangles), FCA owner2/revision2 (6370), KFT
  owner3/revision3 (336). All three assets acknowledged, zero asset rejections,
  three captures, no capture failures/IO failure. Instance draws:4718/4707/2078.
- Persistent scene:18293 changing-pose publications,11094 offscreen updates,
  zero failed updates/rejections, no registry destruction. No scheduling-anchor
  rebind. Thus frequent whole-return omissions are not explained by geometry
  repeatedly unloading or camera-away object retirement in this run.
- Raw synchronized audit validates:5412 records,4713 paired,697 without a
  matching returned image,one warmup,one reset; no dropped/failed audit records.
  After first successful match:692 missing of5405 records (12.803%). Prior aligned
  multi-ship run:655/5407 (12.114%). Accepted single-FCA run
  `20261022-042653-754380-in-game`:3/5400 (0.0556%). Not identical scenes or a
  controlled GPU benchmark, but confirms a material delivery regression.
- Post-first-match missing clusters:504 single,39 double,11 triple,3 quadruple,
  one65-frame cluster. Longest:sourceframes3370–3434; first-to-last audit span
  1071.1142ms. At frame3370 output completion took1075.118ms from source offer;
  the renderer waited1073.464ms for its D3D9/Remix output-completion query.
- Cross-join missing delayed scene frame with retained `gpu/live-input.csv`:
  690/692 have **no completed output record at all**,not simply an image arriving
  a little late. Two have eventual output; one completion receipt precedes and
  one follows the compositor observation. Completion is after peer ACK, so do
  not equate it exactly with first GPU-resource readiness.
- Output resources:zero overwrites,invalid packets,not-ready imports,resource
  failures or GPU-busy compositor events;one stale packet. Eleven per-instance
  decode/projection rejections and eight unprepared-instance omissions remain
  unlocalized; not enough to explain692 whole-cohort omissions.

## Diagnosis and confidence

**CONFIRMED static defect — notification precedes complete publication.** In
`m1_live_scene.h::updatePersistent`, `directSource.offer(r)` exposes the selected
anchor input while the collector is still iterating owners. Only after that loop
does `cohort.publish(...)` publish the matching full tracked-set packet. On the
other CPU, `LiveOwnerInput::next` consumes that anchor, then
`MultiSceneRuntime::next` attempts one exact cohort read. If the producer has not
finished, the outer host loop executes `continue`: no retry and no retained
pending request. This is a real permitted producer/consumer interleaving, not a
claim that GPU output is too slow to draw any three ships.

**STRONG HYPOTHESIS — this race causes a substantial share of regular flicker.**
Runtime has5162 accepted inputs but4718 live cohort draws/outputs,444 discarded
after input acceptance. There are zero light omissions and no all-instance-failed
draw calls (cohort frame count equals live output count). The186 aggregate input
admission failures combine checks before and after acceptance. Therefore current
control-flow accounting bounds exact-cohort-read failures at258–444; logs do not
separate header/slot readiness/sequence causes, so do not label all of them proven
early-publication races. Add stage counters and a deterministic interleaving test
when fixing publication rather than claiming exact attribution now.

**CONFIRMED contributing policy/timing problem.** Input is admitted only within
2ms of its offer and checked twice. It retains that single-ship policy even
though matching saved-scene presentation is about31ms after offer in joinable
misses.186 admissions fail; cannot partition old-frame versus2ms-age versus
before/after-check from existing counters. Multi-ship output-GPU stage median
10.405ms,p95 16.171ms,p99 18.497ms; accepted single-ship median5.646ms,p95
6.912ms. Median draw/Present submission is only0.303ms; projection/input checking
is around0.003ms. Most measured cost is GPU/Remix completion, not mesh reconstruction
or Python image decoding per frame. Longer cycles make the narrow take window
fragile. Do not widen it blindly or weaken source/camera matching.

**CONFIRMED separate long interruption; cause unresolved.** Fighter appears at
sourceframe3305 and first logged cohort drawing at3315. The65-frame disappearance
begins3370 and coincides with the1.073s GPU completion wait. STRONG HYPOTHESIS:
late asset/material admission triggers runtime processing/warmup. Shader compile,
material-layer reload, GPU scheduling or another internal wait cannot be
distinguished by retained logs. Do not claim the synchronous CPU asset loader
itself consumed that second: draw/Present submission was0.269ms at3370.

The compositor shows original SFC normally when the exact matching returned
cohort is absent. Since returned ships share one output, a single skipped cohort
can blink all copies together. That policy explains visibility of missing work;
it is not a proposed final replacement fallback and not a solution to the misses.
No stale-pixel hold, prediction or extra buffer is implemented in this review.

## Reproduction, bounds, cleanup and next action

Use bundled Python with `tools/remix_runtime` and `tools/d3d9_proof` on sys.path.
Decode `D3D9-SYNC-BUFFER-001.bin` with `synchronized_buffer.decode(raw, session,
pid)` and `D3D9-LIVE-TIMING-001.bin` with `live_owner_timing.parse_audits`; session
is `manifest.json.semantic_calibration.scene_session`, pid is result.target_pid.
For streaks use synchronized RECORD fields:status[3],scene[1],qpc[12]; remove
only entries before the first status1. Join scene[1] to `live-input.csv.source_frame`;
join that to `frame-timing.csv.source_frame`, excluding bootstrap timing row.
Frequency10000000. CSV `sequence` is host-loop index, not output sequence.
Raw decoder counts independently agree with saved analysis. Curated numbers and
raw hashes are in [evidence](../reconnaissance/evidence/20261022-d3d9-multiship-flicker-diagnosis.json).

Images93,870,746bytes below128MiB (above64MiB warning),91 full-cohort samples
below120; worker evidence2,178,507bytes,unsaturated. Geometry hook OFF. Source
timing has two invalid/two snapshot-miss observations:partial timing evidence,
not a spotless source qualification. Known0x00509843 count7205,zero semantic
rejections; no evidence it explains return omissions. Original/copy client hashes,
launcher/config restoration,proxy restoration,normal game exit,controller0,
hooks restored/unloaded and renderer0 confirmed by final runtime records.
Pinned runtime still logs40 undisposed common objects at shutdown; unresolved,
not a zero-leak claim.

Exact next action:fix/test atomic tracked-set readiness and add explicit rejection
stage counters before another sponsor test;then evaluate admission against the
actual synchronized deadline and isolate late-asset runtime stalls. Do not begin
replacement, redo camera/pose discovery or hide this regression with stale pixels.
This request does not authorize implementation. Only this record, curated evidence
and newest HANDOFF checkpoint changed; all prior source work preserved. No staging,
commit or push; index empty, HEAD unchanged. No active session needed to resume.
