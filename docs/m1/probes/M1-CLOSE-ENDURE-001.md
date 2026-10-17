# M1-CLOSE-ENDURE-001 — neutral semantic endurance

Status: executed — endurance/measurement PASS on tested stack; M1 CONTINUES
pending dependency-baseline reconciliation. [Evidence](../evidence/M1-CLOSE-ENDURE-001-20261014.md).
Preparation instructions below preserved for reproducibility; no repeat requested.
Authority: [approved gate amendment](../../decisions/2026-10-14-m1-m2-gate-allocation-amendment.md).
Question: does the existing neutral component remain operational for at least
30 tactical minutes, with bounded presentation/memory data and clean removal?

## Baseline and configuration

- Supported client2.5.6.4 SHA256
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`,
  MD5 `2BE8F713F81B1C68D50EAD6088C32886`; launcher2.1.0.22 original hashes checked.
- Existing component0.13/semantic schema unchanged; no new hooks or ABI changes.
  Five semantic/lifetime hooks only. Geometry, corner, wrapper, private-copy,
  tint/shading/surface flags OFF. Capture120 detailed scene epochs or10,000
  events, eight active owners; then summary counters continue, not hook removal.
- Controller `--max-seconds 1830 --stop-on-burst 0
  --gate-timeout-seconds 600 --unload-after-stop 1`. It starts the duration after
  validated ship tactical gate, not launcher/menu time. Original bytes restored
  before optional unload; no private-copy module pin applies in this mode.
- Qualified [measurement probe](M1-CLOSE-MEASURE-001.md), pinned PresentMon2.3.1
  and per-process GPU/system memory. Actual baseline:
  `20261014-002725-disabled-auto-gate`; valid raw reanalysis and normal sponsor
  observations retained. Do not mistake historical parser false flag for failed
  capture. No fresh geometry/native draw transcript required.
- New `-Endurance` is opt-in; rejects visual features, geometry hook, short or
  mismatched duration/detail settings. Existing non-endurance defaults unchanged.

## Launch and sponsor procedure

From the existing scoped Administrator PowerShell parent:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\m1_component\start_m1_endurance_session.ps1"
```

PS5 shim invokes bundled PowerShell7.6.5. Entry checks elevation through validated
policy, dependencies/hash, refuses an existing game, builds/tests, launches the
verified SFC Launcher via existing runner. No automatic UAC, scheduled task,
machine security change, alternate renderer or game-directory file installation.
Python3.12.14, existing VS2026 x86 build/runtime tools; exact runtime component/
controller hashes plus config recorded in each fresh run directory.

Sponsor: use same practical two-ship choices as baseline if possible; keep a
single tactical mission open and play normally for >=30minutes. No camera
choreography, timestamps, required target tracking or visible effects. If mission
ends early, do not concatenate battles or count menus: report it. Exit safely
if problems occur; do not force a broken game to continue. At about30min30s after
tactical entry, two long beeps and console request mean exit SFC normally. Keep
runner open for collection. Report rendering/HUD/cursor/targeting/camera/control
issues, pauses/mission transitions and whether same mission stayed active.

## Capture controls and lifetime

- Max tactical component window1830s (<35min). Separate bounded launcher/client
  wait600s, tactical gate600s, normal-exit wait600s; these are not tactical time.
- Existing controller owns restoration even after detail saturation; runner
  supplies gate timeout for neutral endurance explicitly. Runner uses actual
  tactical event before launching measurement exactly once. Poll latency <=1s;
  30s component duration margin covers collector startup/finish. End observed
  wall/tick times and component gate tick support duration adjudication.
- PresentMon1800s, PID only, no ETL/capture-all;64MiB CSV/64KiB stderr hard limits,
 8KiB line limit,128-record queue, N+10s collector wall guard. At qualification
  rate~14KiB/s expect ~26MiB, not a guarantee; cap marks failed measurement rather
  than successful truncation. This separate stream cap is not a relaxation of
  component event-log16MiB warning/32MiB hard stop. Total expected <64MiB, worst
  configured logs well below sponsor10GB ceiling.
- Memory1800s at1Hz,2MiB cap,2s CIM query timeout, process start-time identity
  and exact PID aggregation. Expected<1MiB. Missing values are not zero.
- Early game/controller end requests shared `measurement-stop.signal` so both
  owned collectors stop promptly, frame child/session is cleaned, and partial
  evidence retained. Never kill SFC or arbitrary PresentMon/ETW sessions. Unique
  session cleanup uses only the created session name. Deadline/cleanup failures
  are recorded as incomplete, never PASS. Leave original renderer behavior alone.
- No dynamic semantic buffer growth. Existing frame counters keep counting after
  detail saturation; initial detailed identity evidence plus final counters do
  not establish per-frame owner history for every minute. Mission continuity
  needs controller timing, presentation coverage and sponsor attestation; disclose
  pauses/view gaps rather than infer continuous tactical state from process life.

## Output, analysis, cleanup and acceptance

Fresh `artifacts/m1/runs/<timestamp>-enabled`: config/metadata, component CSV and
summary, controller output/restoration receipts, process telemetry, frame CSV /
collector analysis, memory JSONL/summary, run-result. No reference files changed.
Analyze actual PID/swap-chain/time coverage, dropped frames/interval distributions,
full requested memory span/errors and baseline comparison. Compare matched early
windows where defensible; full mission workload differs from10s disabled baseline,
so do not report that difference as controlled causal component overhead. No new
M1 numeric performance threshold or later TRL5 limit imposed.

Require gate-detected duration trigger, >=30min valid mission evidence, semantic
summary progression, no invalidating state/association/overflow failures, usable
controls/UI, bounded complete telemetry, restored bytes/unload, normal exit and
unchanged client. Incomplete measurement, early mission end or missing continuity
attestation => M1 CONTINUES / bounded gap, not automatic full rerun. Separately
adjudicate any baseline-related incident or invalidating failure.

After analysis compress useful raw and verify entry hashes before any scoped
cleanup. Raw/generated tools/binaries ignored. No deletion/commit during setup.
This is M1 closure evidence only; no M2 enhancement or aggregate TRL4 PASS implied.
