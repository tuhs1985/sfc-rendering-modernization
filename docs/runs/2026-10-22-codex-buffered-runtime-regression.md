# Run107 — buffered runtime regression, early-ended evidence review

2026-10-22 America/New_York. Sponsor ended buffered run early because the extra
ship constantly flickered. Read Run106, authoritative handoff, actual result/raw
audit, receiver and writer/slot-reservation code. Fuel Guard recent hook
confirmed. HEAD0fc1300; prior implementation remains unstaged, index empty.
Diagnosis/documentation only: no gameplay launched, helper, agent, source change,
staging, commit or push. Run106 offline preparation is historical, NOT runtime
acceptance. Buffered launcher must not be recommended for another run unchanged.

## Direct runtime evidence — CONFIRMED

`artifacts/remix-runtime/runs/20261022-040533-028542-in-game`:

- Sponsor: “i ended early, you changed made the model constantly flicker”.
- 36.344-second prepared workflow; early exit explicitly classified
  `Game exited before the requested tactical observation completed`.
- 424 outputs published,206 overwritten,215drawn;zero stale/invalid/retired/
  resource_failed/depth_missing. Inputexpired7;unqualified0;invalid0.
- Buffer audit434records:215paired,215withoutship,2warmup,2reset,zero failed/
  dropped,maxage19.206ms. Raw SHA256
  `4a2ef16ec69e1f9df9f1a5e377ede4ed614488a60358dc31f2c436ba2e4ee9ac`.
- Of430paired-or-missingrecords,428adjacent transitions flip status. Example:
  current304/saved303 missing,305/304 paired,306/305 missing,307/306 paired,
  continuing through323/322 paired. This is a regular alternating delivery
  regression, not merely occasional camera-reacquisition delay.
- Selected owner2/revision2;no recorded identity retirement/rejection. Typical
  source-to-Present lead15.47ms, comparable to successful unbuffered run15.32ms.
- Normal process exit and renderer exit0; original/copied critical files match,
  launcher settings unchanged, proxy restored. Controlled hook unload NOT
  confirmed: controller8, game exited before requested unload; final native
  worker/persistent summaries absent. Do not report complete unload PASS.
  No owned SFC/host/receiver process remained at review.

## Static support and inference

CONFIRMED static: `game_output_wire.h::reserve` first reserves idle slots, then
overwrites ready slots. The buffered consumer deliberately leaves current output
ready until it becomes the previous scene, while a just-drawn slot remains
acquired until its GPU fence is polled at a subsequent Present. Two slots can
therefore be simultaneously occupied: pending GPU read and queued next image.

STRONG HYPOTHESIS / concrete defect mechanism: the next publication overwrites
the queued image before its delayed scene is presented, causing alternating
missing output.206overwrites and428status flips corroborate the conflict; a
per-overwrite event identity is not recorded, so not every overwrite has an
individually proven causal join. This is not an NVIDIA-recording explanation.
No asset reload or camera identity rediscovery is indicated.

Qualification gap: standalone buffer fixture deliberately used ~3.5ms lead and
therefore tested mostly late delivery; actual SFC output can arrive early under
~15.5ms lead. Offline success did not cover this early-ready/pending-lease phase
interaction. Existing full-scene/depth/identity safety checks must remain.

## Disposition and exact next action

Buffered runtime test FAILS continuity; no acceptance, no universal seam failure,
no formal milestone claim. Keep old unbuffered persistent mode as working
comparison. Do not rerun unchanged or mask the problem by holding stale pixels,
removing fences, or increasing timeouts.

Next smallest action: reproduce early-ready publication with an outstanding
GPU read in the standalone fixture, then correct bounded output-slot ownership
so the exact queued frame cannot be overwritten before presentation. Cover
both early/late phases, slow GPU/read completion and full resource limits before
another sponsor test. Merely forbidding overwrite with two occupied slots may
drop every other newly produced image instead; that is not an adequate fix.

Files changed this review: this run record and newest HANDOFF checkpoint only.
Fast validation: bounded raw audit decode/status analysis, result/proxy/hash
review, source reservation/consumer inspection, `git diff --check`. Generated
evidence retained ignored and unmodified; no new generated capture. Final state:
HEAD0fc1300, all prior/new work unstaged/uncommitted, index empty.
