# Performance and test modes

Current: Run130, 2026-10-23. Ordinary-D3D9 retained multi-ship path only. These are evidence policies, not different renderers or different appearance presets. No CDD change, ship suppression or TRL completion claim.

Run134 opt-in diagnostic: append `-StartupProfile` to the public launcher to measure ONLYstartup(128fixedexternalworkerpoints;currently84),includingperbootstrapDraw/PresentQPCandselectedprocess/systemmemory. DefaultOFFinPerformanceANDTest;flagforwardedthroughmodernPowerShell,callerflagrestoredonexit. Nofulltracing,appearancechangeorrefreshcap. Standalonefixturealsoaccepts`--startup-profile`with`--prewarm`,optionally`--menu-idle-seconds 60`;onlythatexplicitexperimentuses100sinsteadof60sfixturewatchdog,gameboundsunchanged. [Run134 findings](../runs/2026-10-24-codex-first-output-startup-profile.md):intermittent~2sblockinsideRemixPresent,notgeometryDrawCPU;idlealoneNOTsufficientcause,exactvendorcauseunresolved. Sub2stargetOPEN;no performancefixclaimedfromnewinstrumentation.

Run135 keeps normal rendering unchanged. Standalone-only `--render-prewarm empty|triangle` and `--isolate-initial-material-library` are diagnosis, NOT usable game presets; normal relay strips warm-up flag and qualification rejects experimental output. Private triangle warm-up triggered early RTX but did not eliminate later full-material stall; withholding master material imports removed most delay in that comparison but changed appearance. See [Run135](../runs/2026-10-24-codex-render-prewarm-experiment.md). Profiler now also measures first complete cohort draw/copy/ACK (88normalpoints,90withwarm-up) within128capacity. Fast bootstrap alone is not complete-scene readiness; no sub2s claim or appearance reduction.

Actual game qualification caveat — [Run131](../runs/2026-10-23-codex-launch-time-allocation-failure.md): first sponsor run010857-214073 failed on native Remix allocator rejection before first returned image. Early device readiness/offline PASS are NOT actual-game startup PASS. High system commitment is a plausible contributor, not proven root cause or full VRAM exhaustion. No source/config rollback or appearance reduction made from that evidence; same launcher retry after freeing memory is pending. Controlled component unload was not demonstrated on this failure; original files/proxy restoration and normal game exit were confirmed.

[Run132 memory cross-check](../runs/2026-10-23-codex-system-memory-crosscheck.md) refines this caveat: previous SUCCESSFUL actual game startup already had43.46GiBsystemcommit versusfailed43.91GiB. FailedphysicalRAMuse was lower. Highcommit alone does not explain failure; Run131's contributor confidence is superseded as possible/unproven. No orphaned harness found; startup-duration/processmemory isolation is the next engineering diagnostic, not a presumed RAM/quality fix.

[Run133 actual-game retry](../runs/2026-10-24-codex-launch-time-stable-runtime-review.md) supersedes the pending-success caveat:042240-261146 succeeded,7instances/6contents,normalexit/hookrestore/unload/filechecksPASS,sponsorstable. Device/runtime ready56.558s before freshdiscovery,but firstmatchingcompositionstill5.783s afterdiscovery(2.180spreparation/activation+3.603spostactivation). Sub2sOPEN;differentmodelsetpreventsexactA/Bclaim. Startupcommit36.48GiB,priorallocatorcauseunresolved. Nextprofileasset-dependentfirstoutput,notthealreadyoverlappeddeviceinitialization.

## Launch-time initialization — Run130

The multi-ship runner starts the real native host immediately after copied-game PID/path verification, before waiting for the observation component. The host loads the pinned Remix runtime, creates D3D9/D3D11 devices, shared outputs and visual shaders, then sleeps until fresh assets are qualified. It does not render a dummy ship or continuously Present in menus. No earlier asset discovery was added.

The supervisor publishes the full initial material library before atomically activating that SAME host. The104-byte activation carries verified game PID/session, model/source, initial catalog mask, asset identity, binding cookie, offset and checksum. Native validation precedes scene load, receiver startup and mesh upload. Replacement assets remain disabled during empty idle and are enabled through the supported runtime API after activation; material/mesh replacement policy for actual rendering remains unchanged. Existing material-only USD policy is still needed, not Toolkit geometry ingestion.

Image/quality configurations are read at early launch and checked again before activation; changing them in menus requires restarting this prepared workflow. Existing live tuning after activation remains separate. No hooks, original assets, light/material values or output resolution changed. Idle activation wait180s, owned workflow285s and existing120s selection/90s tactical limits remain; idle cancellation permits30s for native teardown (observed~13.2s). A failed/invalid activation does not suppress original game drawing.

Device initialization is not full scene warm-up: the existing24bootstrapPresents/10mssleeps and asset-dependent Remix work remain after activation. [Run130](../runs/2026-10-23-codex-launch-time-renderer-baseline.md) documents measured scopes and the pending SFC comparison. No sub2s claim.

## Launch

Performance is the active multi-ship launcher's default:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_multiship_session.ps1"
```

Use bounded detailed evidence when investigating a problem:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_multiship_session.ps1" -Mode Test
```

Both still require the established elevated parent, the familiar skirmish, and normal exit at the two-low-beep request. Selection120s/tactical90s/total285s bounds unchanged. No automatic UAC prompt, extra game run or broader mission qualification is implied. Original ships remain ON with the established camera-left copies. Lights/material/image/quality baselines are unchanged.

The Python runner/standalone fixture accept `--pipeline-mode performance|test`; their compatibility default is test. The public multi-ship launcher explicitly defaults to Performance and forwards the selection through PowerShell7, the game, collector, renderer and receiver using `SFC_PIPELINE_MODE`. Invalid CLI mode is rejected. This flag does not replace source/live/persistent flags that carry functional protocol state.

## Actual differences

| Work | Performance | Test |
|---|---|---|
| Fresh geometry/textures, independent owners, persistent simulation state, camera, shared lights, actual Remix output | ON | ON |
| Content/session/epoch identity, bounds, source/reference hashes, packet checksums, GPU fences, closed-frame matching | ON | ON |
| Owned cleanup, original-client/proxy checks, config provenance, final draw/error/lifecycle-state counters | ON | ON |
| Historical output inventory | Setup only: ledger snapshots once; existing preflight also inventories. Session ledger thereafter | Same efficient ledger; deliberately slow worker scans are not needed for testing |
| Four concurrent worker reservations and committed asset bytes | ON | ON |
| Repeated geometry decode after successful identification | Reuse that worker's validated mesh; recheck exact packet/reference byte hashes | Independent decode retained |
| Extra per-group original-to-packed-upload pixel comparison | OFF; original image hashes and native upload/catalog checks remain | ON |
| Native VB/IB/texture upload readback and byte/row comparisons | OFF; normal validated upload retained | ON |
| Semantic event detail / full identity census | OFF (minimal component summary/header can still exist) | Existing bounded detail/census |
| Native detailed update JSONL / lifecycle event journal | OFF | Existing bounded journals |
| Source latest-state and frame correspondence storage | ON | ON |
| Fixed-capacity native timing/correspondence audit buffers and final exports | Retained: current transport/cleanup/evidence contract still consumes these; memory-only during rendering | Retained |
| Native light diagnostic files/latest-file mirrors | OFF; shared-memory light publication stays ON | Existing files/mirrors |
| Sampled cohort packet file | OFF | <=120 samples |
| `frame-timing.csv`, `live-input.csv`, per-output RETURNED/RECEIVED lines | OFF | ON, bounded/deferred live logging |
| Current-run recursive supervisor output reconciliation | At most once/second; process/error/clock checks still each iteration | Existing reconciliation cadence |
| Supervisor history samples | Every5s | Existing250ms |
| Continuous CPU image readback/high-volume geometry hook/broad capture | OFF | Still OFF; separate offline/probe workflows only |

Performance-mode reports explicitly identify omitted evidence; disabled identity census is not misreported as capture failure. Absence of a detail journal no longer blocks scene preparation: fresh packet, association and exact live-row provenance replace the old mandatory journal hash. No fake journal or fabricated PASS receipt is created.

## Budget protection without the loading stall

`Reservations` performs one historical inventory before tactical loading and checks disk availability. Each external asset worker holds256MiB of conservative temporary disk allowance under a short lock; the ledger tracks held reservations plus actual finalized/partial output. At exit it inventories only that worker's bounded asset directory and atomically replaces the reservation with its actual byte count. Failed output is still charged. Historical directories are never traversed under this lock or in preparation exit checks.

The20,000,000,000-byte output allowance,32MiB evidence reserve, per-asset decode bounds and native retained-memory limits remain. This is session-owned accounting, NOT a filesystem quota against arbitrary unrelated writers. Do not run unrelated bulk artifact producers concurrently; a new independently started session takes a new inventory. The owned job/supervisor remain independent current-run backstops. No claim that the20GB disk allowance permits20GB VRAM.

## Performance result and remaining work

Run130 supersedes host-start-at-first-assets behavior: initialization now overlaps menus. Final-source standalone prewarm fixtures004135-988733performance/004236-434695test pass four owners/three contents, steady595/600 and596/600, unchanged fixture HUD, resize/recreation and clean exit. Synthetic discovery->matchedcomposition6.155s/6.481s, activation->matchedcomposition3.337s/3.305s; host starts only~0.27s before synthetic discovery, so this does not quantify the intended menu-time benefit. Actual SFC run still needed; sub2s OPEN. The following Run128/129 measurements remain historical comparisons, not current-source timing.

Actual sponsor run reviewed in [Run129](../runs/2026-10-23-codex-performance-startup-runtime-review.md): preparation2.569s, hostlaunch2.695s, first matching in-game composition6.600s after first collector discovery. Host-to-first-composition alone3.905s. Sponsor reports7–8s; physical-display timing is not instrumented. The acceptance measure is full fresh-asset-to-in-game-readiness, not the preparation subtotal below. Fighter-arrival blip and earlier discovery are deferred.

CONFIRMED: the historical scan/lock convoy was removed. Real four-asset source-to-prepared benchmark now completes identification+preparation in2.395s and2.371s in performance mode versus2.690s test mode. Preflight inventory2.61–2.68s is separate setup work, not hidden in these numbers. All499 geometry/upload/DDS files per batch match the accepted run byte-for-byte; settings are not reduced to obtain speed.

Final standalone GPU fixtures use three different captured assets plus an independent shared-asset owner:

- Test `20261023-215402-299547-return-fixture`: initial discovery->host launch2.562s, all4owners drawn841times, steady595/600, no partials/resource failures, CSVs present,14cohort samples.
- Performance `20261023-215456-184002-return-fixture`: initial discovery->host launch2.231s, all4owners drawn841times, steady596/600, no partials/resource failures, CSVs absent,0cohort samples.
- Both preserve native fixture HUD/scene pixels, exercise device resize/recreation, and exit normally. Native performance worker separately proves120current updates and no update journal; shared-light test proves both owners' lights without file mirrors. No actual SFC gameplay run occurred in this increment.

**Sub2s fresh-availability-to-textured-render-readiness remains OPEN.** These measurements do not include all native runtime/GPU startup. The next optimization must target remaining asset conversion/identity work and native startup, with explicit justification for retained costs. Earlier asset discovery remains deferred by sponsor. A mode name is not evidence that the target passed.

Do not disable correct-owner identity, GPU synchronization or unsupported-asset rejection to force an apparent fast result. Late unique material-library reload remains a separate known pause. Full scene replacement, arbitrary mission coverage, appearance tuning and vendor patching are outside this change.

## Reproduction / validation

Run136 adds standalone-only loading diagnostics (`--loading-policy async|blocking`, `--material-library flat`, `--native-log-level error`), all requiring the opt-in startup profile/prewarm fixture. Defaults remain inherited loading/layered materials/unchanged logging; normal qualification rejects experimental cases. Native renderer inputs are recorded separately in `gpu/loading-inputs.json`: the observation wrapper's historical async-compilation override does NOT automatically reach the ordinary-D3D9 host. Neither explicit async settings, single-file material publication nor error-only logging eliminated the first-use stall in the controlled cases. Do not promote a switch or trade missing maps for apparently faster output. See [Run136](../runs/2026-10-24-codex-built-in-loading-investigation.md). Optional profiled fixtures retain one sampled compositor BMP, not continuous capture or a new gameplay readback.

Run137 adds standalone-only `--api-texture-prefetch` and optional `--overlap-texture-prefetch`, requiring the existing startup profile/prewarm/multiship fixture. These queue never-drawn public-API materials for the exact generated DDS resources, not SDK geometry. Actual overlap/cache reuse does not establish texture residency or a speed fix; normal qualification rejects these modes and normal gameplay leaves them OFF. Optional profiled standalone fixtures now save at most TWO bounded compositor BMPs (cohort sample and end-of-existing-window sample when matching), not continuous capture. First matching geometry is not a material-ready guarantee. See [Run137](../runs/2026-10-24-codex-public-texture-prefetch.md).

Run138 adds standalone-only `--material-texture-loading stream` (normal `preload`) and `--loading-policy rtxio`, using pinned NVIDIA material loading/RTX IO settings rather than a new loader. Streaming derivatives preserve original generated stages/images and change only the preload boolean; first staging is not thereby proven asynchronous. RTX IO inputs are recognized, but no sub2s result or exact residency fence was established. All experimental fixtures remain ineligible for normal qualification; gameplay defaults unchanged. See [Run138](../runs/2026-10-24-codex-vendor-texture-loading-paths.md). Next profiling should use NVIDIA Nsight Systems process-only, pending tool-install approval, not another custom readiness mechanism.

Use bundled Python/pwsh paths from the current run record. Offline entry points (no SFC launch):

```text
python -m unittest discover -s tests -p "test_*.py" -q
pwsh -NoProfile -File tools/d3d9_proof/build_direct64.ps1
pwsh -NoProfile -File tools/d3d9_proof/build_receiver.ps1
pwsh -NoProfile -File tools/m1_component/build_light_discovery.ps1
pwsh -NoProfile -File tools/d3d9_proof/build_persistent_scene.ps1
python tools/remix_runtime/run_return_fixture.py --multi-ship --multi-ship-resources --pipeline-mode test --prewarm
python tools/remix_runtime/run_return_fixture.py --multi-ship --multi-ship-resources --pipeline-mode performance --prewarm
python tools/remix_runtime/qualify_multiship.py --fixture <completed-test-mode-fixture>
python tools/remix_runtime/run_return_game.py --multi-ship --pipeline-mode performance
python tools/remix_runtime/run_return_game.py --multi-ship --pipeline-mode test
```

Sandboxed Windows child processes could not open the synthetic current-user mapping; the same bounded native tests passed through approved outside-sandbox execution, with no game or security-policy change. Python tests use the writable `artifacts/test-temp` directory rather than the inaccessible sandbox Temp. Qualification remains exact-source/binary/config locked; both modes must pass relevant regressions after changes. Performance mode cannot stand in for missing detailed evidence during a new RE investigation.
