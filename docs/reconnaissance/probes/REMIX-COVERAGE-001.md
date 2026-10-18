# REMIX-COVERAGE-001 — standalone runtime depth/owner output qualification

## 2026-10-17 native-depth conversion replay extension (Run20)

Result:[Run20](../../runs/2026-10-17-codex-native-depth-conversion.md) demonstrates
all3corrected actual-runtime replays,maskIoU1.0,Zerror<4.33e-7. Uncorrected
control has same mask but.01237Zerror. No SFC launch or original suppression.

Before new standalone use:reuse the SAME pinned native host/binary/96frames and
output limits below. No C++/SDK interface/game/observer change. New runner
--calibration-run <exact-run> --snapshot0..2 --owner2 selects independently
verified semantic sidecar and fresh same-session rigid mesh. Phase5uses original
model/camera without fit. --native-depth sets SDKnear=b/a,far=b/(a+1),derived from
native P coefficients;reference is ALWAYS nativeZ for these inputs,even when
--native-depth is deliberately omitted for a negative control. FOV/XY/pose/assets
unchanged. No depth fitted to pixels. Old default historical workflow preserved.

Execute three corrected pose replays plus one same-pose uncorrected control.
Each owned host <=120s/32MiB,warning16MiB,four256square GPU outputs<=1MiB,
18retained planes~4.5MiB;four-run ceiling128MiB under existing10GB. No continuous
screenshots. Scene/staging/output ownership,synchronization and cleanup below
unchanged. SDK40-object teardown warning remains an open issue,not cleared by
normal process exit. Only owned fixture process may be terminated on failure.

```text
python tools/remix_runtime/run_coverage_probe.py --execute --calibration-run artifacts/remix-runtime/runs/20261018-025737-262069-in-game --snapshot 0 --owner 2 --native-depth
```

Repeat snapshots1/2;negativecontrol uses snapshot0WITHOUT --native-depth. Expected
negative result is PARTIAL for camera-depth criterion,with successful output/ID/
transfer tests and unchanged coverage. Positive requires actual runtime maskIoU
>=.95 and median nativeZ error<1e-5,not merely CPU equation or API success. Native
SFC and256square SDK grids differ:do not call this exact same-pixel/MSAA equality.
Run19 already provides paired native-depth comparison. No sponsor gameplay needed.

Status: standalone outputs and historical camera replay demonstrated. Final
200529-953300-coverage,96frames,no SFC launch. See Run16 and
remix-depth-coverage-contract.md for exact proven scope and remaining gap.
Question:does pinned Remix output-copy provide fresh,interpretable depth and
owner coverage,including a real captured ship,without guessing alpha from black?
This does not establish frame matching to Run15:its depth capture has no paired
semantic asset/camera record. Never borrow camera/owner pointers from another run.

Use existing pinned Remix1.5.2 x64/SDK0.6.4,header/runtime hashes in dependencies
manifest,VS2026x64 C++20 /W4 /WX. New `coverage` mode of standalone output probe,
existing process-local NRC/DLSS/RR OFF,synchronous shader compilation. No Toolkit,
game files,API interception,driver/configuration change or runtime patch.

Before launch prepare immutable geometry-only derivative from historical fresh
SFC packet+same-run resource associations using existing decode_mesh validation.
Preserve source positions/corner normals/UVs. Duplicate corners for SDK vertices;
explicit uniform instance fit/centering ONLY,not geometry repair or rotation.
Default opaque diagnostic material;original image/material roles not validated by
this experiment. Source packet/reference hashes and group assignments retained.

Native host64 uses three256x256 outputs:colorBGRA8,depthR32F,pickingR32F plus
three CPU readback surfaces. After private-output discovery,qualify native GPU
sharing:an owned explicit10_1 D3D11 consumer allocates the three shared surfaces,
Remix imports them through public D3D9Ex CreateTexture. GPU EVENT completes
before native CopyResource/readback;all bytes must match independent Remix
readback. No CPU pixels are written back to GPU. Three extra staging surfaces
keep total diagnostic readback below2MiB. This is standalone same-user sharing,
not yet cross-process ship integration. A fourth owned R32_UINT target verifies
explicit10_1 shader-side `asuint(Texture2D<float>.Load)` preserves every picking
bit (small IDs are subnormal float bit patterns,not float-valued IDs). Native
vs_4_1/ps_4_1 draws only into that target;compare all pixels after GPU readback.
No game shader/pipeline modified. Four output allocations<=1MiB;seven CPU
staging/readback allocations<2MiB. Decoder shader created once before samples.
Test whether public picking copy preserves uint
bits or numerically converts IDs;neither interpretation assumed. First picking
call only primes retention and is not valid output. Explicit background depth
-1234 and picking0 requested;observed clear values must be checked. Every image
copy completed with owned D3D9 EVENT query<=5s before bounded readback. API
returnSUCCESS alone not accepted as fresh image/coverage evidence.

Six deterministic pose windows:two known triangle owners7/11 at viewZ6/9;
move7toZ8;retire7;reappear with NEW owner13;replace control scene by captured ship
owner23;then replay that asset's historical native model/camera observation as
owner29 without fitting. Rigid asset frame4/revision2 is matched to pose/camera
frame5 by same epoch/model/source/revision,NOT claimed as same-frame geometry
snapshot or deformation support. Historical packet/reference/update file hashes+frame/
epoch/revision recorded. Existing camera_state validates native composition;
SDK parameterized left-handed basis uses inverse-view position/right/up and
negative native forward. Reject off-axis projection rather than guess offsets.
Independent CPU projection/rasterization of native composed matrix compares
coverage/depth with replay. This is NOT contemporaneous SFC GPU calibration.
Render16frames per window and retain ONLY final color/depth/picking
triplet:18files,~4.5MiB. No continuous screenshots. Static control projection known70deg
verticalFOV/aspect1,near.1/far100,explicit triangle coordinates. Offline analysis
compares candidate depth interpretations (viewZ,ray distance,normalized depth)
and owner changes/background. Failures produce PARTIAL,not substitute coverage.

Bounds:<=96rendered frames,4output GPU surfaces<=1MiB,readback<2MiB,one source
geometry<=2MiB,32MiB output/warn16MiB,120s owned workflow. Existing10GB aggregate
output allowance checked first. Runner owns only its child;timeout terminates
owned probe,never SFC. Logs/evidence in artifacts/remix-runtime/runs/<UTC>-coverage.
No UAC expected;normal standalone user process. SDK mesh retirement queued then
GPU drain before normal shutdown;existing runtime40-reference/driver risks remain
open unless directly disproven. Preserve failed logs.

Build:build_output_probe.ps1. Execute:run_coverage_probe.py --execute.
Preparation/analysis is default read-only-to-game;only ignored generated files
written. No new network dependency. Native stdout names API/HRESULT stages,
retained images include phase/frame provenance;manifest records source hashes,
DLL/header/executable hashes and exact limits. Analyze then CRC-verified archive;
no auto raw deletion. Cleanup closes owned window/resources;no DLLs placed in game.
