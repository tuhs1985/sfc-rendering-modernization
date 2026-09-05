# Codex Run Record — M1 runner image query correction

- Run ID/date: `CODEX-20260904-M1-RUNNER-FIX`, 2026-09-04.
- Active task: M1 Increment A, disabled baseline preparation; M1 CONTINUES.
- Starting commit: `51ab372`; existing Increment-A documentation, tools and
  tests untracked/unstaged. No tracked changes or staged work observed.
- Question: can the watcher resolve the actual launcher-elevated client without
  requiring module enumeration or an additional privilege prompt?
- Prior attempt: runner detected SFC but `MainModule.FileName` was null;
  `Get-FileHash` rejected the null `LiteralPath` before capture or injection.
  An earlier watcher timed out. Neither produced accepted runtime evidence.
- Evidence reviewed: direct runner, component runbook, Increment-A run record,
  Git status and starting commit.
- Decision: use `QueryFullProcessImageNameW` with only
  `PROCESS_QUERY_LIMITED_INFORMATION`; close its handle in `finally`.
  Reject the earlier proposed hard-coded path fallback: hashing that file would
  not establish that the selected PID runs it. Query failure remains fatal.
- Files created: `tools/m1_component/ProcessImagePath.psm1`,
  `tests/test_m1_process_image_path.ps1`, this record.
- Files modified: `tools/m1_component/run_m1_increment_a.ps1`,
  `docs/m1/probes/m1-a-component-runbook.md`.
- Runner now checks both expected client hashes before capture, records the
  image-query method, prints capture start, and compares both hashes afterward.
- Validation: `pwsh -NoProfile -File tests/test_m1_process_image_path.ps1` passed
  real self-process path comparison and missing-PID rejection. PowerShell parser
  checks passed for all component PS1/PSM1 files. `git diff --check` passed.
- Confidence: local query behavior CONFIRMED; elevated SFC compatibility remains
  STRONG HYPOTHESIS until the next disabled baseline retry. No gameplay run or
  client hash measurement was performed in this correction session.
- Probe: existing `M1-A-BASELINE-001`; next retry uses disabled mode, 120-second
  sample limit and 600-second launch/exit waits. Existing output location and
  limits unchanged. Path query allocates at most 32,768 characters and produces
  no bulk output. No runtime evidence generated this session.
- Blockers: elevated-target access and subsequent telemetry still need live
  validation. Sandbox initialization now works; no security configuration edits
  were made here. No helper invoked.
- Final repository disposition: correction and existing Increment-A work remain
  unstaged/uncommitted. Nothing staged or committed in this session.

## Disabled retry — 20260904-220527

- Command: `pwsh -NoProfile -File tools/m1_component/run_m1_increment_a.ps1
  -Mode disabled -MaxSeconds 120 -WaitForClientSeconds 600
  -WaitForExitSeconds 600`.
- Evidence directory: `artifacts/m1/runs/20260904-220527-disabled/` (ignored).
- Actual client PID 23100 resolved and both hashes verified. Limited image query
  against launcher-started SFC is now CONFIRMED at runtime.
- Telemetry reached 119.507 seconds; CSV 9,489 bytes. Metadata 689 bytes,
  result 274 bytes, module-enumeration error 60 bytes and empty module CSV.
  No component injected. Both final client hashes match the supported baseline.
- Run ended at 22:07:28 ET with `normal_exit_observed=false`; the selected process
  was still discoverable immediately afterward. The configured 600-second exit
  wait did not elapse. Suspected restricted access to Wait-Process is an inference;
  the current catch discards the exact error, so cause is not confirmed.
- Result: image-path correction works and bounded process telemetry collected;
  complete baseline NOT accepted. Normal-exit observation remains unresolved,
  module inventory unavailable, and sponsor tactical-entry timing unspecified.
  Capture begins at process detection, not a confirmed tactical gate.
- Sponsor asked to exit normally after capture. No runtime PASS or sub-gate PASS
  claimed. No staging or commit performed.
