# Codex run — actual fresh multi-ship asset delivery

Run/date:2026-10-16-fresh-live-scene-runtime /2026-10-16 EDT.
Task:adjudicate LIVE-SCENE-001 from sponsor-operated skirmish. Starting HEAD
fee152f137a55a3efeb47a5c236ebf9e3e1951cb,index empty,inherited dirty work preserved.
Read current HANDOFF,prepared protocol/probe and actual native/viewer records.
No implementation,game launch,requirements change,helper/subagent or gate claim.

Sponsor:"it worked, it even caught the fighters this rando frigate had lol. It did
take a bit for it to load my model." Follow-up on original SFC behavior:
"sfc was normal." CONFIRMED sponsor observation;no independent pixel capture
or instrumented full-control checklist inferred.

## Actual evidence / fresh geometry

Session artifacts/live-bridge/965ba86ea9ad44098ba439e77857f3ce/result.json:
replay=false,game_runner_exit0,preview_exit0,elapsed134.391s.
Native artifacts/m1/runs/20261016-223535-enabled,component0.20/protocol3.
Preview C:/Project/RemixJobs/preview-20261017-023526Z-c06bfb89 (UTCfolder,Oct16 EDT).

| Revision | Owner epoch | Model | Positions / triangles / groups | Viewer updates |
| --- | --- | --- | --- | --- |
|1|1|assets/models/kff/kff.mod|254 /452 /5|408|
|2|2|assets/models/fca/fca.mod|3493 /6370 /58|0|
|3|3|assets/models/fca/fca.mod|3493 /6370 /58|862|
|4|4|assets/models/kff/kff.mod|254 /452 /5|860|
|5|5|assets/models/kft/kft.mod|170 /336 /2|560|

Five fresh captures/transfers,three unique content assets,four displayed owner
epochs. NOT four distinct physical ships:epochs2/3 share ship405170816,
visual382292480,model404472332;epochs1/4 share ship383888776,visual383797528,
model404473112. Native owner2 retires21032ms,owner1 retires22688ms;fresh epochs
3/4 subsequently qualify. Existing raw pointers alone did not revive old epoch.
Fighter observation plus fresh kft asset corroborate at least that additional
model path,not every fighter/squadron or all tactical object categories.

2690 accepted viewer/camera updates,zero viewer/camera rejects/asset failures;
template_loaded=false,geometry/material readbacks verified,session-layer only.
All2690 viewer(slot,sequence,owner,revision) records join actual native records.
Read native packet/reference for every revision with decode_mesh;asset provenance
also joined by supervisor packet SHA. Geometry is NOT the prepared Klingon asset.
Two repeated contents shared cached geometry/image assets after new qualification.

Independently recomputed same-frame camera_state for all2690 joined records using
first accepted native supplied translation as common origin and captured used
mesh points:max direct S*P*V*M vs engineC discrepancy.000965571432pixel.
Actual USD hierarchy/camera logged maximum.000965816119pixel (<.25threshold).
Native elapsed63..89969ms (89.906s),5364observedframes. No exhaustive geometry
hook/DrawIndexedPrimitive transcript in this run;downstream anchor remains prior
validated evidence,not a new measurement.

## Loading delay — measured limitation, not gameplay stall

Model fca has6370triangles/58groups/84 resource references,versus kff452/5/10.
First fca capture at141ms;native packet written1792204549.273595 epoch seconds;
viewer verification manifest written1792204573.981777:24.708s gap. First fca owner
retired before preparation finished and was never displayed. Fresh same-content
owner3 begins22016ms,first accepted viewer sample25110ms;its own packet-to-manifest
gap3.131s,partly waiting behind initial preparation. kff first gap1.728s;reappeared
kff1.657s;kft.979s. First fca display uses native sample at25.110s tactical.

These are native packet-write to completed viewer manifest filesystem timestamps
and native sample times,NOT exact first visible GPU frame or per-stage timings.
Code runs one asset/image preparation task sequentially,then USD authoring.
Evidence localizes substantial delay AFTER native capture and before qualification
completion;does not yet apportion read/hash/decode/PNG/DDS/USD/GPU upload costs.
Largest actual native capture10396QPCticks/10MHz=1.0396ms. This cannot explain a
25s viewer delay and sponsor confirms SFC remained normal. Do not call this zero
latency or guess one particular converter is solely responsible.

## Materials / information still unqualified

95 unique image contents loaded. Independent SHA verification of all95 original
game files plus PNG/DDS derivatives PASS;supervisor also reports original images
unchanged. Primary contribution displayed;secondary image associations preserved
but not applied (kff5, fca31, kft2 role warnings per unique asset). No rejected/missing
asset reported. This proves fresh mesh/primary-image delivery,NOT exact original
secondary lighting/alpha fidelity. All captured effective LODs0;no genuine LOD
transition/in-place deformation coverage claimed. Broader missions/any enemy
remain unproven beyond these three model assets and sampled mainline.

## Bounds / cleanup / hashes

Worker4540records/2967232B,five attempts/transfers,zero capturefailure/owneroverflow/
invalid/unsent/iofailure,stoppedtrue. Eight deliberate nonblocking busy-mailbox
drops;latest-state transport kept running,no cross-association observed. Viewer
2690records/988509B,combined state3955741B,well below32MiB. Neither saturated/warned.
General semantic rejections0,known00509843count5368,owner/thread overflow0.
CSV339483B,no truncation/warning;geometry hook OFF. Detailed120frame saturation
is expected;summary/live counters continue for full window.

Images:originals9879050B,PNG2688520B,DDS39118720B,total51686290B (~49.3MiB),below
64MiB warning/128MiB hard limit. Logical asset reserve85042944B (<256MiB).
Kit113.484s/exit0/stop_reason0,console25978B,peak scratch53443885B,no warning,
remainingowned0. Total prepared134.391s (<300s),tactical90s retained.

Controller component_state=removed/hook_bytes_restored=true;native summary
hooks_restored=true. Normal exit/client unchanged confirmed by runner. Independent
review finds no active StarFleetOP/controller and no owned winmm.dll,
m1_component.dll,m1_gate.dll,m1-component.ini in game directory. Installed client
independently rehashed unchanged:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.

## Analysis / versionable checkpoint

Tools:PowerShell7,bundled Python3.12.14,existing decode_mesh/camera_state plus
hashlib/json/struct/zipfile. Read-only commands parse native/viewer JSONL,join by
(slot,sequence),check owner/revision and recompute camera arithmetic per record;
group by revision,compare native capture/sample times and packet/manifest write
times;SHA original/PNG/DDS and client;inspect controller/worker/guard cleanup.
No rebuild/full test rerun needed for documentation-only review. Diff/path checks
PASS. Fuel Guard exact-thread recent hook verified,directsandbox denied/quota
unknown,no daemon started. No active session/tool/server must survive restart.

Archive artifacts/remix-ingest/evidence/20261016-fresh-live-scene-runtime.zip:
344entries/7357176B,SHA256
8FB4387F565F332D1182C9166BCFE342D4B4FE992833B9D354CF51ABA6890700.
All entry SHA compared to source. Native run,supervisor,useful preview files and
original/derived image evidence retained;portable/shader caches excluded. Raw
retained,no deletion,no continuous screenshots. This run has sponsor observations,
not a new comparison screenshot;don't reuse offline screenshot as actual runtime.

Files changed:this new run record,docs/HANDOFF.md,
docs/reconnaissance/probes/LIVE-SCENE-001.md. No implementation changes.
HEAD unchanged,index empty,inherited dirty work preserved,nothing staged/committed.

Result:CONFIRMED fresh multi-ship geometry/primary-image delivery with live camera,
content reuse and observed retirement/requalification;original gameplay normal
by sponsor. Overall appearance/coverage remains PARTIAL as above;no gate advance.
Known deficiency:initial fca asset preparation~25s.

Exact next action:sponsor review and authorize bounded first-asset loading-stage
profiling before optimization;measure read/hash/decode/conversion/USD/first-render
timing separately. Do not blindly rerun,cache unqualified old owners,broaden RE,
tune lighting or begin image-return implementation to work around loading delay.
