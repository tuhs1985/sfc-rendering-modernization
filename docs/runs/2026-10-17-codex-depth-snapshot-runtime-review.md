# Codex run — depth snapshot runtime failure review

Run SFC-RETURN-20261017-13,2026-10-17 EDT. Sponsor completed prepared test and
reported final `Depth snapshots incomplete or invalid; preserve partial evidence`.
Read HANDOFF,Run12,REMIX-DEPTH-001,actual manifest/result/depth status/analysis,
ReShade log,gate-controller/launcher logs and native probe initialization.
FuelGuard actual-thread receipt verified;no daemon/helper/delegation,new gameplay,
implementation fix,staging or commit. HEAD e96765a,indexempty,existing dirty work
preserved. This execution analyzes and records failure;does not silently qualify
a retry or change game/translator settings.

## Actual result — PARTIAL,no depth images

Exact run artifacts/remix-runtime/runs/20261017-185115-506823-in-game.
Verified copied gamePID11952,gate controller38148. Requested20s tactical capture;
prepared run48.313s total. Depth status:files0,io_errors0,gpu_failures1,
ambiguousfalse,issued0,pending_abandonedfalse. No depth packets or comparison
images exist. This is NOT merely a strict parser rejecting otherwise usable
images. The probe disabled before issuing its first GPU snapshot.

CONFIRMED mechanically:normal_game_exit true,launcher CHILD_EXIT code0,
gate-controller exit0,hook_bytes_restored true,component_unloaded true,host exit0,
proxy restored,accepted critical files/settings unchanged and copied critical
hashes restored. Original/copied client SHA256
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29;
copied dxgi proxy E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7.
Sponsor reported completion/error,not explicit visible-behavior equivalence for
this run;do not infer normal HUD/control appearance solely from normal exit.

Native shutdown warning persists exactly:
`Reference count for ID3D11Device0 object 08AED8F0 (0D891F14) is inconsistent (67).`
No new Remix runtime was started. No original-ship drawing suppressed.

## Compatibility diagnosis / evidence classes

CONFIRMED ReShade.full-support.log records each D3D11 device as `Using feature
level a100.` (10_1),including last device before swapchain initialization:
14:51:17:542. Device creation requested one feature level,Flags0. This rules out
single-threaded-device creation flags as the supported explanation here.

CONFIRMED tools/remix_runtime/depth_snapshot.h::Capture::init compiles `cs_5_0`
and calls CreateComputeShader,then CreateDeferredContext. Any of these failures
sets one generic gpu_failures counter and disables further observation. Existing
GPU fixture requested the highest available feature level,not explicit10_1;
its success did not qualify SFC's actual feature mode. Prior ready-for-runtime
checkpoint is superseded,not evidence of actual SFC compatibility.

Microsoft primary documentation:
https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/specifying-compiler-targets
https://learn.microsoft.com/en-us/windows/win32/direct3d11/direct3d-11-advanced-stages-compute-create
lists10_1 shader targets and chooses cs_5_0 only for feature level>=11_0.
Thus a cs_5_0 compute shader is incompatible with the observed10_1 device even
on RTX hardware. This is a probe compatibility defect,not proof the depth
resource is absent or unreadable. Do not change translator/device feature level
just to accommodate the probe.

STRONG HYPOTHESIS:CreateComputeShader rejected the incompatible shader at init,
explaining one GPU failure and zero issued snapshots. Exact failed API/HRESULT
was NOT logged,so do not assert a measured E_INVALIDARG or claim every alternative
failure stage is excluded. Independent static code,actual feature-level log,and
official capability table corroborate the definite incompatibility.

## Smallest next action / rejected scope

Do not repeat unchanged -DepthSnapshots run or broad capture. Next:offline-test
the reader at explicitly requested D3D_FEATURE_LEVEL_10_1,replace its SM5-only
extraction with a10_1-compatible bounded read-only path (e.g.pixel-shader sampling
of the existing multisample SRV),and log stage/HRESULT/actual feature level.
Qualify this path and existing state/cleanup regressions before sponsor retry.
No fix implemented in this review. No new wrapper,device-feature override,
renderer architecture,ship suppression or milestone-completion claim justified.

## Preservation / validation / repository

Raw manifest/result/logs remain unchanged. JSON result/status and post-run hashes
reviewed;existing read-only preflight and git diff --check validated. Normal gate
restore/unload evidence is independent of failed capture. No native rebuild/full
suite needed for this documentation-only review. Added this record,curated runtime
evidence;updated HANDOFF,probe and readiness disposition. Exact generated output
and archive sizes are in curated runtime evidence;archive retains logs/JSON but
no generated DLLs. Small raw run retained,no deletion. Final HEAD e96765a,
indexempty,all current work unstaged/untracked;no commit.
