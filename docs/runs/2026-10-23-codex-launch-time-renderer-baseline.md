# Run130 — launch-time renderer and lean baseline

Date:2026-10-23 America/New_York; final fixtures2026-10-24UTC. Active work: bounded ordinary-D3D9 retained multi-ship startup/performance increment. M1/CDD gates unchanged; no replacement or milestone PASS claim.

## Authority / starting state

Sponsor: remove costly comparisons; initialize renderer at launch; clean performance baseline. Read authoritative handoff, Run129 actual startup review and Run128 modes/audit; retain existing architecture and safeguards. FuelGuard attached through trusted workflow; no task daemon/helper/agent. Starting HEAD `d40f8f230fc7504023e4a052c99a81b5a08ce6b4`, branch `codex/github-sanitized`, index empty, extensive prior unstaged/untracked work preserved. “Clean baseline” means lean execution policy, NOT discarding work or resetting settings. No commit/push authorization.

Question: can real runtime/device startup overlap SFC menus while detailed verification is confined to Test, with the same fresh-asset, owner/camera, GPU transfer and visual settings path?

## Material decisions / implementation

- Performance skips native managed VB/IB/texture upload readback+memcmp verification in addition to Run128's CPU pixel/decode comparisons. Actual uploads, schema/finite/index/count checks, original/resource/packet content identity, owner epochs, catalog hashes, fences, frame correspondence and cleanup remain. Test retains comparisons. No global removal of asset verification.
- `MultiSceneRelay.start_on_launch(pid)` runs immediately after copied-game path/PID verification, BEFORE observation-component readiness. Starts SAME native64-bit host/pinned Remix/D3D9/D3D11/shared surfaces/fences/shaders via existing owned guard. Empty scene has output extent only; no saved or fabricated ship, source frame or cookie. Host sleeps10ms while idle, no Presents/image generation/game-thread wait. Asset discovery/capture unchanged and still tactical.
- Full initial catalog/material publication precedes activation. Native starts with replacement assets disabled during empty idle, then calls supported `SetConfigVariable("rtx.enableReplacementAssets","True")` after validated activation. Replacement materials ON, replacement meshes OFF for actual scene as before; no vendor patch. Provisional empty stage is not geometry ingestion. Existing policy textures/materials remain required.
- Version1 immutable activation104bytes: magic/version/size, verified PID,4session words, model/source IDs,64-bit catalog mask/cookie,32-byte asset SHA,float offset,reserved0,FNV checksum. Atomic pending->activate file, exact length/finite/bounds/checksum/PID/session validation; native applies late binding, loads actual scene then starts receiver/renderer. Existing current-user mapping remains transport. Control files in owned per-run folder; no new ACL claim. Ready receipt16bytes(QPC,hostPID). Process-start and scene-activation clocks separately recorded, never relabeled to hide startup.
- Image/quality read at early start and checked at activation; menu-time edits require restart. Material/light/quality/image baselines, output resolution, ordinary D3D9 geometry submission and Remix-specific UV policy unchanged. Same camera-left copies, original ships ON, normal UI retained; no earlier discovery, appearance tuning or fighter-reload fix.
- Pre-activation exit/cancel is handled without assets. Native180s activation deadline; total owned guard285s,120s selection/90s tactical limits unchanged. Initial10s cancellation grace proved too short for runtime teardown(~13.2s), changed to30s with owned fallback. Do not interpret deferred shutdown time as asset load time.
- Existing24initialPresents with10mssleeps remain; asset-dependent runtime preparation was NOT eliminated or claimed unnecessary. User's sub2s objective remains open.

## Exact files this run

New: `tools/d3d9_proof/warm_start.h`, `tools/remix_runtime/warm_start.py`, `tests/test_warm_start.py`, this record, `docs/reconnaissance/evidence/20261023-launch-time-renderer-baseline.json`.

Modified (preserving prior edits): `tools/d3d9_proof/d3d9_replay.cpp`, `tools/d3d9_proof/d3d9_direct_host.cpp`, `tools/remix_runtime/multi_scene_relay.py`, `tools/remix_runtime/live_owner_timing.py`, `tools/remix_runtime/run_return_game.py`, `tools/remix_runtime/run_return_fixture.py`, `tools/remix_runtime/qualify_multiship.py`, `docs/HANDOFF.md`, `docs/reconnaissance/pipeline-modes.md`, `docs/reconnaissance/d3d9-retained-multiship-contract.md`, `docs/reconnaissance/d3d9-retained-multiship-probe.md`, `docs/reconnaissance/pipeline-work-and-diagnostics-audit.md`. No semantic-hook/ABI modification this run. Other dirty files predate this task.

## Tools / reproduction

Bundled Python `C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`; bundled pwsh `C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`; VS2026v18.7.3 Win32/x64 build scripts. Pinned Remix1.5.2/current exact dependency/config qualification unchanged. Native build uses `tools/d3d9_proof/build_direct64.ps1` (rebuild,loaded-light11,combinedGPU65 tests).

```text
python -m unittest discover -s tests -p "test_*.py" -q
pwsh -NoProfile -File tools/d3d9_proof/build_direct64.ps1
python tools/remix_runtime/light_discovery.py
python tools/remix_runtime/run_return_fixture.py --multi-ship --multi-ship-resources --pipeline-mode performance --prewarm
python tools/remix_runtime/run_return_fixture.py --multi-ship --multi-ship-resources --pipeline-mode test --prewarm
python tools/remix_runtime/qualify_multiship.py --fixture artifacts/remix-runtime/runs/20261024-004236-434695-return-fixture
python tools/remix_runtime/run_return_game.py --multi-ship --pipeline-mode performance
python tools/remix_runtime/run_return_game.py --multi-ship --pipeline-mode test
git diff --check
```

Python tests TEMP/TMP=`C:\Project\SFC-Modernize Engine\artifacts\test-temp`. Windows current-user native mapping/GPU fixtures require approved outside-sandbox execution; no security-policy change. Last two game commands are read-only preflights without launch flags. Existing exact-source/binary/config locks refreshed normally, never forged/bypassed.

Probe: existing bounded standalone return/multi-ship fixture plus `--prewarm`; three different captured meshes with fresh synthetic session ownership and independent shared-content fourth owner. Read-only captured mesh data, not model-folder geometry import. Actual Remix output through GPU sharing into native D3D11 fixture/ReShade compositor; native scene/HUD oracle, resize/recreation, identity/fence and owned cleanup checks. Four workers/32owners/64revisions/four2MiBslots/native256MiB backing unchanged,20GB generated-output allowance; no continuous image dumps or diagnostic geometry hook. Standalone bounded fixture is not SFC or universal model coverage.

## Results / confidence

CONFIRMED offline:

-467Python tests PASS including4warm activation/layout/rejection/atomic-order tests. Native rebuild/loadedlights11/worker/combinedGPU65 PASS. Exact-source multi-ship qualification (including native persistent tests in both modes) and both read-only preflights PASS.
- Final Performance `20261024-004135-988733-return-fixture`:4owners/3contents,all788draws each,steady595/600matched,0assetpartials/invalid/stateerrors. Test `20261024-004236-434695-return-fixture`:all841draws each,steady596/600,0assetpartials/invalid/stateerrors. Both genuine returned image, original scene/HUD preserved, resize/recreation, normal exit and zero owned leftovers. Both init before activation, complete material library enabled; vendor texture-ingestion logs corroborate actual replacement texture loading. See curated hashes/clocks.
- Pre-activation cancellation with no scene:exit0,zeroowned,13.166s. Checksum-valid wrong-session activation rejected:exit1 as expected,zeroowned,13.265s. Preserved under `artifacts/d3d9-proof/warm-start-tests/latest.json`; these use earlier initialization-policy revision but SAME native activation/cancel validation implementation. Final fixtures test latest replacement-disabled-while-idle policy.
- Accepted/copy client SHA256 both `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`; copied proxy `E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7`, unchanged. No actual SFC launch or installed proxy changes this turn.

Not a speed acceptance claim: latest synthetic Performance discovery->activation2.819s->firstmatchingcomposition6.155s; Test3.176s->6.481s. Activation->match3.337s/3.305s remains. Ready receipt occurs1.954s/1.906s after native process launch. Synthetic host starts only~0.27s before discovery, unlike real menu overlap; cannot infer actual game speedup. First matching compositor clock is not physical display latency. Compare eventual SFC result with Run129 actual6.600s, not Run1282.37s prep subtotal.

Preserved deficiencies: late unique material reload/fighter blip; asset-dependent bootstrap/runtime delay; sub2s target open. Concurrent full Python suite+GPU attempt produced Python MemoryError and receiver HRESULT8007000e; sequential full suite and GPU reruns pass. One10s cancel test timed out despite native Shutdown0; observed13.2s led30s bounded grace. Earlier fixtures are prototypes, not final-source qualification. Vendor mipmap/suboptimal texture warnings persist; do not expand into appearance/mipmap tuning in this task. No new blocker requiring sponsor input for implementation.

## Final state / next exact action

`git diff --check` and referenced-path checks PASS. HEAD/branch unchanged,indexempty; all prior and current work unstaged/uncommitted,no push. No active owned game/renderer/test process. Aggregate generated artifacts16,789,906,111bytes<20,000,000,000 at inventory. No raw evidence removed/archived in this run; retained ignored,curated metadata versionable. No persistent tool/server session needed for resume; qualification receipts generated locally must be refreshed after source/binary/config edits.

Next exact action: sponsor repeats familiar six-ship fixture using default Performance launcher, observe fresh copied ships/normal game behavior and actual initial wait, exit at twoLOWbeeps. Analyze full fresh-discovery-to-matching-in-game-output against Run129 before claiming improvement or selecting the next startup optimization.
