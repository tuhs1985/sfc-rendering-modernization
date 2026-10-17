# M1-CLOSE-MEASURE-001 — measurement qualification

**PASS after offline parser correction; M1 CONTINUES.** No second gameplay run
needed. [Probe](../probes/M1-CLOSE-MEASURE-001.md) /
[run record](../../runs/2026-10-14-codex-m1-measurement-runtime.md).

## Direct evidence

Run `artifacts/m1/runs/20261014-002725-disabled-auto-gate`, exact supported client,
PID22376. Prepared00:27:25, automatic tactical gate00:28:51.455-04:00,
capture start00:28:51.676; normal exit recorded00:29:22.586.
Gate controller confirms `hook_bytes_restored=true`, `component_unloaded=true`
before capture. No semantic/geometry/visual component remains active during
this disabled measurement, so these numbers are not component overhead.

- PresentMon2.3.1 exits0, stderr empty, elapsed10.125s, CSV143,403bytes.
- 596 rows, all `StarFleetOP.exe` / PID22376 / one swap chain
  `0x000000000551CE10`, capture-relative time0.0344386..9.9574067s.
- All report `Runtime=DXGI`, `Hardware: Independent Flip`, Dropped0. This confirms
  PID-attributed **presentation observation in this native-launch configuration**,
  not that SFC's engine uses a newly chosen DXGI renderer, nor a native D3D7 draw
  transcript or physical-display timing equivalence.
- `msBetweenPresents`: mean16.6713199664ms, p95(nearest-rank)18.479ms,
  max38.4703ms. No new numeric M1 acceptance threshold applied; no attribution
  of individual intervals to gameplay or instrumentation.
- Memory10/10 records available over10.0023s,3,200bytes, no PID/lifetime mismatch
  or query error. Process private196,067,328..224,952,320bytes;
  working set220,229,632..248,950,784bytes; GPU dedicated519,585,792..523,386,880;
  GPU shared16,875,520..16,998,400bytes. Provider accounting, not exact residency;
  no leak/stability inference from ten seconds.

## Parser defect and recovered result

Original `frames.result.json` and metadata honestly retain failure:
`PresentMon v1 columns missing; native coverage unqualified` and
`measurement_collectors_passed=false`. Capture itself succeeded. Actual v1 CSV
uses `msBetweenPresents`, whereas analyzer expected `MsBetweenPresents`.
Corrected header lookup to case-insensitive matching, reject case-colliding
duplicate columns, added regression using actual observed header/PID form.
Reanalysis of unchanged raw CSV stored in `frames.reanalysis.json` confirms the
numbers above. Original failure records were not overwritten or relabeled.

**CONFIRMED:** useful PID-filtered presentation intervals and per-process GPU/
system-memory sampling available for paired M1 work. Critical claim corroborated
by actual raw rows, independently checked PID/time distributions, collector
exit/sizes and separately corrected analyzer. Not proof of long-run reliability,
repeatability/overhead, enhanced quality or any aggregate TRL gate.

## Preservation, size and next step

Client unchanged/normal exit; zero added game-directory files in runner result.
Independent installed/reference SHA256 recheck:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
No game/controller/PresentMon process observed at analysis. No forced stop or
new probe/gameplay launched; original hot geometry hook remains off.

19 raw files including reanalysis156,970bytes, safely below64MiB frame/2MiB memory
caps. Verified archive
`artifacts/m1/archives/M1-CLOSE-MEASURE-001-20261014-002725.zip`,29,025bytes;
SHA256 `C0F079B4921FB80BA18B3D9C9682E622D2AF32E4BA130A816F9D020046C78FC6`.
Every entry hash verified against source; small raw retained ignored, no deletion.
Observed frame CSV ~14KiB/s in this fixture, not a universal upper bound.

Next: prepare automatic-gated neutral enabled endurance with these methods,
component summaries retained for>=30minutes, paired disabled comparison and
normal removal/reproduction. Reuse this successful measurement qualification;
do not rerun for capitalization, extra counts or cosmetic changes. Sponsor
subsequently confirmed rendering, HUD, cursor and controls behaved normally:
"Yes, no issues noticed" (2026-10-14). CONFIRMED sponsor observation for this
short run only, not a sustained reliability or measured-overhead claim.
