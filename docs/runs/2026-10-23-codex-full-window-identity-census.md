# Run120 — full-window native identity observations

Date:2026-10-23. Active M1 retained multi-ship integration diagnostic.
Authority:Run119 and sponsor authorization to add the small identity record.
Starting HEAD:d40f8f230fc7504023e4a052c99a81b5a08ce6b4,codex/github-sanitized.
Existing Run113–119 implementation/docs dirty and untracked;index empty;preserved.
FuelGuard attached to actual session;no helper,subagent or game launch.

## Question and decisions

CONFIRMED:Run118 two-ship delivery stable by sponsor observation. Run119 six-ship
test captured four owners,displayed three different assets;FCA explicitly image
budget blocked. Two identical Klingon instances absent upstream of registry.
Native tuple CSV stopped at2015ms;first Klingon capture9265ms. Continuous poses
are downstream of assignment and cannot recover lost native associations.

STRONG HYPOTHESIS:shared visuals plus first-match model lookup collapse repeated
ships. Static ambiguity confirmed;actual native sharing not yet corroborated.
Do not implement that speculative fix before observing incoming/chosen owners.

Added fixed association census across the full gate,not full-rate transcripts.
Existing callback reads/locks and guards reused. No ABI/hook,wire or ownership
behavior change. First-seen/changed tuples retained;repeat counters summarized.
256tuple capacity,27,680bytes storage,<128KiB serialized output;overflow explicit
PARTIAL,not silent completeness. Non-multi-ship paths remain inactive.
Post-stop analysis never runs in the render callback.

Separate considerations deliberately NOT conflated:aggregate128MiB image-output
accounting vs256MiB resident memory;known late-material reload pause;owner vs
shared asset;retirement vs visibility;synthetic vs actual executable evidence.
No cap/material/appearance changes,cache redesign,replacement or vendor patch.

## Files and reproduction

Created:
- tools/m1_component/m1_identity_census.h
- tools/m1_component/identity_census.py
- tools/m1_component/build_identity_census_tests.ps1
- tests/m1_identity_census_tests.cpp
- tests/m1_identity_component_tests.cpp
- tests/test_identity_census.py
- this run record.

Modified this run:tools/m1_component/m1_component.cpp,
tools/remix_runtime/run_return_game.py,tools/remix_runtime/qualify_multiship.py,
docs/reconnaissance/d3d9-retained-multiship-probe.md,docs/HANDOFF.md.
All other existing changes belong to prior runs.

Use bundled modern PowerShell and Python. VS2026Community x86/x64 /W4 /WX,
production /O2 /MT /arch:SSE2,/Brepro. Reproduce:

```powershell
pwsh -NoProfile -File tools/m1_component/build_identity_census_tests.ps1
python -m unittest discover -s tests -p 'test_*.py'
pwsh -NoProfile -File tools/m1_component/build_m1_component.ps1
pwsh -NoProfile -File tools/m1_component/build_light_discovery.ps1
pwsh -NoProfile -File tools/d3d9_proof/build_persistent_scene.ps1
python tools/remix_runtime/run_return_fixture.py --multi-ship
python tools/remix_runtime/run_return_fixture.py --multi-ship --buffer-early-ready
python tools/remix_runtime/qualify_multiship.py --fixture <current-normal-fixture>
python tools/remix_runtime/run_return_game.py --multi-ship
git diff --check
```

Final command without--execute performs preflight only. No SFC launched by Codex.
Exact paths/revisions retained in generated qualification receipt;runtime
dependencies and configuration unchanged. Existing automatic gate,capture
limits,90second window,five-minute workflow and20GB artifact allowance retained.

## Validation / handoff

Portable census tests9checks on each architecture PASS;full-cap/overflow/repeat
accounting and worst-case output bound exercised. Actual x86 production recorder
synthetic fixture:3native ship epochs sharing1visual,2existing-choice mismatches,
all after detailed saturation/frame600/time9265ms PASS. No claim of actual game
ownership success. Python439tests PASS. Remaining build/preflight results below
are updated before handoff.

Final:M1 native regressions PASS;light observer17checks/arch and actual native
worker qualification PASS;persistent18checks/arch and actual120update collector
PASS. Standalone fixtures042843-170556(normal) and042921-889275(earlyready)
PASS:594/600 and600/600steady draws respectively,two distinct FCA/RCA assets,
unchanged native HUD/scene,state_errors0,resize/recreation and normal exit.
Exact source/binary/config qualification refreshed;read-only game preflightPASS.
No actual game/renderer started by preflight. These fixtures do not establish
real six-ship coverage or remove known late-material reload risk.

[Versionable evidence](../reconnaissance/evidence/20261023-d3d9-full-window-identity-census.json)
records exact artifact receipt hashes. Original and copied clientSHA256 both
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29;
copied baseline proxyE35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7.
Existing budget checker inventory12,179,658,445bytes<20,000,000,000;no deletion or
compaction needed this run. Raw fixtures and census fixtures remain ignored.
git diff--checkPASS;HEADunchanged,indexempty,allchangesunstaged/uncommitted.
No active owned game,host,receiver or standalone fixture remains.

Mechanical development corrections:initial synthetic test called nonexistent
lowercase recorder name;corrected to actual RecordHook and rebuiltPASS. One
shell wrapper expanded nested variables prematurely;reran builds directly with
explicit script paths. Neither failed attempt launched SFC or changed assets.

Next exact action after offline qualification:repeat six-ship fixture with the
same three identical Klingon enemies and cycle cameras;review raw census with
capture/registry outcomes before changing ownership logic. Existing originals
remain drawn and the image-budget blocked model may still be absent.

No staging,commit,push or changes to accepted assets authorized/performed.
