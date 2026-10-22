# D3D9-CAMERA-RECOVERY-001 — two alive camera returns

Default-off dedicated runner,known Federation FCA player cruiser and different
enemy model. [Contract](../d3d9-owner-rebind-contract.md). Existing D3D9 additive
image path,original game drawing stays ON;no replacement or appearance tuning.
Uses LIFECYCLE-001 full-window state/journal capture without destruction phase.

From established elevated testing PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_camera_recovery_session.ps1"
```

`-CheckOnly` performs qualified dependency/hash checks without starting SFC.
Keep both ships alive. Enter usual two-ship skirmish;let extra ship prepare.
Automatic gate/first-image readiness starts timed cues;no manual timestamps.

| Cue | Action |
| --- | --- |
| One beep,15s | Hold own ship/camera still. |
| Two HIGH,25s | Switch camera to enemy;own ship out of view. |
| Three HIGH,40s | Return to own ship;look for extra copy beside it. |
| Two HIGH,55s | Switch to enemy again. |
| Three HIGH,70s | Return to own ship again;check copy returns. |
| One beep,80s | Hold steady. |
| Two LOW,after recording and restoration | Exit normally. |

Do NOT destroy a ship in this check. Keep game open during restoration message;
recording ends at90s but controller's existing120s watchdog still governs safe
live removal. Runner now waits against that actual gate-relative deadline.
Sponsor reports whether copy returned BOTH times and visible/control anomalies.

Expected:copy disappears when own ship isn't rendered and returns after fresh
epoch/content qualification without repeated asset conversion. No promise of
instantaneous recovery before actual latency measured. No stale image follows
camera while waiting. Normal SFC should remain unaffected.

Run98 amendment:dedicated recovery worker and shared-memory light delivery remove
serial main-loop/file-reader waits. Known-old inputs are discarded before GPU
work,not displayed from cache. Offline first-new-epoch→first-matched-Present was
33.19/33.10ms versus prior66.11/66.25ms in the same synthetic fixture. These are
NOT SFC return latency or photon measurements. Real game improvement remains
the purpose of the next run;record delay rather than assume instantaneous return.
Input admission counters and shared-light receipt now retained in run analysis.

Existing90s formal,<=30s image preparation,120s semantic watchdog,five-minute
workflow;32MiB evidence/warn16MiB,128MiB images/warn64MiB,20GB aggregate. Geometry
hook OFF,8calibration revisions,16MiB mapping,two GPU slots,no repeated image dumps.
Rebind control128bytes,max64generations;worker logs/evidence bounded as contract.
No routine sponsor UAC/admin/RE work. Copied test installation only.

Success for this check:two fresh epoch bindings ACKed with matching current-frame
display,unchanged resident asset signature,correct fresh lights;no wrong-owner or
stale output;normal game/renderer exit,controlled hook removal/unload,hash/proxy
restore and sponsor visual confirmation. If no actual new epoch occurred,record
that narrow limitation rather than claim recovery. Missing content/ambiguous
fixture,unload failure or lost evidence remains PARTIAL. Not formal TRL PASS.
