# Run89 — one-ship worker efficiency;offline-qualified next game test

Local2026-10-20 America/New_York;UTC artifact folders20261021. M1 CONTINUES.
Sponsor approves optimizing one ship BEFORE expanding;during execution explicitly
raises aggregate output budget to20GB(decimal). Per-run image/log/time bounds are
unchanged. Read HANDOFF/Run88/approved additive execution authority. Fuel Guard
attached via trusted-hook receipt,no daemon. HEADd29111f7,index empty,existing dirty
work preserved. No SFC/helper/agents/stage/commit/push.

## Changes and safety

- Worker-only DeferredDiagnostics replaces per-insertion unitbuf file/pipe writes
  with preallocated append storage. Text is written at orderly teardown,not on the
  delivery path. Host stdout1MiB,live timing1MiB,frame timing2MiB,receiver2MiB:
 6MiB total. Saturation drops further bytes with a truncation marker;qualification
  rejects incomplete diagnostics. Critical errors still use stderr. A crash can
  lose buffered worker details;native SFC observation evidence remains separate.
  No logging thread,allocation during append or SFC callback I/O was added.
- Explicit /O2 /fp:precise for host and receiver,with inherited CL/_CL_ cleared
  ONLY in compiler child;build-policy.json records flags. -Optimization Off selects
  /Od for comparison. No fast-math or SFC hook/ABI build changes.
- Private WorkerPoll timer requests250microseconds for input availability and
  D3D9query checks. SFC_D3D9_POLL_US=0 retains Sleep(1) for OFFLINE comparisons;
  other values reject. No process-global timer change,unbounded spin,callback wait
  or unrelated D3D11fence substituted. Same actual D3D9completion query remains
  mandatory;existing5s completion bound,lease ACKs,exact identity checks and native
  D3D11fences retained. Windows high-resolution timer unavailable -> explicit failure,
  not silent unsafe completion. Observed actual waits exceed requested250us.
- Added bounded input-validation/poll/sleep/last-not-ready/ready timings to existing
  CSV and receiver copy-complete/pool-publication timestamps to deferred log. No
  protocol layout/version change. Validation time excludes inbox take/checksum.
  GPUwait still includes true work plus scheduling;not claimed isolated shader time.
- Shared evidence_budget.py now supplies20,000,000,000B to active D3D9/runtime
  guards and broad archive allowance. Per-run caps/resource dimensions unchanged.
  No budget reset,unbounded trace or cleanup requirement removed.
- Qualification requires250us policy,complete deferred diagnostics and existing
  image/state/fixed-window gates. Gameplay override to legacy polling rejects
  preflight. Source/binary/settings receipt refreshed ONLY after validation.

Current textures,roughness/emission,lights,image controls,AA/resolution and camera-
left diagnostic offset unchanged. No old-image hold,buffering,original suppression,
all-model expansion or architecture switch. Run86texture load improvement retained.

## Offline sequence / reproducibility

Bundled modern PowerShell/Python;VS2026 vcvars64/vcvars32,existing pinned Remix1.5.2
and full-event ReShade proxy. No external download or security-policy change.

```powershell
pwsh -NoProfile -File tools/d3d9_proof/build_direct64.ps1 -Optimization Off
pwsh -NoProfile -File tools/d3d9_proof/build_receiver.ps1 -Optimization Off
# Initial measurement used legacy Sleep(1),before WorkerPoll was added.
python tools/remix_runtime/run_return_fixture.py --d3d9-additive --graceful
pwsh -NoProfile -File tools/d3d9_proof/build_direct64.ps1
pwsh -NoProfile -File tools/d3d9_proof/build_receiver.ps1
$env:SFC_D3D9_POLL_US='0'
python tools/remix_runtime/run_return_fixture.py --d3d9-additive --graceful
$env:SFC_D3D9_POLL_US='250'
python tools/remix_runtime/run_return_fixture.py --d3d9-additive --graceful
python tools/remix_runtime/run_return_fixture.py --d3d9-additive --graceful
python -m unittest discover -s tests -p 'test_*.py'
python tools/remix_runtime/light_discovery.py
```

Initial /Od comparison retained buffers/timing but predated final pool-publication
log fields/private timer option. /O2legacy vs250us comparisons use identical final
binaries and current settings. These are short sequential comparisons,not controlled
GPU-clock/thermal benchmarks. Source rows cycle accepted distinct captured camera/
pose snapshots under synthetic16ms lead,NOT real SFC contention/user input timing.

All four folders under artifacts/remix-runtime/runs/:

| UTC fixture | Build/wait | Median / p95 / max ms | Fixed-window draws |
| --- | --- | --- | --- |
|20261021-033807-214685-return-fixture|/Od,Sleep(1)|10.004 /11.204 /13.568|599/600|
|20261021-034102-429000-return-fixture|/O2,Sleep(1)|9.921 /10.927 /13.503|599/600|
|20261021-034200-721375-return-fixture|/O2,private250us|8.485 /9.290 /13.595|598/600|
|20261021-034352-842284-return-fixture|/O2,private250us repeat|8.467 /9.486 /11.076|599/600|

End-to-end quantiles use first599nonbootstrap live-input rows. Display window is
independent600frames;do not equate sample counts or manufacture100% delivery.
Timing command:load csv.DictReader(gpu/live-input.csv)[:599],calculate
(completed_qpc-offered_qpc)*1000/frequency,np.quantile([.5,.95,1]). Match
frame-timing.csv[1:600] for query/input stage metrics.

Legacy final-query observation interval median~2.000ms,p95~2.014ms;private repeat
median.515ms,p95.547ms,max2.140ms. This brackets readiness detection,not measured
pure wasted time:GPU can be busy through part of it. Median query counts5->14;
more wakeups/query calls,not free CPU efficiency. No CPU utilization/energy gain
claim. /O2input validation median15->5us in sequential samples,not dominant work.
Median end-to-end margin improves~1.45ms vs optimized legacy. Worst-case did NOT
improve in first fine-poll sample;do not promise gameplay flicker eliminated.

All final fixtures:pixel change154820..155025,border untouched,graphics state
errors0,resize/recreation tested safe hide,normal fixture/host/job exit0,no owned
processes,source validation zero invalid/drop/wrong-thread. Offline replay lights
explicitly identified;actual live light sync not re-proved here. Vendor warning40
remains unresolved;do not claim leak-free shutdown. No diagnostic truncation.

Native:11loaded-light,29wire,18source-timing,31pool checks PASS;bounded deferred-log
tests x86/x64 and private-timer lifecycle/legacy/malformed options PASS. Full372
Python tests PASS;Pillow getdata deprecation warnings remain. Native light discovery
queue/decoder qualification refreshed and PASS. Final additive receipt refreshed
against034352fixture;start_d3d9_offset_ship_session.ps1 -CheckOnly PASS,no launch.

## Storage,failed preparation attempts and repository state

Before sponsor budget increase a fixture attempt was blocked by192MiB/10GB reserve.
An attempted archival of historical214708partial was correctly rejected for missing
owned-job completion;no evidence removed. Compacted an eligible completed private
fixture instead:20261019-022538-965332-live-private/textures,274entries,61,712,858B
generated copies ->5,208,887B ZIP,decompressed hashes verified. Archive SHA256
3CBC074FA45B5B5DF8D1BE0FD0658E1172CB3B60B65E1FBBE744B712E46C85C5.
Original files/source provenance untouched;removed copies recoverable.

After analysis each new fixture's199generated inputs/copied binaries compacted
82,187,000B ->~6,859,955B ZIP under artifacts/remix-runtime/archives/,exact receipt
in binary-archive.json. Logs,timing CSV,source rows,manifests/results retained.
Aggregate9,778,503,054B/20,000,000,000B after compaction. No source/client assets
deleted;all removed generated copies recoverable. New budget not used to retain
unnecessary bulk. Latest archive source qualification remains valid after compaction.

Both accepted/copied StarFleetOP.exe hashes unchanged:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Files:worker_poll.h,deferred_diagnostics.h,live_owner_input.h,d3d9_direct_host.cpp,
output_receiver.cpp,build_direct64.ps1,build_receiver.ps1,new native timer/log tests;
evidence_budget.py and test_evidence_budget.py,aggregate guard imports/errors in
run_offline/run_direct64/run_intercept/probe_bridge_api/profile_preparation/
qualify_material_binding/run_return_fixture/run_return_game/qualify_live_owner/
broad_capture/archive_broad_evidence;additive_qualification.py,README,this record,
curated receipt,contract/probe notes and HANDOFF. Existing unrelated dirt retained.
Index empty,all changes unstaged/uncommitted,no commit/push. No active owned runtime.

## Sponsor test / exact next action

READY FOR ONE-SHIP SPONSOR TEST,not steady-delivery PASS. Use SAME known Federation
cruiser fixture;extra textured ship remains left of original. Enter two-ship skirmish,
observe a stationary camera briefly,then normal movement and a few brief fast camera
changes while player ship remains visible. Report flicker and initial appearance
delay;no timestamps/manual analysis needed. Exit normally at runner cue,90s tactical
window unchanged. Established elevated parent,normal launcher,no rebuild/UAC request.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_offset_ship_session.ps1"
```

Next exact action:sponsor runs that one-ship fixture;Codex joins new pool-readiness/
ACK/poll timings to adjudicate actual camera delivery. Do not expand to all models
until single-ship result is satisfactory. No formal TRL or replacement claim.
