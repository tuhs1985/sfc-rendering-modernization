# Codex run — M1 neutral endurance adjudication

- ID/date:2026-10-14-m1-endurance-runtime. Active M1 closure/reliability, not M2.
- Sponsor completed prepared test and confirmed same tactical session/no pauses
  or rendering/HUD/cursor/target/control issues; reports enemy destruction near end.
- Baseline `fee152f`, inherited119 dirty status paths, none staged. Fuel Guard
  trusted hook verified; no daemon/helper/subagent. No new gameplay launched here.
- Question: did>=30min neutral semantic operation preserve tactical behavior,
  stay bounded, generate usable measurements and restore/unload normally?
- Authority: HANDOFF, approved M1 plan plus SFC-GATE-20261014, probe
  M1-CLOSE-ENDURE-001, qualification baseline002725 and preparation run record.

## Evidence and adjudication

Read run `artifacts/m1/runs/20261014-005117-enabled`: exact config/metadata,
controller receipts, component summary/detail/analysis/log, frame/memory raw and
summaries, run result, loaded-modules inventory. Reviewed existing RT-006/007/008/
009 exclusion evidence and current classification code, not new reverse engineering.

CONFIRMED: controller gate-detected duration trigger1830s, independent elapsed
tick1831.265s including shutdown/polling,109,688 semantic frames,107,951 PID-frame
records over1800s,1,800/1,800 available memory samples, normal sponsor operation,
restored hooks/unloaded component/normal exit/unchanged client.60Python tests pass.
Exact measurements, chain identities, finite exceptions and confidence limits in
[runtime evidence](../m1/evidence/M1-CLOSE-ENDURE-001-20261014.md).

Initial two chains coherent; later detail intentionally saturated.9 retirements
in summary but not initial CSV; no new full lifetime-history claim.101,922 observer
classification exclusions exactly reconcile to known signatures004EFC49,
00413B2D and associated0042FDD5 owner-missing, no signature/owner/thread overflow.
Kept unknown caller category/fail-open policy, no scope broadening. Generic
analyzer retains partial/review because geometry off; not a new lifetime/draw
proof. Rejection analyzer remains lead-review-required, not auto-harmless.

Mean frame16.67375ms/p9518.4722/max64.4624; six5min windows stable. Memory initially
grows then dedicated GPU provider usage plateaus~675MiB; private memory not
progressively increasing across whole run. Not a causal-overhead or leak-freedom
claim. Disabled baseline10s is descriptive comparison, not workload-controlled
30min baseline. Explosion timestamp unobserved; last30s component interval has
no frame telemetry, so no claim explosion was necessarily inside it.

## Material configuration discrepancy

On-run loaded modules show local DDRAW.dll/D3DImm.dll plusDXGI.DLL. Read-only
current file product metadata identifies dgVoodoo2.8.6.5/ReShade6.7.1; exact hashes
added to current manifest. This contradicts historical no-external-renderer claim.
No DLL installed/modified/removed by this execution. Existing timestamps predate
tests, not proof of prior loaded configuration. Qualified disabled baseline lacks
equivalent module/config inventory. Preserve successful endurance on actual stack;
M1 CONTINUES until dependency baseline/scope reconciled, not an automatic new
endurance run, failed seam or authorization to remove wrappers/select architecture.

Current post-exit configs copied read-only to ignored
`artifacts/m1/config-snapshots/20261014-005117-postexit`, each source/copy hash
verified before any future launch can rewrite them. These are post-exit snapshots,
not retrospective frozen start configs. ReShade.ini PresetPath `.\SFCOP_1_Preset.ini`,
PerformanceMode0; preset activation/visual contribution not adjudicated here.

| File | Bytes | SHA256 |
| --- | --- | --- |
|dgVoodoo.conf|15,429|1A9A53DC8185C7DFD7E984B2CAA19A615AD475FD5C0FC26DC6842E5C43209DCD|
|ReShade.ini|2,763|D1CC3C67F48EFCA88B43A4EBB81A11C995F77CB40159E43BECE2290270E59FF8|
|ReShadePreset.ini|0|E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855|
|SFCOP_1_Preset.ini|14,785|B84F1F3AD77222B3E642057168FC9EE418EBEA804E7AD3C807D780960E718105|
|sfc.ini|1,421|FB3689DCC28AF4C3C86DA7E0E4989F2C267D8AA640572C052EA16B7BB53FB0C4|

## Commands, tooling, validation and storage

PowerShell7.6.5, Python3.12.14 actually queried; bundled dependency paths same
as preparation. Signed/pinned PresentMon2.3.1 as in probe. No fresh build needed
for analysis-only change. Sandbox OS CIM query denied, no OS build inferred.

- Existing launch: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File
  "C:\Project\SFC-Modernize Engine\tools\m1_component\start_m1_endurance_session.ps1"`.
- `python tools/m1_component/analyze_m1_rejections.py
  artifacts/m1/runs/20261014-005117-enabled`: LEAD_REVIEW_REQUIRED,issues empty.
  Fixed narrow probe-ID allowlist to include M1-CLOSE-ENDURE-001 (old generated
  label defaultedRT-005); added subprocess/metadata attribution regression and
  regenerated derived rejection report only. No original capture overwritten.
- `python -m unittest discover -s tests -p 'test_*.py'`:60 pass with process-local
  TEMP/TMP existing absolute artifacts/m1/test-temp.
- Independent Python CSV/JSONL aggregation: exact PID/runtime/swap-chain/drop
  counts, min/max timestamp gaps, nearest-rank p95, six300s windows, GPU/private
  min/max/medians/first-last; source fields and results in evidence for reproduction.
- Read-only Get-FileHash for client/reference/launcher and loaded local DLLs;
  Get-Item VersionInfo for wrapper product/version. Exact runtime client/tool
  hashes in evidence/metadata; client unchanged independently verified.
- Compress-Archive and per-entry .NET SHA256 verification. Raw22files27,345,757B;
  main archive4,036,052B SHA256
  `2380E4A9C905EC7550621F7E02C377531424739D273428B1EC1EFBB1095E7220`.
  Path `artifacts/m1/archives/M1-CLOSE-ENDURE-001-20261014-005117.zip`.
- Postexit config archive12,872B,
  `artifacts/m1/archives/M1-CLOSE-ENDURE-001-20261014-postexit-config.zip`, SHA256
  `0471305078C24E9AA0CD4BF4A164040383FCDEEAF3F5A6C9CBA633DA3B5AB601`.
  Raw configs34,398B; source/copy and archive-entry hashes verified. Small raw
  retained ignored, no deletion.64MiB frame/2MiB memory/32MiB semantic caps respected.

## Changed files / result / next action

Added this record and `docs/m1/evidence/M1-CLOSE-ENDURE-001-20261014.md`.
Updated `docs/HANDOFF.md`, `docs/m1/m1-a-development-manifest.md`,
`docs/m1/m1-a-risk-deficiency-register.md`, `docs/m1/m1-closure-evidence-checklist.md`,
`docs/m1/probes/M1-CLOSE-ENDURE-001.md`,
`tools/m1_component/analyze_m1_rejections.py`, `tests/test_analyze_m1_rejections.py`.
No component/controller/renderer implementation, hooks, requirements or game files
changed. Captures/config snapshots and binaries remain ignored.

Endurance PASS on tested stack. M1 CONTINUES pending dependency-baseline closure
review, no formal aggregate TRL4 or M2 work. Git diff/local links/status checked;
inherited dirty work preserved, none staged/committed atfee152f. No active game/
controller/PresentMon process observed. No admin/tool/session state assumed.
Final validation: main archive22/config archive5 entries hash-verified;113 local
Markdown links valid, diff check passes,122 pending status entries,0 staged,
HEADfee152f; config snapshots correctly ignored.60Python regressions pass.
Exact next action: reconcile launcher graphics configuration/dependency baseline
against preserved current inventory/snapshots, then present a scoped M1 closure
decision. Do not repeat30min, remove wrappers or make new enhancements blindly.
