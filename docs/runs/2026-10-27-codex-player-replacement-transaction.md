# Run208 — complete-picture player replacement; paused by sponsor

2026-10-27. Parent `93e8dba`. Sponsor authorized implementation, then explicitly
requested an overnight pause. **Implementation is parked; final qualification
and gameplay are pending. Do not offer the launcher as ready yet.** No SFC was
launched by Codex. Nothing staged, committed or pushed; prior dirty work retained.

## Completed implementation

The [versioned transaction contract](../reconnaissance/player-replacement-transaction.md)
records the shared layout, states, source/receipt/output matching, stop protocol,
bounds, API references and exact fixture/gameplay procedures. Run207's isolated
zero-count proof remains valid; its additive missing-frame blocker is now
addressed by a separate default-off transaction, with final qualification pending.

Capture original geometry/resources/transforms first; then only qualified
`006AC5A0` primary/secondary list counts can become zero. Unknown/nested or
non-mainline selected calls invalidate the picture transaction. Other owners
remain native. Primary/secondary share their frame's first accepted decision,
even when the first-list lease expires between them; actual revocation still
invalidates the frame. Stored mesh/list/image data and original control flow stay.

Two pending GPU color/depth pairs and one last-complete pre-ReShade color image
replace the additive restore-before-match sequence in this mode only. Compose
offscreen and commit the entire matching scene/HUD/replacement together. Missing
output holds the complete picture for at most two extra presentations. Sustained
failure revokes suppression, waits for an intact native source and latches native
rendering until restart. No repeated automatic fallback cycle or new refresh cap.
Pending inputs retain the 50ms limit and two-earlier-source-frame admission.
The hold applies to a whole completed picture, not stale ship pixels on a new scene.

The 4,416-byte version1 ledger is inside the existing mapping below12MiB. Shared
output keeps its existing ownership/fences and adds exact source/generation/
owner/revision/epoch bindings. Native stop sets native_stop and waits outside the
render callback at most2s for a newer intact-frame acknowledgement; failure returns
12 with hooks/storage retained, rather than unsafe unload. Process exit is not
controlled-unload proof. Device recreation latches original; unsupported dimensions
do not enable replacement. No game-thread file IO/allocations/waits introduced.

**Selection limitation:** current player identity is the existing unique configured
fixture model (F-CA), not a proved engine player flag. Reject two matching owners;
first gameplay must use F-CA versus a different model. Only that owner's Remix
instance is drawn, at zero offset. Other captured owners remain in the registry
and native drawing. Current tuning/offset files are not changed.

## Files changed by this increment

New:

- `tools/d3d9_proof/replacement_transaction.h`
- `tools/d3d9_proof/build_player_replacement.ps1`
- `tools/d3d9_proof/start_d3d9_player_replacement_session.ps1`
- `tools/remix_runtime/replacement_presentation.h`
- `tools/remix_runtime/player_replacement.py`
- `tests/player_replacement_tests.cpp`
- `tests/m1_player_replacement_component_tests.cpp`
- `tests/test_player_replacement.py`
- `docs/reconnaissance/player-replacement-transaction.md`
- This run record.

Extended existing files (some already dirty before Run208):

- `tools/m1_component/m1_component.cpp` — capture-first suppression, receipt start,
  unknown-selected-path invalidation and acknowledged stop.
- `tools/d3d9_proof/game_output_writer.h`, `multi_scene_runtime.h`,
  `input_admission.h`, `live_owner_input.h` — binding, player-only rendering,
  opt-in two-frame pending admission and cached mode flag.
- `tools/d3d9_proof/run_offline.py` — count new replacement evidence in20GB cap.
- `tools/remix_runtime/scene_frame_buffer.h`, `d3d9_game_receiver.h` — separate
  transaction mode, pending render targets, whole-picture commit/hold/recovery.
- `tools/remix_runtime/live_owner_timing.py`, `multi_scene_relay.py` — unique
  configured model selection, zero placement, player report and default-off launch.
- `tools/remix_runtime/run_return_game.py`, `run_return_fixture.py`,
  `return_fixture.cpp`, `source_timing_fixture.h` — separate game/standalone flags,
  gate, metadata/messages, synthetic native receipts and test-only missing output.
- `docs/HANDOFF.md`, `docs/STATUS.md`, `docs/reconnaissance/ship-replacement-contract.md`,
  `ship-replacement-readiness.md`, `probes/PLAYER-REPLACEMENT-001.md` — current
  checkpoint while preserving historical evidence. Obsidian mirror refreshed if
  unchanged from the repository snapshot.

Ignored artifacts under `artifacts/player-replacement/run208` include build/test
logs, protected input settings, orchestration scripts, SHA-verified archives and
the pause receipt. Proprietary extracted instructions remain ignored from Run207.
No vendor runtime, installation, source assets or live rendering settings edited.

## Validation and discoveries

- Strict32/64GPU transaction tests PASS30checks each. Actual production x86
  recorder fixture PASS12checks: original capture preserved, both lists zeroed,
  unrelated/nested/revoked passthrough. Includes source/generation/revision/session
  rejection, exact GPU pixels, offscreen commit and no repeated image grading.
- 578Python regressions PASS (`python-final6.txt`). One initial new truncation test
  exposed acceptance of a missing padding byte; exact4416byte validation added.
  A restricted Windows-temp run failed access; ordinary-Windows rerun passed.
- Native full component/proxy/gate/contracts/tint/shading/corner/surface/mesh/live
  scene regressions PASS (`native-final4.txt`); dedicated native-light observer,
  shared worker/restoration gate PASS (`light-final4.txt`). Normal/candidate hosts,
  receiver and returned-image builds PASS. Existing synchronized-buffer32/64GPU
  checks PASS. Launcher PowerShell parsing PASS.
- Actual pinned Remix standalone tests exercised transport/composition, known
  background/HUD markers, resize/recreation and graphics state. Earlier steady
  smoke600/600; reviewed598/600 pass with isolated repeats. Earlier failure fixture
  withheld one then two output presentations: resumed after one, latched native
  after two, repeat_max2, recovered1, exact native recovery markers/state0.
- Two test/implementation issues were corrected, not hidden by gate relaxation:
  synchronous test screenshot readback expired a live permit, so readback now
  occurs after the600frame delivery window; and a pending-input50ms check was
  incorrectly applied to an already completed whole-picture hold. The input
  freshness bound stays; the separately approved hold is counted in presentations.
  An earlier run recovered after an isolated hold and is partial evidence, not
  the final steady baseline. No continually renewed stale overlay was added.
- The latest final-source steady fixture
  `20261027-054131-181602-return-fixture` delivered **600/600**, state_errors0,
  resize/recreation exercised and child exit0. Final missing-output fixture
  `20261027-054158-705753-return-fixture` was already running when pause arrived;
  the validation-sequence supervisor was stopped so it cannot start more tests.
  Let only this existing fixture finish cleanup; record its final result in the
  pause receipt. Do not infer qualification from this paragraph alone.
- Initial standalone component fixture C++20 static initialization exceeded its
  default stack before main; the test now uses production C++17/MT and passes.
  No production stack increase or capture redesign. Small diagnosis retained;
  the generated large assembly listing was removed.

The final-source replacement receipt is not yet issued; legacy normal/initial/
late/tuning qualifications must also be refreshed through actual tests. Do not
edit stored hashes. Existing receipts may be stale after Run208. No actual SFC
suppression, weapons/shields depth, live hook-unload or sponsor-visible replacement
success is claimed. No M1/TRL completion or performance improvement claim.

## Bounds, preserved settings and runtime parking

Fixed output allocation about118.65MiB including the extra7.91MiB complete image,
within128MiB. Existing16MiB scene mapping, image/log limits,90s tactical/285s
workflow and20GB evidence ceiling retained. New evidence included in accounting.
Reviewed old/final attempt bulk is ZIP archived with decompressed SHA verification,
per-run `run208-archive.json` receipts and original logs/results retained. Restore
before pixel/raw reinspection. No useful evidence intentionally discarded.

Current `rendering.toml` SHA256
`78177E1D40498186B60C7912B46B897BA08D332DF4A24EA41F92C042E89202C5`;
current `lights.toml` SHA256
`1DBB9BF007927DA891EAFBF93BB3F3C015080BA98F23E375997F881D85861FE0`.
Both match Run208 pre-work backups. FrozenR3 comparison had **not started** when
the sequence supervisor was stopped; active sponsor settings remain intact.
No SFC launched by Codex. Confirm no owned fixture/renderer remains before ending
the pause. Fuel Guard attached existing daemon, advisory only; no new server.

## Exact next action

**Read the final two fixture results/logs and the Run208 pause receipt, then run
the replacement qualifier against those existing runs if they satisfy its checks.**
Afterward refresh normal/initial/late/tuning regression gates, preserving current
settings with a finally-restored temporary R3 comparison, and pass both replacement
and current tuning read-only preflights before handing the sponsor the launcher.
Do not blindly rerun `final_checks.py`: it starts a sequence from the beginning
and archives reviewed outputs. No gameplay while paused. Do not repeat seam,
texture/camera/depth discovery, relax receipt matching, or overwrite newer tuning.
