# Run128 — performance/test policies and loading bookkeeping

Date: 2026-10-23, America/New_York. Sponsor authorizes minimizing runtime overhead and separate performance/test modes, with sub2s target. This is implementation, not authority to discard correctness or change CDD capability gates.

Authority: Run127 audit, latest handoff, existing multi-ship contract. Starting HEAD d40f8f230fc7504023e4a052c99a81b5a08ce6b4, index empty, existing Run113–127 changes unstaged/untracked. Fuel Guard attached using current thread; advisory credits permitted continuation. No helper, subagent, broad RE, new game run, asset replacement, vendor patch or security-policy change.

## Implementation

Canonical behavior/controls: docs/reconnaissance/pipeline-modes.md. Public multi launcher defaults Performance; `-Mode Test` restores bounded detail. Python compatibility default test. A validated mode is explicitly propagated to game, native observer, external renderer and receiver. Actual source/live/epoch/cohort protocol and fence behavior are retained.

Curated measurement index: docs/reconnaissance/evidence/20261023-pipeline-modes.json. Existing preflight inventories remain before launch in addition to the ledger's single snapshot; “no worker inventory” does not mean no setup cost.

Historical scans removed from worker entry/exit. One initial budget snapshot before gameplay, lock-protected concurrent temporary reservations, actual committed/partial directory-byte accounting, disk/free-space/aggregate reserve checks retained. One asset cannot wait behind full-history scans. Non-session external writers are outside this ledger; independent current-run supervisors remain.

Performance suppresses census/semantic detail, native detail/lifecycle journals, light-file mirrors, cohort sample file, CSV generation and per-output log lines. Shared-memory lighting and latest-state publication precede optional evidence branches. Fixed-size source/correspondence buffers and final summaries remain because current validation/control contracts use them. Source provenance no longer requires detailed updates JSONL in performance mode. Supervisor output reconciliation1Hz/history5s; process/error/time and transport service still run normally.

Performance also skips duplicate pixel comparison and reuses already validated geometry decode with fresh packet/reference SHA checks. Geometry and generated images unchanged. No artistic setting is disabled; requested roughness/emission/lighting retained. Test mode keeps independent decode/upload verification. Native std::cout and existing CSV buffering were inspected: CSVs ALREADY used DeferredDiagnostics before this task; Run127 description of direct per-frame writes was too broad. Current change disables their formatting/collection in performance, not falsely claims a new fix to unbuffered disk writes.

## Files created/modified

- New tools/remix_runtime/pipeline_mode.py; tools/d3d9_proof/pipeline_mode.h; tests/test_pipeline_mode.py.
- tools/remix_runtime/multi_scene_resources.py; multi_scene_relay.py; run_return_game.py; run_return_fixture.py; live_owner_timing.py; qualify_multiship.py.
- tools/d3d9_proof/start_d3d9_multiship_session.ps1; material_binding.py; d3d9_direct_host.cpp; output_receiver.cpp.
- tools/scene_bridge/scene_bundle.py; tools/m1_component/m1_component.cpp; m1_live_scene.h.
- tests/test_asset_preparation.py; tests/test_scene_bundle.py.
- New docs/reconnaissance/pipeline-modes.md; this record; curated evidence JSON. Update docs/HANDOFF.md, retained multi-ship contract and audit pointer/correction. Prior checkpoints retained.

Generated fixtures/binaries/receipts stay ignored. No on-disk client artifact modified by implementation.

## Validation and evidence

463Python tests PASS, including mode validation,4concurrent ledger reservations, aggregate exhaustion, partial-output accounting, no repeated inventory, public launcher selection, shared-publication-before-logging, no-journal scene preparation, identical scene bytes and stale qualified-reference rejection. Initial ordinary unittest execution hit inaccessible sandbox Temp (200errors); rerun with TEMP/TMP pointing to artifacts/test-temp passed. This was environment setup, not suppressed failures.

Native builds PASS: actual component/light core9 and observer17 per architecture; receiver output wire29/source timing18/game output649; persistent18perarchitecture; direct64 loadedlights11/deferred buffer/worker polling/combinedpost65. Initial synthetic observer start failed inside sandbox (`scene worker start/current-user mapping`); approved outside-sandbox qualification passed unchanged. Both native source modes and performance shared lights tested with owned synthetic processes; no game.

Final GPU fixtures:

- Test artifacts/remix-runtime/runs/20261023-215402-299547-return-fixture/result.json SHA256 e73469f9cc9c70df62545fc49600fa98e894aa68fe97c88599f63c15a37dfc83.
- Performance artifacts/remix-runtime/runs/20261023-215456-184002-return-fixture/result.json SHA256 bc7e7a45a553a3c1f2ed051afc9f8f104397887bb7b1bdcc03cdaf4f550771ab.
- Both exact-build inspections PASS,4independent owners/3contents/all841draws, no asset partial/resource failure, intact HUD/scene pixels, device resize/recreation/normalexit. Steady595/600test,596/600performance (not literal perfect delivery). Performance has no frame-timing/live-input CSVs and no cohort snapshots; test retains them.
- Actual shared-light performance proof: artifacts/d3d9-proof/performance-mode-tests/shared-lights-a938f15e28554c47af45fab947d4d640/result.json; owners1/2 observed, no native light files or detailed update journal, native exit0.
- Final4asset benchmark folders215203-958043/215210-616753performance and215217-280470test under artifacts/d3d9-proof/performance-mode-tests. Concurrent identification+preparation2.395/2.371/2.690s. Preflight scans2.613/2.683/2.650s separately.499per-batch scene/upload/DDS files byte-identical;192615091performance/192615195test committed directory bytes. Earlier2.577s before decode reuse is historical, not final-source result.
- Benchmark invokes real PreparationQueue + Relay.identify_asset/prepare_asset on copied fresh capture packets and their saved rows/config. No native MOD geometry import. Copy input setup and initial Reservations inventory excluded from timed critical interval; identification INCLUDED. Raw case reports record spans, scope and outputs. This is not cold-cache or GPU-startup timing.

Exact-build qualification receipt refreshed using final test fixture plus native source tests for BOTH policies. Both read-only run_return_game preflights PASS. No launcher bypass or stale receipt override. Source hashes include mode header/module/tests.

Original and copied StarFleetOP.exe SHA256 both4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29; copieddxgiE35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7. Native/game proxy paths untouched. No SFC running due to this work; standalone jobs report owned normal cleanup.

## Result / next action

CONFIRMED two distinct policies work end-to-end in standalone/native tests, same geometry/material output, no historical worker scan convoy. **Sub2s end-to-end target NOT MET**: real four-asset performance preparation2.37–2.40s (different3asset GPUfixture2.231s to host launch), native runtime startup additional. Do not count a smaller fixture, exclude identification silently, change appearance or omit identity checks to claim the target. Earlier discovery remains deferred. Late unique material reload is still separate known issue.

Next smallest engineering action: profile remaining essential image/geometry preparation and native host startup separately in performance mode; optimize retained work rather than re-enable diagnostics. Prepared launcher may be used for sponsor comparison, but target acceptance remains open; no extra sponsor gameplay is required to continue offline work.

Final Git HEAD unchanged; index empty, prior work preserved, all task changes unstaged/uncommitted, no push. Validation includes parser/source checks, referenced paths, git diff --check and unchanged client hashes. New generated output remains under authorized20GB; no compression/deletion performed.
