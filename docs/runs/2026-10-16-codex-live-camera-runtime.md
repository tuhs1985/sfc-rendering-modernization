# Codex run — actual camera-aligned live bridge

Run/date:2026-10-16-live-camera-runtime /2026-10-16 EDT. Active task:
LIVE-CAMERA-001 bounded live connection, not a new milestone/gate claim.
Question: does fresh SFC ship AND active camera state drive the separate Remix
ship view? Sponsor reports "we did it! it worked!" with side-by-side screenshot.
Starting HEAD fee152f137a55a3efeb47a5c236ebf9e3e1951cb,index empty,
inherited dirty implementation/evidence retained. No new game launch/build/code.

Authority read: newest HANDOFF, camera preparation record, LIVE-CAMERA-001,
live-camera conversion/rejection source and actual run/worker/viewer metadata.
Tools: PowerShell7,bundled Python3.12.14,existing live_camera.camera_state,
component0.19,Toolkit1.6.0-dev. Exact captured component SHA:
858DEF8EA9D82294A207983FC41FC28F84E83F88B78C457C94B754A529898EAF;
different from preparation build because launcher rebuilds. Runtime is authoritative.

## Direct evidence / adjudication

- Session artifacts/live-bridge/009e8edf0d2340919622c3be0426dc6d/result.json:
  replay=false,game_runner_exit0,preview_exit0,126.171s workflow.
- Native artifacts/m1/runs/20261016-215022-enabled:1859 protocol2/96word records,
  worker dropped0/invalid0/asset_rejections0/attempts1/io_failedfalse/stoppedtrue.
  Owner1/model259638552/source77149788 stable; process-local labels only.
- Preview C:/Project/RemixJobs/preview-20261017-015011Z-36c024c3:
 1858 accepted,zero rejected/camera rejected/errors/asset failures,one qualified
 epoch,no hide. Content verified kff.mod signature
 74cd4f327c589b7b6445123a640dae27e947df3ae9e649077795f78b0c0425e4;
 unchanged source/session-only transforms. Every viewer record joins native
 sequence and owner; every authored matrix readback match=true.
- Native elapsed94..89984ms,frames4..5382,max update gap234ms;1799 distinct
 view matrices,1839 distinct object matrices,one projection. Actual tactical
 viewport origin200,30,size1720x1020,not whole1920x1080.
- Re-ran camera_state on ALL1859 records with verified mesh's three test points
 and first supplied translation as origin: maximum direct S*P*V*M vs engineC
 error.0026351762pixel. Viewer actual USD hierarchy/camera projection maximum
 .0026333647pixel. Both below approved.25 threshold; zero failures.
- Sponsor screenshot copied unchanged to
 docs/reconnaissance/images/20261016-live-camera-sponsor.png: selected Klingon
 visible in both SFC and separate preview. Different window dimensions, provisional
 lighting,HUD/background/effects exclusion remain intentional. Screenshot and
 sponsor report corroborate live camera use,not pixel-identical final rendering.

CONFIRMED: real fresh semantic owner/model and directly captured camera feed the
separate renderer repeatedly,including changing view and object state; original
path continues,not synthetic playback. No assumed improvement/final architecture.
Single frozen screenshot does not independently prove all camera modes,zoom/clip
interval,pixel centers or GPU depth equivalence. Follow-up sponsor answer on
2026-10-16 to whether rendering/controls stayed normal while the separate view
followed the camera: "yes, everything worked as expected." CONFIRMED sponsor
observation of normal operation, not instrumented verification of every control.
Selected-owner retirement/reappearance
not observed,so don't promote offline lifetime tests into runtime proof.

## Exceptions / unsuccessful attempt

General summary has1280 rejected semantics,NOT zero:640 visual kind2/reason2
(ship vtable mismatch),640 model kind3/reason12(no mainline owner),72.703–78.078s.
Supported by current validation branches in m1_component.cpp. These do not become
qualified selected-owner updates; bridge/viewer reject counters remain zero.
General owner_retired3,known00509843 count5386,owner/thread overflow0. Specific
object/category causing late rejections unproven; don't infer destruction from
screenshot alone or call every render category supported. Preserve for future
exception/lifetime work if necessary; no new broad archaeology this review.

Prior sessionbe1c07d0961a498082e438f92a756bd3/result.json is PARTIAL,
game_runner_exit1,"Game runner failed; preserve cleanup evidence before retry",
38.047s. Preview guard exit0/remainingowned0. No corresponding native run record
available in current runs listing to establish cause. Preserve separately; later
successful run does not erase failure or prove repeatable startup.

## Bounds / cleanup / validation

LIVE-CAMERA-001 unchanged90s tactical,300s prepared workflow,2700update/30Hz,
2MiB user-only mapping/8MiB bridge logs,existing16/32MiB event limits and
ten-image/128MiB image limit. No geometry firehose or perframe image dumps.
Native log1182678B,viewer455589B,total1638267B. CSV341980B,5382observedframes,
no warning/truncation. Kit111.625s/exit0/stop_reason0,console25111B,
peak scratch2961512B/no warning,remainingowned0.

Controller component_state=removed/hook_bytes_restored=true; component log all
hooks restored; worker joined/stopped. Run-result normal_exit_observed=true,
client_unchanged=true,exit_outcome=exited,no mesh-pipeline failures. Independent
review finds no owned winmm.dll,m1_component.dll,m1_gate.dll,m1-component.ini
in game directory,no StarFleetOP/m1_controller process. Installed client SHA:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29,
matches recorded before/after. No original client/assets/security edits.

Read-only JSON analysis: parse both JSONL,assert96words,join sequence/owner,
assert readback matches,unpack firstM translation,call camera_state for each
record and verified check_points,measure distinct states/ranges/max errors.
Reproduction tests: bundled python -m unittest discover -s tools/remix_ingest
-p test_live_camera.py:3 PASS with PYTHONDONTWRITEBYTECODE=1 and workspace
TEMP/TMP=artifacts/m1/test-temp. No claim full preparation suites rerun.
git diff --check and referenced path checks PASS. An initial guessed timestamp
path and optional nonexistent workflow filename read failed harmlessly; actual
directory inventory used instead,no mutation/fallback tooling changes.

Archive artifacts/remix-ingest/evidence/20261016-live-camera-runtime.zip:
83files/3024829B,SHA256
852004DB10B7D25593B1C8EF3C455AE9A2C046A8E022D52E1CF4C79B9A253022.
ZIP_DEFLATED,actual M1run + both supervisor sessions + useful preview top-level
files + sponsor screenshot;exclude cache/meta. All entry SHA compared with source.
Raw retained,no deletion. Screenshot is documentary evidence,not instructions.

Files changed this review: this record,docs/HANDOFF.md,
docs/reconnaissance/probes/LIVE-CAMERA-001.md,and copied screenshot above.
No code modifications. HEAD unchanged,index empty,nothing staged/committed;
inherited dirty work preserved. Fuel Guard exact-thread hook verified,direct
sandbox connection denied/quota unknown,no daemon/helper/subagent started.

Result: camera-aligned selected-ship live bridge DEMONSTRATED in this run.
Not aggregate plan acceptance/formal TRL PASS,light extraction,or picture return.
Exact next action: sponsor review and authorize the next bounded round-trip
investigation; don't automatically implement lights/return or tune appearance.

Follow-up documentation-only execution2026-10-16: recorded the sponsor's explicit
normal-rendering/control confirmation above and in HANDOFF. No runtime, code,
configuration or evidence changes. Fuel Guard exact-thread hook attach attempted;
no daemon spawned. Validation: referenced current records read and git diff
--check passed. HEAD/index unchanged; inherited dirty work retained, nothing
staged/committed. Next action remains the bounded round-trip decision above.
