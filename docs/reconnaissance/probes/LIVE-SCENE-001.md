# LIVE-SCENE-001 — fresh multi-ship assets, separate live renderer

Status: fresh geometry/primary-image delivery DEMONSTRATED in actual SFC;
[runtime adjudication](../../runs/2026-10-16-codex-fresh-live-scene-runtime.md).
2690accepted camera/ship updates,kff/fca/kft fresh contents,zero asset/camera
rejects,clean normal exit/unchangedclient. Sponsor reports fighters appeared and
SFC remained normal. Initial fca preparation~25s remains a measured deficiency;
unknown secondary roles/coverage retain overall partial status,no formal gate PASS.

Historical preparation: implementation/offline validation; runtime pending. Sponsor
approved Fresh Live Assets plan2026-10-16, selected ALL visible ships on confirmed
mainline, first fixture TWO different classes. Not aggregate TRL/M1/M2 acceptance.

## Question / hypothesis / seam

Can fresh geometry/resource packets from multiple SFC ship owners construct the
separate scene,without imported Klingon USD or accepted-template content lookup?
Hypothesis: existing read-only Mesh/Texture collectors plus owner epochs suffice
for the established rigid triangular mainline. Dynamic original image files may
be loaded once by proven filename; geometry must originate from current capture.

Same hooks/ABI as LIVE-CAMERA-001,not new detours. tEntityShip004162B9,
visual0042FD3F/model0042E4B2,wrapper006AC5A0 confirmed mainline return0042E55D.
Manager supplied+6F4/composed+6B0/view+628/projection+55C/viewport+75C..770.
Geometry006AB410 hook OFF,original render calls unchanged. No GPU readback,
COM writes,engine calls,model replacement in SFC or frame return.

## Tools / build / launch / privileges

VS2026/MSVC14.51 x86 C++17/component0.20;bundled PS7.6.5/Python3.12.14/Pillow12.3;
installed Remix Toolkit1.6.0-dev+main.30229.3f23f80a.gl. Build:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/m1_component/build_m1_component.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/remix_ingest/build_remix_job.ps1
```

Sponsor command from EXISTING elevated parent (PS5 forwards to bundled PS7):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\m1_component\start_live_scene_session.ps1"
```

No new RunAs/UAC/security policy changes. Process-only execution-policy bypass.
Runner builds/tests,creates explicit current-user-only channel,prewarms EMPTY
session scene,then starts validated SFC Launcher via established workflow.
Old start_live_bridge_session.ps1 remains single-Klingon diagnostic/protocol2.
No helper/subagent or vendor/global configuration edits.

## Capture / transport / lifetime

Protocol3 is incompatible with old live channels; no inferred wire sizes.
16MiB pagefile mapping,unique Local\SFCBridge_<32hex>,same explicit UUID checks
and current-user SID DACL. Viewer has write access ONLY to acknowledge transfer
generations; no control commands reach SFC. Layout in live-scene-contract.md.

32 owner state slots,up to30Hz/owner (34ms spacing),latest state replaces old.
Four2MiB acknowledged asset-transfer slots;native preallocated staging holds
four LiveMeshPacket+256-reference records. Worker is sole serializer/file writer.
Capture at most once per rendered frame,only first observation/new model/source/
list/count/LOD identity. Guarded bounded copy/recheck; no render-thread allocation,
file I/O,image decoding,blocking acquisition or viewer call. Existing hook lock
unchanged; mailbox TryAcquire drops if busy. Record capture QPC maximum for review.
Mesh ceilings65536 positions/8192triangles/32768corners/256groups,combined mesh+
references<=2MiB. Nontriangles/malformed/nonfinite/unresolved data reject,not repair.
64 successful revisions/session;32 concurrent owner slots. Retired slot may be
reused only for fresh owner epoch,with monotonic slot sequence;pointer reuse alone
cannot revive a ship. In-place deformation without identity change UNQUALIFIED.

Receiver asynchronously verifies packet+same-epoch associations and loads original
images,hashes content and builds fresh USD meshes/materials ONLY in session layer.
Positions/indices/percorner normals/UVs/group face lists read back;original winding
and values retained. Identical geometry+group/image content share an internal USD
asset reference; owner transforms separate. Shared scene origin/scale100 and the
proven camera conversion retained. Each owner checked vs engineC<=.25nativepixel.
Newest accepted frame's camera restored after per-owner projection checks.

No imported model/template loaded; standalone empty scratch stage contains no
ship geometry before first transfer. Primary images only/provisional MDL material;
secondary associations preserved but secondary contribution NOT guessed or tuned.
Alpha/native blending and untextured flag paths remain explicit limitations.
Stale>=1s,retired,bad/pending asset or invalidcamera hides affected ship; normal
SFC path continues. Retired old owners/backwards revisions cannot reconnect.

## Bounds / raw-output safety

-90s tactical gate window;300s prepared workflow AFTER builds. Preview startup
 <=180s but game not launched if readiness takes>45s. Existing discovery/gate/
 exit deadlines30/90/30s retained. Never force-kill game/controller with live hooks.
-2,700 detailed records/owner per process. Native state JSONL<=16MiB and viewer
 <=16MiB (combined32MiB);warn8MiB each (combined16MiB),summary after saturation.
-At most64 asset packets,each combined<=2MiB;no perframe mesh/image dumps.
-256 unique image contents;4096square;original+PNG+DDS total128MiB,warn64MiB.
 Original files untouched;PNG and uncompressed DDS pixel roundtrip verified.
 DDS is renderer input;PNG is comparison evidence,not supplied to Remix.
-Conservative logical viewer asset reservation<=256MiB,not a bound on total Kit
 process working set. Account Python/mesh storage and decoded/GPU image reserve;
 actual driver/runtime allocation overhead is not precisely measured here.
-Existing owned-Kit scratch256MiB warning128MiB,console8MiB and owned-process
 guard remain. Reaching a lower aggregate guard yields partial,not larger budget.
-Expected two ships:roughly1–5MiB state logs plus one packet/asset and unique
 images. At maximum32owners raw JSON could grow around1MiB/s combined without
 caps; caps are enforced BEFORE relying on a run. No unbounded multi-GB capture.
 Unsupported texture formats can repeat console errors rapidly; guard stops at
8MiB console. Supervisor treats unsupported-image/texture-load errors as partial.
-Only offline --replay mode permits ONE comparison PNG;no continuous screenshots.

## Sponsor actions / analysis / cleanup

Enter familiar two-ship skirmish with different ship classes. Both should appear
in separate camera-aligned view,not only Klingon. Keep both visible briefly,
change camera angle,move/turn normally. No special marker/color or original SFC
lighting match expected. Exit normally on two beeps/request~90s tactical. Report
missing/wrong ships and rendering/HUD/control anomalies;no timestamps or RE.

Evidence:artifacts/live-bridge/<session> configuration/result/console;
artifacts/m1/runs/<timestamp>-enabled native LIVE-SCENE-001 packets/references/
updates/worker summary and existing run metadata/exit/hooks/hash evidence;
C:/Project/RemixJobs/preview-* perrevision provenance,images,viewer logs/results.
Supervisor joins viewer packetSHA to actual native packet,checks worker failures/
unsent/overflow,hook restore/normalexit/client unchanged and original image hashes.
Two constructed owners required; visual feedback still needed for acceptance.

Normal stop:drain callbacks,restore hooks,join worker<=5s,then unmap/unload. Failed
join prevents unload;preserve evidence and safely park,do not free live storage.
Viewer disconnect/failed decode/slow consumer cannot stall game. Guard owns only
its preview children;existing runner removes owned proxy/config and verifies client.
After analysis archive useful evidence+hashes,exclude portable/shader caches;raw
retained until approved cleanup. No automatic broad deletion/staging/commit.

Tests:full native build/tests/exports;project Python;preview/actual x86 worker IPC;
triangle/array/material readback;two synthetic shapes/shared thirdowner;
retirement/slot reuse/LOD changes;bad packet/association/path/images/bounds;
acknowledgements,torn state,slow/disconnected receiver,clean join with unsent
assets;empty preparation with absent imported job;PowerShell workflow/parsers.

Acceptance: actual two different ships from fresh packets,correct original image
associations,independent live state/camera,no regressions,normalexit/cleanhooks/
unchangedclient,bounds respected. Unknown material role/unsupported asset/lifetime
or category => explicit partial. Broader missions/any enemy are NOT established
by synthetic rehearsal or this first two-ship run alone.
