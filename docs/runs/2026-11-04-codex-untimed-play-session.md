# Run292 — Untimed minimal-recording play session

Date:2026-11-04. Sponsor requested a timerless diagnostic-free launcher for
campaign testing, using visual observations to guide subsequent focused tests.
No new gameplay run is claimed by this record.

## Launch and exit

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\native_insertion\start_native_multiship_session.ps1"
```

The normal launcher passes `--play-session`: no session, tactical or menu-selection
deadline and no timed cues. Exit SFC normally to clean up. `-TimedTest` restores
the90-second tactical/285-second prepared checkout. Existing completion/light
diagnostic switches select that timed workflow. PS5→7 forwarding preserves this
choice. Direct Python play mode requires native-all-ships/performance and excludes
diagnostic capture/tuning flags.

ExtraFrame policy, current visual profile, baseline damage, light submission,
native suppression/insertion and resource ownership are unchanged.

## Lifetime and output policy

- `SFC_PLAY_SESSION=1` propagates to the control host, game/capture, renderer,
  receiver and owned GPU job. `SFC_PLAY_PARENT_PID` pins a supervisor process
  handle for passive helper/job lifetime. Game and supervisor exit remain stop
  conditions; output/activation identity and GPU/fence operation limits remain.
- Controller accepts duration0only in explicit play mode; the generated INI has
  one authoritative MaxSeconds value. No bootstrap or activation identity is
  weakened. Passive prewarm/receiver lifetime is also untimed, so waiting in
  campaign menus does not exhaust preparation before the first battle.
- Capture admits newly observed models beyond90seconds. Native light sampling
  no longer stops at90seconds/900samples in play mode, but keeps its fixed queue
  and normal shared-memory publication. No disk mirror is enabled.
- Functional Present/completion consumption remains active. Diagnostic source
  timing arrays and native-gate ring records/drain thread are disabled. Retain
  at most120recentfive-second status samples; console log caps at2MiB and
  discards excess without killing rendering. Exit writes a compact scene/gate/
  cohort summary; no full-frame trace parsing is required after saturation.
- Original/fresh mesh and prepared image/material files remain functional cache
  inputs, created per new asset/revision. This is not zero storage or unlimited
  capacity: existing20GB aggregate allowance,256owners,1024asset revisions and
  GPU residency bounds remain. Do not promise universal campaign object support.
- Normal process exit uses Windows reclamation of game-side hooks plus existing
  owned-worker shutdown/proxy restoration and unchanged-client verification.
  Do not relabel that as a controlled live DLL unload. No new PID auto-attach.

## Validation

Native32/64-bit lifetime tests include delayed activation and continued active
life at simulated one-/two-day times, single activation, unchanged finite-mode
expiry, and explicit zero-duration renderer input. Completion-observer tests
verify inbox consumption without growing diagnostic audit arrays. Actual scene
worker/light tests cover simulated one-day elapsed time, bounded queue shutdown,
and no diagnostic light binary/JSONL accumulation in performance play mode.

Disposable native-helper tests cover cancellation before first output and
supervisor death. Owned-job tests cover zero-duration play, console saturation
without session termination, supervisor death cleanup, and unchanged finite-mode
deadline/log/scratch behavior. The compact exit path accepts no-first-asset exit.
Full Python suite:683tests PASS. No SFC launched by these tests.

Both600-frame native GPU regressions passed: ExtraFrame
`20261104-055652-813162-return-fixture` and Strict
`20261104-055812-200740-return-fixture`. Three owner instances/two reusable assets,
zero pixel mismatches/state errors, correct native depth/text and exit codes0.
These use the finite diagnostic fixture, demonstrating rendering was preserved;
they are not a long campaign demonstration. Native gate1216/cohort193checks
passed32/64-bit; pinned flush12300and actual suppression-hook82checks passed.
Renderer/receiver/control/controller/guard/capture endpoints rebuilt; native-light
worker and both-policy source qualification refreshed. Untimed ON and timed
damage-OFF read-only preflights PASS; launcher parse and diff checks PASS.
Standalone guard tests:7PASS. Python suite683PASS, including3new play-session
helper/summary tests. No game was launched by this validation.

Campaign mission transitions, object lifetime across campaign menus and
long-session capacity remain sponsor gameplay checkout, not an offline claim.

## Next action

Use the normal launcher without diagnostic flags. Enter/leave campaign battles,
switch cameras and exit SFC normally when finished. Sponsor reports visible
problems to choose targeted future observations; no manual timestamps required.
Changes remain unstaged and uncommitted, including Run291 baseline damage work.
