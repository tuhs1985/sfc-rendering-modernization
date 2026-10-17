# Codex run — wire active SFC camera into live bridge

Run/date:2026-10-16-live-camera-preparation /2026-10-16 EDT.
Sponsor authorized "ok, yea go"; selected ship should share game camera angle,
zoom/tactical placement, NOT complete HUD/background/otherobjects/exact lighting.
Starting HEAD fee152f137a55a3efeb47a5c236ebf9e3e1951cb,index empty,inherited
dirty work retained. No requirements/milestone change, helper or subagent.

Authority/evidence read: newest HANDOFF, active camera map/36 original-PE anchors,
camera recovery, real0.18 bridge run/probe/contract and current source. Installed
viewport API source confirms set_texture_resolution; imported USD hierarchy
confirmed identity World beneath uniform100 XForms scale. No camera-mode RE.

## Implementation / capture definition

LIVE-CAMERA-001: component0.19/protocol2/96words. Prefix48 retained;48 valid1;
49–65 directV17words,66–82 P17words,83–88 viewport x,y,w,h,half-w,half-h. Native
read/rechecks camera plus repeats M/C check afterward, same atomic record guard.
2MiB/user-only ACL/30Hz/2700updates unchanged. No new hook/native state write,
engine calls/render-thread I/O/wait/allocation. Worker owns channel/files/cleanup.
Old live protocol refused; saved48word logs remain supported offline.

Default runner --game-camera, explicit --fixed-camera retains old diagnostic;
separate view/Frame controls disabled in aligned mode. Camera view inverse and
model share nativeorigin/importscale100. P supplies lens/aperture offsets; viewport
supplies tactical resolution, NOT assumed full1920gamebuffer. Standard-perspective
near/far reproduce P, not yet a qualified returned-depth convention.

Three mesh points compare direct S*P*V*M against engineC, then effective USD scene
hierarchy+Gf camera projection against C,<=.25nativepixel. Reject nonfinite,
nonrigid/reflected view, orthographic/skew/bad aspect/unsupported clip or viewport;
hide/PARTIAL, no fixed-camera fallback. No cached-native-vertex hook added:
numeric checks are independent direct-state vs engine-composed matrix and USD,
NOT framebuffer/GPU pixel comparison. Actual SFC alignment still unproven.

## Tools / reproduction / validation

VS2026/MSVC14.51 x86 C++17;PS7.6.5;Python3.12.14/Pillow12.3.0;
Toolkit1.6.0-dev+main.30229.3f23f80a.gl. PYTHONDONTWRITEBYTECODE=1,
TEMP/TMP=artifacts/m1/test-temp. User-only IPC/Kit tests outside restricted sandbox;
no ACL/security relaxation. Commands:

```
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/m1_component/build_m1_component.ps1
python -m unittest discover -s tests -p test_*.py
python -m unittest discover -s tools/remix_ingest -p test_*.py
python tools/remix_ingest/run_live_bridge.py --replay
pwsh -NoProfile -ExecutionPolicy Bypass -File tests/test_mesh_export_workflow.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File tests/test_texture_export_workflow.ps1
git diff --check
```

Final native build/contracts/exports PASS;93 project/44 preview-camera-IPC tests
PASS, PS policies/three runner parsers/diff PASS. New tests: viewport/projection
offsets, origin/units, mismatched camera/aspect, invalid projections; native
camera mutation read-recheck/no publication, protocol2 worker lifecycle.
Native build repeated after final coherence check; IPC suite repeated against
completed native producer. No game run or native hook restoration runtime claim0.19.

Three real-Kit SYNTHETIC rehearsals passed. Final session
073df242b9e341b8b4c1070f49421aaf, preview
C:/Project/RemixJobs/preview-20261017-014214Z-e9a8d876 (Oct16 EDT):118camera/ship
updates,zero rejects/asset errors,twoepochs/onehide,authored matrix readback match;
max actual USD hierarchy/camera projection error.000052198133pixel against supplied
nativeC. Includes viewportorigin200/projection offsets.12/-.08 and camera/object
motion. Supervisor16.969s,Kitguard16.328s/exit0/stop_reason0/remainingowned0;
console24544bytes,peak scratch2531511bytes,no warnings. Replay is not SFC proof.

Probe limits unchanged:90s tactical/300s total after build,180s viewer startup but
game only starts if readywithin45s;2700updates/2MiB transport/8MiB bridge core
evidence,16/32MiB events,ten images/4096square/64warning/128MiB hard. Extra160byte
camera read twice plus final M/C recheck; no mesh/image-per-frame or multi-GB
mechanism. Existing parent elevation/PS5->7 handoff/no new UAC retained.

Archive artifacts/remix-ingest/evidence/20261016-live-camera-offline.zip,
40files/70951bytes,SHA18734FEBA5B6BAAF659AD01A650BEFC2D7C5219C160B4A02345653AB6ADA1862;
all entry hashes verified, useful rehearsal/config/source/reports/logs, no caches.
No original/raw/cache deletion. Prepared0.19 componentSHA
E2CAB2A470F07D9FF51A99EC9A64984BCF057A688DF901A23805EC8DEA0BB2B4,
proxySHA E25B5A4B7337D64DE1C46A15B31CC2ED947F9002323C7B68C8D1F7DAEBF8EE25.
Entry rebuilds; future runtime metadata must record actual rebuilt hashes.
Installed client independently rehashed unchanged:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.

## Files / final state / next action

New:tools/remix_ingest/live_camera.py,test_live_camera.py;
docs/reconnaissance/probes/LIVE-CAMERA-001.md;this record.
Modified:tools/m1_component/m1_live_bridge.h,m1_component.cpp,
analyze_live_camera.py,start_live_bridge_session.ps1;tests/m1_live_bridge_tests.cpp;
tools/remix_ingest/live_bridge.py,test_live_bridge.py,kit_live_bridge.py,
kit_mesh_preview.py,run_live_bridge.py,run_mesh_preview.py,README.md;
docs/reconnaissance/live-bridge-contract.md;docs/HANDOFF.md.

READY FOR SPONSOR RUNTIME TEST, camera/raster alignment NOT runtime proven.
No appearance/UV/winding/normal edits, originals/vendor/global config unchanged.
No game/controller or owned Kit/session/server active; Fuel Guard exact-thread
hook verified,directsandbox connection denied/quota unknown,no new daemon/helper.
HEAD unchanged/index empty,inherited dirty work preserved,nothing staged/committed.
One documentation patch context mismatch failed atomically; corrected with no
evidence overwrite. Final link/diff checks PASS.

Exact next action: run same prepared start_live_bridge_session.ps1 from existing
elevated parent; usual two-ship skirmish,keep selected Klingon visible while
changing SFC camera/zoom,exit normally at two cues. Then inspect fresh numeric/
visible alignment,gameplay/cleanup/hashes; do not begin lights/image-return work.
