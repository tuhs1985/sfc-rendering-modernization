# REMIX-RETURN-001 — additive in-frame runtime image (development)

## Latest broad result — 2026-10-17

[Run11](../../runs/2026-10-17-codex-broad-depth-runtime-review.md):actual182017
10s capture/141,285events/no drops,18MBraw,normal exits/rollback/hashes. Persistent
1920x1080/8sample D32_FLOAT DSV with shader-readable companion,67,290associated
draws,unbound at600Present notifications. Confirmed descriptor/binding discovery,
NOT usable depth contents or ship replacement. No unchanged repeat capture
needed. Next bounded depth-value/static-state qualification requires separate
probe preparation;no new runtime workflow prepared by this offline review.

## Current broad-pull variant — approved / offline-qualified 2026-10-17

Latest [startup/recovery correction](../../runs/2026-10-17-codex-broad-startup-recovery.md):
first actual attempt failed gate load24 before graphics readiness,no tactical
records. Later retries refused deferred full-proxy state. Verified rollback now
complete;runner waits readiness,controller retries transient read-only module
snapshots,and next executing broad run can recover a unique interrupted
transaction after process absence. No injection retries/security changes/cap
increase. Same -BroadCapture command;revised startup still pending actual gameplay.

Sponsor approved matching full-add-on-support ReShade in offline fixture and
isolated test copy ONLY. -BroadCapture now selects the public application event
logger. [Contract/runbook](../broad-capture-contract.md),
[implementation/validation run](../../runs/2026-10-17-codex-full-support-broad-capture.md).
Both valid-scene positive/negative fixtures zero losses/state errors,normal exits;
isolated copied-proxy install/rollback validated. Actual SFC broad capture pending.
Full-support6.7.1.2131 pinned separately from limited6.7.1.2133;only opt-in session
changes copied proxy,with restoration after game exits. Accepted install untouched.
10s tactical detail,2GB writer hardcap,1GB warning,16MiB ring,32MiB ancillary
watchdog,10GB overall source/archive ceiling. No images/mesh dumps/Remix load,
native application-method patches or geometry hook. Exact enumerated coverage,
tools/builds,privileges,outputs,cleanup and archive procedure in linked contract.

Established elevated parent runs:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\remix_runtime\start_return_image_session.ps1" -BroadCapture
```

Enter usual two-ship skirmish,briefly both visible,play normally;no visual change
expected. Two beeps/console request normal exit after~10s tactical capture.
Do not use old -SearchDepth as a substitute for this event-level discovery pull.

## Historical broad-pull prerequisite — resolved by explicit approval

Sponsor requests broad capture retaining cap. Current limited-support ReShade
blocks external resource/view lifecycle and target-binding callbacks. Six-phase
getters below cannot become exhaustive coverage by increasing log volume.
[Coverage review](../../runs/2026-10-17-codex-broad-capture-coverage-check.md)
records source/log evidence and proposed10s/2GB metadata burst under10GB overall.
No broad runner implemented or capture launched. Approval needed to qualify a
matching full-add-on-support build offline and in isolated test copy, preserving
rollback; no accepted-install change, restriction bypass or proxy swap authorized
by this note. Historical six-phase runner remains scoped, not a substitute.

## Existing expanded-checkpoint probe

Expanded fixture --slow-end-scene holds a synthetic original EndScene call2s
after4s activity,then runner signals stop while it is active. Header reserved
is fixture handshake1inside/2returned,not production semantics. Verify restoration
and return via resident DLL stub,not a freed trampoline. Production observer has
NO sleeps. Same25s fixture/100s total/32MiB cap. Mid-call stub replays FF5128/85C0
then resumes original+5; original COM stack/HRESULT retained,observer FP/state
restored. Must pass offline before live engine use.

Expanded search in preparation: -SearchDepth implies observation-only host,not
Remix rendering. Records throughout90s at scene begin0069E300,scene-end entry
0069E3D0,postflush/pre-EndScene0069E41B,engine-present0069EB90,DXGI Present,
overlay. Engine code expected-byte verified and startup-only detoured in copied
client memory; registers/flags/FPU/SIMD/stack preserved,all original calls kept.
No006AB410 diagnostic geometry hook. Owned worker restores hooks using enrolled
thread transaction at stop; verify original bytes/mask15 before accepting cleanup.
Failure aborts claim,leaves project DLL resident; exit game normally,never hot unload.

Capture is descriptor/counter-only,6phases/32distinct observed resource rows,
fixed2304B extension at mapping256 (searchversion1),inside existing4KiB user-only
channel. No8sample limit or name/ship/resource-size filter; all90s counted.
Explicit no-context,wrong-thread,missing,invalid,busy and table-overflow counters.
Still scoped to selected active native context,not all GPU memory,other devices,
deferred contexts or temporary bindings inside translator calls. No resource
lifetime/owner/usable depth claim from pointer labels. Noimages/CPU readback.

Keep existing90s tactical/300s workflow/32MiB output bounds. Metadata expected
<2MiB,summary tables rather than per-call transcripts. Stop switches off capture,
worker detaches/verifies bytes,then normal exit. Full probe definition must be
updated with final runner/test commands before sponsor use. Offline stand-in
only until ABI,positive/negative and restoration checks pass.

Expanded workflow now offline-validated; current sponsor command from existing
elevated parent:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\remix_runtime\start_return_image_session.ps1" -SearchDepth
```

PS5->bundledPS7,existing elevation-policy module (no routine UAC),VS2026x86/x64,
bundledPython3.12.14. Copied client path/hash and exact sitebytes verified before
activation. Normal two-ship skirmish,play until two-beep90s exit cue; no triangle
or replacement. Missing/skip counts over fullwindow matter as much as found rows.
Native phase lastTick and global captureWindowMs retained; inactive phase>2s
before stop classified partial,not full coverage. Worker verifies byte restore
before exit cue. result.json expanded_search contains bounded6phase/32row table,
statuses,masks,limits,verdict; manifest records exactbuild hashes/configuration.
No render-thread disk/alloc/wait/readback. Output expected<2MiB new metadata plus
small retained build binaries;32MiBhard/16MiBwarning,300s whole workflow. No
unbounded multiGB tracing. Archive JSON/log/config only after analysis; keep
source and useful evidence; never delete loaded DLL or force-kill game.

Early observation runtime150957-452095 completed:8scope2 samples,0boundDSV,
normal sponsor gameplay/exit/cleanup/hashes. Both presentation getters negative.
[Review](../../runs/2026-10-17-codex-early-depth-runtime-review.md) records distinct
engine scene-end candidate; do NOT repeat either unchanged presentation probe.
The procedures below remain reproducibility history,not a request for another run.

Current next read-only test uses `-InspectEarlyDepth -ObservationOnly` together.
ObservationOnly host creates SAME4KiB current-user channel but NEVER loads Remix,
creates GPU device or window. It prints MODE OBSERVATION_ONLY and SESSION; waits
at most290s for stop,then prints sample summary/exit0. This isolates scene-depth
access from intermittent renderer-driver fault found in offline default-mode
regression. SFC component remains default-off; explicit gate arm enables only
eight read-only descriptors; image enabled flag always0. No triangle/appearance
change expected. Existing component still has bounded two256square resources,
but no output producer/copies. Do not call this a rendering/output regression.

Prepared command from established elevated parent:
`start_return_image_session.ps1 -InspectEarlyDepth -ObservationOnly`.
Same90s tactical,300s prepared,32MiB log limit and two-beep normal-exit request.
Keep both ships visible briefly; no new sponsor action/admin/timestamp required.
Earlier non-ObservationOnly procedure below remains historical experimental
option,not currently recommended default after driver fault143920-741724.

Offline control-only validation: `run_return_fixture.py --graceful
--inspect-early-depth --observation-only` with and without `--with-depth`.
Known synthetic D24S8 VIEW may use typeless R24G8 RESOURCE through existing proxy;
record depthViewFormat at180 separately (remaining72bytes reserved). Compare
captured resource/view descriptor exactly with fixture's independent native log,
not assumed requested resource format. Resize at sample3,recreate at5,stop at8;
25s fixture/100s total/32MiB caps unchanged,no saved screenshots in this mode.
Both processes exit normally,0image draw/copy; scalar sample results only.

### Earlier supported Present observation (2026-10-17 preparation)

`start_return_image_session.ps1 -InspectEarlyDepth` forwards --inspect-early-depth
and sets ONLY child SFC_REMIX_INSPECT_VISIBILITY=2. Exclusive with late option.
Use public addon_event::present,not reshade_present; pinned DXGI source905-913
places it before ReShade effects. Allowed by existing limited build's event
policy. Filter exact active runtime device/HWND/backbuffer resource identity.
Same eight descriptor reads>=1s apart after tactical arm,90s test/300s workflow,
32MiB hard/16MiB warning and no-suppression/cleanup rules. Same triangle sequence;
sponsor only enters ordinary two-ship skirmish,briefly keeps both visible,plays
until two-beep exit. No timestamps/admin dialogs/manual RE.

Optional visibilityScope at176:0legacy/absent,1late,2early;depthViewFormat180,
remaining72bytes reserved. Extensionversion1 and mandatory v2 prefix unchanged. New mode never
reports early result as late result or qualifies descriptor as scene depth.
No observed DSV still does not mean game has no depth elsewhere.

Offline `run_return_fixture.py --graceful --inspect-early-depth --with-depth`
binds fixture-only D24S8 depth view,depth testing disabled,requires8positive
observations/viewformat45/exact native resource descriptor/samples1 (actual
resource44/bind72 observed). Width/height must match recreated
1024x768 fixture. No-depth early variant requires8zeroDSV; default fixture remains
unchanged. One BMP only,25s fixture/100s orchestrator/32MiB caps; transient GPU
DSV<=1024x768x4(~3MiB),not an output-surface or scene-transport increase.
All inputs/outputs under existing ignored artifact run folders. No SFC run before
offline validation. Capture metadata in manifest/result,archive evidence after
analysis and retain originals; cleanup only owned host/fixture,normal game exit.

Visibility result2026-10-17: actual061033-016248-in-game yielded8checks/0bound
DSV; sponsor no issues,normal exits/hashes/limits. See
[review](../../runs/2026-10-17-codex-late-visibility-runtime-review.md). Late-depth
availability hypothesis resolved negatively,not proof of no depth elsewhere.
Do not repeat unchanged visibility run; next qualify one earlier scope.

### Default-off ship-visibility prerequisite (2026-10-17)

`start_return_image_session.ps1 -InspectVisibility` forwards
`run_return_game.py --inspect-visibility`; same isolated-copy/elevation/gate,
90s/300s/32MiB limits and cleanup as below. No ship suppression or black cutout.
It sets child-only SFC_REMIX_INSPECT_VISIBILITY=1. Existing shader/proxy settings
unchanged. Use ordinary two-ship skirmish, keep both visible briefly, play until
two-beep exit cue. Ships stay normal; the previously verified triangle sequence
is retained, not a new replacement demonstration. No manual timestamps/RE.

Only eight late-overlay depth-stencil binding observations, at most1Hz AFTER
tactical gate. OMGetRenderTargets/GetResource/GetDesc only; transient COM refs
released immediately, no binding change/GPU copy/readback/file/allocation/wait.
No original depth contents dumped. Optional v2 reserved-byte extension:
144visibilityVersion(1),148visibilitySamples,152depthPresentSamples,
156depthWidth,160depthHeight,164depthFormat,168depthBindFlags,
172depthMultisamples; remaining80bytes reserved. Mandatory256byte v2 prefix and
old single-image workflow remain compatible; zero means absent/defaultOFF.
Python state snapshots retain these counters in existing bounded result.json.

This asks ONLY whether a DSV remains bound at the current supported late insertion
point. Presence does NOT prove tactical scene-depth provenance, nonempty values,
depth convention, shader readability or preservation before HUD. Absence does
NOT prove SFC has no depth; it motivates one earlier scoped observation.
Any positive result still requires scope/content/convention qualification before
using it for occlusion. Descriptor counts never authorize original suppression.

Offline `run_return_fixture.py --graceful --inspect-visibility` verifies absent
depth, bounded sample counts and unchanged image/state. NoSFC. No extension use
in default ordinary fixture. After analysis archive log/JSON/BMP only; release
owned host/fixture normally, leave originals and testcopy intact.

Cleanup variant: run_return_fixture.py --graceful signals shared stop after
recreated phase instead of killing renderer. Same fixture<=25s/orchestrator100s,
32MiB hard/16MiB warning, one BMP, explicit same-user mapping, noSFC. Require
hostexit0,SDKShutdown0 and fixture5phases/state checks; separately inspect exact
common-object warning. Default crash variant unchanged. Stop signals only owned
host/fixture; fixed output directory perUTC. Used to compare teardown before and
after any supported host change, not to infer game replacement safety.

Runtime result2026-10-17: [review](../../runs/2026-10-17-codex-remix-return-runtime-review.md)
confirms actual in-SFC image/sponsor normal gameplay, bounded output, normal
exits and unchanged clients. Later preparation text is historical procedure,
not current UNTESTED status. Cleanup warning remains open; no ship replacement.

## Current prepared SFC procedure (authoritative; gameplay not yet exercised)

Build/validation: VS2026Community18.7.3, cl19.51.36248 x86/x64 /W4 /WX;
bundled PowerShell7.6.5 and Python3.12.14. Pins and control/resource ownership:
[v2 contract](../remix-return-contract.md). Existing M1 native build prepares
the unchanged one-shot gate/controller; build_return_probe.ps1 builds project
startup loader,component,host,native wire tests and offline fixture. Preparers:
prepare_runtime.ps1,prepare_reshade_sdk.ps1,prepare_detours.ps1,
prepare_test_install.ps1; no download/build occurs on the render callback.

From the ALREADY elevated testing parent:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\remix_runtime\start_return_image_session.ps1"
```

PS5 forwards to bundledPS7. Bypass applies only to that process; no policy/registry
change. ProbeRunnerPolicy requires existing elevated parent, never requests
RunAs/UAC. Routine preparation should be done by analyst, not sponsor.
For read-only verification without processes:
`<bundled-python.exe> tools/remix_runtime/run_return_game.py` (no --execute).

Runner directly launches ONLY C:/Project/SFC-Remix-Return-Test/StarFleetOP.exe.
Do NOT launch copied GUI launcher: its saved paths still point at accepted game.
No proxy files copied over accepted installation. Project DLL resides in the new
artifact run directory and is startup-imported in process memory only.

Sponsor enters familiar two-ship skirmish, keeps playing normally and observes
normal ships/HUD/controls plus green animated triangle in256square upper-right.
No ship tint/replacement expected. Automatic tEntityShip::render004162B9 gate:
oneframe/event/owner; hook restored and DLL unloaded before arming image.
One beep starts90s: imageON30s,OFF15s,ON15s,host stops/imageOFF30s.
Two beeps and console request mean EXIT NORMALLY NOW. No timestamps or RE work.
Report image sequence and any HUD/cursor/targeting/control issue. Window corner
placement is a pending SFC check, not an already-qualified universal UI exclusion.

Limits: build+prepared workflow<=300s (Python remaining<=285), hoststartup60s,
child verification20s, tactical gate wait90s, tactical test90s, exitwait30s within
remaining total. Delays may abort before completing stages; not all maxima can
be consumed together. Two256square GPU textures524288B,4KiB mapping, one
in-flight packet.32MiB run-folder/log hard cap; warn16MiB; state sampling4Hz,
summary counters. Expected<2MiB new logs/JSON plus bounded copied binaries; zero
gameplay screenshots/image dumps. Native fixture saves only1BMP1,920,054B.
Raw DXVK information/full call traces can grow quickly and are not enabled by
this runner. No unbounded apitrace/geometry transcripts or multi-GB capture.

Results under artifacts/remix-runtime/runs/<UTC>-in-game: manifest.json,
result.json,host.log,launcher.log,gate-controller.log,gate/M1-A-summary.json and
bounded gate evidence. Copied installation may generate its normal ReShade/game
logs; preserve/review these separately, not as altered client binaries. Compare
accepted critical hashes and global launcher paths before/after, copied-client
hash and component startup/epoch/sequence/copy/draw/clear counters.

Stop disables image, signals host and waits bounded shutdown. Never force-kill
SFC. A timeout leaves game alive and any active gate controller to restore its
hook; result records controller PID/exit/running state. Sponsor exits normally;
analyst verifies no live controller before cleanup. Do not delete loaded DLLs.
Normal game shutdown releases resources; next ordinary direct copied-client
launch without runner is removed state. No accepted proxy uninstall is required.
Archive selected run JSON/log/BMP/dump after analysis, exclude vendor binaries,
retain source+curated docs. No broad recursive cleanup. Do not remove test copy
or accepted files automatically. A failing frozen copied config needs explicit
review/rebaseline, not automatic edits to hide mismatch.

Until sponsor run: READY FOR SPONSOR RUNTIME TEST only. Actual in-SFC image,
normal exit, removed-state gameplay, UI preservation and return-path gate remain
unconfirmed. No ship suppression until that gate is adjudicated.

### Startup-only external registration (current prepared loader)

To avoid registering callback vectors concurrently with a running renderer,
return_launcher.exe uses official Microsoft Detours4.0.1 startup import support,
commit e4bfd6b03e50de46b47abfbd1e46b384f0c5f833. Source archive SHA256
FEF0B17C5C3C9356FB8BA7366A3B196149DAADD131FB6A92ABEDA1CB4D3B9B85.
prepare_detours.ps1 bounds download8MiB/60s, extraction16MiB/2048entries; x86
nmake only, generated dependency files ignored, no system installation.

Launcher permits only the exact copied StarFleetOP.exe or owned native fixture;
checks both executable/component SHA256, creates child suspended, verifies actual
process image path/hash before ResumeThread, then waits. Failed verification
terminates only the still-suspended owned child. No global launcher registry
change, on-disk game patch, APC/private-address guessing or proxy replacement.
Detours temporarily adds a component import in the NEW PROCESS memory only;
component DetourRestoreAfterWith restores that memory header before game entry.
Native protocol startupRestored/startupVerified must both be1. Ordinal1 helper
export and static import of the existing DXGI ReShade registration export follow
the pinned loader/SDK contract. Limited ReShade still enforces its event policy;
only permitted runtime/overlay callbacks are registered.

The component's normal DXGI import ensures existing proxy initializes first;
its forwarding remains unchanged. SFC original client/config/assets hash checks
remain mandatory. Actual client path verification occurs before any new game
entry/graphics callback. Fixture launcher owns a kill-on-close job; GAME launcher
does not kill a running game on timeout (leaves original renderer usable).
No hot-unload while active. Process-local default-off flags remain necessary.

Optional owned-fixture crash diagnostic: SFC_RETURN_CAPTURE_CRASH=1 installs a
fixture-only vectored handler for access violation/stack overflow; reserves64KiB
exception stack, prints at most32module/offset frames, writes ONE MiniDumpNormal
to fixture-crash.dmp using Windows dbghelp, then ends only the owned fixture.
No full-memory dump, SFC exception handler, system debugger setting or third-party
debugger installation. Expected<16MiB dump; same32MiB job watchdog. Purpose:
identify startup recursion observed only after external component registration.
Never enable this in SFC; it is not normal capture or an error-recovery policy.
Actual crash diagnostic20261017-050513-575921:88,717B minidump; exception maps
to own module __chkstk RVA0x5827, called by DLL thread dispatch. Source DllMain
reserved two32768wchar arrays (~128KiB) on every thread entry, including small
driver-created threads. Fixed by separate process-attach helper and1024char
bounded paths (long/truncated paths fail inert), no large all-reason prologue.
Static CRT thread notifications remain enabled. This is a project startup bug,
not evidence that the semantic seam or ReShade cannot work. Runtime confirmation
of the correction is required; retain failed logs/dump rather than hiding them.

Status: preparation only. Standalone GPU prerequisite passed; no in-game return
claim until actual tactical sponsor observation and recorded presentation join.
No ship suppression or visual replacement permitted by this first image proof.

Question: can a256square animated Remix scene appear inside the copied SFC
frame using its existing D3D11/dgVoodoo/ReShade path, with original game drawing
and controls preserved and safe disconnect/disable/removal?

Prerequisite: REMIX-OUTPUT-001 cross-process genuine final-colour/hash/pose proof,
30native contract checks and slow/disconnected consumer recovery. No Toolkit or
CPU screenshot transport. Geometry006AB410 hook remains off.

## Isolated preparation (before any game launch)

tools/remix_runtime/prepare_test_install.ps1 independently copies accepted
C:/Games/Taldren Software Inc/Starfleet Command Orion Pirates into NEW
C:/Project/SFC-Remix-Return-Test. Refuses an existing destination or source
reparse points; max20000files/5GiB, required disk headroom+2GiB. Current source
5781files/3063787385B. Each source/copy SHA joined in ignored
artifacts/remix-runtime/test-install/source-copy-files.json; concise manifest
alongside. No hardlinks to game assets, original writes or automatic deletion.
Partial preparation is retained for explicit recovery, not overwritten blindly.

Frozen client SHA2564D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Reference launcher2.1.0.22 SHA25684D3A5F89A922C4BEE6815CF0614538C3565C4BDB7DB3AA187C552CB727EF890
is copied for provenance but NOT launched blindly: HKCU global Paths/Client2Op
still selects accepted install. Read-only inspect_launcher.ps1 reads managed IL
with PS7/.NET MetadataReader (no execution), hash guard, <=8selected methods,
<=4096IL bytes/method; output normally<32KiB, ignored if retained. No broad
launcher reconstruction. Observed LaunchApplication sets full filename and
working directory explicitly; clsCFG.Start prepares selected-path sprite/config
data. Already-working installed assets/config are copied exactly. Test-local
launch must avoid repointing original global launcher settings and verify full
process path before activating anything. If it cannot start with frozen copy,
report that specific launch blocker instead of touching accepted configuration.

## Candidate compositor (not yet implemented/qualified)

Existing proxy ReShade6.7.1.2133 exports add-on registration and logs addon32
discovery. Official matching tag8cf85bd12d56697d756d4fcb45e501f5d1b540fa;
ImGui submodule3912b3d9a9c1b3f17431aebafd86d2f40ee6e59c. Supported
reshade_overlay callback runs even with menu closed. An image-only noninteractive
draw list could reuse built-in state preservation, with no desktop overlay or
new proxy. Must validate API/GUI ABI, GPU transfer, state/input preservation and
cleanup offline before installing a default-off addon32 in test copy.

Planned runtime envelope stays90s tactical/300s total, output pool<=4 and128MiB,
256square first proof, logs32MiB warning16MiB. Sponsor only enters skirmish,
observes returned scene/normal controls and exits normally when requested. No
manual timestamps/UAC/trace analysis. No actual runtime entry command is ready
yet; do not improvise it from a historical runner.

Cleanup is removal of only owned test-copy add-on/proxy support files after
normal component shutdown; accepted installation never receives them. Preserve
test copy/config manifest and curated evidence. No game executable patch.

### ABI prerequisite (no game/device)

prepare_reshade_sdk.ps1 fetches only8headers at pinned ReShade commit plus
imgui.h/imconfig.h from pinned submodule into ignored dependencies; manifest
records hashes/sizes. build_return_probe.ps1 uses VS2026 x86/C++20 /W4 /WX.
reshade_abi_probe.exe loads ONLY copied test-install DXGI.DLL, prints requested
SDK API and ImGui versions, calls supported registration/unregistration, unloads
and exits. Never pass accepted-install proxy path. No GPU/device/game created.
Runner must cap20s/2MiB textual output and terminate only owned probe if needed;
ReShade.log is generated only in copied test location or probe artifact folder.
Registration must pass API and ImGui function-table checks before image add-on
implementation is called compatible. Capture actual stdout/exit and proxy hash.

## Offline compositor fixture (no SFC launch)

build_return_probe.ps1 builds x64 return_host.exe, x86 SFCRemixReturn.addon32 and
d3d11_return_fixture.exe using /W4 /WX. Protocol2 in return_wire.h/return_channel.py
is a separate256B diagnostic control block in a4KiB user-only GUID mapping, not
the scene transport or a synchronized ship-replacement contract. C++ publication
and ACK use Interlocked32-bit operations. Python changes only independent
armed/enabled/stop flags through aligned32-bit stores on supported Windows x86/x64;
it does not publish resource/frame payloads or image data.

run_return_fixture.py (bundled Python3.12) starts the pinned runtime host, waits
<=60s for its explicit session name, and launches only an owned native D3D11
fixture with a copied ReShade proxy/add-on in a new ignored run folder. Add-on
is inert without explicit session AND matching expected full executable path.
No accepted-install DLL/config/registry setting changes, no original game launch.
Process-local NRC/DLSS/RR off and synchronous shader compilation as qualified.

Native fixture alone clears blue; only genuine SDK output can supply the green
triangle. ReShade's supported image draw-list callback composes the shared GPU
image into that frame, not a desktop overlay. No windows/widgets accept input.
Native shared texture and private display copy: two256square outputs<1MiB total.
Producer EVENT completes before publication. Game-side GetData(DONOTFLUSH)
never waits; ACK only after GPU copy to the private display texture completes.
Last display hides if stale>1s, stopped, disabled, unarmed or invalid. No game-side
Map/readback, disk I/O, shader compilation or direct pipeline rebinding.

Fixture tests enabled -> disabled -> reenabled -> ResizeBuffers -> device/swap
recreation -> owned renderer termination and stale-image hiding. Native runtime
destroy clears READY before releasing resource ownership; a new epoch prevents
old output reuse. Fixture checks OM/RS/IA state sentinels across actual Present
and takes five fixed verification readbacks, saving only the first image BMP
(800x600,1920054B), not a continuous image stream. DXGI_SWAP_EFFECT_SEQUENTIAL
preserves the backbuffer for verification after Present, per Microsoft's DXGI
SWAP_EFFECT documentation. This choice is ONLY the offline fixture, not a change
to SFC's swap effect or existing proxy settings.

Limits: native fixture25s after device setup; orchestrator100s total/32MiB whole
job (including copied small binaries),16MiB warning; poll50ms; host startup60s;
no game/driver/security-policy changes. On failure only owned fixture/host are
terminated. Generated job retained for analysis; no automatic broad deletion.
Expected files host.log,fixture.log,ReShade.log,result.json and at most one BMP.
Success here is OFFLINE validation, not in-game RETURN PATH DEMONSTRATED.

Actual first fixture20261017-050102-615502: auto-discovery refused .addon32 because
installed ReShade is limited-support build. All1476original frames retained
graphics state; no component loaded/image shown. ABI registration success did
NOT establish auto-load support. Pinned addon_manager.cpp:237 refuses automatic
loading, while ReShadeRegisterAddon and allowed runtime/overlay events remain
publicly available (restricted application events still blocked at:572).
Next fixture explicitly LoadLibrary's project SFCRemixReturn.dll after loading
copied proxy, then uses supported external registration. No ReShade replacement,
binary patch, restricted-event use or change to proxy forwarding. Native fixture
alone loads its owned DLL; future SFC loader must independently verify test-copy
process path and use the approved component-loading discipline. No hot unload
while active; disable flags first, normal runtime destroy before DLL unload.
