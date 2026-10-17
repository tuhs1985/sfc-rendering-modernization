# Codex run — 2026-10-13 RT-008 adjudication

- Run ID: 2026-10-13-codex-m1-repeated-private-copy-runtime; active M1/C-01.
  Starting HEAD fee152f, 77 pending path entries from prior work, all unstaged.
  Fuel Guard attach through trusted recent hook; direct connection sandbox denied;
  no daemon/helper/subagent started. No implementation changes in this execution.
- Question: did the prepared bounded repeated-copy test satisfy its contract while
  preserving expected gameplay? Read authoritative HANDOFF, RT-008 definition,
  current run metadata/component summary and scoped prior RT-007 evidence.
- Sponsor ran prepared `start_m1_repeated_private_copy_session.ps1` and reports
  "did as instructed, game ran as expected". Runtime run20261013-225853-enabled,
  PID26148/component0.11, 90s, 32-attempt cap /1-second spacing, 20-second setup,
  fixed657,004-byte bank, 16/32MiB CSV /3MiB corners, geometry/tint/shadingoff.
- Tools: existing PS7/.NET, Python3.12.14 analyzers, Git. Reran
  `python tools/m1_component/analyze_m1_private_copy.py artifacts/m1/runs/20261013-225853-enabled`
  and wrapper/rejections/corner analyzers on the same directory. No native rebuild
  or tests claimed as rerun for this documentation-only adjudication.
- Result **CONFIRMED**:30 fresh pointers,60 scoped prep receipts,30 parent closures,
  zero copy failures/mismatches, all intact at stop. Series spans29.016seconds /
  1,740 rendered-frame intervals. Normal sponsor behavior and clean runtime exit.
  Selected epoch retired51.000s, fresh4 observed51.110s; no lease transfer. Same
  sampled model/source later, but no identity continuity across epochs asserted.
- Original strict32-record criterion unmet; analyzer correctly returns
  ADDITIONAL_BOUNDED_EVIDENCE_REQUIRED with count/limit issue only. Other three
  analyses have empty issue lists. M1 CONTINUES; no criterion relaxation, full
  RT-008 PASS, reusable-buffer or full TRL4 claim. No speculative camera/destruction
  diagnosis or sponsor blame. No blind repeat merely to fill the remaining slots.
- Independently checked installed client SHA256, game/controller absence and no
  remaining generated proxy. Raw18files/1,166,084bytes compressed to131,826-byte
  ZIP, verified entry count and every entry SHA256 against source streams. Small
  raw retained ignored; nothing deleted. Exact archive/binary/client hashes in
  [evidence](../m1/evidence/M1-C01-RT-008-20261013-repeated-copy.md).
- Files created: this run record and runtime evidence. Modified: docs/HANDOFF.md,
  docs/m1/probes/M1-C01-RT-008.md status, docs/m1/m1-c-cte23-increment-plan.md
  current checkpoint. Existing source/requirements/old evidence preserved.
- Known tooling deficiency: metadata retains legacy corner cue array0/15/30 in
  copy mode; actual cue log/gate are authoritative for this run's20s setup/start.
  No silent code correction during runtime adjudication.
- Final checks: document links, Git whitespace/staged state. No staging/commit,
  client changes, runtime launch, new architecture or C-02 implementation. Next
  smallest action: review a bounded fresh-epoch requalification contract, without
  merging owner IDs or recycling existing copies, before any follow-on code.
- Final Git state: fee152f;79 pending path entries (13 modified tracked,
  66 untracked, including prior work), zero staged. Documentation links and
  whitespace checks pass (line-ending notices only); raw/ZIP confirmed ignored.
