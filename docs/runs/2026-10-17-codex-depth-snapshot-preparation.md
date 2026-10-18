# Codex run — focused depth-content test preparation

Run SFC-RETURN-20261017-12,2026-10-17 EDT. Task: prepare the smallest read-only
test of Run11's depth candidate;no SFC/gameplay launch. Starting HEAD e96765a,
indexempty,existing tracked HANDOFF/controller edits and untracked runtime/docs/
tests from earlier approved work preserved. No staging,commit,helper or delegation.
FuelGuard actual-thread recent-hook attach confirmed,no daemon started.

## Authority / question / adjudication

Read HANDOFF operating convention,current approved M1 plan/disposition,Run11,
REMIX-RETURN-001,readiness map and actual capture/runner/native sources. Run11's
persistent1920x1080/8sample depth resource and DSV+SRV creation/binding observations
justify a narrow content test,not another full-rate trace. Ship-shaped values,
depth direction,coverage and safe suppression remain unknown.

CONFIRMED offline: private deferred compute reads an existing shader-readable
R32_TYPELESS/8sample resource through R32_FLOAT view,producing sample0/min/max/mean.
Never resolve MSAA depth as ordinary color or assume a single sample represents
all samples. Actual native DSV at original immediate draws selects resource;no
recorded pointer reused. Static depth-enable/write/compare+stencilRef combinations
are recorded with draw counts (up to16),NOT guessed from pipeline names.

No engine reverse engineering,owner suppression,camera/asset changes,new renderer,
Remix runtime,visual tuning or requirement changes. Existing0x004162B9 tactical
gate unchanged;diagnostic0x006AB410 geometry hook remains OFF.

## Implementation / reproducibility

New tools/remix_runtime/depth_snapshot.h: default-off,three preallocated CPU slots,
worker-only file writes;private deferred context restores original immediate
state via ExecuteCommandList TRUE. Compile once at effect-runtime init before
gate. Bound texture/query creation occurs only for first qualified snapshot.
No draw/Present file I/O,waits or polling loops. Present uses DONOTFLUSH query and
DO_NOT_WAIT Map then bounded memcpy (<16.6MB,three times);device recreation,
resource ambiguity,unsupported dimensions/formats,state overflow or >2s pending
GPU work disables capture,not game. Require source actually bound for a draw in
current frame. Native AddRef holds selected resource through test;new competing
resource is explicit ambiguity rather than guessed lifetime continuation.

Worker shutdown occurs during runtime destruction,outside loader lock;signals
stop and joins <=250ms. If writer remains stalled,keep CPU slots resident until
process exit;never hot unload. Synthetic normal teardown finished;forced disk
stall and actual-game device-loss behavior not independently runtime-proven.

New depth_snapshot_analysis.py validates wire/counts/finite/range/order/provenance,
renders diagnostic derivatives without overwriting raw. Raw full color retained;
display RGB ignores alpha only for screenshot readability (alpha range recorded),
nearest half-size color aligns with every-second-pixel depth. Each float-plane
display uses recorded observed min/max contrast,NOT linear distance/reversed-Z
interpretation. Uniform depth is not mistaken for ship-shaped content.

New qualify_depth_snapshots.py records native and actual callback positive/negative
qualification,source hashes and exact DLL. build_return_probe.ps1 links D3DCompiler
and /Brepro:two full rebuilds produced identical DLL SHA256
98E7B202A035A03B1F951EF62B343B306289DC45A63DF19D4BF8F3469DB5FCC0.
This avoids a routine sponsor rebuild invalidating qualified binary by timestamp.

Updated return_addon.cpp,return_fixture.cpp,run_return_game.py,run_return_fixture.py,
start_return_image_session.ps1,prepare_full_reshade.py,recover_broad_session.py,
archive_broad_evidence.py. New tests/depth_snapshot_gpu_tests.cpp and
test_depth_snapshot_analysis.py;updated CLI/archive tests. Recovery accepts
only verified broad/depth full-support transactions,after native game-absence
check;unknown edits/ambiguous pending transactions still fail closed. Archive
whitelists only depth-0/1/2 packets and their five named PNG derivatives,not DLLs
or arbitrary binary dumps. Probe definition written before GPU fixture use:
[REMIX-DEPTH-001](../reconnaissance/probes/REMIX-DEPTH-001.md).

Prepared command (only sponsor gameplay remains):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\remix_runtime\start_return_image_session.ps1" -DepthSnapshots
```

Existing elevated parent,PS5 forwards to bundled PS7.6.5,no routine UAC or global
policy change. Fixture instructions:two ships visible,hold first camera,small
rotation at next single cue(~5s),hold,two beeps exit normally(~20s). Snapshots
>=2/7/12s. Existing copied-process path/hash/readiness handshake and tactical
gate restored/unload checks remain. No SFC source-install writes.

Bounds:three fixedCPU slots49,766,400B;newGPU allocations<32MiB;images64MiB
warning32MiB;ancillary32MiB warning16MiB;96MiB run,total10GB archive-coexistence
admission;20s tactical,300s build+workflow. No continuous image capture or geometry
dump. Expected packets at1920x1080 total49,768,704B;not multi-GB-capable in this
three-slot mode. Old broad2GB mode remains separate,not selected.

## Validation / exact evidence

VS2026 v18.7.3,x86 C++20 /W4 /WX;native D3D11 hardware,driver617.42,RTX4070Ti.
Bundled Python3.12.14. SDK/full-support dependency unchanged and hash-pinned in
existing manifest. Relevant commands:

```text
tools/remix_runtime/build_return_probe.ps1
artifacts/remix-runtime/return-bin/depth_snapshot_gpu_tests.exe <new-run-directory>
python tools/remix_runtime/run_return_fixture.py --depth-snapshots --observation-only --graceful [--with-depth]
python tools/remix_runtime/run_return_fixture.py --broad-capture --observation-only --graceful [--with-depth]
python tools/remix_runtime/prepare_full_reshade.py --qualify <positive-broad> <negative-broad>
python tools/remix_runtime/qualify_depth_snapshots.py <positive-depth> <negative-depth> <native>
python tools/remix_runtime/run_return_game.py --depth-snapshots --observation-only
python -m unittest discover -s tests -p test_*.py
artifacts/m1/bin/m1_module_snapshot_tests.exe
git diff --check
```

`python` above is bundled dependency executable,not assumed PATH interpreter.
Test TEMP/TMP set to artifacts/test-temp. All fixture folders below under
artifacts/remix-runtime/runs/;original raw results preserved:

|Final fixture|Evidence|Result|
|---|---|---|
|Native GPU|20261017-depth-snapshot-gpu-03|3pairs,known uniform.625 then per-sample.1..8 => sample0/min/max/mean=.1/.1/.8/.45;original DSV/depth/stencil/viewport/compute binding restored|
|Actual callback positive|20261017-184531-014262-return-fixture|948frames,3pairs,zero state/GPU/I/O errors,normal exit|
|Actual callback negative|20261017-184615-737131-return-fixture|946frames,0pairs,zero state errors,normal exit;explicit incomplete content,not false success|
|Existing broad positive|20261017-184543-845477-return-fixture|588frames,zero state errors/drops,resize/recreation,normal exit|
|Existing broad negative|20261017-184628-025939-return-fixture|580frames,zero state errors/drops,resize/recreation,normal exit|

Positive content is KNOWN SYNTHETIC clear depth,not tactical geometry. Native
separate sample-frequency shader verifies all8samples with different values.
Python149tests PASS2.348s;native wire37/search13/broad14 checks PASS and controller
retry212PASS;PowerShell parser PASS;depth read-only preflight PASS. Wrong mode
combinations,malformed/truncated packets,nonfinite/out-of-range data,budget/count
violations and missing content covered. No game/runtime started by preflight.

Early build sandbox overwrite failure (LNK1114,error5) resolved via scoped external
build execution;compile /WX caught an enum narrowing conversion,fixed explicitly.
First full Python test attempt hit sandbox TEMP permissions,not code failures;
project TEMP/TMP rerun passed. Initial qualification command mistyped one output
folder and failed read-only;correct exact returned path used subsequently. Native
GPU01/02 and earlier actual callback/broad runs remain historical successful
development iterations,not substituted for final binary fixtures above.

Offline archive:artifacts/remix-runtime/archives/20261017-depth-snapshot-offline.zip,
322642B,51entries,15176794Bselected source,CRCverified,SHA256
4456B34EDD50EF67809E53EDEDF2A4E277BDF4A480975C2261D0BBAF5E5E8813.
Raw retained,not deleted;no source/reference originals modified.

## Current result / handoff

READY FOR SPONSOR RUNTIME TEST,not depth-content or replacement PASS. CONFIRMED
offline state/readback/format/callback behavior;STRONG HYPOTHESIS the known SFC
candidate contains usable ship depth. Actual pixels/camera/visibility unqualified.
Native SFC device-reference warning67 remains open;absence in synthetic fixture
does NOT resolve it. No active SFC/host/fixture or persistent session required.
Original/copied client SHA256 remains
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29;
copied baseline proxy remains
E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7.
Final HEAD e96765a,indexempty;all current changes unstaged/untracked,prior work
preserved. No commit. Next exact action:run prepared -DepthSnapshots fixture,
then compare paired depth/color before any original-ship suppression.
