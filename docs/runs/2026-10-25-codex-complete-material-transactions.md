# Run191 — completed material transactions tested; long queued-work stall remains

Authorized next step from Run190: test one completed enhancement revision per asset,
retaining immediate original-textured base delivery. Fuel Guard attached through a
recent trusted hook. No game launch, production implementation/default/settings
change, runtime patch, API-route resumption, staging, commit or push.

## What was tested

`docs/reconnaissance/probes/20261025_material_transaction_probe.py` imports the
existing bounded fixture and temporarily replaces `flush_enhancements` in that
Python process. The same up-to-four-group IO drain writes already-ready image files,
but queues a material-stage/master publication only when that asset's complete
event arrives. Exact group membership is checked. Each asset proceeds independently;
no bootstrap wait or all-owner barrier. Base publication, native asset preparation,
texture upload, timing, GPU synchronization and the atomic-publication retry/release
paths remain unchanged. Failures retain the base and report partial rather than
publishing an incomplete enhancement revision.

Five synthetic self-check cases cover independent owners, four-group drain bounds,
unpublished base ordering, failed enhancements, and incomplete complete events.
Existing22parallel-asset tests PASS. This is a diagnostic implementation, **not a
production rollout or new normal qualification**. Each result is marked ineligible;
original reference locks remain only under a diagnostic label.

## Ordinary-host transaction result

`artifacts/remix-runtime/runs/20261025-233122-789525-return-fixture` used the unchanged
normal host and pinned1.5.2runtime. Three distinct asset contents plus a fourth
shared-asset owner acknowledged;0asset rejection/partial. Native uploads107initial,
0staged/unsupported. Original-textured bases published independently at0.673,0.925,
1.700s from first discovery. Enhanced stages published at4.720,4.893,5.739s with
58,5,47groups respectively. These heavier standalone fixture timings are not the
two-ship game's preparation timings.

| Metric | Retained Run188 partial-group control220919 | Completed-stage233122 |
| --- | ---: | ---: |
| Master publications | 43 | **3** |
| Bootstrap wall | 3.374s | **0.698s** |
| First matching output from first discovery | 6.107s | 3.716s |
| Post-start omitted returned layers | 79 | **167** |
| Longest omission run/span | 78records/1.309s | **165records/2.779s** |
| Later600-frame window | 594/600 | 598/600 |

The long new gap begins5.376s and ends8.156s after discovery, during/after the
completed-stage publications. A good settled600-frame window does not erase it.
This is not a paired physical-display speed test or a seamless delivery PASS.
No repeat game test is needed to establish that the problem remains.

All381selected final geometry/image/material files are byte-identical to the
retained control. Late ship-region RGB mean absolute difference0.258/0.254/0.249
per255; not bit-exact or a whole-interval material-readiness proof. Native HUD/scene
exact, state_errors0, resize/recreation and normal owned exit pass for233122.
Existing light/material/image/quality configuration remains unchanged.

**Finding:** reducing progressive library writes removes needless reload requests,
but repeat count alone does not explain or solve the seconds-long material-stage
interruption. Do not promote the transaction merely because startup/settled metrics
look better. Keep Run190's pinned-source unload/load/scene-clear findings, but do
not equate each file write with an observed runtime reload.

## Slow-frame attribution derivative — partial fixture, useful timing

`--prepare-slow-frame-host` creates an isolated copy of the current native host with
exactly one changed condition: the existing deferred `OUTPUT_STAGE_TIMING` line is
also recorded when a complete output iteration exceeds50ms. The same fixed1MiB
diagnostic stream stores it until teardown. No timing waits, resources, thread or
sync behavior changes. The source is checked against the expected one-condition
derivative before launch. Build x64 `/O2 /fp:precise /W4 /WX` PASS, using the current
pinned header and original shared includes; output remains under artifacts only.
Compiler setup/link inputs match `tools/d3d9_proof/build_direct64.ps1`, but the normal
build directory is not overwritten.

`artifacts/remix-runtime/runs/20261025-233420-738803-return-fixture`:

- Output iteration117/source201874: draw/Present**886us**, output-copy submission1us,
  **GPU completion query wait3416894us**, postprocess1754us, peer1149us. Cumulative
  asset-service work through there21.742ms, not3.4s. All native asset admissions
  occurred earlier. A blocking completion wait joins already-queued work; it is
  not evidence that polling itself consumes3.4s of CPU or that all that work is GPU
  execution. It does establish that a material-period stall need not block Present.
- Bootstrap was an extreme **25.641s draw/Present aggregate**. Cause unassigned:
  new diagnostic executable/cache/scheduling is not controlled. Do not compare it
  as a production regression or attribute it to the extra deferred records.
- Native host exited0/no guard stop/no remaining children after45.921s. Fixture
  exited1 because resize/recreation checks were not reached (`resized=0 recreated=0`),
  although state_errors0 and the recorded HUD/scene sample was exact. No600-frame
  delivery window completed. **Overall partial/failing fixture**, not discarded
  timing and not a clean pass. First matching output36.573s is also retained.
- Three completed-stage writes and4ownersack/0rejected/partial; final381selected
  asset-file hashes match the control here too. No complete-scene or performance
  claim from the partial fixture. No SFC process was involved.

**CONFIRMED:** source asset prep, returned-image transfer, Present-side waits and GPU
completion waits are distinct. **STRONG HYPOTHESIS:** substantial remaining work is
queued Remix material/texture/shader consumption. **UNKNOWN:** division among USD
processing, GPU texture upload, shader preparation/finalization and driver waits.
Removing completion checks would expose unfinished images and would not fix it.
The existing `[40] common device objects were not disposed of` teardown diagnostic
remains in both successful native exits; internal disposal is not declared fixed.

## Evidence, bounds and checkpoint

Versioned analyzer:`docs/reconnaissance/probes/20261025_material_transaction_analysis.py`;
full analysis:`artifacts/material-transaction/analysis.json`; curated:
`docs/reconnaissance/evidence/20261025-complete-material-transactions.json`.
Input/host/runtime hashes, actual derivative SHA, results and native logs remain in
each run. Both probes retain existing100s/32MiB non-image fixture limits and1GiB
reservation under20GB aggregate. Native console58927/59783B; no truncation recorded.
Two bounded screenshots per fixture, no continuous capture. New generated asset
duplicates143656648B each archived with per-file SHA verification to8908008/8908013B;
logs/packets/images/failing evidence and current qualification/golden fixtures kept.

22existing focused Python tests, five probe self-check cases, native `/WX` build,
two actual graphics attempts (one complete, one partial), archive-based analyzer,
AST/JSON/reference checks and`git diff --check` performed. The earlier615suite is
not re-labelled as rerun. Normal production host/runtime/relay source hashes stayed
unchanged. No owned process/channel remains. No client file changes or gameplay
claims. HEAD`9ff2d3d`; all old/new changes remain unstaged/uncommitted, nothing pushed.
HANDOFF/STATUS and the identical Obsidian snapshot updated; older evidence retained.

Changed this run: this record, curated JSON, two versioned diagnostic Python files,
HANDOFF/STATUS and Obsidian snapshot; generated derivative executable/source, archive
scripts/receipts and analysis under artifacts. Production launcher is unchanged.

**Exact next action:** prepare a bounded process-only NVIDIA trace of the current
pinned1.5.2ordinary host with the completed-stage control to distinguish runtime
material processing/upload/shader work during the completion gap; reserve its output
space and verify elevation before launching. Existing1.6.1candidate trace does not
answer this. Current process is not OS-admin; the established Nsight detours capture
needs an elevated parent. Do not silently switch runtime/architecture or repeat
gameplay, delay materials as a fix, remove synchronization or promote this probe.
