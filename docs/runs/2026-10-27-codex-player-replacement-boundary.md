# Run207 — player replacement: empty-list candidate tested; presentation blocker reproduced

2026-10-27 America/New_York. Sponsor approved implementation of capture-first,
owner-specific player suppression, explicitly stopping if existing buffering
cannot prevent presentation of a suppressed source without its replacement.
Depth behavior and previous aligned-overlay success are accepted sponsor evidence;
this run does NOT reopen their discovery or redo light/material tuning.

## Completed offline work

Read authoritative handoff, approved M1/gate disposition, current replacement
contract, semantic wrapper/capture ordering, ordinary-D3D9 receiver and frame
history. No subagents/helper, SFC, Toolkit or Remix host launched. Fuel Guard
attached existing exact-thread daemon; no new daemon. No active game observed.

Read-only verifier tools/recon/verify_player_suppression.py checks the complete
copied client SHA against accepted2.5.6.4, thirteen instruction anchors and
manager vtable007B8D4C slot180h=006ABFC0. It extracts only439wrapper and1494prepare
instruction bytes into ignored artifacts/player-replacement/run207, never Git.
No client file is changed. Original and copied accepted EXE hashes also pass
existing read-only launcher preflight.

Zero count reaches006ABFFD/006AC004/006AC006 and branches to006AC561 before
polygon-list load at006AC00C. It still returns through state restoration and
AL=1/ret10h at006AC57E..006AC587. Wrapper006AC5A0 keeps its own setup/branching,
including possible two-pass preparation, and ret0Ch cleanup. Known owner scopes
and primary/secondary return sites remain0042E55D/0042E626. No early return or
shared-batch flush suppression was introduced.

Actual x86 excerpts executed in a standalone test with PAGE_NOACCESS polygon
list,32state/branch combinations,225checks. Saved EBX/ESI/EDI/EBP and exact stack
cleanup pass; all tested manager bytes unchanged; one/two prepare calls receive0.
State-vtable calls are TEST DOUBLES, not real D3D7 driver execution. This is a
qualified empty-list candidate, not production owner selection/capture wiring,
hardware state proof, hook-restoration proof or gameplay replacement PASS.
Harness corrections: the fast-availability branch legitimately makes no mode
setter call; byte-return/byte-argument state methods must ignore upper-word
stack garbage. Final checks cover those branches rather than excluding them.

## Confirmed replacement-specific blocker

Current receiver d3d9_game_receiver.h restores previous source color/depth at
line129 BEFORE acquiring/validating returned output in the loop at140. Failed
composition at158 or no ready matching slot reaches164 and presents the restored
source. That source still contains the original ship in the additive workflow.
Therefore a global ready flag or matching asset does not authorize dropping a
future source frame's original mesh. The first source capture and history reset
also have paths that return without composition. No suppression acknowledgement
or unsuppressed alternate source exists in History.

Actual existing scene_frame_buffer::History tested on D3D11 in32and64bit builds:
10checks each, synthetic full-size1920x1080/MS8depth with ship/HUD markers.
Missing-output additive case keeps the original marker. The identical operation
with suppressed source pixels keeps HUD/frame/pose identity but loses the ship.
This is a GPU counterexample using the real History class plus reviewed receiver
control flow, NOT an execution of the full game receiver or a new gameplay run.
No continuous image dumps or retained screenshots.

Matching depth/alignment when output IS present remains accepted. The missing
fact is transactional presentation/recovery when output is NOT present after an
irreversible earlier draw suppression. Disabling suppression on the next frame
cannot reconstruct pixels already omitted from the saved frame. Holding an old
completed frame beyond the existing adjacent-frame rule or adding GPU waits
would change policy; neither was silently adopted.

## Disposition and validation

BLOCKED at the plan's explicit presentation safety stop. Runtime hooks, capture,
wire protocols, renderer and return compositor remain unchanged. No suppression
flag/launcher enabled, no copied-install changes. Offset/tuning workflows kept.
575existing Python tests PASS; strict /W4/WX x86 native and32/64GPU probes PASS;
current1.6.1 D3D9 tuning read-only preflight PASS. Final diff/path/storage checks
recorded in closeout. Extracted code/builds/logs are ignored local evidence.
No full production build/GPU matrix rerun: no qualified production source changed.

Exact files added: tools/recon/verify_player_suppression.py;
docs/reconnaissance/probes/player_zero_count_native.cpp;
docs/reconnaissance/probes/player_replacement_buffer_counterexample.cpp;
docs/reconnaissance/probes/PLAYER-REPLACEMENT-001.md;
docs/reconnaissance/evidence/20261027-player-suppression-boundary.json; this record.
Updated docs/reconnaissance/ship-replacement-contract.md,ship-replacement-readiness.md,
docs/HANDOFF.md and docs/STATUS.md. Existing dirty work/HEAD93e8dba preserved;
index empty, no commit/push. No baseline or active TOML edits.

## Exact next action

Qualify a replacement-specific presentation commit/rollback transaction before
connecting zero-count suppression to gameplay. It must never expose a suppressed
source without matching output, including first activation, single miss,
consecutive misses, reset and disconnect. Specify how an intact full frame is
available on refusal; the existing additive buffer cannot supply that guarantee.
Use the established depth/placement as given, not another discovery run. Do not
present loader readiness as per-frame output readiness or solve normal operation
by continually reverting to originals. No sponsor gameplay needed at this stop.
