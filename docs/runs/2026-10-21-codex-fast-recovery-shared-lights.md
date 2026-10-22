# Run98 — remove serial camera-return handoffs

2026-10-21 America/New_York. Sponsor "go" after rejecting the offscreen-return
delay authorizes bounded efficiency work. Execution authority:authoritative
HANDOFF Run97,Run97 raw timing analysis,approved amended M1 plan and additive
execution plan,owner-rebind contract and camera-recovery probe. No formal gate
advancement. Fuel Guard attached with trusted recent-hook receipt;no daemon
spawned. HEAD `d29111f7a513c4510c4d33aeeda2c355d98443a5`,index empty,large existing
Run69–97dirty work preserved. No helper,agents,gameplay,stage,commit or push.

## Question and decisions

CONFIRMED Run97:first fresh returning owner→first producing offer365.061ms,
output381.399ms,first strict matched Present580.309ms. Source and implementation
show serial main-runner50ms polling,recovery100ms scan,light relay100ms scan and
file-reader10ms polling. These are opportunities,not individually measured
causal shares of580ms. Initial outputs also miss successive frame deadlines;
vendor compilation/workload cause remains unproven. No new executable RE or ABI
judgment required. Rejected stale pixel holds,retirement bypass,old-light replay,
weakened identity checks and repeating gameplay before offline improvement.

Implemented one bounded external recovery worker with interruptible2ms waits,
exclusive receiver-drain ownership and reuse of freshly validated decoded mesh
transfers. This is not a guaranteed500Hz service. Full captured content/image
signature still qualifies resident assets. Fresh native same-epoch lights are
staged BEFORE binding request;ACK doesn't trigger another serial file handoff.

Added default-off raw/encoded light cells in the previously unused lastMiB of
the existing16MiB current-user-only mapping. Native callback adds original QPC
to existing fixed queue;no disk/allocation/wait/Remix calls. Native worker
publishes raw first,then diagnostic files. Python converts to existing light
policy packet without refreshing capture timestamp. Renderer reads stable shared
packet at submit,not file/reader mutex. Existing5Hz/owner sampling,first fresh
epoch capture,context/checksum/age checks and original settings preserved.
The camera-recovery runner explicitly enables shared mode;legacy file path
remains available for historical workflows,not a game fallback.

Before expensive projection/GPU work and again after lighting,reject source
inputs no longer current/bad-frame or older than2ms. This discards obsolete work,
not exact-frame output qualification. No new30Hz cap,no stale output buffering.
Expired/old-epoch counts and shared-light receipt retained in run analysis.
Join recovery worker before storage release;failed join forbids unmapping its
storage and retains error. Normal original drawing remains ON.

## Exact files changed this run

- Native:`tools/m1_component/m1_light_transport.h`(new),
  `native_light_observer.h`,`m1_live_scene.h` in that directory.
- D3D9:`tools/d3d9_proof/light_transport.py`,`recovery_service.py`,
  `input_admission.h`(new);`direct_lights.h`,`live_owner_input.h`,
  `d3d9_direct_host.cpp`,`live_light_binding.py`,`light_fixture.py`,
  `build_frame_ingress.ps1`.
- Integration:`tools/remix_runtime/present_calibration.py`,
  `live_owner_timing.py`,`run_return_game.py`,`light_discovery.py`,
  `additive_qualification.py`.
- Tests:`tests/shared_light_transport_tests.cpp`,`test_fast_light_transport.py`,
  `test_recovery_service.py`(new);`d3d9_live_owner_tests.cpp`,
  `test_owner_recovery_relay.py`.
- Documentation:this record,`docs/HANDOFF.md`,
  `docs/reconnaissance/d3d9-owner-rebind-contract.md`,
  `docs/reconnaissance/probes/D3D9-CAMERA-RECOVERY-001.md`,
  [curated evidence](../reconnaissance/evidence/20261021-fast-recovery-offline.json).

No lighting/material/image/quality TOML,client binary,proxy forwarding,semantic
detour point or calling convention changed. Diagnostic geometry hook stays OFF.

## Reproduction and validation

Use bundled modern PowerShell/Python under the configured Codex runtime. From
repository root:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/build_direct64.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/m1_component/build_light_discovery.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/build_frame_ingress.ps1
python -m unittest discover -s tests -p 'test_*.py'
python tools/remix_runtime/light_discovery.py
python tools/remix_runtime/qualify_lifecycle_capture.py
python tools/remix_runtime/run_return_fixture.py --d3d9-additive --rebind-owner
python -c "import sys;sys.path.insert(0,'tools/remix_runtime');import additive_qualification as a;a.qualify('artifacts/remix-runtime/runs/20261021-112631-606560-return-fixture')"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/start_d3d9_camera_recovery_session.ps1 -CheckOnly
git diff --check
```

Actual invoked interpreter paths:Python
`C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`;
pwsh same dependency root `native\powershell\pwsh.exe`. Existing SDK/runtime,
driver,output dimensions and visual config frozen by fixture manifests/hash
qualification. No dependencies downloaded. Temp ACL-sensitive native/offline
tests ran with approved ordinary host access,not a sponsor UAC request.

- Final398Python regressions PASS,including actual Relay service ownership,
  ACK and immutable transfer reuse with disk re-decode forbidden.
- Native x86/x64:ingress142,owner/admission51,shared-light9,observer17checks
  each PASS. Direct64build,loaded-light11,deferred diagnostics and private-timer
  tests PASS. Dedicated x86light component build PASS.
- Actual native scene worker published owners1/2with original captureQPC into
  shared cells and marked stopped before unmap. Evidence:
  `artifacts/remix-runtime/native-light-tests/shared-6a72378e87874479b5bd30e8d93759ab`.
  Normal/tuning worker and lifecycle late-detail/transition/drain tests PASS.
- Transport tests cover malformed/torn/stopped/wrongPID/epoch/collision,not just
  a pointer write. Fresh-input tests cover old/future/time/frame/bad-frame.
- First build exposed const atomic-read and implicit padding /WX errors;fixed
  Header reference and explicit36byte raw padding,rebuilt PASS. Shared-worker
  qualifier initially unpacked `(raw,QPC)` backwards;test corrected,rerun PASS.
  Isolated relay test exposed implicit module-path dependence,now explicit;
  four isolated tests plus full suite PASS. None of these failures was promoted.
- Final PS5CheckOnly PASS,starts no game/renderer. Additive qualification now
  requires actual shared lighting receipt,admission policy and two owner rebinds.
  Parser/import coverage through suite and preflight;diff check PASS with existing
  LF/CRLF warnings only.

## Direct offline runtime evidence

Baseline fixture061525had two synthetic return transitions,first observation to
first exact matching Present66.1145/66.2475ms. Actual new ordinary-D3D9→pinned
Remix→shared GPU→x86receiver→real-proxy/D3D11consumer fixtures:

| Fixture suffix | owner12return | owner13return | fixed delivery window |
| --- | --- | --- | --- |
| 112219-768773 |33.1874ms|33.0968ms|594/600 |
| 112631-606560 |33.2385ms|32.7042ms|594/600 |

Method:parse stage1source records,first QPC for fresh epoch;join same-session,
same-PID status1current-frame presentation audit. Use source QPC frequency10MHz.
Final first/matched source frames200380/200381 and200560/200561. These are
software timestamps,NOT camera switch/photon latency. Synthetic fixture directly
requests bindings and replays lights;it does NOT independently time real game
fresh asset discovery or the new Python/native shared handoff. Separate actual
native-worker and recovery-service tests validate those paths. Real SFC
improvement is STRONG HYPOTHESIS pending next run,not CONFIRMED instant return.

Final782inputs,invalid0/unqualified0,599published/595drawn total,2stale,3light
omissions,780output transfers,ACK3/reject0,expired0/oldEpoch0. Status1audits597
are not identical to total game draw595;do not collapse these counters. Existing
gpu_busy595counter also retained;it is not595lost frames. State errors0,known
resize/recreation pass,source timing anomalies0,normal owned exit. Vendor40
common-device-object warning persists;no leak-free claim. No stale hold or
zero-loss claim. Offline preparation2.844s is NOT game initial-load performance.

## Bounds,archive,final state and next action

Existing90sformal/five-minute workflow,120ssemantic watchdog,32MiBevidence,
128MiBimages,20GBaggregate unchanged. Shared cells fit within existing16MiB.
Native queue8,raw cells32,encoded latest1,recovery assets8revisions,existing
64generation binding limit remain bounded. No continuous image dumps.

Both fixture generated inputs were hash-verified,compressed,and decompression
verified by `archive_fixture_binaries.ps1 -RunDirectory <exact fixture>` before
removing199generated copies each. Each82,188,024bytes became~6.862MB;recoverable
ZIPs under `artifacts/remix-runtime/archives/`,hashes in curated evidence. Raw
logs/source/control/asset packets retained. Aggregate artifacts11,942,283,735bytes
<20,000,000,000. Run97partial game evidence deliberately not cleaned/promoted.

Both original/test clients stillSHA256
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
No active game/owned renderer/receiver/native-test worker after tests;no bridge
session survives restart. HEAD unchanged,index empty,all prior/new edits
unstaged/uncommitted. No remote changes. Latest local receipts source-hash lock
current implementation;code/config changes require requalification.

READY for bounded sponsor camera-return test,NOT fixed-latency runtime PASS.
Initial~16.6s preparation,Run97controlled game unload and vendor warning remain
open. Do not blindly repeat old lighting/file delays,disable retirement,reuse
stale pixels,change appearance,expand to all ships or claim formal TRL.

Exact next action:sponsor runs existing camera-recovery launcher,keeps both
ships alive,switches enemy/own at HIGH cues twice,and waits for two LOW exit
beeps after restoration;then join first fresh-owner QPC to first actual matched
Present and adjudicate visible delay plus controlled unload.

## Sponsor evidence clarification — subsequent2026-10-21 discussion

Sponsor requests assumption labels rather than attributing our epoch changes
to SFC. Recorded in owner-rebind contract and authoritative HANDOFF:CONFIRMED
our observer's lifetime label changes;SFC persistent ship identity change is
NOT established. Working assumption is same SFC ship survives camera change.
Continued offscreen simulation/position updates are STRONG HYPOTHESIS,consistent
with sponsor's tracking-projectile/fighter observations,not direct offscreen
transform evidence. Continued same-path drawing is SPECULATIVE,not implied by
simulation. Observation gap cause remains unknown. No implementation/probe or
runtime changes. Reviewed current HANDOFF/record/contract;Fuel Guard recent-hook
receipt confirmed. Documentation diff validation PASS,index still empty,no commit.
