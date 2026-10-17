# Codex run — M1-C-RT-001 runtime adjudication

- Run ID/date: `2026-10-11-m1-c-rt-001-adjudication`, America/New_York.
- Active M1 C-01 lighting-control diagnostic, M1 CONTINUES. Sponsor authorized
  runtime, launched prepared entry, reported enemy magenta then shading-off;
  follow-up explicitly confirms shading returned and no other skirmish issues.
  Mild loading-screen glitching disappeared upon entering session.
- Starting HEAD `fee152f`, prior preflight HANDOFF modification and untracked
  preflight record preserved, nothing staged. No source implementation changes.
- Sources: newest HANDOFF/probe/preparation, actual run metadata/summary/CSV/
  analyzers/controller logs/run-result, prior risk register, sponsor observations.
- Fuel Guard trusted hook verified/direct denied, no daemon spawned. Bundled Git,
  PowerShell JSON/hash/ZIP/process inspection, bundled Python3.12.14 shading
  analyzer; no helper, architecture choice, broad RE or gameplay automation.
- Runtime tool versions/config: component0.4, x86 MSVC build via entry, existing
  controller/PS7.6.5 workflow. Actual DLL/controller SHA256 and exact run path in
  [curated evidence](../m1/evidence/M1-C-RT-001-20261011-shading-off.md).
  Probe M1-C-RT-001, auto gate600s wait,75s tactical,120 detailed epochs/10,000
  events/eight owners,16/32MiB cap,96 fixed summary samples; hotgeometryoff.
- Material analysis: Get-Content/ConvertFrom-Json of named run files, sampled
  identity grouping, general generated evidence review; `python.exe
  tools/m1_component/analyze_m1_shading_off.py artifacts/m1/runs/20261011-180531-enabled`.
  No issues; visual pending automated status deliberately preserved.
- Result CONFIRMED:76 stable selected-owner samples, source0x23→0x21,
  mode5/five lit referenced entries,6,649 lighting-off substitutions/releases,
  428 cue/releases, zero safety failures/live scopes, restored original source
  after58s. Sponsor visible off/return corroborates runtime. Two early owner
  chains distinguishable; no fresh downstream correlation or lifetime proof.
- Exception00509843 finite11,091 vs11,087 gated epochs, unchanged/unassigned.
  Loading glitch is confirmed sponsor report, causal attribution SPECULATIVE;
  rejected inference that successful tactical behavior proves loading noninterference.
  Hooks execute before gate; no timestamp/image/present evidence isolates artifact.
- Cleanup: controller removal and restored bytes true, exit classified exited,
  client unchanged; installed/reference/launcher hashes independently rechecked.
  No SFC/controller observed. No on-disk original or game-directory proxy/config
  modified by this direct-injection workflow; post-run absence verified.
- Raw handling:13 files415,692 bytes; CSV336,573/summary20,815. Compress-Archive
  exact run directory to ignored archives/M1-C-RT-001-20261011-180531.zip,
  19,954 bytes. All13 entries streamed through SHA256 and matched original files;
  archive hash in curated evidence. Raw small/retained; no material deletion.
- Files created: this record and curated evidence. Modified: newest HANDOFF,
  M1-C-RT-001 runtime disposition and risk register. Preflight work preserved.
- Validation: analyzer rerun, source/release/cap checks, archive hashes, client
  hashes, hook restoration/exit classification, local links/whitespace/status.
  No build/tests repeated because source unchanged and entry completed validation.
- Final repository: HEAD unchanged; documentation changes unstaged/uncommitted,
  no stage or commit. No persistent tool/admin session assumed.
- Exact next action: prepare bounded paired loading-screen comparison for sponsor
  review; this completed diagnostic does not authorize enhancement implementation.
