# Codex run — manual loading-screen baseline check

- Run ID/date: `2026-10-11-m1-manual-loading-baseline`, America/New_York.
- Task: answer whether the shading test permanently modified the base game;
  assess sponsor's manually launched loading artifact without changing settings.
- Starting HEADfee152f; three tracked documentation changes and three untracked
  preflight/runtime/evidence records preserved. No source changes/staging/commit.
- Sponsor reports manual launch also shows transient grid-like/noisy edges,
  disappearing after a while; suggests resolution/refresh mismatch. Occurrence
  CONFIRMED as sponsor report; proposed display cause SPECULATIVE, not diagnosed.
- Fuel Guard trusted hook verified/direct access denied; no daemon spawned.
  Tools: PowerShell Get-FileHash/Test-Path/Get-Process/Get-Content, rg on the three
  runtime entry/runner scripts, bundled Git status and whitespace checks.
- Installed/reference client SHA256 both
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`;
  reference launcher SHA256
  `84D3A5F89A922C4BEE6815CF0614538C3565C4BDB7DB3AA187C552CB727EF890`.
  Exact known baseline matches; prior run-result independently reports unchanged
  client/normal exit. Game-directory winmm.dll and m1-component.ini absent.
- Reviewed workflow writes evidence/config below ignored project artifacts,
  not display settings or assets. Its hooks/source substitution are in-memory,
  restored on stop/discarded on exit. No SFC/controller observed in current query;
  no live module dump captured from the sponsor's manual launch.
- Scope limitation: hashes corroborate executable/launcher, not every asset,
  save or game-maintained setting. Launcher/game may persist their own settings;
  this check cannot certify historical display configuration unchanged.
- Adjudication: baseline/manual reproduction supports that the component is not
  necessary for this artifact (STRONG HYPOTHESIS), not proof of exact cause or
  equal enabled/disabled severity. Preserve M1C-DEF-001 as baseline-observed,
  monitor rather than treat this sole occurrence as a component-specific blocker.
  No reason to alter resolution/refresh/security or repeat RE from this report.
- Files created: this record. Updated: HANDOFF, risk register and curated shading
  evidence with manual baseline disposition; older conclusions retained as history.
  Validation: hashes, path/write-site inspection, links/whitespace/Git status.
- Final repository: documentation only, unstaged/uncommitted; no game files or
  settings edited, no runtime injected, no capture cleanup needed.
- Exact next action: adjudicate remaining C-01 numeric normal/transform input gaps
  before selecting a beneficial enhancement; no implementation authorized here.
