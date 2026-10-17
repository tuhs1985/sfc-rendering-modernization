# Codex run — measurement runtime adjudication

- Run ID/date: 2026-10-14-m1-measurement-runtime; M1 closure measurement.
- Baseline: `fee152f`, inherited dirty/unstaged work from preparation; no staging
  or commit authorized. Fuel Guard hook verified, no daemon spawned.
- Question: did prepared10s qualification capture real SFC presentation intervals
  and per-process graphics/system memory with clean removal/exit?
- Authority: handoff, approved SFC-GATE-20261014/M1 plan, probe
  M1-CLOSE-MEASURE-001; latest run `20261014-002725-disabled-auto-gate`.
- Reviewed exact metadata/result, controller output, gate summary, raw CSV and
  JSONL, collector summaries/errors, current capture/analyzer source and tests.

## Execution and correction

Sponsor executed prepared entry and reported "done". No game launched here.
PresentMon exit0 and596 rows; memory10/10 available. Parser alone rejected actual
v1 `msBetweenPresents` capitalization. Corrected lookup to casefold with duplicate
collision rejection; regression covers actual header. Added `--analyze-only`
and exclusive `--analysis-output` to reprocess raw evidence without overwriting
the original failure report or launching another trace.

Tools: bundled Python3.12.14, PowerShell7.6.5, Git, .NET ZIP/SHA256, pinned
PresentMon2.3.1 from preparation (no new tool download/configuration).
Material reproduction:

```powershell
# Bundled python.exe, process-local TEMP/TMP = artifacts/m1/test-temp absolute.
python -m unittest discover -s tests -p 'test_*.py'
python tools/m1_component/capture_m1_frametimes.py --analyze-only --pid 22376 --output artifacts/m1/runs/20261014-002725-disabled-auto-gate/frames.csv --analysis-output artifacts/m1/runs/20261014-002725-disabled-auto-gate/frames.reanalysis.json
```

Independent read-only Python CSV/JSONL aggregation checked PID/application,
runtime/swap-chain/drop distributions, time range and memory ranges; results in
[evidence](../m1/evidence/M1-CLOSE-MEASURE-001-20261014.md). No runtime repeat.
Capture limits unchanged:10s,64MiB frame CSV/64KiB stderr,2MiB memory; no ETL,
no high-volume geometry hook. Used automatic tactical gate and its restoration/
unload receipts; actual process22376 and start-time identity recorded by runner.

## Result / validation / files

CONFIRMED measurement qualification after parser correction, not endurance or
M1/aggregate TRL PASS. Original `measurement_collectors_passed=false` retained;
reanalysis is an explicitly separate adjudication. Reported presentation runtime
DXGI does not reinterpret the established engine API or select an architecture.
Sponsor visible-behavior attestation requested separately; not assumed from done.

58 Python tests pass; original/reference client hash matches known SHA256,
gate restored/unloaded, normal exit and no added game files in original result.
Diff check and referenced paths/status reviewed. No native code changed, so no
additional native rebuild required beyond preparation's passed build/tests.

Files modified: `tools/m1_component/capture_m1_frametimes.py`,
`tests/test_m1_frametimes.py`, `docs/HANDOFF.md`,
`docs/m1/m1-closure-evidence-checklist.md`,
`docs/m1/probes/M1-CLOSE-MEASURE-001.md`.
Files created: this run record and evidence record above. Ignored generated
`frames.reanalysis.json` and verified archive retained with original raw.
Archive19entries29,025bytes, raw156,970bytes; exact path/hash in evidence. Every
entry hash verified; no deletion and no uncontrolled bulk data.

Final repository: `fee152f`, inherited dirty work preserved, all changes
unstaged/uncommitted. No active SFC/controller/PresentMon process observed;
no surviving admin/ETW session assumed. Remaining gap: automatic tactical start
for neutral endurance, duration/paired telemetry/reproduction evidence.
Exact next action: prepare neutral enabled>=30-minute endurance runner using
qualified collectors, rather than another short visual or measurement repeat.

## Sponsor observation follow-up — 2026-10-14

Sponsor answered the rendering/HUD/cursor/control question: "Yes, no issues
noticed". Added attestation to evidence and updated current handoff; short-run
non-interference observation only. No new runtime, code, staging or commit.
Validation: referenced evidence/handoff paths exist; documentation diff check
passes. Next action unchanged: prepare sustained neutral-component runner.
