# Codex run — M1 visual tint runtime adjudication

- Run ID/date: `2026-10-10-m1-b-rt-001-adjudication`, America/New_York.
- Task/hypothesis: one semantic owner can receive reversible visible tint
  while original tactical operation continues. M1 CONTINUES, not formal TRL4.
- Starting HEAD `b115260c32b28bfff5b148f940cf29317fda747c`, five tracked
  modifications/twelve untracked from preparation; nothing staged.
- Context: HANDOFF, approved M1 plan, M1-B-RT-001, preparation record and
  narrow RGB-source analysis. No helper, requirements change or architecture choice.
- Sponsor ran corrected entry in elevated parent, two-ship fixture, automatic
  gate. Earlier pre-controller PowerShell failure is preserved in preparation
  record, not live proof. Component 0.3 and existing hooks/ABI unchanged.
- Capture: M1-B-RT-001, 60 seconds/3,000 detailed epochs/50,000 events/eight
  owners, 16/32 MiB bounds, 600-second gate wait, geometry hook off.
- Tools: existing x86 controller/component, bundled Python 3.12.14,
  PowerShell/.NET ZIP and SHA-256, bundled Git. Fuel Guard hook receipt valid;
  direct daemon access denied by sandbox, no daemon started.
- Material commands: bundled `python.exe tools/m1_component/analyze_m1_visual_tint.py
  artifacts/m1/runs/20261010-172437-enabled`; Get-FileHash on CSV, installed/
  reference client and archive; Compress-Archive of that run directory to
  `artifacts/m1/archives/M1-B-RT-001-20261010-172437.zip -CompressionLevel Optimal`.
  Archived CSV independently streamed through SHA-256 and matched raw.
- [Curated result](../m1/evidence/M1-B-RT-001-20261010-visual-tint.md):
  **CONFIRMED** bounded visible-control proof, 1,179 tint/restores, two coherent
  owners, 25.343 detailed seconds/3,000 epochs, normal exit/restored hooks/
  unchanged hashes. Sponsor saw enemy magenta then normal, functional gameplay.
- Adjudication: tint analyzer coherent/no reasons; general analyzer PARTIAL
  retained because downstream hook off. No new lifetime, downstream or formal
  performance claim; comprehensive other-surface verification not separately
  attested. No blocker for this bounded proof; remaining TRL4 evidence not waived.
- Raw handling: CSV 8,717,242 bytes, ZIP 210,587 bytes/13 entries verified.
  Small raw retained; ignored/local files need explicit transfer to another host.
- Files created: this record and curated runtime evidence. Modified: HANDOFF,
  RGB analysis and probe runbook runtime status. Ignored analyzer JSON regenerated
  and ZIP created. No implementation edits during adjudication.
- Validation: tint analyzer rerun, archive CSV hash match, client hash match,
  normal exit and hook restoration, post-documentation Git whitespace/link checks.
- Final HEAD unchanged; five tracked modifications/fourteen untracked,
  nothing staged or committed. No runtime process observed during analysis.
- Exact next action: sponsor review of evidence and uncommitted tooling before
  authorizing commit/new increment. Do not repeat settled discovery blindly.
