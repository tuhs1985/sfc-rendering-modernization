# Run162 — remove the live iteration-count cutoff

## Completed

Sponsor authorized the next correction from Run161. Fixed IF09 only; no renderer
architecture change, material/loading-policy change, runtime upgrade or gameplay
test. Fuel Guard attached the existing trusted hook; no daemon/helper/agent.

The native host no longer stops live mode after 6,001 outer-loop iterations.
`run_lifetime.h` supplies a small constexpr policy used by the real loop and
input deadline check: live iterations are source/deadline-controlled; offline
replay remains frame-count-controlled. `LiveOwnerInput::next` retains its actual
shared source-stop check, original 90s legacy / 110s game-output elapsed watchdog,
and existing input validation/admission. Receiver130s and supervisor90s tactical
window are unchanged. Skipped/omitted attempts cannot spend a hidden lifetime
budget. No extra sleep, throttle, buffering, worker or logging added.

Changed implementation/test files this turn:

- `tools/d3d9_proof/run_lifetime.h` (new, allocation-free policy).
- `tools/d3d9_proof/d3d9_direct_host.cpp` (outer loop condition/comment only,
  layered on existing Run160 changes).
- `tools/d3d9_proof/live_owner_input.h` (equivalent elapsed comparison through
  tested policy; source-stop guard retained).
- `tests/d3d9_multi_scene_tests.cpp` (43 additional checks).
- `tools/remix_runtime/qualify_multiship.py` (requires the new 93-check receipts
  rather than accepting old 50-check native tests).

Documentation: this record, retained-multiship contract and authoritative HANDOFF.

## Validation

- `build_multiship.ps1`: strict native x86 and x64, **93 checks each PASS**.
  Fake elapsed time tests 60/120/240/1000 attempts per second for the full110s,
  including all-omitted and mixed skipped/output cases (6,600 to110,000 attempts).
  Deadline exact edges for90s/110s, synthetic source-stop at8,000 attempts and
  unchanged finite offline replay counts pass. These deterministic tests exercise
  the production lifetime predicates, not a new110second live/GPU stress run.
- `build_direct64.ps1`: actual host strict `/W4 /WX /O2 /fp:precise` build PASS;
  loaded-light11 checks, deferred diagnostics, private worker polling and actual
  combined-post GPU65checks PASS. No global timer/security setting changed.
- All **504 Python tests PASS9.061s**; existing Pillow deprecation warnings only.
- Standard pinned1.5.2 standalone fixture:
  `artifacts/remix-runtime/runs/20261024-221455-060160-return-fixture`.
  Command: project Python `-B tools/remix_runtime/run_return_fixture.py
  --multi-ship --multi-ship-resources --pipeline-mode performance --prewarm
  --startup-profile` (single invocation).
  Four owners FCA/RCA/FDD/FCA, three unique contents, all4 ACK, no partial assets;
  785 output transfers, **592/600** measured-window frames. Native HUD/scene exact,
  border preserved, state_errors0, resize/recreation, exit0/owned cleanup pass.
  Resize/recreation is consumer/compositor evidence, not automatic host recovery.
- Refreshed exact-source multiship qualification through its existing native
  collector tests; Performance AND Test read-only gameplay preflights PASS.
  No qualification bypass or SFC launch. Source change makes old candidate1.6.1
  qualification stale; isolated candidate must rebuild before future use.
- Initial sandboxed fixture `20261024-221442-667263-return-fixture` failed with
  `[WinError 5] Access is denied.` Evidence retained as failed setup, not a pass.
  Existing scoped outside-sandbox execution then completed the same fixture; no
  administrator/UAC or security-policy change was requested from the sponsor.
- Final diff whitespace and referenced paths checked. No original game/client,
  tuning files, accepted textures or pinned vendor dependencies edited. Existing
  20GB aggregate cap unchanged; no cleanup/deletion needed or performed.

Native host SHA256:
`5e59d67ece5c34101c98c7326062c6099dfb4bbe32f6877647347b10ef2b1314`.
Old accepted host remains recoverable in the Run160 ignored rollback directory;
do not select an old binary without restoring its matching source/qualification.

## Limits and next action

This fixes early lifetime exhaustion, not frame loss, initialization speed or
material residency. The 24-Present startup, serial relay/ACK, single-owner gate,
GPU admission on host worker and union coverage remain unchanged. Do not infer
that IF09 caused the previously observed brief hiccups. No seamless replacement,
universal-model or milestone PASS claim.

HEADfe2eaf7; index empty; all previous dirty work preserved. New edits remain
unstaged/uncommitted, no push. No owned fixture/game/channel left active.

Exact next action: qualify the existing NVIDIA initial-material lifecycle against
first and settled output before attempting to remove transitional24 startup.
