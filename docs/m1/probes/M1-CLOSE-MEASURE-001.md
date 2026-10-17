# M1-CLOSE-MEASURE-001 — bounded measurement qualification

Status: executed — PASS after offline parser correction; native-launch SFC
presentation/memory coverage confirmed. See [runtime evidence](../evidence/M1-CLOSE-MEASURE-001-20261014.md).
Preparation and non-admin preflight notes below are historical, not a remaining
ETW-permission blocker for the executed elevated workflow. No endurance claim.
Question: can we measure real presentation intervals and process-attributed
memory without a high-volume geometry hook or altering the game's renderer?

## Tools and exact configuration

- PresentMon console **2.3.1 x64**, standalone official release, no MSI/service/
  overlay installation. Source:
  <https://github.com/GameTechDev/PresentMon/releases/tag/v2.3.1>.
  CLI reference:
  <https://github.com/GameTechDev/PresentMon/blob/v2.3.1/README-ConsoleApplication.md>.
  Downloaded421,312bytes; Authenticode Valid; pinned SHA256
  `364E5D98D4D134BD54DD25C22ED2CA2F4883F8BC3ED6502BEE0C151E3436D30C`.
- `tools/m1_component/capture_m1_frametimes.py`: Python 3.12, process-ID filter,
  `--v1_metrics --output_stdout --no_console_stats --process_id PID --timed N
  --terminate_after_timed --session_name SFCM1_<unique>`; no ETL, no capture-all,
  no stop-existing-session, no automatic privilege restart. Captures only its
  own child; never stops SFC or another PresentMon session.
- `tools/m1_component/capture_m1_memory.ps1` and `M1ClosureTelemetry.psm1`:
  PowerShell 7.6.5; 1Hz process working-set/private bytes and PID-matched
  `Win32_PerfFormattedData_GPUPerformanceCounters_GPUProcessMemory` dedicated/
  shared counters, each query timeout 2s. Missing/unreadable counters are
  unavailable, not zero. Adapter totals are not substituted for process usage.
- GPU provider read-only preflight succeeds outside sandbox; sandbox CIM/counter
  access denied. Already-scoped elevated parent is required for formal capture;
  no sponsor UAC, no security policy changes. No target memory writes or hooks.

## Launch / bounds / stop / output

From existing elevated parent, use exact Python/pwsh paths recorded in the run:

Sponsor-ready automatic entry (Windows PowerShell5 shim to bundled7):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\m1_component\start_m1_measurement_qualification.ps1"
```

Requires already-elevated parent; otherwise fail before launch, never request UAC
or weaken policy. Uses existing disabled automatic gate, exact launcher/client
validation, build and one-shot gate removal/unload before metrics. Start both
collectors only after confirmed tactical gate/restoration. Capture10s, wait for
owned collectors, preserve failure summaries and request normal exit even if
metrics are unavailable. Qualification path rejects >30s; no formal endurance
claim. No normal semantic observer, geometry or visual intervention stays active.
Runner still verifies normal exit/client hashes; collector PASS is recorded
separately and must be adjudicated, not inferred from baseline runner completion.

Standalone analyst collector commands below are for diagnostics:

```powershell
python tools/m1_component/capture_m1_frametimes.py --tool artifacts/m1/tools/PresentMon-2.3.1-x64.exe --pid <verified-game-pid> --seconds 10 --output artifacts/m1/measurement-check/frames.csv
pwsh -NoProfile -File tools/m1_component/capture_m1_memory.ps1 -TargetProcessId <verified-game-pid> -Seconds 10 -OutputPath artifacts/m1/measurement-check/memory.jsonl
```

Standalone collector commands do not launch/inject into SFC or control the
automatic tactical gate. The prepared qualification entry supplies the verified
PID after gate removal; formal endurance orchestration is not yet qualified.
Never guess a PID or copy a stale value. Use fresh output paths, no overwriting.

- Qualification 10s; general ceiling 2100s. Frame collector wall guard N+10s,
  bounded stdout queue/line length, <=64MiB CSV and <=64KiB stderr. On cap/error
  stop owned collector; mark failure, never present a capped capture as complete.
  On failure terminate only its uniquely named ETW session, with a5s cleanup
  guard; retain cleanup result. Never stop the default/another user's session.
- Memory <=2101 records, 1Hz, <=2MiB JSONL; original PID/start-time bound, stop on
  exit/reuse. Summary files <=small fixed JSON metadata, fresh paths.
- Expected 10s frame output <2MiB, memory <16KiB; formal frame CSV may approach
  tens of MiB at high FPS, but bounded. Limits are not license for multi-GB ETL.
  No game trace run yet: actual SFC size/rate remains unknown until qualification.
- Cleanup: collectors stop their own child/resources; no game directory files.
  Preserve raw under ignored artifacts; after analysis archive useful files and
  verify hashes before any scoped deletion. Never delete other ETW sessions.

## Analysis / acceptance / hazards

2026-10-14 preflight: live GPU provider sample3/3 records available (947bytes).
Non-admin ETW attempt exited6, exact error: `error: failed to start trace session:
access denied.` Follow-on owned-session cleanup exited7 (session never started).
This verifies failure capture, **not successful ETW start or native SFC support**.
No security/group setting changed; already-elevated workflow remains required.
Smoke raw4,435bytes/11files archived to ignored
`artifacts/m1/archives/M1-CLOSE-MEASURE-001-offline-20261014-001945.zip`,3,358bytes;
all entry hashes verified, raw retained, nothing deleted. No high-volume output
observed. Real SFC output rate remains unmeasured.

Frame analyzer requires exact PID, expected columns, finite positive intervals,
and reports each swap chain separately; zero/invalid rows or mixed processes
must not silently pass. CPU work/display intervals are not interchangeable.
Memory analysis requires available per-PID counters, no duplicated instances,
explicit missing samples and correct process lifetime. Summed dedicated/shared
usage are provider accounting values, not proof of exact physical residency.

Only a real SFC tactical capture can confirm PresentMon native legacy coverage.
Do not launch a 30-minute formal test before that. Tool overhead/workload matching
must be considered in paired results. This probe does not adjudicate M1 PASS.
