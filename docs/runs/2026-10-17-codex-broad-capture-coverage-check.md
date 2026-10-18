# Codex run — broad capture coverage prerequisite

- Run: SFC-RETURN-20261017-08, 2026-10-17 EDT.
- Task: sponsor requests one broad discovery pull, retaining the output cap.
- Baseline: HEAD e96765a; index empty; existing uncommitted return-path work
  retained. No helper, delegation, game launch, staging or commit.
- Read: HANDOFF, approved M1 plan/current disposition, REMIX-RETURN-001,
  expanded-search run, component/wire/runner, pinned ReShade source and headers.
- Fuel Guard: exact-thread recent-hook receipt verified; no daemon started.

## Question / evidence / adjudication

Can increasing capture volume expose creation and transient depth/target bindings
missed by six engine/presentation checkpoints?

CONFIRMED static: pinned ReShade v6.7.1 source
`artifacts/remix-runtime/deps/reshade/addon_manager.cpp`, function
`ReShadeRegisterEventForAddon`, under `RESHADE_ADDON == 1`, rejects external
application events between `destroy_effect_runtime` and `present`.
Source commit: 8cf85bd12d56697d756d4fcb45e501f5d1b540fa.
`init_resource`, `init_resource_view` and
`bind_render_targets_and_depth_stencil` are inside this blocked range.

Runtime corroboration of limited-build identity:
`artifacts/remix-runtime/runs/20261017-050102-615502-return-fixture/ReShade.log`
reports auto-loading skipped because the build has limited functionality.
Not a new runtime test of each registration: event restriction is supported by
pinned source; existing allowed Present/overlay events remain usable.

Six-phase collector has no owner/name/resolution filter but sees only bindings
current at those checkpoints. Full-rate transcripts would still miss bindings
created and removed between them. Rejected: equate bigger output with exhaustive
coverage, patch/bypass restrictions, silently replace proxy, or revive hot-path
geometry logging. No capture launched merely to repeat this known limitation.

## Proposed capability / envelope — NOT IMPLEMENTED

Seek authorization to qualify matching full-add-on-support ReShade first in the
offline fixture, then ONLY isolated test copy. Preserve existing proxy/config
and rollback manifest; accepted Community Edition install and translator remain
untouched. Pin hash/version, verify forwarding, permitted read-only callbacks,
state preservation and removal before gameplay. If matching build unavailable,
report instead of substituting an arbitrary release.

Then add metadata-only resource/view lifecycle, target bindings, draw summaries
and presentation provenance without owner/name/format/size selection filters.
Enumerate exact event coverage; not an exhaustive GPU trace. Account separately
for startup-created resources and the tactical detail gate.

Proposed tactical detail10s; trace hard2,000,000,000B/warn1,000,000,000B;
overall sponsor ceiling10,000,000,000B includes raw/derived/archive coexistence.
Fixed preallocated queue, explicit loss/saturation counts; no callback disk,
allocation or waits; original drawing continues after capture stops. Actual
metadata rate unmeasured. No images, texture-content or geometry dumps. These
limits are NOT implemented safeguards yet; test budgeting before collection.
After analysis verify a useful archive and document exact generated cleanup
targets; reserve source-plus-archive room. No evidence deleted this run.

Sizing support: 20260905-101749-enabled counted32,409,660 geometry events in~56s,
retaining66,355events in17,393,499CSV bytes. Average-row extrapolation gives~8.5GB
for all events in that interval, NOT an actual full trace or depth-rate estimate.
Geometry hook remains disabled.

## Commands / files / validation / state

Read-only: source/header/record inspection, git status --short,
git diff --cached --name-only, Get-FileHash -Algorithm SHA256, process inventory.
No StarFleetOP found (no-match status is not a failed game exit).
Both clients retain SHA256
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29;
copied dxgi.dll retains
E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7.
Changed only this record, HANDOFF and probe prerequisite note; no implementation
or dependency change. No build/runtime-test claim. Existing artifacts retained.
Whitespace/path checks performed after writing. Index empty; all existing/new
changes unstaged/untracked; no commit. No handoff relies solely on chat.

Result: **BLOCKED pending narrowly scoped dependency-change authorization.**
Observation access, not disk space or evidence that depth does not exist.
Earlier six-phase runner remains available but is not the requested broad
transient-binding capture; do not launch it as a substitute.

Exact next action: sponsor approval to qualify full-add-on-support ReShade in
offline fixture and isolated test copy, preserving original rollback files.
