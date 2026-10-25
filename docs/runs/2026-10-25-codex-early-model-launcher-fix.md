# Run176 — early-model launcher polling defect fixed

2026-10-25 America/New_York. Sponsor run
artifacts/remix-runtime/runs/early-20261025-171118-187044 failed with
`'dict' object has no attribute 'error'` before verified-child startup polling
completed. This is a parent harness defect, not evidence against the model path.
Its result has no native report, launcher log empty, normal_exit=false, host0 and
accepted/copied critical hashes plus launcher settings unchanged. Do not call it
a completed timing or hook-cleanup proof. Read-only outside-sandbox process check
afterward found no remaining StarFleetOP process. Nothing terminated by Codex.

## Cause / correction

Channel.snapshot returns a dictionary. The early observer's polling loop alone
used attribute-style .error; shared wait_component_ready already uses dictionary
access correctly. Previous standalone fixture skipped the game-specific verified-
child wait, hiding this defect despite successful native/DLL tests.

New tools/early_model_probe/supervision.py uses the explicit dictionary contract,
bounded deadline/enforcement/error/child-exit checks. run_probe.py uses it and
executes verified-child polling for BOTH standalone and game paths. Result records
actual snapshot-check count; qualification requires at least one. No renderer,
native hook/source/binary/wire/limits change. No new game launch.

## Validation / current qualification

7new supervision regressions plus15existing parser tests:22PASS0.088s. Cover
dictionary startup polling, already-ready/native-error, child exit, normal exit,
bounded timeout and malformed missing error key (fails closed).
58native checks rerun PASS including expected pressure/exception controls.
Exact-current actual startup-loaded fixture:
artifacts/remix-runtime/runs/early-20261025-171338-086475.
3actual live-channel dictionary checks,46records23680B/4named timing chains,
zero issues/loss, restored9/active0/hookedfalse, normal child/host0 and unchanged
accepted/copied/configuration checks. WindowsPowerShell5.1CheckOnly PASS with
process-local execution-policy bypass. Refreshed source/test/dependency/binary
lock in artifacts/render-survey/early-model-probe/qualification.json.
[Curated receipt](../reconnaissance/evidence/20261025-early-model-launcher-fix.json).

Run175qualification is historical after these source changes. The current source
is newly qualified; no source-lock check was weakened or manually bypassed.
Prior Run174/175 work preserved; HEAD6d847dd/indexempty/allunstageduncommitted/
nopush. Updated HANDOFF/STATUS/probe/README and reviewed Obsidian tracker.
Existing evidence/caps remain; no deletion/helper/agent/daemon, FuelGuard existing
hook attached. No owned runtime session remains. Game behavior/timing still pending.

**Exact next action:** sponsor retries the SAME start_early_model_session.ps1
command, familiar multi-ship skirmish, normal play/exit at two-beep request.
No extra Remix ship expected. Preserve first failed evidence as harness failure,
not a timing result; analyze the new actual capture before asset-pipeline changes.
