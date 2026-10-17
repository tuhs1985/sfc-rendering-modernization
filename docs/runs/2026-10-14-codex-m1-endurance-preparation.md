# Codex run — neutral endurance preparation

- Run ID/date:2026-10-14-m1-endurance-preparation. M1 closure/reliability.
- Sponsor "ready" following qualified measurement; prepare actual sustained
  neutral test, not another cosmetic/short qualification. No M2 implementation.
- Starting HEAD`fee152f`, inherited dirty work114 status entries before edits,
  nothing staged. Fuel Guard recent hook verified, no daemon. No helper/subagent.
- Authority reviewed: current HANDOFF, approved M1 plan/SFC-GATE-20261014,
  measurement probe/evidence and latest run record, existing runner/controller/
  component counters/gate/removal paths, semantic analyzer and owner tracker.

## Decisions / implementation

Reuse component0.13 and confirmed neutral path; no C++/ABI/hook changes. Add
opt-in `-Endurance` to runner/bootstrap; it rejects altered features, geometry,
wrong duration/detail settings. Pass controller tactical gate timeout explicitly,
`1830s --stop-on-burst 0 --unload-after-stop 1`; first tactical event starts
duration, not menu time. Independent runner gate check starts qualified1800s
frame/memory collectors exactly once. Thirty-second margin covers polling/startup
and normal capture shutdown before component removal. Record gate/end UTC/tick
times and metric status; no auto-M1-PASS flag.

Keep120frames/10,000 detailed events then summary counts with hooks active;
existing16/32MiB component limits, frame64MiB/stderr64KiB, memory2MiB. At measured
qualification rate frame CSV~26MiB expected for30min, hard cap remains necessary.
No high-volume geometry callback, full owner transcripts or ETL. Paired disabled
comparison reuses002725 qualification, not a newly imposed30min disabled mission;
do not infer causal overhead from unmatched workloads. No numeric M1 performance
threshold invented and no TRL5 threshold applied early.

Added cancellation file to collectors/jobs for early game/controller failure;
only owned consumers/session stop. No blanket process killing. Metadata/partial
failure result retained if controller exits nonzero. Default non-endurance paths
unchanged; historical modes keep previous waiting semantics.

Prepared entry uses existing elevation policy and PS5->7 shim, refuses existing
SFC, checks pinned tool before launch, builds then existing verified launcher.
No automatic UAC or machine changes. Sponsor needs normal gameplay in one
representative tactical session; no choreography. Ends with two long beeps and
normal exit request. Early mission completion/pauses must be reported; do not
stitch different battles/menu time into continuous tactical evidence. Existing
summary counters plus long presentation coverage need sponsor mission attestation,
not an invented automated proof of per-frame tactical continuity/identity.

## Exact changed paths

Added:
- `tools/m1_component/start_m1_endurance_session.ps1`
- `tests/test_m1_endurance_workflow.ps1`
- `tests/test_m1_measurement_cancel.ps1`
- `docs/m1/probes/M1-CLOSE-ENDURE-001.md`
- this run record.

Modified:
- `tools/m1_component/run_m1_increment_a.ps1`
- `tools/m1_component/start_m1_enabled_session.ps1`
- `tools/m1_component/M1MeasurementJobs.psm1`
- `tools/m1_component/capture_m1_frametimes.py`
- `tools/m1_component/capture_m1_memory.ps1`
- `tests/test_m1_frametimes.py`
- `tests/README.md`
- `docs/m1/m1-closure-evidence-checklist.md`
- `docs/HANDOFF.md`

## Tools / reproduction / validation

Bundled Python3.12.14, PowerShell7.6.5, WindowsPowerShell5.1 fixture, VS2026
18.7.3 x86 existing build (MSVC /W4 /WX), Git and PowerShell SHA256 checks.
Process-local TEMP/TMP existing ignored absolute artifacts/m1/test-temp.

- `python -m unittest discover -s tests -p 'test_*.py'`:59 pass, including real
  child cancellation/size/deadline/cleanup and actual PresentMon header regression.
- `pwsh -NoProfile -File tests/test_m1_endurance_workflow.ps1`: production policy
  rejects unsafe modes/duration/bounds; synthetic real event verifies no start
  before gate, exactly one start after, correct1800s PID. No SFC launched.
- `pwsh -NoProfile -File tests/test_m1_measurement_cancel.ps1`: synthetic job
  cancellation signal, failed status, output retention and disposal pass.
- `tests/test_m1_closure_telemetry.ps1` and
  `tests/test_m1_corner_action_cues.ps1`: pass, no old phase regression.
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File
  tests/test_m1_visual_entry_runtime.ps1 -EntryName start_m1_endurance_session.ps1`:
  PS5->7 actual harmless shim fixture passes.
- Seven changed/new PS files parsed. Existing full native build/tests run to
  verify entry's build workflow and preserved surrounding implementation.
  Build/exports/all native test groups passed. Prepared component SHA256
  `1D29FCAAEE79D33A210F2B035CD35DA5552F4DE2E8D71A6F3A288896FD5A640A`;
  controller `757283B6DA5D71C8A9F68279267ACB2A47F21242598A9E4CA58BE7E118D07907`.
  Runtime entry rebuilds, so its recorded hashes supersede these if different.
- Installed/reference client SHA256 both
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`;
  launcher SHA256
  `84D3A5F89A922C4BEE6815CF0614538C3565C4BDB7DB3AA187C552CB727EF890`.
- Diff check, local doc references, staged/unstaged and active process checks.
  Final check: diff passes (LF/CRLF notices only),99 local links valid,119 pending
  status entries,0 staged,0 active SFC/controller/PresentMon processes.

Probe M1-CLOSE-ENDURE-001 records exact launch/limits/cleanup/evidence mapping.
No gameplay/capture initiated by Codex. No new bulk raw or archive; synthetic
fixtures small/ignored, prior compressed measurement evidence untouched. Runtime
component/controller hashes are recorded by runner because entry rebuilds.

## Disposition / handoff

READY FOR SPONSOR RUNTIME TEST; offline confidence CONFIRMED, sustained runtime
outcome unknown. M1 CONTINUES, no overall TRL4 or enhancement claim. Formal M1
closure still requires run adjudication, mission/behavior attestation and risk/
reproduction review. Nothing staged/committed; inherited dirty work retained at
fee152f. No surviving game/debug/admin/session state assumed.

Exact next action: run `start_m1_endurance_session.ps1` from existing elevated
parent; sponsor enters same practical skirmish and exits normally only after
request, or reports/ends safely on failure. Do not rerun old diagnostic effects.
