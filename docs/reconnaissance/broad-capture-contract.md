# Broad capture contract — REMIX-RETURN-001-BROAD

Status: offline-qualified; actual SFC capture pending. Sponsor approved optional
full-support ReShade ONLY for isolated test copy. No requirement/TRL change,
renderer architecture selection, original suppression or accepted-install change.

Current startup correction: [run10](../runs/2026-10-17-codex-broad-startup-recovery.md).
First actual attempt failed gate load24 before graphics ready;no tactical data.
Saved proxy/config now restored. Runner waits verified graphics readiness before
gate,controller retries only read-only snapshot BAD_LENGTH <=100attempts,not
injection. Unique verified interrupted transaction can recover automatically on
next executing attempt ONLY with no SFC running;read-only preflight never writes.
Inventory errors/ambiguous backups refuse action. Same cap/sponsor procedure.

## Coverage and provenance

Purpose: locate retained/transient depth and render-target relationships missed
by six sampled engine/presentation getters. Pinned full-support6.7.1.2131/API18
uses supported external callbacks,not patched restrictions or new native hooks.
Existing limited6.7.1.2133 proxy is backed up/restored. See
[dependency manifest](remix-return-dependencies.json) and
[run09](../runs/2026-10-17-codex-full-support-broad-capture.md).

All callback devices/command lists/resources are admitted;no ship,owner,name,
format,resolution,resource-ID or selected-device filter. Lifecycle plus target
bindings/reset are retained from startup,including menus;other detailed events
start after the existing automatic tactical gate. A gate is not an object filter.
No resource contents or pointer dereferences after callback lifetime. Native
labels are process-local,not portable GPU handles or semantic owner identity.

Enumerated event IDs (see broad_events.h for precise argument layout):

| IDs | Events / payload |
|---|---|
|1–2|device creation/destruction; API kind|
|3–4|resource creation/destruction; type,usage,heap,flags,initial state,buffer size/stride OR texture dimensions/layers/mips/format/samples|
|5–6|view creation/destruction;resource,usage,type,format,range|
|7–9|command-list creation/destruction/reset|
|10|target bindings;RT count,DSV,up to all8 D3D11 RT views|
|11–12|draw/indexed counts,instances,offsets;no vertex/index contents|
|13–14|depth/color clears;view,clear values,rectangle count;rectangle contents not retained|
|15–17|resource/texture copy and resolve;source/destination/subresources;copy-box coordinates not retained|
|18|Present;queue,swapchain,backbuffer label|
|19–21|viewport values,pipeline handle/stages,dynamic-state values|
|22|execute-command-list relationship;queue/list labels|
|23|reserved;gate time is recorded in header,not an emitted event|

This is **not an exhaustive API/GPU trace**: indirect draws,shader contents,
pipeline creation descriptors,descriptor tables,buffer/image contents and full
deferred command replay are not captured. ReShade-internal operations need not
emit public application events;their absence cannot establish no GPU activity.
Pipeline handles alone do not establish depth-test enable/intent. Descriptor,
binding or draw correlation is NOT usable scene-depth/ship coverage proof.

## Binary / shared status

Independent magic0x42524431,version1. Exact128B little-endian file header,then
128B records. Shared header at offset256 in existing4KiB current-user-SID-DACL
GUID return mapping;main version2/256B prefix unchanged. SearchDepth and Broad
are mutually exclusive. Runner stores explicit GUID session,verified game PID,
component/dependency hashes and qualification in manifest.json.

Header layout:

- 4u32:magic,version,recordBytes,headerBytes.
- 8signed32:status,error,reason,warning,attempts,dropped,written,queued.
- 4u32:PID,three reserved.
- 8u64:QPC frequency,start,gate,end,fileBytes,hardBytes,warningBytes,durationMs.

Statuses1prepared/2running/3closed/4error. Reasons1duration,2bytecap,3externalstop,
4I/O failure,6watchdog. Headerfile is finalized before shared status3 publication.
Record:sequence u64,QPC u64,event u32,thread u32,object u64,device u64,11u64 args.
Floats retain raw32bit IEEE bits in u64 fields. Records preserve accepted order;
concurrent producer skips/ring saturation increment dropped,never wait for SFC.

16MiB ring preallocated before registering callbacks. Producers try-lock only
against producers;worker uses acquire/release indices,no disk-write lock on
callbacks. No callback allocation/filesystem/waits/readback/rebinding or viewer
calls;all bool interception callbacks return false to continue original drawing.
No observer retains resource COM references. Worker drains active callbacks and
queue on stop;storage is process-resident,not hot-unloaded/released under callbacks.

## Bounds / safety / cleanup

- Detail10s after tactical gate (worker polling2ms;runner waits10.1s),plus bounded
 startup lifecycle/target prelude;285s component watchdog,300s prepared workflow.
- Trace hard2,000,000,000B including header,warn1,000,000,000B. Worker checks
 overflow-safe remaining budget before EACH batch;never writes over cap.
- 16MiB ring,256record worker batches;loss/error/cap producesPARTIAL,not fabricated
 absence. Writer failure/saturation leaves original renderer untouched.
- Ancillary32MiB watchdog/warn16MiB;ReShade.log in test directory included in
 watchdog. Not a system-wide filesystem quota. No image or repeated mesh dumps.
- 10,000,000,000B overall sponsor ceiling:2GB trace plus32MiB ancillary;reserve
 up to same size for verified archive;do not fill remaining allowance speculatively.

Admission counts existing runtime runs/archives as well as reserving the new
worst-case source+archive/ancillary space;disk-free check too. Archive tool checks
existing output plus proposed ZIP allowance. This is a single-workflow admission
budget,not a filesystem quota against unrelated concurrent programs. At closeout
existing runtime run/archive files total387,596,530B,comfortably below reserve.

Default-off environment SFC_REMIX_BROAD_OUTPUT set only by explicit runner;output
CREATE_NEW in unique ignored artifacts/remix-runtime/runs/<UTC>-in-game/broad.bin.
Main scope still validates expected image and current-user GUID channel.
prepare_full_reshade.py downloads bounded64MiB from official site,hash-checks,
extracts only ReShade32.dll without executing installer. Do not update driver,
load Remix,change translator,security controls or global launcher settings.

Launch from established elevated parent using start_return_image_session.ps1
-BroadCapture. WindowsPowerShell5 forwards to bundledPowerShell7;builds first,
then uses remaining five-minute budget. No routine new UAC. Enter usual two-ship
skirmish,keep both visible briefly,play normally. No changed ship/triangle is
expected. One beep starts tactical recording;two beeps plus console ask normal
exit after~10s. No manual timestamps or RE. Gate itself is restored/unloaded by
existing controller;full-support module stays resident until normal process exit.

On normal exit:verify byte/log close,process exit,accepted hashes and settings;
restore copied proxy/config from verified per-run backup and compare critical
baseline. If game survives failure,disable capture,leave module/proxy resident,
request normal exit;do NOT hot-swap DLL or kill SFC. Then use guarded
restore_test_proxy only with exact backup and no StarFleetOP process,or stop for
review if independent changes detected. Stage conflicts are not overwritten.

Streaming analyze via broad_capture.py <exact broad.bin>;counts/dropped/errors,
creation-aware views/resources,per-context bindings and nonzero draw association.
Reset/retirement clears known state;unknown associations remain unknown. Analyzer
maps bounded65536resources/views,4096contexts/candidates;first512ranked summaries;
overflow yieldsPARTIAL,raw records remain for later questions. No blanket
"no depth" verdict for uncovered events/deferred execution.

After analysis run archive_broad_evidence.py with explicit archive ZIP and exact
run directory. Excludes binaries,keeps raw transcript plusJSON/log/INI;prechecks
source+archive allowance,uses ZIP64/deflate1,validates CRC and saves archive hash.
No automatic raw deletion. If storage requires cleanup,remove only exact
verified archived generated capture after recording path/hash,never source or
rollback file for an unresolved process. Old captures stay historical.

## Offline evidence / acceptance

Final positive180332-043697:582frames,zero state errors/drops,resize/recreate,
normal host+fixture exit,12,785records/1,636,608B;3creation-distinguished depth
view epochs. Original valid draws reach callbacks before depth unbind atPresent.
Depth testing intentionally disabled in fixture;NOT tactical-depth qualification.
Final negative180344-409639:579frames,zero state errors/drops,normal exits,
no depth candidates. Full-support external registration/API/ImGui acceptance,
callback delivery and actual state preservation corroborated dynamically.
See run09 for failed iterations;do not discard or relabel them.

Actual SFC acceptance:10s post-gate coverage,resource/view creation provenance,
target/draw/presentation relationships with no losses (or explicitPARTIAL),normal
sponsor-observed rendering/HUD/controls,normal exit,proxy/config restored,client
hashes unchanged,bounded evidence. This is discovery,not ship replacement or
milestone completion. Next experiment depends on observed depth/coverage path.
