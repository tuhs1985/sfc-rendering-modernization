# REMIX-DEPTH-001 — paired depth-content check

Status: actual tactical depth-content observation DEMONSTRATED in
20261017-190353-769314-in-game:3pairs,zero GPU/I/O errors,ship silhouette+grid
matching paired color/camera change,normal sponsor behavior and cleanup/hash
checks. See [Run15](../../runs/2026-10-17-codex-depth-content-runtime-review.md).
Native reference warning67,complete coverage and safe suppression remain unresolved.
Actual185115-506823-in-game saved0images/issued0,one generic GPU failure;
normal exit/rollback/hashes passed. Device feature level10_1 conflicts with
probe cs_5_0. Higher-feature offline fixtures did not qualify this mode.
See [Run13](../../runs/2026-10-17-codex-depth-snapshot-runtime-review.md).
The cs_5_0 mechanism was historical and failed before producing images. Revised
reader uses vs_4_1/ps_4_1 on the unchanged game device. Status now records actual
feature level,failure stage and HRESULT. Old raw evidence remains unchanged.
Question: does the live D32_FLOAT/8sample candidate contain ship-shaped depth
matching the displayed tactical view? Static depth state is sampled at original
draws. Binding alone and a recognizable picture do not establish safe suppression.

Uses existing isolated copied installation, pinned full-support ReShade6.7.1.2131
(SHA256 A1BA732B5E31E0405CDE322CC5EC62CF972B3FBAEFBB6CBDC8A24DA00D58AE24),
matching SDK/API18, VS2026 x86 C++20 /W4 /WX, D3D11/D3DCompiler and bundled
Python3.12. No Remix renderer, geometry hook, owner suppression or original-install
writes. Existing REMIX-RETURN-001 process-path/hash/gate/rollback discipline applies.

## Mechanism and limits

Default-off SFC_REMIX_DEPTH_OUTPUT explicitly names a new run directory.
Before tactical capture allocate three fixed CPU slots (49,766,400B total), start
writer; shader compiles at runtime initialization, not on a drawing callback.
At original immediate-context draw notifications, query actual bound native DSV
and depth-state descriptor. Qualify only R32_TYPELESS, one mip/layer,8samples,
shader-readable+depth binding, <=1920x1080. Multiple matching native surfaces are
ambiguous: disable rather than guess. Retain one resource until runtime teardown;
no persisted pointer used across runs. No semantic-owner identity inferred here.

At pre-effects Present, request at most three snapshots, >=2/7/12s after automatic
tactical gate. Require candidate observed drawing in the same frame. A private
deferred graphics context draws a triangle ONLY into an owned float4 target,
using vs_4_1/ps_4_1,depth disabled,cull-none and scissor disabled. No original game
output target is attached. The pixel shader samples all8samples at every second source pixel;
save sample0/min/max/mean separately as float4. Not a single-sample resolve or
linearized distance. Nonfinite/range violations must remain visible to analysis.
GPU command execution restores original immediate state (RestoreContextState TRUE).
Copy the same Present backbuffer (BGRA/RGBA8, single sample,matching dimensions)
for comparison; no image replacement. No continuous screenshot stream.

GPU event polling uses DONOTFLUSH; staging Map uses DO_NOT_WAIT on subsequent
Present. No sleep/wait/file I/O in drawing or Present. A pending GPU snapshot
times out at2s and disables the probe. Readback memcpy is bounded (~16.6MB once
per snapshot); file writes and analysis run elsewhere. GPU allocations <=32MiB
at1920x1080,excluding retained existing game resource. CPU slots <48MiB.
Three image packets <=49,768,704B; image budget64MiB (warning32MiB), ancillary
logs32MiB (warning16MiB); whole run96MiB. Overall10GB archive-coexistence rule
remains.20s tactical check,300s build+workflow. Unsupported dimensions/formats,
device recreation,ambiguity,unfinished query or I/O failure => PARTIAL,never fallback
to guessed depth. Up to16 observed static state/reference combinations; overflow
disables. Draw counts describe sampled native state,not proven ship pixels.

Normal runtime destruction disables capture,releases retained GPU objects and
signals writer,joins <=250ms outside loader lock. A stalled writer retains fixed
CPU storage until process exit; no hot unload. Proxy/config restore ONLY after
game exit. Never kill game for cleanup; deferred recovery uses verified transaction.
Native ReShade device-reference warning67 remains unresolved; do not hide it.

### Compatibility correction — 2026-10-17

See [Run14](../../runs/2026-10-17-codex-depth-fl101-correction.md).
Native test and snapshot fixtures explicitly request ONLY feature level10_1;
no fallback to a higher mode. Known per-sample AND spatial gradient verifies
sample0/min/max/mean,XY orientation and stride. Original cs_5_0 creation is
independently reproduced failing HRESULT0x80070057 on10_1;actual old SFC call
remains unlogged. Revised extraction is vs_4_1/ps_4_1 with no compute/UAV use.
Both shader objects and private fixed states are created before tactical capture.
Original device/translator settings are not changed. Qualified DLL SHA256
5B32A337865F5D92BB7D00AF8E059597C1B48B125166585D8BB60B8663596F02.
Stage enum in depth_snapshot.h and analyzer STAGES decode failures;status records
reader,feature_level,failure_stage/failure_hresult and source/color descriptors.
An incomplete final message now includes stage/HRESULT;exit cue says capture
window finished and validation follows,NOT premature test success.
Limits,three captures,automatic gate,sponsor procedure and cleanup unchanged.

## Output and analysis

artifacts/remix-runtime/runs/<UTC>-in-game: depth-0/1/2.bin,depth-status.json,
usual manifest/result/gate/logs. Each packet: little-endian 768B header (32uint64
fields +16rows of4uint64 native depth states), float4 depth grid, packed color.
Fields: magic0x44535031,version1,headerBytes768,depthWidth/Height,colorWidth/Height,
sourceWidth/Height,samples8,pixelStep2,QPC,PresentFrame,resourceEpoch,depthBytes,
colorBytes,DXGI color format,stateCount; remaining fields reserved0.
Rows: depthEnable|(writeMask<<8)|(stencilEnable<<16),compareFunc,stencilRef,drawCount.
Frame/QPC refer to GPU command submission,not wall-clock screenshot or owner ID.

Offline analyzer validates sizes/counts/finite ranges,produces bounded PNG depth
visualizations and paired color,records raw hashes. Inspect silhouettes against
color at identical capture. No automatic claim of tactical coverage,depth direction,
distance linearity,HUD ownership or safe replacement. Preserve raw packets and
archive after analysis; cleanup only exact reviewed generated outputs,never source.

## Qualification and sponsor procedure

Build: tools/remix_runtime/build_return_probe.ps1. Native
depth_snapshot_gpu_tests.exe <new-output-dir> uses only synthetic D3D11 textures,
no game/Remix. Validates all8sample aggregation,paired color,original pipeline
restoration,three-file bound and unsupported descriptors. Existing full-support
positive/negative fixture still exercises event registration,resize/recreation and
normal teardown. Runner refuses stale qualification hashes. Test output typically
<0.2MiB; owned fixture processes <=100s,never SFC.

Prepared entry (only after qualification): start_return_image_session.ps1
-DepthSnapshots,from established elevated parent; forwards WindowsPowerShell5
to bundled7 with process-only ExecutionPolicy Bypass. No routine UAC/security
changes. Sponsor enters usual two-ship skirmish,keeps both visible and holds
camera until cue (~5s),then makes a small camera rotation,stops,and exits normally
at two-beep request (~20s). No visual change expected. Runner automates everything
else. Gameplay must not be launched during offline preparation.
