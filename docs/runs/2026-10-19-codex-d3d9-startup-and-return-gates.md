# Run71 — approved D3D9 startup-to-additive-test implementation

Status:BLOCKED — inactive Windows input desktop;Gate1 not passed.
Date2026-10-19 America/New_York(UTC output folders20261020).
Sponsor approved the proposed gated plan after selecting EXTRA SHIP ONLY.
Original SFC ships remain ON;no suppression,appearance tuning,supersampling,
D3D12 implementation,requirements change or formal maturity claim.

Starting HEADd29111f7a513c4510c4d33aeeda2c355d98443a5,index empty,
13modified tracked/36untracked files. Preserve all Run65–70 work. No commit/push.
Fuel Guard exact-thread trusted hook attached;direct sandbox connection denied,
no daemon spawned. No helper/subagents. Read HANDOFF,Run70,transition/scene and
replacement contracts,pinned runtime/header manifest and existing return code.

## Approved execution gates

1. Isolate native D3D9 adapter/window/format/session startup failure;fix only
   evidenced cause. Full native replay/negative/reset/projection tests must pass.
2. Verify actual normal-Remix camera output,not USD reconstruction;qualify color,
   depth,coverage and completion/ownership through normal x86 interception using
   pinned interfaces. No SDK mesh registration or continuous CPU screenshots.
3. Offline source-frame-correlated return harness,source cadence,no arbitrary30Hz,
   <=4surface sets/128MiB,max1920x1080. No explicit render-thread GPU waits,old-pose
   reuse or normal-frame fallback masquerading as successful delivery. Stop for
   architecture decision if current topology cannot meet correspondence/budget.
4. Only after offline PASS,default-off adapter in copied SFC;fresh qualified ship,
   documented offset,existing D3D11/ReShade compositor and current native depth.
5. Prepared90s additive sponsor test with setup periods and audible cues;5min
   workflow,32MiB logs/16MiB warning,existing asset bounds and10GB total evidence.
   No original suppressed. Normal gameplay/UI,steady correspondence and cleanup
   required. CDD p95<=33.3ms unchanged;no full qualification from a short run.

At any blocked gate,preserve evidence,update HANDOFF and report exact missing
capability rather than implementing a speculative alternative. Archive finished
generated payloads recoverably;do not erase source evidence or original assets.

Durable [approved plan](../reconnaissance/d3d9-to-sfc-additive-execution-plan.md)
records all gate details,bounds and sponsor procedure;do not depend on chat.

## Implementation and observed result

Added standalone x86`d3d9_startup_probe.cpp`,built /W4 /WX /Brepro alongside native
reference by`build.ps1`. No geometry/textures/Remix/game dependencies. Enumerates
<=16adapters;identifies HMONITOR/display rectangle and actual thread/input desktop;
tests A8R8G8B8,X8R8G8B8,UNKNOWN windowed HAL plusD24S8 and independent device
creation. Successful devices would Clear/Present and release;all current attempts
fail before drawing. Logs bounded by20s subprocess/1MiB. No desktop/security writes.

Added`startup.py` classifier/receipt runner;ordinary`run_offline.py` now requires
this preflight. Inactive desktop produces explicit blocker before native scene
tests instead of an unexplained generic failure. Availability is NOT full native
proof;all native oracle/reset/negative checks still required after admission.

Reproduce with installed modern PowerShell/build and bundled Python3.12:

```powershell
pwsh -NoProfile -File tools/d3d9_proof/build.ps1
python tools/d3d9_proof/startup.py --execute
python tools/d3d9_proof/run_offline.py --execute
```

CONFIRMED in both sandbox and approved execution:session1,WinSta0,thread desktop
Default,active input desktop Screen-saver. Actual TOKEN_ELEVATED0 in BOTH final
contexts;tool escalation is not proof of Windows elevation. Earlier commentary
“with/without elevation” is superseded by this measured token evidence.
Adapter0DISPLAY2 1920x1080@60,adapter1DISPLAY1 1200x1920@59,bothNVIDIA4070Ti.
GetDeviceCaps,CheckDeviceType and depth format checks all8876086a;all six device
creation attempts8876086c. Final APIrefs0,no child processes. This isolates failure
from mesh contents,texture upload,camera conversion and default-adapter selection.

STRONG HYPOTHESIS:inactive input desktop explains unavailable native hardware
devices. Not CONFIRMED cause until paired awake-desktop rerun succeeds. Do not
disable virtual monitors/change drivers,or fix mesh/camera code on this evidence.
No source bug correction asserted and no gate PASS. Existing x86 normal bridge
exports remixapi_InitializeLibrary,confirmed read-only in planning,but output
operations remain unqualified;no later gate executed around this prerequisite.

Final receipts:
`artifacts/d3d9-proof/startup/20261020-021517-099306`(approved context),
`20261020-021527-927934`(sandbox),identical log SHA256. Native runner
`artifacts/d3d9-proof/runs/20261020-021518-525578`explicitly BLOCKED.
[Curated evidence](../reconnaissance/evidence/20261019-native-d3d9-startup.json).
These tiny logs need no asset ZIP;existing large captures/ZIPs left untouched.

Validation:both native binaries build PASS;302Python tests PASS4.104s,including
6new startup classifier cases. Available/inactive/unsupported/malformed/duplicate/
count-mismatch/retained-reference cases covered. Full native render regression
remains BLOCKED,not falsely reported as passing. Final parser/diff/link/hash/status
checks recorded at closeout. Original client/appearance settings unchanged.

New/modified this run:probe C++,startup.py,build.ps1,run_offline.py,
tests/test_d3d9_startup.py,this run,approved execution plan,curated startup receipt,
README,transition plan,HANDOFF. Prior dirty files preserved,no stage/commit/push.

Exact next action:sponsor wakes/unlocks normal Windows desktop (no SFC launch),
then Codex reruns the startup probe and full native reference to test causality.
Do not bypass admission or execute Gates2–5 until Gate1 passes.

## Closeout

PowerShell parser,document links,curated source/EXE/evidence checks PASS;
git diff --check PASS(line-ending warnings only). Accepted/copied StarFleetOP.exe
remain SHA256`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Four appearance TOMLs have no diff. Process inventory finds no owned native probe,
replay,bridge,SDKhost,SFC or Toolkit. No administrative/security change attempted.
Final Git13modified tracked/42untracked individual files,index0;HEAD unchanged.
Only Gate1 diagnostics/admission are implemented;remaining approved work is parked
at the environment prerequisite,not represented as completed or semantic failure.
