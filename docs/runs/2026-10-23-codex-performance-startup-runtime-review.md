# Run129 — actual performance-mode startup review

Date: 2026-10-23 America/New_York. Read-only review of completed sponsor run; documentation only. Sponsor reports7–8second initial load and fighter-arrival blip; asks to examine completed evidence. Fighter fix explicitly deferred.

Authority: Run128 handoff, pipeline modes/retained multi-ship contract. Starting/final HEAD d40f8f230fc7504023e4a052c99a81b5a08ce6b4; prior dirty work preserved, index empty. FuelGuard attached via verified hook; no daemon/helper/agent/game/renderer launched. No implementation/configuration change, staging, commit or push.

## Sources and method

Actual run artifacts/remix-runtime/runs/20261024-000410-735623-in-game (UTC folder; localOctober23). Reviewed result/manifest, native worker/component summaries, gpu/job-console.log, job-result.json, retained binary presentation audit. Compared producer code in d3d9_direct_host.cpp/multi_scene_runtime.h and audit decoder in synchronized_buffer.py. Curated index: docs/reconnaissance/evidence/20261023-performance-startup-runtime.json.

Parsed D3D9-SYNC-BUFFER-001.bin using HEADER<16I and RECORD<8I5Q. Find first record status1; its final field is QPC. Divide by persistent_scene.qpc_frequency10,000,000 and subtract first job discovered_ns/1e9. Initial preparation finish is maximum end_ns across initial IDs1–4. Native asset timing at_us is same system QPC expressed in microseconds; compare with the common origin. Reproduction: bundledPython, json/struct and existing decoder definitions only; no tracing run or file writes to captures. The result manifest SHA256 is a86ba6f52818b9500f378341302ea5d43f185cdcbb933e5e6378ebdd41888c9a.

## Confirmed timeline

Origin is first collector asset discovery, not exact engine availability, tactical entry or physical display.

| Checkpoint | Seconds after discovery |
|---|---:|
| Initial4asset external preparation complete | 2.5694633 |
| Native renderer launch | 2.6948109 |
| All4initial assets admitted by native renderer | 6.2698805 |
| First matching game-side buffered composition | 6.6002069 |

Thus external preparation/startup scheduling2.695s PLUS host-launch-to-matching-composition3.905s =6.600s. Manifest separately reports additive tactical preparation6.859s (different start/stop conditions). These substantiate sponsor's approximate7–8s wait; do not invent exact physical-pixel timing. The earlier2.37s benchmark was a preparation subtotal and did not establish user-visible loading success or a factor-four asset-conversion discrepancy.

Native admission CPU stages sum123127microseconds; GPU admission16857microseconds, total0.139984s for all4. This excludes host/runtime/device initialization, bootstrap Renderer construction/warmup, material ingestion, output/receiver startup and first image readiness. It is NOT evidence that the whole3.905s is GPU drawing or native geometry upload.

Log timestamps: runtime begins20:04:43.613, first D3D9 swapchain reset20:04:45.272 (1.659s observed interval). Static source still performs24bootstrap Presents and10ms sleeps while warming (>=240ms deliberate sleeps when reached); useful initialization vs test artifact requires isolated adjudication before changing it. Existing timestamps do not individually apportion all remaining initialization/material/first-frame costs. STRONG HYPOTHESIS: serial host initialization/bootstrap and initial material processing dominate the residual phase. Exact substage culprit remains unresolved; don't blame RTX4070 throughput, Reflex, texture warnings or a vendor feature without isolated evidence.

## Run integrity and coverage

CONFIRMED performance policy active; worker records0/bytes0/lifecyclefalse, CSV detail absent, no census requirement. Four initial models KFF/FFF/FDD/FCA all admitted and each drawn5340times. Total8owner revisions,5unique contents,3shared aliases; every catalog entry ACK1, no partial/rejection. Persistent source supplies offscreen state; no identity/architecture conclusions reopened.

Returned-image pool5307draws,0invalid/resource_failed/error/gpu_busy, no overwritten slots. Buffered audit5307paired/123without-ship,0failed/dropped, maxage19.778ms. IMPORTANT: this audit begins6.136s after first discovery; its omissions do NOT cover or measure the full initial loading interval. Per-cohort counters must not be interpreted as every native instance sharing the anchor's identity. No new sponsor “everything normal” assertion is invented beyond reported successful loading/blip.

Late native KFT first discovered13.016s after origin, prepared0.126s, one additional material library rewrite. Other late owners reuse KFF or KFT content. This is compatible with known late material reload; no isolated causal/fighter classification or fix attempted. Blip remains separately deferred, not folded into initial-loading timings.

Known00509843 count7202, finite to completed run; no runner error, normal game exit, clean hook/controller exit, rendererexit0, jobstop0, zero remaining owned processes, client/launcher critical checks unchanged per runner. Do not promote known exception count alone into seam failure or new runtime corroboration of its internal cause.

## Decision and next smallest action

**PERFORMANCE_MODE_RUNTIME_CONFIRMED; SUB2S_VISIBLE_READINESS_TARGET_NOT_MET.** Governing performance clock must span fresh asset availability to first matching in-game composition, with observation/presentation limitations stated. Preparation and native admission timings are subtotals only.

Next: bounded OFFLINE startup substage timings around runtime/device creation, bootstrap construction/warmup, material readiness, receiver startup and first valid return. Do not start another sponsor gameplay test simply to recover timings available through existing captured assets. Earlier asset discovery and fighter blip fix remain deferred. No source change authorized by this review request.

Files created: this record and curated evidence JSON. Files modified: docs/HANDOFF.md newest checkpoint, docs/reconnaissance/pipeline-modes.md measurement clarification. Validation: JSON parsing/audit record checks, QPC arithmetic, code/log correlation, referenced paths, git diff --check, empty index/unchanged HEAD. No build or gameplay regression needed for documentation-only review. Captures/binaries unchanged and still ignored.
