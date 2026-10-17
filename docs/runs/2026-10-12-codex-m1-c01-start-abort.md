# Codex run — RT-003 startup abort diagnosis

- Run ID/date: `2026-10-12-m1-c01-start-abort`, America/New_York.
- Sponsor supplied failed RT-003 runner output. Task: determine failure stage
  and preserve evidence; no automatic retry, source change or commit.
- Baseline fee152f with prior uncommitted tooling/tests/docs; preserved unchanged.
  Read HANDOFF, RT-003 configuration, failed controller/bootstrap logs, native
  start/thread transaction and controller return path. No new rendering analysis.
- Fuel Guard hook verified/direct denied; no daemon/helper/subagent. PowerShell
  Get-Content/Get-FileHash/process inspection, bundled Git/rg, .NET ZIP verification.
- Attempt artifacts/m1/runs/20261012-000603-enabled, PID32508, start00:06:03-04:00,
  controller7; stderr `M1StartW failed: 5`, DLL loaded at60120000. Configuration
  enabled read-only RT-003/90s/36 snapshots/3MiB, geometry/tint/shadingoff.
- CONFIRMED runtime+source relationship: M1StartW code5 is returned when
  suspend_other_threads reports false, before installation loop/g_running=1.
  It resumes/closes handles it had successfully suspended on the failed path.
  No semantic gate/capture or hook installation from this attempt; loaded inert
  DLL/trampoline allocations persist until process exit. Do not claim successful
  runtime restoration/normal exit or qualified numeric evidence.
- Precise Win32 API/thread/error not logged. Startup thread churn/transient
  SuspendThread failure is SPECULATIVE, not confirmed cause. Snapshot/enumeration
  failure is also possible. Missing diagnostics prevent narrower adjudication.
  Static observation: failed OpenThread is silently skipped in current helper;
  safe transaction behavior warrants review, not blind retry/bypassing checks.
- Runner exception prevented run-result/hashes/exit-classification file. Current
  installed client independently hashes to supported SHA256
  4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
  Read-only outside-sandbox process query confirms PID32508 no longer running;
  absence is not evidence of a classified normal exit. Codex did not terminate it.
- Failure output seven files10,684 bytes, no corner/semantic capture. Archived
  exact run to artifacts/m1/archives/M1-C01-RT-003-20261012-000603-start-abort.zip,
  4,003 bytes, SHA2562148CFB8CD00290E9697D8D4F0EEF195CC64A152284F24405DFFB674BF9DD6B0.
  Allseven archived file hashes independently match source. Small raw retained;
  no material deletion. Bootstrap transcript separate/local retained.
- Files created: this record; updated newest HANDOFF and probe attempt status.
  No source/build/test edits, no runtime restart, no security/display changes.
- Validation: return-path/log correlation, client hash, process absence, archive
  hashes, paths/whitespace/status. No native tests repeated without source changes.
- Result M1 CONTINUES; this repeat aborted before activation, not seam failure.
  All pending work unstaged/uncommitted atfee152f. No persistent runtime assumed.
- Exact next action: add bounded thread-transaction API/TID/Win32-error diagnostics
  and validate fail-safe startup/rollback before any retry; no relaxed patch safety.
