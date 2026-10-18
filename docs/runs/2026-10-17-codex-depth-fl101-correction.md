# Codex run — correct depth reader for SFC feature mode

Run SFC-RETURN-20261017-14,2026-10-17 EDT. Sponsor authorized correction after
Run13's no-image failure. Scope:offline-qualify bounded10_1-compatible extraction
and prepare same sponsor test;NO SFC launch,renderer replacement or suppression.
Starting HEAD e96765a,indexempty,prior tracked HANDOFF/controller changes and
untracked runtime/tool/evidence work preserved. FuelGuard actual-thread hook
receipt confirmed;no daemon/helper/delegation/staging/commit.

## Authority / evidence / decisions

Read HANDOFF,approved M1 plan/current disposition,Run13,REMIX-DEPTH-001,current
native source,fixture,analyzer/qualifiers. Actual SFC log feature level0xA100
(10_1),old reader cs_5_0,and0files/one generic GPU failure are starting evidence.
Confirmed compatibility defect does not invalidate previous depth discovery or
prove unusable depth. Old exact runtime API/HRESULT was not recorded.

Replace only extraction stage:vs_4_1 full-screen triangle +ps_4_1 explicit
Texture2DMS<float,8>.Load into an owned float4 render target. Keep private
deferred context,ExecuteCommandList(TRUE),three fixed snapshots,nonblocking
readback,worker I/O,current-frame source qualification and original device
unchanged. Set private viewport,cull-none/scissor-off,depth-disabled state;
no original game output attached. No ComputeShader/UAV now required. Native
pixel-resource and vertex/pixel-shader preservation assertions added.

CONFIRMED offline at explicitly requested10_1:old SM5 shader creation returns
E_INVALIDARG0x80070057(decimal2147942487);corrected reader captures all8samples.
Sample-frequency shader with XY gradient verifies every output pixel:
source pixel(2x,2y),base=.1015+.002x+.004y;
sample0=min=base,max=base+.56,mean=base+.28. First snapshot uniform.625.
Tests cover all32x24positions,not one constant pixel. This reproduces the
incompatibility independently;actual old SFC failure call remains STRONG HYPOTHESIS.

Status gains actual feature level,reader ID,first stage/HRESULT and source/color
descriptors. Analyzer names stages and formats HRESULT;unchanged wire v1 packet
and raw-provenance rules. Qualifier requires exact10_1 andps_4_1,not merely newer
hardware success. Negative missing-depth fixture must have zero GPU/I/O errors,
not hide initialization failure behind0images. Runtime workflow's exit cue
explicitly distinguishes capture-window completion from post-exit validation;
future partial message includes images/stage/HRESULT/feature level.

Rejected alternatives:forcing game feature11_0,changing translator/wrappers,
altering original install,raising capture volume,redoing broad renderer RE,
GPU screenshots continuously,ship suppression,or claiming milestone completion.

## Files / reproduction / capture definition

Modified tools/remix_runtime/depth_snapshot.h,depth_snapshot_analysis.py,
qualify_depth_snapshots.py,return_fixture.cpp,run_return_game.py;
tests/depth_snapshot_gpu_tests.cpp,test_depth_snapshot_analysis.py;
REMIX-DEPTH-001,readiness,HANDOFF;new this record and curated qualification JSON.
Dependency qualification JSON/binaries/run outputs generated only under ignored
artifacts/remix-runtime. build_return_probe.ps1 recipe unchanged in this run;
existing /Brepro verified by two rebuilds yielding identical DLL
5B32A337865F5D92BB7D00AF8E059597C1B48B125166585D8BB60B8663596F02.

Probe [REMIX-DEPTH-001](../reconnaissance/probes/REMIX-DEPTH-001.md) updated before
new fixture use. Existing ReShade6.7.1 full-support/SDK pins unchanged. VS2026
18.7.3 x86 C++20 /W4 /WX,Windows D3D11 hardware (RTX4070Ti,driver617.42),bundled
Python3.12.14. Native fixture restricts device feature to10_1;actual callback
fixture logs `DEPTH_FEATURE_LEVEL 41216` and ReShade `feature level a100`.

Commands (python means bundled dependency executable):

```text
tools/remix_runtime/build_return_probe.ps1
artifacts/remix-runtime/return-bin/depth_snapshot_gpu_tests.exe <new-native-dir>
python tools/remix_runtime/run_return_fixture.py --depth-snapshots --observation-only --graceful [--with-depth]
python tools/remix_runtime/run_return_fixture.py --broad-capture --observation-only --graceful [--with-depth]
python tools/remix_runtime/prepare_full_reshade.py --qualify <positive-broad> <negative-broad>
python tools/remix_runtime/qualify_depth_snapshots.py <positive-depth> <negative-depth> <native>
python tools/remix_runtime/run_return_game.py --depth-snapshots --observation-only
python -m unittest discover -s tests -p test_*.py
artifacts/m1/bin/m1_module_snapshot_tests.exe
git diff --check
```

Project artifacts/test-temp used for TEMP/TMP. Build/graphics fixtures used scoped
external execution where needed for generated-file/graphics access;not assumed
an elevated admin token,no global UAC/policy change. Existing sponsor-elevated
parent remains runner requirement. No game launched by these commands.

Limits unchanged:3pairs at>=2/7/12s,20s tactical/300s prepared,CPU49,766,400B,
GPU<32MiB new allocations,64MiB raw+derived images warning32MiB,32MiB ancillary
warning16MiB,96MiB run/10GB overall archive-coexistence envelope. No multi-GB-capable
output in this three-slot mode. Existing diagnostic geometry hook OFF.

## Final offline evidence / validation

Folders under artifacts/remix-runtime/runs:

|Fixture|Evidence|Result|
|---|---|---|
|Native10_1|20261017-depth-snapshot-fl101-02|3pairs,all8sample+XY values correct,old SM5 rejected0x80070057,state restored|
|Depth callback positive10_1|20261017-185839-279602-return-fixture|948frames,3pairs,0state/GPU/I/O errors,normal exit|
|Depth callback negative10_1|20261017-185928-419893-return-fixture|947frames,0images,0state/GPU/I/O errors,normal exit|
|Broad positive regression|20261017-185851-711003-return-fixture|588frames,0state errors/drops,resize/recreation,normal exit|
|Broad negative regression|20261017-190000-950730-return-fixture|583frames,0state errors/drops,resize/recreation,normal exit|

152Python tests PASS2.354s,including rejecting missing/higher-mode/old-reader
qualifications and naming HRESULT/stage;native37wire+13search+14bounded-trace
checks PASS;existing controller212PASS. Strict native build and current-source/
binary qualification/read-only preflight PASS. Original/copy client hashes and
copied proxy hash remain frozen. No game/host/fixture process left active.

Archive artifacts/remix-runtime/archives/20261017-depth-fl101-offline.zip:
328919B,52entries,15182791Bsource,CRCverified,SHA256
66F6079B7360B615B78D6539F6C470DD842E49A32FB52A8E29D822E497A8F24D.
Small raw retained,no deletion. Native fl101-01 remains historical uniform
development evidence;final fl101-02 gradient test is used for qualification.

## Result / remaining uncertainty / next action

READY FOR SPONSOR RUNTIME RETRY. CONFIRMED exact-mode offline correction and
state/readback/callback operation,NOT actual SFC depth silhouettes/coverage or
ship replacement. Native SFC device-reference warning67 remains unresolved;
synthetic warning-free teardown does not resolve it. No requirements/gate change.
Final HEAD e96765a,indexempty,prior/current changes unstaged/untracked,no commit.
No live session state needed;qualifications persist and reject stale sources.

Exact next action:established elevated parent runs existing prepared
start_return_image_session.ps1 -DepthSnapshots. Same two-ship fixture,hold
camera at first beep,small rotation at next single beep,hold,two beeps request
normal exit. No visual change expected. Analyze paired depth/color before any
suppression/replacement. Do not repeat broad capture or force game device settings.
