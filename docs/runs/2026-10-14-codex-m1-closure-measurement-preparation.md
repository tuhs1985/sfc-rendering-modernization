# Codex run — M1 closure measurement preparation

- ID/date: 2026-10-14-m1-closure-measurement-preparation.
- Authority: approved M1 plan plus SFC-GATE-20261014; sponsor "acceptable, begin"
  following reliability closure recommendation. No M2 implementation authorized.
- Baseline: `fee152f`,101 pending status entries; inherited dirty work retained,
  no staged paths or commit. Fuel Guard attached/recent hook verified; no daemon.
- Question: what evidence actually remains, and can bounded real presentation/
  process-memory collectors replace another redundant visual test?

## Reviewed evidence and engineering decisions

Read current handoff/amendment, M1 plan/checklist, latest RT-010, M1-A-RT-003,
component runbook/development manifest, existing baseline/enabled runners,
controller tactical-gate wait and semantic activation source. Reuse established
semantic and controllability PASS; do not repeat for extra counts.

Remaining: sustained component mission, repeatable actual presentation/frame
timing and per-process graphics-memory comparison, formal reproduction/risk
review. Found neutral enabled runner does not currently pass controller's
gate-timeout option except in visual/corner modes. Documented fix needed before
endurance; no launch of an incorrectly timed formal run.

Selected measurement candidate: standalone signed PresentMon2.3.1, no MSI/service,
no renderer translation. Official API release metadata reports421,312bytes;
download pinned URL and SHA256 in probe. Authenticode Valid, `--help` identifies
2.3.1 and required flags. Official docs reviewed:
<https://github.com/GameTechDev/PresentMon/blob/main/README-ConsoleApplication.md>.
Native D3D7 coverage is still unproven, not inferred from generic DirectX support.
Per-process GPU provider available outside sandbox; no device-total substitution.

## Implementation / exact files

Added:
- `docs/m1/m1-closure-evidence-checklist.md`.
- `docs/m1/probes/M1-CLOSE-MEASURE-001.md`.
- `tools/m1_component/capture_m1_frametimes.py` (PID filtered stdout pipe,
  strict caps/timeout, owned child/session cleanup, per-swap-chain v1 analysis).
- `tools/m1_component/M1ClosureTelemetry.psm1` (PID-exact GPU aggregation).
- `tools/m1_component/capture_m1_memory.ps1` (1Hz, process start-time bound,
  unavailable !=zero,2MiB cap, bounded query/summary).
- `tools/m1_component/M1MeasurementJobs.psm1` (pinned dependency, two collectors).
- `tools/m1_component/start_m1_measurement_qualification.ps1` (PS5 shim, existing
  elevation policy, normal two-ship gameplay instructions,10s automatic gate).
- `tests/test_m1_frametimes.py`, `tests/test_m1_closure_telemetry.ps1`.
- this run record.

Modified `tools/m1_component/run_m1_disabled_baseline.ps1` with opt-in
`-CaptureMetrics` (automatic-gated <=30s only; defaults unchanged). Collector
failure retained separately from normal baseline/gameplay result. Updated
`tests/README.md` and `docs/HANDOFF.md`. No component/controller C++ change.

## Tools, material commands and validation

Python3.12.14: bundled `dependencies/python/python.exe`; PowerShell7.6.5:
bundled `dependencies/native/powershell/pwsh.exe`; WindowsPowerShell5.1 shim;
VS2026 x86 developer environment18.7.3 via existing build script.

- Process-local TEMP/TMP=`C:\Project\SFC-Modernize Engine\artifacts\m1\test-temp`.
  `python -m unittest discover -s tests -p 'test_*.py'`: **57 pass**.
  Initial new tests hit restricted default sandbox TEMP (5 infrastructure errors);
  rerun with existing temp convention passed. No implementation judgment from
  those filesystem errors; no broad temp cleanup attempted.
- `pwsh -NoProfile -File tests/test_m1_closure_telemetry.ps1`: pass PID-prefix,
  adapter summing, duplicate/negative rejection and unavailable-not-zero checks.
- Six new/changed PS files parsed successfully.
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File
  tests/test_m1_visual_entry_runtime.ps1 -EntryName start_m1_measurement_qualification.ps1`:
  pass. Initial fixture lacked PSCommandPath in extracted block; changed entry
  to established explicit entry-path convention, then reran successfully.
- Existing `build_m1_component.ps1`: native compile, exports and all contract,
  forwarding, tint, shading, corner, copy and surface test groups passed.
- New frame tests: per-chain attribution, bad/missing/nonfinite rows, wrong PID,
  non-overwrite, output/line caps, nonzero child and silent-child deadline cleanup.
- Read-only `Get-Counter -ListSet 'GPU Process Memory'` and CIM failed in sandbox;
  outside sandbox provider enumeration succeeded. `nvidia-smi` identifies RTX4070Ti,
  driver596.36; global memory not used as process evidence.

## Infrastructure smoke evidence / limitations

Probe M1-CLOSE-MEASURE-001: two-second collectors on own non-rendering shell;
PresentMon exit6, `error: failed to start trace session: access denied.` Outside
sandbox does not mean admin token. Owned cleanup exit7; no session had started.
This verifies error propagation only, not a successful no-frame negative test.
Do not mislabel it native SFC incompatibility. No security/group setting changed.
Prepared runtime requires already-elevated parent and never self-elevates.

Separate read-only three-second provider smoke on existing GPU process39896:
3/3 available records,947byte JSONL,complete true. Not SFC/gameplay evidence.
Captured before final cadence rounding correction; final collector anchors each
next sample to sample start+1s rather than rounding below a second boundary.

Raw `artifacts/m1/measurement-check/offline-20261014-001945`:11files/4,435bytes.
Compressed archive `artifacts/m1/archives/M1-CLOSE-MEASURE-001-offline-20261014-001945.zip`:
3,358bytes; SHA256
`35CF6D502501950731A90E5CC4A2BE3FD14FA21527B2E110547C8FBB18008EF0`.
Every entry hash verified; small raw retained ignored, no deletion.
Tool artifact421,312bytes, SHA256
`364E5D98D4D134BD54DD25C22ED2CA2F4883F8BC3ED6502BEE0C151E3436D30C`.
Frame CSV64MiB/stderr64KiB hard limits, memory2MiB, qualification10s plus bounded
cleanup; no ETL/all-process capture. Observed non-SFC smoke very small; native SFC
rate unknown. All source/probe/runner details versionable, generated tool ignored.

## Preservation / result / next action

Installed/reference client SHA256 both unchanged:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Launcher unchanged:
`84D3A5F89A922C4BEE6815CF0614538C3565C4BDB7DB3AA187C552CB727EF890`.
No SFC launched/injected by this run; no gameplay, visual or formal duration
claim. No helper, architecture selection or new semantic hooks. M1 CONTINUES;
CONFIRMED offline/preflight capabilities; actual ETW/native-game coverage open.

Final validation: diff check/local links/status reviewed; inherited work plus
these files remains unstaged/uncommitted atfee152f. No active game/controller or
owned collector left by this execution; no persistent admin/session created.
Final checks:90 local Markdown links valid,112 pending status paths,0 staged,
0 active game/controller/collector processes; tool/archive correctly ignored.
Diff check passes with existing LF/CRLF notices only.
Exact next action: sponsor runs prepared10s measurement entry from existing
elevated parent, enters usual skirmish and exits normally when requested. If
measurement works, proceed to endurance preparation rather than more cosmetics.
