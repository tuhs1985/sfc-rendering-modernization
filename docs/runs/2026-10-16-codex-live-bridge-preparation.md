# Codex run — live ship bridge implementation and offline validation

Run ID/date: 2026-10-16-live-bridge-preparation / 2026-10-16.
Authority: sponsor explicitly approved/ordered implementation of Live Bridge plan.
Task: bounded separate real-time ship viewer, not rendering replacement or M1/M2
gate advancement. No requirements/default material/normal/winding/UV changes.
Starting HEAD fee152f137a55a3efeb47a5c236ebf9e3e1951cb,181 inherited short-status
entries/index empty. All inherited work preserved; no helper/subagent invoked.

## Baseline and evidence used

Read HANDOFF newest material/eligibility checkpoints, handoff operating convention,
approved M1 plan current disposition, MATH-001/transform qualification, single-ship
export contract, latest texture-path run/JSON, accepted imported preview and its
packet/group/image provenance, source of existing hook/config/export/viewer/guard.
Confirmed selected latest capture20261016-171830-enabled and accepted job
C:/Project/RemixJobs/20261016-050350Z-6dffd5be remain original evidence, not new
live runtime proof. Do not join across processes by pointer/resource-ID equality.

Narrow static extension: ship vtable00796F0C+6C=00419DD2, caller00416318 with0,
00416323 hands result to manager+E4. Getter constructs ship+9C4 from ship state,
returns it;006AA550 copies into+6F4 before composing+6B0. Existing scalar map
confirmed row arithmetic, not a standard graphics4x4. Added six in-memory anchors
to existing verify_m1_c01_shading_bytes.ANCHORS for this check ONLY:
00796F78 D29D4100;00416318 FF506C;00419DDC 8DABC4090000;
00419E3C E8FF2A2800;0069C940 D9442404;006AA57C E86F15FFFF.
verify(installed_client) reports48 STATIC_PREFIXES_MATCH with unchanged exact SHA.
Supplied transform's camera-independent world interpretation remains STRONG
HYPOTHESIS until runtime motion/camera corroboration; no decompiler-only promotion.

## Implementation decisions

Default-off LiveChannel config, strict UUID/user-only2MiB mapping. Existing hook/
stub ABI/state-preservation untouched; no new hook, engine calls, writes to game
assets or image capture. Live observer runs before existing one-shot export budget
exit, so remains active after detailed-event saturation. Guarded/rechecked fixed
transform records <=30Hz, nonwaiting mailbox, worker-only IPC/files. Two immutable
asset epochs; fresh452poly kff mesh/refs captured once/epoch and checked against
accepted mesh/group/image content. Worker summaries distinguish dropped/invalid/
asset-rejection counts; saturation/logging failure never backpressures renderer.
Worker drained/joined before unmap; timeout returns failed stop/no unload.

Receiver uses explicit row-to-USD transpose and per-epoch translation origin;
applies anonymous-session parent op at World BELOW existing uniform100 import
scale (root placement would scale translation incorrectly). Proper-rigid checks,
sequence/asset/epoch validation,1s stale hide, retirement hide/fresh qualification,
manual Frame ship, no continuous tracking. Provisional materials/lights unchanged.
No live stage save, asset reimport or game-camera extraction. Native pointers remain
opaque labels. Unsupported model/LOD/additional epochs -> hidden/PARTIAL.

Runner prewarms real Toolkit, then existing validated elevated-parent/game workflow.
No new UAC/RunAs/security relaxation. Default offline guard180s unchanged; guard
maximum increased to approved300s for explicit live mode. Build precedes timed
workflow; viewer startup180s but game only launches if ready within45s, preserving
255s for discovery30/gate90/capture90/exit30 and overhead. Deadline safe-parks
pending game/controller cleanup; never kills SFC with potentially live hooks.
Exact wire/capture/cleanup: LIVE-BRIDGE-001 and live-bridge-contract.md.

## Validation and evidence

Tools: VS2026 Community18.7.3/MSVC14.51 x86 C++17, bundled PowerShell7.6.5,
Python3.12.14/Pillow12.3.0, installed Toolkit1.6.0-dev+main.30229.3f23f80a.gl.
PYTHONDONTWRITEBYTECODE=1,TEMP/TMP=artifacts/m1/test-temp. Material commands:

```
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/m1_component/build_m1_component.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/remix_ingest/build_remix_job.ps1
python -m unittest discover -s tests -p test_*.py
python -m unittest discover -s tools/remix_ingest -p test_*.py
pwsh -NoProfile -ExecutionPolicy Bypass -File tests/test_mesh_export_workflow.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File tests/test_texture_export_workflow.ps1
python tools/remix_ingest/run_live_bridge.py --replay
git diff --check
```

Full native compile/tests/exports PASS; new live test executable is run by Python
actual-Windows-channel test (not standalone without creator).89 project/41 preview
Python tests PASS. New tests exercise x86 worker vs64-bit reader, user-only ACL,
nonwaiting busy mailbox,34ms throttle, nonfinite drop, worker join/close, config
exclusivity, torn/malformed/session/bounds, stale/retirement/pointer reuse, content/
group/hash mismatch and explicit affine rotation/translation/origin. Existing
mesh/texture policy checks PASS; four modified/new PowerShell parser checks PASS;
diff check PASS. Actual game hook restoration/runtime overhead remain untested0.18.

Initial test exposed restricted sandbox token cannot reopen user-only DACL mapping;
same tests outside sandbox PASS, ACL NOT broadened. Initial missing-file assertion
corrected to accept OSError (expected safe refusal). One premature test invocation
preceded native executable build; final suites ran after completed build.
First viewer attempt af222acf418240b0b80bb1cf0449938b failed before Kit because
existing guard capped180s. Corrected guard to approved300s, rebuilt; preserved
failure evidence, no game launched. Subsequent three replays clean, latest:

- Session4bfe9802556847aeb26b632db142468b, preview
  C:/Project/RemixJobs/preview-20261016-215005Z-9fe8ab91.
- Supervisor16.968s, owned Kit job16.328s/exit0/stop_reason0/zero remaining processes.
-119 accepted updates,0 rejected,0 asset failures,2 qualified fresh display epochs,
  1 hide transition. Synthetic translation/rotation then retirement and fresh epoch
  with same model/source pointer labels; every applied matrix readback matched.
-24544-byte native console,2481786-byte peak scratch/no warning. No per-frame
  screenshots, image dumps or real SFC runtime. Proves connection/authoring only,
  not GPU pixel fidelity, gameplay stability or camera independence.

Archive artifacts/remix-ingest/evidence/20261016-live-bridge-offline.zip:
42 files/65437bytes, SHA256
F3023476F3633F5BFDE6B51EB0D1B2568D15A7080C277860E31834A73E5EF035.
Every entry SHA verified against originals; contains all supervisor attempt logs
and useful final-preview top-level inputs/reports/code, excludes caches. Existing
image archives/assets remain untouched; no raw/cache deletion.

Final prepared0.18 component SHA256
3B1449242BB382D6B024D1420FD5FA033F1EB74C893B871313D940D81E1404B0;
proxy C6AF932F935742FF5DAAA7B6B907089A154D89A754AB05F80AEB2162AFBF24F4.
Entrypoint rebuilds; eventual runtime metadata must record actual rebuilt hashes,
not assume those timestamps/binaries survive. Installed client rechecked unchanged:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.

## Files and final state

New: tools/m1_component/m1_live_bridge.h,start_live_bridge_session.ps1;
tests/m1_live_bridge_tests.cpp; tools/remix_ingest/live_bridge.py,
kit_live_bridge.py,run_live_bridge.py,test_live_bridge.py;
docs/reconnaissance/probes/LIVE-BRIDGE-001.md,live-bridge-contract.md; this record.
Modified: m1_component.cpp,build_m1_component.ps1,run_m1_increment_a.ps1,
start_m1_enabled_session.ps1; tests/m1_mesh_component_tests.cpp;
tools/remix_ingest/run_mesh_preview.py,kit_mesh_preview.py,bounded_job.cpp,README.md;
docs/HANDOFF.md. Existing inherited contents retained, no unrelated cleanup.

Result: READY FOR SPONSOR RUNTIME TEST, integration/runtime still UNPROVEN.
No active SFC/controller/owned Kit/session/server; channel handles closed; no
helper or new daemon. Fuel Guard exact-thread hook verified; direct sandbox
connection denied/quota health unknown. HEAD unchanged/index empty, nothing
staged/committed; final188 short-status paths. Sponsor gameplay is only remaining dependency; no manual RE,
timestamps, admin dialogs or new installation required.

Next exact action: run prepared start_live_bridge_session.ps1 from existing
elevated parent; enter normal skirmish within90s of game detection, observe live
selected Klingon ship and camera-independence, exit normally at two exit cues.
Adjudicate new evidence/cleanup/hashes before any success claim or commit.

Final entry review avoids passing an empty LiveChannel value from Windows
PowerShell5 to native PS7: optional arguments added only when set. Four scripts
reparsed and diff check rerun PASS after that correction. No actual game launched
to test the entry; fresh gameplay/runner result remains an explicit dependency.
