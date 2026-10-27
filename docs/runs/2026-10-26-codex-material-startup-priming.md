# Run199 — prime the material machinery during renderer startup

2026-10-26 America/New_York. Parent93e8dba. Sponsor selected startup priming as the single next experiment. No manual-reload experiment, retry-notification scheme, material tuning, API unpark or new game capture performed. No staging/commit/push.

## Implementation and authority

NVIDIA documents that changes during initial USD loading can precede file-watcher registration. The pinned implementation registers callbacks when the initial stage is applied. We exercise existing Remix/D3D9 preparation rather than patching vendor code: [documented startup caveat](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/RtxOptions.md), [pinned apply step](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_mod_usd.cpp). Packaged5a7eec84/public0a6cd5b instruction parity remains unverified.

Only explicit `-AsyncMaterialCheckout` changes. Its owning native child enables replacement loading before initial processing and invokes the existing private triangle startup pass once(24triangle+32emptyPresents). No private output is published. Graphics state is restored and GPU completion checked before the existing renderer-ready receipt. Thereafter the existing wait loop sleeps/checks activation/liveness; no repeated draws/reloads or accumulation of scene objects. Normal1.5.2selection is unchanged. No new C++renderer/shim or public API was added.

`async_material_checkout.py` delays only enhanced-library publication if it races that one-time preparation. Base catalog/geometry/movement delivery remains independent and is regression-tested before readiness. No fixed per-ship delay or500mswindow. Preparation tasks still run concurrently. Partial readiness reads are retried without sleeping; malformed receipts fail closed. Already-completed readiness is retained per renderer session. The receipt means private startup completed, not that any particular material was installed or that the native file-watch subscription has a public ACK.

`qualify_async_material.py` now checks the actual single private pass, native host/QPCidentity, configuration, and enhancement-publication ordering. Tests cover base progress, enhancement gating, partial/malformed readiness, child-only configuration and unchanged inherited settings. Exact source changes:those two Python files and `tests/test_async_material_checkout.py`. Documentation/probe files are additional. No lighting/material/image/quality TOML or captured mesh/UV/original image changes.

## Idle and cancellation evidence — separate findings

Probe:`docs/reconnaissance/probes/20261026_material_priming_idle.py`; creates only an owned sleeping liveness process and the real external renderer, never SFC or a scene. Measures CPU/private allocation/resident working set/handles, checks no public images and cancels through the existing path. Fixed logs/process/time/output bounds apply.

Primed60s045051:one private pass,no activation/public image; zero positive settled private-allocation growth and handle growth; native job0/stop_reason0/remaining0. Resident working set rose from~1.65GBto~1.81GB:do not call all memory flat or claim indefinite stability. Native private allocation settled~4.66GB, versus~2.74GBunprimed:about1.9GBadditional committed process memory is reserved earlier. This is fixed preparation cost in these tests, not a measured active-game peak increase.

Strict quiet-CPU criterion FAILED:primed194.53%ofonecore. The matched15scontrols showed unprimed193.287%andprimed193.291%,each dominated by two unnamed threads. This points to pre-existing renderer-process idle CPU use,not an added priming CPU regression; thread/module cause remains unknown. Do not retroactively label the absolute idle test PASS. Track it separately. The unprimed control also lacks a normal native job receipt; normal shutdown is not proved for that control. No claim that all controls cleaned up normally.

Primed15s050802normal native job0/stop_reason0/remaining0. Early cancellation045734also exited normally with no scene/public output or owned children;totalnativejob19.734s,so early teardown is clean but not instantaneous. Primed60sjob63.375sincludes its idle window; fixed preparation was~3.3s. Process memory/handles are bounded in measured intervals,not proof of safe operation forever.

The normal runner retains its180sactivation/285sprepared-workflow watchdogs. This task does not remove test limits to promise indefinite menus. No repeated priming while waiting. Production indefinite-idle policy is not qualified here.

## Functional validation

552main Python tests PASS; matching candidate x64/O2/WX build and actual native-light qualification PASS. Normal045947GPU/source qualification PASS. Primed initial050347:four owners/three assets/381selected files match after the already-qualified mapping conversion;596of600settled returns,one isolated whole-interval post-start omission. Late050531:599of600,one isolated omission. Native HUD/scene exact,state errors0,resize+recreate/normal exits,no invalid/rejected/partial assets. Both real read-only launcher preflights PASS including audit JSON serialization.

Priming completed once before every enhanced master publication. The late fixture's first logged FCA enhanced-image processing is approximately3.192sfromfresh discovery, before the later distinct asset at5.943s. This demonstrates consumption without another arrival in that replay,not proof the repeated live failure is fixed. Log/QPCwallclock correlation is approximate; no new per-material installed/GPU ACK exists.

Cold standalone first returned images were3.879s(initial)/3.857s(late),because fixtures offered ships while the renderer was still starting. Preparation itself took~3.3s. Do not claim one-second cold startup. In the prepared game workflow this one-time work runs during launch/menus,as the existing renderer initialization already does. Extremely early tactical entry can still encounter unfinished preparation; no artificial ship wait was added.

## Evidence preservation and final state

Curated JSON:`docs/reconnaissance/evidence/20261026-material-startup-priming.json`. Prior qualification receipt saved as`artifacts/candidate-hot-reload/run199-previous-checkout-qualification.json`. Normal launcher without the opt-in remains independently qualified as rollback. Existing mapping fix and canonical source data unchanged.

One capacity rejection occurred before graphics startup. Completed survey141338broad.bin(status3,error0,queued0,normalexit)was byte-for-byte SHA-verified ZIP archived342556800→31632157bytes,then the duplicate raw file removed. Archive:`artifacts/remix-runtime/archives/run199-20261025-141338-349874-broad.zip`;receipt:`artifacts/candidate-hot-reload/run199-broad-archive.json`. Restore its original path from that ZIP before raw survey reanalysis. Results/curated analysis and all raw contents survive. Existing20GBcap/reservations were not lowered. Useful generated asset duplicates may also be verified/compressed after analysis.

**Exact next action:** sponsor runs the same multiship launcher with`-AsyncMaterialCheckout`,using the familiar two ships. Inspect appearance before launching any shuttle or other new model;then add one if desired and exit on the runner request. Confirm whether the initial materials now apply without that arrival. This tests startup priming alone. No manual timestamps,extraUAC or reverse-engineering actions. No formal milestone/complete-enhancement PASS before actual live review.
