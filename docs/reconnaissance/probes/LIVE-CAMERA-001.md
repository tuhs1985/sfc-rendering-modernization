# LIVE-CAMERA-001 — camera-aligned selected-ship bridge

Sponsor authorized camera wiring2026-10-16. Extends LIVE-BRIDGE-001, not a new
renderer, camera-mode reconstruction, image return or lighting extraction proof.
Purpose: selected textured ship angle/zoom/tactical-screen placement follow SFC;
NOT background/HUD/other ships, pixel-identical lighting or complete screenshot.

Status: real camera-aligned bridge DEMONSTRATED2026-10-16; see
[runtime adjudication](../../runs/2026-10-16-codex-live-camera-runtime.md).
1858 accepted actual camera/ship updates,zero camera/asset/viewer rejects,
max actual USD projection discrepancy.002634pixel,normal exit/cleanup/client
unchanged. Sponsor reports worked with side-by-side screenshot. Not full pixel/
lighting equivalence,selected-owner lifetime or formal gate advancement. General
late-run semantic rejection and earlier launch failure retained in runtime record.

Historical preparation status: READY FOR SPONSOR RUNTIME TEST. Final native build/regressions/exports,
93 project/44 preview+IPC tests, PS policy/parser checks PASS. Real-Kit synthetic
camera rehearsal118updates,zero rejects,projection error<=.0000522pixel using
actual USD hierarchy/camera,nonzero viewport/projection offsets,twoepochs/onehide,
clean exit. NOT actual SFC pixel/camera proof.
[Preparation record](../../runs/2026-10-16-codex-live-camera-preparation.md).

## State/ABI/protocol

Same validated wrapper/owner scope, original state-preserving stubs unchanged.
Read/recheck supplied+6F4/composed+6B0 and newly view+628/projection+55C (17words
each),viewport+75C six floats. Static byte anchors and arithmetic in active-camera
state map/36-prefix verifier. No new hooks/native calls/game writes/cache mutation.
No projected-vertex-cache hook: numeric cross-check uses independent direct V/P/S
against already engine-composed C on three verified mesh points, then actual
USD/Gf camera projection against C. This is not native framebuffer/pixel readback.

Component0.19/channel protocol2,96words. First48 unchanged from protocol1;word48
camera-valid1;49..65 nativeV,66..82 nativeP,83..88 viewport x,y,width,height,
half-width,half-height;89..95 reserved0. Same2MiB current-user-only mapping,
guard at256 encloses384-byte record from260. Old logs remain immutable; new
readers reject old live protocol rather than reinterpret bytes. Offline camera
recovery accepts either48/96-word logs. No producer/receiver version mixing.

Receiver applies proper-rigid view inverse, native origin subtraction and import
scale100 consistently to camera and ship. USD camera focal/aperture/offset ratio
comes from P; render resolution is exact tactical viewport width/height, NOT
assumed full game buffer. Native viewport offset included in numerical pixel
comparison; displayed window is tactical viewport crop scaled to fit, no HUD.
Admit inspected standard perspective only; orthographic/skew/nonrigid/bad aspect/
nonfinite/degenerate clip fail hidden/PARTIAL, never silently fixed camera.
Near/far reproduce that matrix's standard perspective form; this does not yet
qualify SFC-to-returned-depth clip interval or pixel-center/GPU raster conventions.

Before display, independently compose S*P*V*M on3 mesh points and compare XY
against native stored C; then read actual USD/Gf camera and compare its projection
against C, threshold.25native pixels. Record errors/counters. Manual preview
view/Frame ship buttons absent in game-camera mode. Original fixed diagnostic
still explicit via run_live_bridge.py --fixed-camera; normal offline viewers intact.

## Reproduce / bounds / cleanup

Tools: existing VS2026/MSVC14.51 x86, bundled PS7.6.5/Python3.12.14/Pillow,
Toolkit1.6.0-dev. Build existing build_m1_component.ps1/build_remix_job.ps1.
Launch same start_live_bridge_session.ps1 from established elevated parent;
PS5 delegates toPS7, process-only policy bypass, no new UAC/security relaxation.
Prewarm outside game, normal two-ship fixture, automatic tactical gate. Once model
appears hold still briefly, change SFC camera angle/zoom while keeping selected
Klingon visible, then normal play. Enemy selection allowed, no manual timestamps.
Exit on two beeps/request. Viewer camera should follow game modes automatically;
no separate view buttons or cosmetic alignment tuning required.

Unchanged90s tactical/<=2700publications/30Hz/twoassetepochs/2MiB transport and
8MiB bridge core evidence;120 detailed frames/10000events/16MiB warning/32MiB
event cap; ten resources4096square/64MiB warning/128MiB image hard cap. Projection
viewport<=4096square, unsupported sizes cause partial rather than silent resize.
Expected movement logs now ~1–3MiB combined, no per-frame meshes/images/screenshots
or rapid multi-GB output. Native reads extra160bytes twice/update after throttle.
Worker still owns IPC/files; fail-open/no renderer-thread I/O/wait/allocation.
Same worker drain/join/unmap, hooks/proxy removal/client hash checks, guarded
preview startup180s/game readiness45s/total300s workflow and owned-process limits.

Outputs: same run folders, raw96-word JSONL, viewer per-update camera error and
summary camera_updates/camera_rejected/errors. Fresh same-epoch asset provenance
unchanged. Replay explicitly synthetic movement AND camera; no runtime success
claim from it. Preserve comparison/evidence archive; no source/cache deletion.
Validation: native capture/recheck/bounds, Python conversion/refusal tests, real
Kit replay with nonzero projection offsets and viewport origin, final parsers/diff.
Runtime success needs sponsor visual alignment + numeric checks, no regressions,
bounded output/cleanup/unchangedclient. No formal TRL claim or picture-return proof.
