# Diagnostic tools reference

Last reviewed: **2026-11-02, Run274**. Start with the newest [handoff](HANDOFF.md) for current problems and permitted test scope. Run270 implements the prepared project dome and removes the separate32-entry hull limit; Run273 promotes standard Windows material-file replacement. Run274 removes the five-second material-publication shutdown. Larger stress checkout remains pending.

## Choose the smallest useful tool

| Question | Start here | Escalate only if needed |
| --- | --- | --- |
| Where did startup time go? | Existing startup profile and output-stage timings | Targeted worker observation, then Windows wait trace |
| Is a completion wait GPU work or something else? | `-CompletionDiagnostics` | Worker stacks for the operation; Windows wait/reply stacks for the blocker |
| Why did replacement fall back or stop? | Native gate/cohort records and terminal reason | Focused fixture for that identity/lifecycle condition |
| Is the cost model preparation or file delivery? | Asset timing records and CPU-only preparation probe | Narrow file-open observation |
| Did the returned ship have the right colour, depth and text ordering? | Standalone native insertion fixture | Focused pixel/depth tests; sponsor observation for actual gameplay |
| What does the engine draw besides ships? | Retained rendering-family/effect captures and offline analysis | Explicit bounded survey run, excluding known bulk ship payloads |
| Is this a graphics-driver/GPU scheduling issue? | Existing timing evidence | NVIDIA Nsight, with a defined target and bounded capture |

Diagnostics should stay opt-in. Do not turn them into normal frame-path work or interpret an observation failure as a reason to disable valid rendering. Packet identity, resource ownership and synchronization are functional requirements, not optional logging.

## 1. Current gameplay timing and replacement records

**Entry point:** [native multi-ship launcher](../tools/native_insertion/start_native_multiship_session.ps1).

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\native_insertion\start_native_multiship_session.ps1" -CompletionDiagnostics
```

Use the established Administrator PowerShell workflow and copied game installation. This is a gameplay launcher, not an offline analysis command. Request a sponsor run only when existing evidence cannot answer the question. The separate32-entry hull failure is fixed in Run270; actual large-mission performance still requires gameplay checkout.

- **Without `-CompletionDiagnostics`:** normal performance-mode evidence policy.
- **With it:** adds bounded slow-completion observations in the external renderer. [Recorder source](../tools/d3d9_proof/slow_completion.h) retains up to 64 records per recorder for waits of at least 100 ms or failures; excess detail is counted.
- `SLOW_COMPLETION` separates total time, time in query calls, asset-service work and polling pauses. A “GPU completion” timeout is **not** proof of that much GPU execution: a queued CPU/file operation can prevent the query completing.
- `OUTPUT_STAGE_TIMING` separates draw/present, copy, completion, post-processing and receiver stages. Use its QPC frequency and source identity; do not mix independent clocks or confuse bootstrap output with the first live ship.
- `-LegacyStartupWarmup` explicitly selects the historical extra startup Presents. It is not a tracing flag, a vendor readiness guarantee or a default performance recommendation.

**Offline readers:** [native gate](../tools/remix_runtime/native_gate.py), [native cohort](../tools/remix_runtime/native_cohort.py), [live-owner timing](../tools/remix_runtime/live_owner_timing.py), [startup profile](../tools/d3d9_proof/startup_profile.py), [startup recorder](../tools/d3d9_proof/startup_profile.h).

Typical evidence lives under `artifacts/remix-runtime/runs/<run>/`: `result.json`, gate/cohort evidence, `gpu/job-console.log`, `gpu/job-result.json`, receiver log and accepted configuration snapshots. Read the component's own result: a supervisor failure does not necessarily mean the GPU job failed, and GPU success does not establish a correct overall test.

## 2. Standalone rendering and lifecycle fixtures

Run270 adds [prepared-environment test builder](../tools/d3d9_proof/build_environment_preparation.ps1), [cache/actual IPC tests](../tests/test_environment_resources.py) and expanded [physical-hull GPU tests](../tests/physical_hull_depth_tests.cpp). They check startup identity/cancellation/ownership, exact live adoption and actual owner pixels across the full admitted scene. They do not launch SFC. See [current contract](reconnaissance/prepared-environment-contract.md) and [Run270 results](runs/2026-11-02-codex-prepared-dome-and-hull-capacity.md).

**Runner:** [run_return_fixture.py](../tools/remix_runtime/run_return_fixture.py). It does **not** launch SFC.

Current focused native multi-ship fixture, from the repository directory:

```powershell
& "C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -B tools/remix_runtime/run_return_fixture.py --native-insertion-policy Strict --native-all-ships --pipeline-mode performance --completion-diagnostics
```

Use `ExtraFrame` only for a deliberate timing-policy comparison. The prepared fixture supports controlled delayed startup through `--startup-profile --menu-idle-seconds 60`; inspect current help and the handoff before combining other historical switches.

The standard fixture tests returned pixels, native depth/text ordering, graphics-state restoration, owner/resource lifetime and cleanup. [Cohort qualification](../tools/native_insertion/qualify_cohort.py), [startup-ticket qualification](../tools/remix_runtime/qualify_startup_ticket.py), [receiver-startup qualification](../tools/remix_runtime/qualify_receiver_startup.py) and [texture-memory qualification](../tools/remix_runtime/qualify_texture_memory.py) target their specific contracts. Check each script's arguments and build requirements before execution; these are not interchangeable full-system tests.

**Known diagnostic exception:** Run265/266's eight-family replay changes the standard scene. Its final Python check still expects the standard three-owner/shared-asset fixture. Preserve the reported mismatch, inspect native/GPU evidence separately, and never label it a normal qualification pass.

## 3. Worker-stack sampling: identify the operation

**Local tools:** [sampler source](../artifacts/player-replacement/run255/sample_workers.cpp), [builder](../artifacts/player-replacement/run255/build_observer.ps1), [observer example](../artifacts/player-replacement/run256/observe_fixture.py).

These briefly suspend an owned standalone renderer thread, inspect its stack and, when available, the file-opening arguments. They identified delayed geometry/texture opens and the exact dome DDS pathname.

- Existing probe is bounded to 24 sweeps, an eight-second observation window and 3 MiB output. It validates the allowed executable/session.
- Sampling perturbs timing. Record suspension cost and treat results as attribution, not an unperturbed performance benchmark.
- A repeated `NtCreateFile` stack identifies **where** execution is waiting. It does not identify the Windows filter responsible.
- Private NVIDIA symbols are unavailable. A nearby exported symbol is not a trustworthy private function name.
- Recheck allowed executable path, PID, mapping offsets and trigger before reuse. Artifact probes are session/investigation-specific, not permanent plug-and-play tools.

**Reference:** [Run256 findings](runs/2026-11-01-codex-memory-geometry-delivery.md), [Run265 comparison](runs/codex-run265-recent-edit-startup-comparison.md).

## 4. Windows wait tracing: identify what blocked it

**Current successful entry point:** [start_dome_wait_trace.ps1](../artifacts/player-replacement/run266/start_dome_wait_trace.ps1), invoking [activation-edge v2](../artifacts/player-replacement/run266/trace_dome_wait_v2.py).

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\artifacts\player-replacement\run266\start_dome_wait_trace.ps1"
```

Requires an actual Administrator token for Windows kernel tracing; an ordinary Codex tool escalation does not supply that token here. No SFC actions are required. No new trace is currently needed: Run268 already directly attributes the first-live file-open wait to Defender.

- WPR must report no existing recording; leave other sessions untouched.
- Recording starts synchronously **before the original activation function**, with unchanged activation arguments. It stops seven seconds afterward, with an initial 12-second watchdog.
- Uses a 256 MiB circular buffer, a 128 MiB final trace bound and the existing 20 GB total evidence allowance. Normal fixture deadlines and cleanup remain.
- Outputs `trace-result.json`, `wpr.log`, fixture console and `dome-startup.etl` in a unique `run266/trace-*` folder. Trace collection and rendering outcomes are recorded separately.
- **Superseded:** `trace_dome_wait.py` / `trace_dome_wait-v1.py`. Their readiness-age estimate missed activation. Do not revive that trigger. Passive receiver-log existence is also not a valid activation trigger.

**Analysis toolkit:** installed Windows Performance Toolkit `xperf.exe` (trace coverage/loss statistics) and `wpaexporter.exe` (decoded waits and stacks). Run268 used cached Microsoft symbols at `artifacts/player-replacement/run241/symbols`; no download was needed. Keep future network symbol requests explicit.

**Saved analysis:** [Run268 reader source](../artifacts/player-replacement/run268/read_host_etl.cpp), [WPA profile](../artifacts/player-replacement/run268/host-waits.wpaProfile), [analysis script](../artifacts/player-replacement/run268/analyze_trace.py), [cause receipt](../artifacts/player-replacement/run268/defender-file-open-cause.json). The reader/analyzer contain this run's PID, worker TID and QPC interval: adapt those deliberately for another trace. Do not reuse them unchanged and infer a new result.

For attribution, match the blocked thread's switch-out stack, readying/reply stack and interval against the actual slow output. Check raw event coverage as well as loss counters. Run268 shows `WdFilter → FltSendMessage` waiting until `MsMpEng → FltpFilterReply`, with independent raw timing agreement. This profile does not record FileIO pathnames; earlier worker samples supply the separate dome-filename evidence. Neither method reveals Defender's private scan rule or proves a malware classification.

**Reference:** [Run268 attribution](runs/2026-11-02-codex-dome-defender-wait-attribution.md), [Run267 trigger correction](runs/2026-11-02-codex-dome-trace-trigger-correction.md), [earlier process-creation attribution](runs/2026-10-31-codex-defender-receiver-cause.md). These are distinct protected operations; do not attribute every stall to Defender by association.

## 5. CPU preparation and historical comparisons

- [CPU-only preparation probe](../artifacts/player-replacement/run255/prepare_probe.cpp) and [supervisor](../artifacts/player-replacement/run255/prepare_cpu.py): separate scene parsing, image receipt and copying from Remix/GPU work. Existing paths/input formats are investigation-specific.
- [Eight-family replay](../artifacts/player-replacement/run265/carrier_ab.py) and [resource-access comparison](../artifacts/player-replacement/run266/replay.py): replay captured geometry/images with synthetic identity/camera placement, without parsing game-folder MOD files or launching SFC.
- [Run266 comparison receipt](../artifacts/player-replacement/run266/comparison.json) records the exact historical renderer hash, matching settings and partial outcomes. Its isolated executable is byte-identical to the recorded pre-light renderer; the whole historical game/supervisor environment was not rolled back.
- Fresh-file, early-read and hard-link variants are diagnostic controls, not implemented production solutions. Single successful first frames do not prove a reliable fix.

## 6. NVIDIA GPU tracing

**Nonfatal material retry check (Run274):** [artifact-only denial fixture](../artifacts/player-replacement/run274/delayed_publication_fixture.py) injects PermissionError for seven seconds at master publication in the existing standalone600frame Strict fixture. No game launch or new trace. Same GPU permissions/544MiB reservation/20GB allowance/owned-process teardown as the normal fixture. Saved injection duration/recovery and final retry-status receipt establish survival past the old five-second cutoff. [Run274](runs/2026-11-02-codex-nonfatal-material-retries.md) records recovery and ordinary ExtraFrame comparison; do not enable injection in a gameplay launcher.

**Production material replacement checks (Run273):** [focused tests](../tests/test_material_publication.py) now exercise the actual ReplaceFileW publisher, packaged reader, shared mappings, denied-sharing retry, long paths and injected documented partial failures. Run with the existing Python unittest runner; disposable files only, no game or GPU host. Exact packaged-reader case needs the installed pinned runtime. [Run273](runs/2026-11-02-codex-windows-material-replacement.md) also records both normal-source600frame GPU fixture passes and refreshed launcher qualification. Run271's artifact monkeypatch replay is historical comparison,not needed for normal testing.

**Material publication controls (Run271):** [packaged reader control](../artifacts/player-replacement/run271/arch_open_control.py) loads only the pinned usd_arch.dll and opens disposable files; tests ordinary replacement and DELETE access before/during/after the reader. [Replacement comparison](../artifacts/player-replacement/run271/rename_solution_control.py) contrasts legacy exchange, ReplaceFileW and handle-based POSIX rename, checking old-reader/new-name bytes and mtime. [Standalone replay](../artifacts/player-replacement/run271/replay_solution.py) uses the existing bounded600frame delayed fixture with an artifact-only exact publisher replacement; no SFC or production edits. Requires the existing DLL/GPU execution permissions, not a new elevated trace. No protection settings change. Disposable files are removed; ordinary fixture owns/drains children and retains bounded evidence. [Results/limitations](runs/2026-11-02-codex-material-publication-investigation.md): legacy4/4denied, ReplaceFileW4/4correct, real replay passes; POSIX one readback anomaly remains. These tools are scoped investigations, not production launchers or a historical-handle ownership proof.

**Additional resource/publication diagnostics:** [Run269 replay](../artifacts/player-replacement/run269/replay.py) compares stable dome-file reuse and supported preparation/handle transfer in an isolated host. [Mapping/ownership probe](../artifacts/player-replacement/run269/mapping_probe.py) runs only on the first publication denial: verifies the exact prototype renderer, queries at most8192 memory regions/250ms for the target mapping, then optionally queries Windows Restart Manager owners. It never requests shutdown/restart or accesses SFC. Empty results do not prove absence of locks or filter activity. See [results and partial failures](runs/2026-11-02-codex-dome-resource-preparation-prototype.md). These helpers are not promoted runtime features or general launchers.

**Historical prepared tool:** [Nsight launcher](../artifacts/start_candidate_nsight_trace.ps1) and [trace supervisor](../artifacts/profile_candidate_nsight.py). See the [setup record](runs/2026-10-24-codex-candidate-nsight-trace-prepared.md) and [trace review](runs/2026-10-24-codex-first-nsight-trace-review.md) before reuse.

Nsight Systems provides graphics/API/GPU scheduling evidence. It is not a substitute for Windows filter wait attribution. That experiment had a useful captured report but incomplete profiled teardown; it is not a current clean-startup qualification. Check installed version, candidate/runtime pins, scope, child cleanup and output limits before running it again. Reuse the existing `.nsys-rep`/SQLite evidence where sufficient.

## 7. Engine discovery and visual investigation

| Tool family | Purpose | Status / caution |
| --- | --- | --- |
| [Early-model observer](../tools/early_model_probe/start_early_model_session.ps1) | Locate model information before first draw | `-CheckOnly` avoids execution; older discovery workflow, not the normal renderer |
| [Rendering-family survey](../tools/render_survey/start_render_family_survey.ps1) | Classify non-ship effects, resources and call origins | Explicit discovery campaign; inspect current bounds and exclusions before launch |
| [Effect-resource observer](../tools/effect_probe/start_effect_resource_session.ps1) | Connect upstream effects/resources with downstream activity | Historical focused observation; not automatic live weapon-light integration |
| [Mesh/texture analysis](../tools/m1_component/analyze_mesh_export.py), [texture-path analysis](../tools/m1_component/analyze_texture_path.py), [camera analysis](../tools/m1_component/analyze_live_camera.py) | Investigate captured geometry, associations, transforms and mapping | Offline analysis; preserve canonical captures and original images |
| `tools/remix_ingest/`, `tools/remix_api_proof/` | Toolkit preview and separate direct-API experiments | Separate/historical paths; not required by ordinary D3D9 native replacement |

Broad discovery, screenshots, geometry dumps and repeated on/off demonstrations do not belong in normal gameplay runs. The proposed targeted light-emission recorder remains planned, not implemented or enabled by this reference.

## Evidence and maintenance

- **Source/documentation:** `tools/`, `tests/`, `docs/`. **Local generated evidence/builds:** ignored `artifacts/`. A Git clone will not contain the linked local artifacts, binaries, installed profilers, original captures or game assets. The run records preserve their definitions and findings.
- Keep normal performance evidence minimal. Select one tool for one question; justify additional callbacks, sampling or recording. See the [runtime-check audit](reconnaissance/2026-10-31-runtime-checks-audit.md) and [historical pipeline audit](reconnaissance/pipeline-work-and-diagnostics-audit.md).
- Keep detailed diagnostic bounds separate from functional transport capacity. Retain the existing 20 GB aggregate allowance; check reservations before another capture using [evidence-budget code](../tools/remix_runtime/evidence_budget.py).
- Use [session cleanup](../tools/remix_runtime/session_exit.py) and the established owned-process/recovery workflow. Do not kill unrelated processes or restore a copied proxy while the game is still using it.
- Archive useful completed evidence with hashes and a restoration receipt before removing redundant generated files. Keep original traces/captures, configuration snapshots, rollback information and decisive compact findings.
- Every new diagnostic should record: question, tool/source/build identity, exact trigger, required permissions, scope, caps, timing perturbation, cleanup, evidence location, result and limitations. Link the result here and in the newest handoff. Mark obsolete launchers explicitly.

This reference adds no runtime features or default diagnostics. No source or configuration changes accompany it.
