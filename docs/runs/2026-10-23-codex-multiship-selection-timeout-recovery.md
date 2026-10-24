# Run121 — ship-selection timeout and retry recovery

2026-10-23 America/New_York. Sponsor could not retry after timing out during
ship selection. HEADd40f8f230fc7504023e4a052c99a81b5a08ce6b4;indexempty;inherited
Run113–120work preserved. Read HANDOFF,Run120probe/authority,current runner,
controller wait logic,recovery helper and startup tests. FuelGuard attached.
No helper,subagent,commit,push or gameplay launch.

## CONFIRMED diagnosis

Actual attempt artifacts/remix-runtime/runs/20261023-190828-113725-in-game:
gate-controller.log confirms tactical_gate=not_detected,stop_trigger=gate_timeout,
component_state=removed,hook_bytes_restored=true,component_unloaded=true. No ship
observations;inactive census expected because tactical scene never reached.
Result remains historical PARTIAL,not a failed ownership experiment.

Game was still running during timeout cleanup,so proxy/config rollback correctly
deferred. At this review no game running. Read-only preflight failed Copied proxy
mismatch. Existing verified recovery helper recognized only broad/depth capture
manifests,not newer ordinaryD3D9 additive/multi-ship full-support transactions.
Initial recovery refused safely before writing anything.

## Changes

tools/remix_runtime/recover_broad_session.py:recognize recorded
D3D9-ADDITIVE-001/D3D9-MULTISHIP-001 transactions with nonempty recorded
full_support_qualification. Exact backup hashes,knownproxyallowlist,othercritical
inputs,normalclosed-game requirement,exactrunpath and ambiguity refusal unchanged.
Automatic pending recovery and explicit recovery use the same predicate.

tools/remix_runtime/run_return_game.py:multi-ship gate wait120seconds instead90,
same duration passed to nativecontroller and Pythonwait;legacy90unchanged.
Print setup allowance before waiting,record exacttimeout in manifest.
Overall285second ceiling unchanged;nominal120selection+120semanticwatchdog+
30normalexit+15setupreserve. Remaining globaldeadline still strictly enforced;
this does not grant unlimited selection time or increase capture/log budgets.

tests/test_return_startup_safety.py:multi timeout/unchangedbudget,known/unknown
transaction classification,actual mocked multi retry restoration/livegamerefusal.
Updated HANDOFF,probe and this record. No native DLL,rendering/material policy,
identity assignment,source assets or accepted gameinstallation modified.

## Recovery and reproduction

Use bundled Python/PowerShell from prior Run120. Commands:

```powershell
python -m unittest discover -s tests -p 'test_return_startup_safety.py'
python tools/remix_runtime/recover_broad_session.py artifacts/remix-runtime/runs/20261023-190828-113725-in-game
python -m unittest discover -s tests -p 'test_*.py'
python tools/remix_runtime/light_discovery.py
python tools/remix_runtime/run_return_fixture.py --multi-ship
python tools/remix_runtime/qualify_multiship.py --fixture <new-completed-fixture>
python tools/remix_runtime/run_return_game.py --multi-ship
```

Explicit recovery succeeded;recovery.json records gameabsence,verified rollback
and all restored criticalhashes. Historical failed result untouched. Copied
ReShade configuration/test proxy restored from exact recorded backups;no manual
binary replacement or launcher bypass. No game-process kill.

11startup testsPASS,442full Python testsPASS. Nativeworker qualificationPASS.
Standalone fixture20261023-191449-284367-return-fixturePASS:two distinct FCA/RCA
assets,592/600steady draws,nativeHUD/sceneexact,state_errors0,resize/recreation,
normal ownedexit. Exact source/binary/configqualification refreshed;read-only
launcherpreflightPASS. No SFC launch. gitdiff--checkPASS,indexempty,HEADunchanged.
Original/copied clientSHA256both
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Copied proxy restored to
E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7.
Recovery receipt confirms all seven frozen critical inputs restored,not onlyproxy.
No additional native rebuild necessary:only Python runner/recovery/tests changed.

Exact next action:repeat same six-ship fixture within120seconds of setup message,
cycle cameras,exit at normal two-low-beep request. Full-window identity question
unchanged. No claim this timeout attempt establishes missing Klingon associations.
All work remains unstaged/uncommitted;no generated binaries/captures added to Git.
