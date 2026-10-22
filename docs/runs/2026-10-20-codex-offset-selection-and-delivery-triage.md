# Run82 — player-fixture selection and missing-image delivery triage

2026-10-20. Active: approved M1 ordinary-D3D9 additive execution Gate3/4,
not replacement or formal TRL PASS. Sponsor stopped the first test early:
enemy selected; extra ship flickering/mostly absent. Authorized fixing selection
and delivery. Fuel Guard attached; credit authorization remains in force.
HEADd29111f7,index empty; Run81/prior dirty work preserved. No new gameplay started,
helper/agents, stage/commit/push. Read authoritative handoff, additive plan,
Run81, source/consumer and fresh run evidence before edits.

## Actual game result: delivery FAIL, useful evidence retained

`artifacts/remix-runtime/runs/20261020-223526-278821-in-game`:
CONFIRMED selected owner1/revision1 KFF enemy by first-qualified iteration;
owner2/revision2 fresh FCA packet also present. Previous SDK path also used first
qualified owner, with additional projected-size/clip checks, not a proven native
player flag. Sponsor's observed prior player selection is valid, but not evidence
that the old code had player-identity logic.

23 displayed/1,736 pool publications (~1.3%);1,705 stale rejections,5 unclaimed
overwrites,1 missing-depth,zero invalid/resource/pool failures.1,737 output transfers,
zero omitted light joins;369 fresh current-session light packets,zero invalid/busy.
1,644 current-Present audits lagged one source frame,100 two frames;24 matched.
CONFIRMED original topology frequently completed after the required source frame.
Not transparency, asset corruption or wrong textures; no stale-identity relaxation.

Live median end-to-end28.188ms,p9532.024ms versus typical owner-to-Present15.616ms.
Median measured render/output/transfer cost15.888ms,p9518.092ms, plus median12.113ms
outside those stages (receipt-to-work queue/light/preprocessing combined; their
individual contributions were not yet instrumented). Prior offline criterion of
120 successful images did not establish sustained delivery: it waited for successes
and was too permissive for launch readiness. This is a harness qualification defect.

Game launcher directly reports CHILD_EXIT code=0. Overall runner incorrectly marked
normal_game_exit=false after intentional early exit; fixed future classification.
Duration remains PARTIAL, not a full90s result. Controller8 / target exited before
controlled removal: no proof of live hook restoration/unload; Windows reclaimed
process memory. Renderer/GPU job exit0, no owned processes remain. Accepted critical
files/launcher settings unchanged; copied critical files/proxy restored. Do not
interpret early test termination as a game crash or discard its useful timing.

## Bounded corrections and evidence

New `tools/d3d9_proof/offset_ship.toml` explicitly selects
`assets/models/fca/fca.mod` for the known player-ship fixture. This is NOT generic
native player ownership. No enemy fallback if missing; multiple matching owners
reject rather than guess. Fresh owner/session/revision still authoritative.
New `owner_selection.py`,4 regression tests, relay selection/config snapshot and
qualification hash. Other player classes require a deliberate fixture config edit
and requalification, not an undocumented filename heuristic.

Combined grade/coverage into one worker-side GPU completion batch; no geometry,
lighting/material/image policy, game callback or identity change. Added input-taken
and light-ready timestamps. Build/native checks PASS;357 Python tests PASS.
Standalone actual-proxy fixture224129normal exit/state/resize/pixels PASS,
18,596 changed pixels; timing188 outputs median15.444ms,p9520.638ms,max26.317ms.
Input age median1.696/p953.862ms;light stage.170/6.248ms;render+transfer11.997/
13.909ms. Faster, but not qualified as a flicker fix. Source lead still synthetic.
Generated copies archived/decompressed-SHA-verified to
`archives/20261020-224129-897233-return-fixture-binaries.zip`,SHA256
684049725DC32C9E9993DEA5EB93B0911E49A4BF705CA3E7C137371025570254;
logs/manifests/source records retained. Aggregate9,688,845,179B before next test.

Next bounded optimization: native D3D11.4 GPU fence events in isolated renderer/
receiver workers replace millisecond query polling at post-processing/copy boundaries.
NO SFC callback wait. Explicit5s timeout/device-removal error, preallocated event,
same ownership/freshness checks; unsupported API fails safely, no guessed completion.
Native22 pool checks include uninitialized-fence rejection. Fixed180-frame delivery
window replaces 'wait until120successes'. Internal preparation guard>=90% is a
diagnostic launcher guard, NOT a new CDD acceptance criterion or steady-game PASS.
No re-enabled gameplay launcher until review of that test. Old qualification stale.

Files so far: new offset_ship.toml,owner_selection.py,worker_gpu_fence.h,
test_d3d9_owner_selection.py; modified live_owner_timing.py,
additive_qualification.py,visual_controls.h,d3d9_direct_host.cpp,output_receiver.cpp,
return_fixture.cpp,d3d9_game_output_tests.cpp,run_return_game.py; this record/handoff
and probe status updated as results mature. No source ABI or client mutation.

Runtime/tool state: no SFC; standalone build/fixture sessions may be active while
this WIP section is current. Exact next action: finish worker-fence/fixed-window
offline test, adjudicate delivery and either qualify a corrected launcher or report
the explicit synchronization blocker. Do not claim this issue solved from pixels
alone, reuse Run81's launcher receipt, hold stale ship pixels or suppress originals.

## Final authoritative checkpoint — corrective launcher READY

WIP statements above superseded. Player-fixture selection correction and worker
timing optimization implemented; actual SFC flicker correction NOT yet confirmed.
No buffering,stale-image hold,game-thread waits or source-identity relaxation.

Worker event completion fixture224455:175/180images,median10.886ms,p9515.852ms,
normal exit,pixel/state/resize checks PASS. Extended independently measured fixture
`artifacts/remix-runtime/runs/20261020-224656-410041-return-fixture`:
588/600 displayed in fixed~10s window (98%). Total589draws,598pool publications,
6stale rejections,1unclaimed overwrite,0invalid/resource/depth/busy errors.
782raw inputs,778output transfers,5light joins omitted;afterresize pool drops are
explicit,not fake completions.935exact Present-overlay source pairs,1870records,
no wrong-thread/invalid/drop. One-shot independent readback12,063changed pixels,
original border untouched;state_errors0,resized1,recreated1. All processes exit0,
API shutdown0,no owned processes remain;vendor warning40retained/unresolved.

598 timed outputs: median end-to-end10.7042ms,p9515.5265ms,max18.2797ms. Median/
p95 inbox age1.1477/1.8077ms;light.1551/5.3770ms;render+transfer8.7229/9.8959ms.
These are OFFLINE synthetic lead/replayed-light conditions,not a direct apples-to-
apples game performance claim. Some misses remain;98% is not a steady-game PASS.
Source lead~16.7ms versus actual game typically~15.5ms;SFC contention still matters.

Final launch guard now requires600fixed frames and>=90%displayed,not waiting for
120occasional successes. Guard unit tests reject missing/short/poor/impossible
evidence. It is a diagnostic readiness guard,not a replacement/CDD criterion.
New test_d3d9_additive_qualification.py adds3tests;360Python tests PASS. Native
receiver29wire+18timing+22pool checks,main return37/13/14/22checks anddedicated
native light x86/x64qualification PASS. Native worker-fence uninitialized use
rejected;actual supported event completion/shutdown exercised in GPU fixtures.
Source/binary/config receipt rebuilt from final fixture;read-only launcher
preflight PASS. Old receipt correctly failed before regeneration.

Final result SHA256 D9AADA4F13B6B639ECDD9A30E7E006CEC92C94EF6D005D5421EFAD3B0BE05E10.
Generated binary/image inputs archived to
`artifacts/remix-runtime/archives/20261020-224656-410041-return-fixture-binaries.zip`,
199entries/6,859,645B,SHA256
1A75CD657FFDC370C3E0E0DEAEE303EE44A1B064C2E8F2A12EF1AB3F260AFBB8.
Each decompressed hash verified before exact generated-copy deletion.224455also
archived similarly;source game captures/assets,manifests/logs retained. Aggregate
9,705,574,806B/10GB with192MiB next-run reservation PASS. No game files removed.

Four appearance TOMLs unchanged. Accepted/copied client SHA256 remains
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Parser/JSON/link checks and git diff --check PASS. FinalHEADd29111f7,index empty;
all previous/current dirty work unstaged/uncommitted. No stage/commit/push/helper/
agents. No live tools/owned processes. CDD/milestone allocations unchanged.

Exact next action: sponsor runs SAME Federation-cruiser fixture via
start_d3d9_offset_ship_session.ps1;Codex reviews the new actual-game evidence and
visible flicker report. Do not claim successful game correction yet or change the
player class/config without requalifying. Original ship remains visible.
