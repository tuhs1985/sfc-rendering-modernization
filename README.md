# SFC Rendering Modernization

An experimental rendering-modernization project for **Starfleet Command: Orion Pirates**, tested against the Community Edition client **2.5.6.4**.

For development, start with [contributing](CONTRIBUTING.md), the
[current checkpoint](docs/HANDOFF.md), the [repository map](docs/REPOSITORY_MAP.md)
and the [staged migration roadmap](docs/REPOSITORY_MIGRATION.md). The overview and
videos below include dated demonstrations; the current handoff and linked
evidence distinguish today's baseline from historical experiments.

The aim is to improve tactical 3D rendering while preserving gameplay, controls, tactical information, missions, campaigns and save continuity. This is not a rebuild of the game engine.

**Current result:** we capture fresh ship geometry and scene state from the running game, submit it through our own **ordinary Direct3D 9 adapter**, and let NVIDIA RTX Remix render it. GPU-shared output returns to SFC's actual colour/depth targets before later native shields, effects and text. Supported multi-ship replacement has passed gameplay checkout, including shared-model instances. The latest aggressive camera-switch checkout showed no visible native/enhanced swaps; small startup/admission exceptions and the earlier cloaked Romulan's upstream admission remain documented. Full-scene replacement is not established. See the [latest gameplay review](docs/runs/2026-10-31-codex-native-camera-stability-checkout.md).

The multi-ship path accepts fresh supported assets, with independent retained owner instances and shared geometry where content matches. The older player-only diagnostic still uses a unique Federation heavy cruiser (`fca.mod`). The new default-off multi-ship replacement removes that filename restriction. See the [current checkpoint](docs/HANDOFF.md).

The [player gameplay checkout](docs/runs/2026-10-31-codex-native-insertion-gameplay-comparison.md) passed both synchronization policies, with normal cleanup and unchanged client files. The [multi-ship extension](docs/decisions/2026-10-31-native-cohort-contract.md) admits one completed scene and inserts each supported owner at its own original mesh boundary. Shield extraction/replay remains parked.

This is a research/development workspace, not a ready-to-install graphics mod.

Alpha packaging is being planned. The [release readiness assessment](docs/releases/ALPHA_READINESS.md)
records required features, existing evidence, deployment gaps and the proposed
test-package sequence. No downloadable alpha or portable installer is ready yet.

## Videos — in-game tests

[![SFC Rendering Modernization — Live RTX Remix Rendering Test](https://img.youtube.com/vi/NCYvT6ypXLY/hqdefault.jpg)](https://youtu.be/NCYvT6ypXLY)

Click the preview to watch on YouTube. The test shows the original FCA alongside its live Remix-rendered copy, with a 360-degree camera pan to demonstrate the lighting response. This is the additive integration proof, not original-ship replacement.

[![SFC Rendering Modernization — Video 2](https://img.youtube.com/vi/O-hdw14ai0E/hqdefault.jpg)](https://youtu.be/O-hdw14ai0E)

**Video 2:** the next SFC rendering modernization demonstration.

[![SFC Rendering Modernization — RTX Remix Weapon Light Test](https://img.youtube.com/vi/0iGcIH7QHTo/hqdefault.jpg)](https://www.youtube.com/watch?v=0iGcIH7QHTo)

**Weapon light test:** SFC's live weapon-light state drives lights in RTX Remix,
illuminating the replacement ships inside the game. This demonstrates functional
weapon lighting; brightness and source size remain adjustable for further tuning.

## What works today

- **Semantic capture:** observe ship/model ownership before the engine reduces it to generic draw calls.
- **Fresh assets:** capture supported rigid triangular meshes and their texture associations from the running game, rather than substituting a prepared ship model.
- **Live scene connection:** supported fresh ships and fighters can be retained through the D3D9-to-Remix additive path. Tested coverage is recorded per run; it does not establish every model or rendering family.
- **Persistent tracking:** a bounded registry retains qualified ship identity, geometry revisions and simulation-derived transforms independently of camera visibility. A camera switch does not itself retire or reload a living ship.
- **Standard graphics input:** a separate 64-bit host builds D3D9 vertex/index buffers and texture bindings from the captured data, then submits ordinary indexed triangle draws that Remix intercepts.
- **In-game return:** a project ReShade add-on inserts matched output into the copied game's native colour/depth targets before later shields, effects and text. Per-owner coverage authorizes suppression only for supported ships included in that completed output. Older offset/buffered modes remain diagnostic references.
- **Lighting and materials:** qualified native directional and weapon-effect light observations drive Remix lighting through separate light bindings. Editable configuration controls light types, brightness, source size, surface roughness and recovered illuminated markings.
- **Damage layers:** baseline damage decals follow SFC's current stage. Two KDD/FCA skirmishes visually confirmed application and corrected first-use transparency. Repair/removal is demonstrated offline; other families still need gameplay qualification.
- **Safety and evidence:** bounded capture, identity/lifetime checks, fallback to original rendering, executable-hash checks and documented test/cleanup procedures.

These are demonstrated capabilities within the recorded test conditions—not claims of complete compatibility, visual parity or final renderer architecture. The semantic integration proof is established; that alone is not an overall TRL 4 or finished-modernization claim.

## How it fits together

```text
Running SFC (32-bit)
  ├─ original simulation, rendering and tactical UI continue normally
  │    → existing compatibility wrappers → D3D11 native game frame/depth
  │                                                │
  └─ semantic model/owner hooks + simulation state   │
       → bounded current-user shared-memory bridge │
       → worker prepares fresh geometry/textures   │
       → 64-bit ordinary D3D9 adapter               │
       → RTX Remix intercepts our D3D9 draws        │
       → GPU color/depth/coverage output            │
       → synchronized GPU output handoff            │
       → project ReShade compositor ←───────────────┘
       → actual SFC game window (qualified meshes replaced; native effects/UI continue)
```

### 1. Read meaningful scene data inside SFC

The prepared runner loads a project-controlled **32-bit component** into a verified separate test copy. It uses reversible **in-memory function detours upstream inside SFC**, where the game still knows which ship owns a model, its selected mesh/LOD, resource associations and transforms. It forwards the original calls with the required machine state preserved. The original executable on disk is not patched.

The established chain is `tEntityShip → t3DVisual_Model → tModel0 → graphics manager → 0x006AB410 → native draw`. The downstream address is a validation anchor, not the primary semantic capture point. This is not a full-rate transcript of every polygon or a new proxy translating all of SFC's graphics calls.

The component captures supported geometry and group/resource associations when a qualified asset is first needed. A persistent registry tracks session-local owner epochs, asset revisions and current simulation-derived world transforms. The active game-camera observation supplies view/projection state. Visibility and object lifetime are kept separate: looking away does not mean the ship has ceased to exist.

### 2. Move bounded data out of the game

Fixed-capacity, session-identified, current-user shared memory carries asset packets and coherent owner/state publications. The rendering callback does not call Remix, wait for another process, decode images or perform file access. Workers handle serialization, preparation and bounded evidence recording outside that callback.

Geometry comes from **fresh in-memory SFC capture packets**, not by converting the installed `.mod` file. The model filename is an identity/selection label. Texture filenames come from the matching captured resource associations; workers read the corresponding original image files from the preserved test installation and prepare renderer resources. We are not reading texture pixels back from the GPU every frame.

Initial preparation currently uses generated binary scene/texture bundles and manifests. That is a local worker-side adapter representation, not an OBJ export/import loop or a prebuilt ship substitution. Once admitted, geometry and textures remain resident; lightweight transform, camera and qualified light updates drive subsequent frames. The persistent source publishes once per qualified scene frame, not at an imposed 30 Hz refresh rate. Bounded diagnostic logging is separate from that update rate.

### 3. Turn captured data into ordinary D3D9 work

The separate **64-bit D3D9 host** uploads the captured positions, per-corner normals/UVs, triangle indices and rendering groups into vertex/index buffers and binds their textures. It converts the established native transform arithmetic into D3D9's matrix convention, supplies world/view/projection state, and issues `DrawIndexedPrimitive` calls.

The host creates its D3D9Ex device through the pinned Remix runtime. **Remix intercepts these normal D3D9 draws**; we are not using SDK `CreateMesh`/instance registration as the geometry input on this path. Supported runtime APIs still provide configuration, qualified lighting and output access. The earlier SDK-only host and Toolkit/USD preview remain historical diagnostic paths, not the current geometry delivery mechanism.

This D3D9 adapter is a step toward a renderer-independent boundary. It does not mean a D3D12 adapter, universal backend compatibility or the final architecture is already complete.

### 4. Bring actual rendered pixels back into SFC

The host uses the pinned runtime's output-copy interface to place actual Remix output into GPU-shareable resources. An owned 32-bit D3D11 receiver copies completed output into a fixed handoff pool. Shared handles, GPU completion signals and session/owner/revision/frame identities govern reuse; a raw image identifier alone is not enough.

Inside the copied game, the project ReShade add-on provides the native insertion adapter. The capture hook coordinates matching output before forwarding the selected original mesh submission. The adapter writes colour and physical depth into the active native targets, then the hook suppresses only the committed owner's mesh lists. SFC continues drawing its shields, effects and text normally. **ReShade remains an integration dependency**, not the source of captured models or ray-traced rendering. The result is inside SFC's displayed frame.

The default-off native replacement waits at one separate coordination point for the exact scene/camera/pose output, within an absolute deadline. Multi-ship replacement shares that admitted output among owners without additional waits. Output slots remain protected until all queued native GPU reads finish. It does not attach an old pose to a new camera.

Offset and late-composition launchers remain diagnostics. In native replacement, missing or invalid output leaves that owner's original drawing intact before commit. Supported multi-ship replacement has passed gameplay checkout; it is not a universal model-coverage claim.

### Where to inspect this pipeline

For developer reuse, start with the
[current interface and exposure guide](docs/reconnaissance/2026-11-03-renderer-interface-exposure-audit.md).
It maps captured assets/state, D3D9 submission, light/material side channels and
native output integration to their source files. Geometry, owner tracking and
camera work are reusable; enhanced materials/lights and output still have
Remix/Windows-specific adapters. This is published experimental source, not a
stable drop-in renderer SDK. The native replacement baseline carries reversible
per-owner damage state through the live scene interface and submits cached
original-image decals. The standard damage path is visually confirmed in tested
skirmishes. See the [live damage results and limits](docs/runs/2026-11-04-codex-damage-live-confirmation.md).

| Stage | Main source/reference |
| --- | --- |
| Semantic capture and native worker | [`m1_component.cpp`](tools/m1_component/m1_component.cpp), [`m1_live_scene.h`](tools/m1_component/m1_live_scene.h) |
| Persistent identity and simulation pose | [`persistent_scene.h`](tools/scene_bridge/persistent_scene.h), [persistent-scene contract](docs/reconnaissance/persistent-scene-contract.md) |
| Asset preparation and live state | [`live_owner_timing.py`](tools/remix_runtime/live_owner_timing.py), [`scene_bundle.py`](tools/scene_bridge/scene_bundle.py), [`live_owner_input.h`](tools/d3d9_proof/live_owner_input.h) |
| Ordinary D3D9 draws and Remix output | [`d3d9_replay.cpp`](tools/d3d9_proof/d3d9_replay.cpp), [`d3d9_direct_host.cpp`](tools/d3d9_proof/d3d9_direct_host.cpp) |
| GPU return and in-game composition | [`output_receiver.cpp`](tools/d3d9_proof/output_receiver.cpp), [`d3d9_game_receiver.h`](tools/remix_runtime/d3d9_game_receiver.h), [`return_addon.cpp`](tools/remix_runtime/return_addon.cpp) |
| Paired frame buffer and GPU-read ownership | [synchronized-buffer contract](docs/reconnaissance/synchronized-buffer-contract.md), [`game_gpu_read_lease.h`](tools/remix_runtime/game_gpu_read_lease.h) |

The **Remix Toolkit is not required** in this return path. See the [renderer-independent boundary gate](docs/decisions/2026-10-18-renderer-independent-boundary-gate.md) for the remaining portability work. Earlier contracts and run records describe their then-current experiments; use the newest handoff to distinguish them.

## Latest validation checkpoint

The corrected buffer was tested in two actual SFC runs: **5,382 paired frames with 24 omissions**, and **5,395 paired frames with 5 omissions**. The constant alternating-frame flicker from the initial buffering experiment is resolved in these runs. The second run has confirmed controlled hook restoration/unload and normal exit; the first exited before controlled removal could be confirmed. Original client hashes and test-proxy restoration passed in both.

NVIDIA recording was active during the second run by sponsor report, which coincided with faster output completion and fewer omissions. The cause is **unresolved**; recording is not a required workaround. These results establish neither zero flicker nor universal model support. See [runtime comparison](docs/runs/2026-10-22-codex-buffered-runtime-comparison.md) and [coverage review](docs/runs/2026-10-22-codex-model-selection-scope-review.md).

## Start here

### To understand the project

1. Read the newest section of [HANDOFF](docs/HANDOFF.md) for the authoritative checkpoint. Older entries preserve history and may describe superseded experiments.
2. Read the [M1 semantic-integration closure report](docs/m1/m1-component-integration-closure-report.md) and [approved milestone/gate allocation](docs/decisions/2026-10-14-m1-m2-gate-allocation-amendment.md) for the scope of the integration evidence.
3. For the current renderer path, see the [fresh ship return contract](docs/reconnaissance/ship-live-return-contract.md), [textured additive delivery](docs/reconnaissance/textured-additive-delivery-contract.md), and [light/material controls](tools/remix_runtime/config/README.md).

The governing requirements are the approved [Starfleet Command Rendering Modernization Capability Requirements v1.0](docs/requirements/Starfleet%20Command%20Rendering%20Modernization%20Capability%20Requirements.md) and explicitly approved amendments. The repository includes an unchanged, hash-verified copy; see its [provenance and amendment guidance](docs/requirements/README.md). Experimental designs and failed tests do not silently change requirements.

### To inspect the code and run Python regressions

With repository access and Git installed:

```powershell
git clone https://github.com/tuhs1985/sfc-rendering-modernization.git
Set-Location sfc-rendering-modernization
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install Pillow==12.3.0 numpy==2.3.5
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Use Python **3.12** for the recorded regression baseline. Pillow and NumPy are needed by image/geometry tests; the versions above match this workstation's validated environment. Using the environment's executable directly avoids requiring PowerShell activation scripts. This command runs the Python regression suite, not the native/GPU qualification or a gameplay test. Windows is the development/test platform; a passing Python suite does not mean the live harness is ready on a new machine.

The repository is public. Game files, downloaded dependencies and local runtime evidence are intentionally not included.

### To build or try the in-game experiment

**There is no portable, one-command installation yet.** The existing runners include development-machine paths, exact dependency hashes, and source/binary qualification receipts. A fresh clone intentionally lacks the game, downloaded dependencies and generated receipts. Do not bypass a failed preflight to make it launch.

Before any runtime test:

1. Obtain a legitimate supported game installation. Preserve the accepted installation and archival originals.
2. Review the [dependency manifest](docs/reconnaissance/remix-return-dependencies.json), [D3D9 proof notes](tools/d3d9_proof/README.md), and [current handoff](docs/HANDOFF.md). Normal Remix **1.5.2** remains a separate baseline; the current material/tuning and player-replacement checkout uses the pinned **1.6.1** runtime/host/header set. The recorded dgVoodoo/ReShade setup and Microsoft Detours also remain qualified dependencies. Use each workflow's matching versions—not whichever SDK header or DLL is newest.
3. Review local paths in `tools/d3d9_proof/`, `tools/remix_runtime/` and `tools/m1_component/`. Builds target Visual Studio **2026 Community**, C++20 and the Windows SDK, with separate x86/x64 tools. The prepared launchers accept Windows PowerShell **5.1** and forward to the pinned modern PowerShell/Python environment; the workflow uses PowerShell **7** and Python **3.12** internally. Buffered GPU-read completion also requires the qualified D3D11 fence interfaces.
4. Prepare and verify an **independent test installation**, dependency hashes, native builds, regression tests and GPU qualification. The preparation entry points include `prepare_test_install.ps1`, `prepare_runtime.ps1`, `prepare_reshade_sdk.ps1` and `prepare_detours.ps1`; they are controlled development steps, not a general installer. Preserve their manifests and review the runbook before using them.
5. Complete the non-executing preflight before launching gameplay:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\d3d9_proof\start_d3d9_buffered_scene_session.ps1 -CheckOnly
```

`-CheckOnly` checks local prerequisites and source/binary/config qualification without starting the game or renderer. A new machine will need setup and qualification before it can pass. The gate requires separate early- and late-delivery standalone tests, not only Python regressions.

**Only in an already prepared and qualified workspace**, launch the multi-ship additive comparison from an appropriately elevated PowerShell parent:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\d3d9_proof\start_d3d9_multiship_session.ps1 -AsyncMaterialCheckout
```

The execution-policy override is process-scoped; do not disable UAC or globally weaken Windows security. The runner checks the prepared tools and launches the verified test-copy workflow. Use a familiar skirmish, play normally and switch cameras freely, then exit normally at the final two low beeps. This diagnostic uses a **90-second tactical window** inside the bounded prepared workflow. Keep the game open through component restoration; early exit retains evidence but may not demonstrate controlled unload.

The unbuffered [`start_d3d9_persistent_scene_session.ps1`](tools/d3d9_proof/start_d3d9_persistent_scene_session.ps1) remains a historical comparison baseline. [`start_light_tuning_session.ps1`](tools/remix_runtime/start_light_tuning_session.ps1) now uses the current fast D3D9/Remix path with live appearance controls; it ends on game exit with its own **30-minute safety ceiling**.

The current prepared native multi-ship replacement checkout is:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\native_insertion\start_native_multiship_session.ps1
```

It defaults to ExtraFrame and inserts supported ships in their normal positions.

Experimental destruction-piece checkout (verified F-CA fixture, with a surviving
wingman):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\native_insertion\start_native_break_session.ps1
```

This opt-in timed checkout adds retained break pieces; it does not change normal
play defaults. Let the enhanced ship appear, destroy it while visible, watch the
fragments and switch cameras, then exit at the cue. Live acceptance is pending;
see the [implementation record](docs/runs/2026-11-07-codex-live-break-prepared.md).

The normal multi-ship launcher without diagnostic flags runs **until you exit SFC normally**: no battle-selection,
90-second tactical, or five-minute session deadline. This supports longer campaign
checkouts in the same game process. There are no timed exit cues. Campaign
transitions still need live qualification; this remains a development workflow,
not a general installer or a claim that every model is supported.

Use `-TimedTest` for the previous 90-second tactical checkout. Adding
`-CompletionDiagnostics` or `-LightDiagnostics` also selects a timed test.
Untimed play does not write continuous frame/light traces or screenshots; it
keeps compact counters, capped console output and recent status samples. Fresh
mesh/material caches are still required for rendering and remain capacity-bounded.
Exit the whole game to trigger owned-process cleanup and copied-file restoration.
Player-name changes saved by SFC are preserved and do not block startup or
cleanup;protected graphics configuration and game/proxy binaries remain checked.
[Untimed play details and limits](docs/runs/2026-11-04-codex-untimed-play-session.md).

Damage is enabled by default in the native multi-ship command. Use
`-NoDamageTextures` for a damage-off comparison; the older `-DamageTextures`
flag remains supported. It reuses captured geometry and original damage images;
those assets are not distributed here. [Diagnostic checks and disable routes](docs/DIAGNOSTICS.md)
remain separate from normal rendering requirements.

The older [`start_d3d9_player_replacement_session.ps1`](tools/d3d9_proof/start_d3d9_player_replacement_session.ps1) preserves the historical complete-picture comparison from [Run213](docs/runs/2026-10-27-codex-player-replacement-auto-recovery.md). It is not the current native insertion workflow. The background itself is **not** sent into Remix.

The [renderer-boundary audit](docs/reconnaissance/2026-10-27-renderer-boundary-audit.md) explains the reusable data/transaction boundaries and remaining Remix/D3D11 assumptions. Interchangeable renderer and presentation adapters remain an open engineering gate.

If setup fails, retain the generated evidence and inspect the reported condition before retrying. Never copy experimental DLLs into the accepted installation or manually delete active-session files to work around an error.

## Adjusting the returned ship

- [`lights.toml`](tools/remix_runtime/config/lights.toml): mapped native lights and an independent project fill light.
- [`rendering.toml`](tools/remix_runtime/config/rendering.toml): the single editable profile for surface materials, emission, generated roughness, texture filtering/AA, whole-image adjustments and native Remix bloom. Sections describe each control's scope; bloom affects the whole Remix image, not illumination alone. Current tuned values are preserved.

- [`rendering.example.toml`](tools/remix_runtime/config/rendering.example.toml): factory restore profile. Generated configuration files inside run folders are evidence snapshots, not alternate settings to edit.
- [Control reference](tools/remix_runtime/config/README.md): units, ranges, live reload, light types and unsupported options.
- [Protected appearance rollback — revision3](docs/reconnaissance/evidence/baselines/20261026-sponsor-appearance-r3/README.md): historical settings, hashes and restoration. Current editable profiles may contain newer sponsor tuning; do not automatically overwrite them with this snapshot. Values are temporary artistic choices, not physically calibrated factors.

Save valid configuration changes while the tuning session is active to apply them live. Invalid edits retain the last accepted settings. These settings affect the Remix-rendered copy, not the original game assets or native lights. Per-light shadow/ray-tracing disable is not exposed by the pinned SDK.

The dedicated `start_light_tuning_session.ps1` now uses the fast ordinary-D3D9
Remix1.6.1 checkout, with live controls and minimal recording until normal exit
(30-minute tactical safety ceiling). It does not use the older SDK/ImGui path.
See [Run204](docs/runs/2026-10-26-codex-current-d3d9-live-tuning.md) for qualification,
restoration and the remaining sponsor gameplay check.

## Important limitations

- Current gameplay checkpoint: sponsor-accepted stable multi-ship replacement using ExtraFrame, now the normal launcher's default. A carrier/fighter run replaced all63 tracked owner revisions across15 model assets with no deadline misses, about19ms median source-to-presentation delivery, and clean teardown. The preceding Strict run handled72 owner revisions but missed96 deadlines. The battles differed; these results establish a tested configuration, not universal mission coverage. Small new-asset admission gaps and occasional whole-game hitches remain documented in the [stress comparison](docs/runs/2026-11-02-codex-extraframe-stress-comparison.md). Use `-TimingPolicy Strict` only for comparison; completion diagnostics remain opt-in.
- Native player replacement, correct foreground shield/text ordering and controlled unload have been observed in gameplay. Supported multi-ship replacement has also passed gameplay checkout; full-scene replacement is not established. See the [current handoff](docs/HANDOFF.md).
- The current multi-ship checkout accepts fresh supported ship assets; the older single-FCA diagnostic remains separate. The current byte-budgeted transport accommodates256 concurrent owner slots and1,024 session asset revisions;160-owner transport tests do not establish100-object GPU performance or universal model/mission coverage. See [fleet capacity preparation](docs/runs/2026-10-31-codex-fleet-capacity-correction.md).
- The established additive buffer pairs one adjacent frame with a 50 ms input limit. Replacement separately retains up to two earlier source frames, checks exact output/receipt identity, and can repeat a whole completed picture twice before temporary native recovery and fresh-output reactivation. Automatic recovery has been exercised; it does not resolve native effect ordering. No motion prediction or indefinite stale overlay is used.
- The qualified buffered output extent is 1920×1080. Resize/device recreation can omit the extra ship until a fresh supported session; automatic recovery at arbitrary resolutions is not established.
- Supported mainline rigid meshes do not imply arbitrary deformation, damage updates, every LOD or every game object is covered.
- Transient native type1/type5 lights now feed Remix positional lights using fresh position, colour and on/off state. The sphere emitter approximation is prepared and tested offline; gameplay brightness and weapon-specific mappings await checkout. See [effect-light integration](docs/runs/2026-11-02-codex-effect-light-integration-checkout.md).
- Native lighting parity, physical brightness conversion and appearance quality remain provisional.
- Runtime cleanup warnings and prior renderer-exit classification issues remain recorded in the handoff/evidence. Successful short tests do not erase those open issues.
- Supersampling, DLSS integration and a final graphics backend are not delivered capabilities.

## Repository map

The [full repository map](docs/REPOSITORY_MAP.md) classifies production components,
development tools and historical evidence in place. The table below is an overview;
folder names alone do not determine what ships in the alpha.

For troubleshooting tools, timing captures and trace limitations, see the [diagnostic tools reference](docs/DIAGNOSTICS.md). Normal gameplay does not require enabling these tools.

| Location | Purpose |
| --- | --- |
| `tools/m1_component/` | Native semantic observer, capture/transport and supporting runners |
| `tools/scene_bridge/` | Renderer-neutral scene representations, persistent identity and simulation pose |
| `tools/d3d9_proof/` | Ordinary D3D9 adapter, live host, GPU output receiver and diagnostic launchers |
| `tools/remix_runtime/` | Remix runtime host, GPU return/compositor, preparation, analysis and controls |
| `tools/remix_ingest/` | Active live/break capture decoding and camera helpers alongside earlier offline/Toolkit inspection tools |
| `src/launcher/` | Portable Windows launcher, bootstrap and recording cleanup policy |
| `src/session/` | Application session coordinator, game-exit monitoring and atomic result reporting |
| `tools/release/` | Development-only build, packaging, dependency review and qualification inputs |
| `tools/recon/` | Focused inspection and publication-audit helpers |
| `tests/` | Python/native regression and protocol fixtures |
| `docs/m0/`, `docs/m1/` | Milestone plans, contracts and evidence |
| `docs/reconnaissance/` | Focused investigations, render/transport contracts and curated results |
| `docs/runs/` | Reproducible execution records |
| `docs/HANDOFF.md` | Current checkpoint and historical handoffs |
| `openspec/`, `.agents/skills/` | Development planning and generated workflows; excluded from the alpha |

Game files, reference originals, SDK/runtime downloads, compiled binaries, extracted assets and bulk captures are excluded from Git. Generated evidence belongs under ignored `artifacts/` or other documented local work areas. A clone is source and documentation—not a game distribution.

## Working on the project

Keep experiments small, reversible and evidence-backed. Separate **CONFIRMED**, **STRONG HYPOTHESIS** and **SPECULATIVE** findings. Preserve client hashes, original assets and useful evidence; document probe configuration, output limits, cleanup and results. Do not broaden engine reverse engineering or change requirements just to make an experiment pass.

For a new development session, read the handoff, choose one bounded task, run the relevant tests and leave a durable run record/handoff. Future contributors should propose a focused change rather than assume every historical experiment is current.

GitHub `master` is the integration line. Use scoped `codex/<change-name>` work
branches under the [contributor conventions](CONTRIBUTING.md#git-conventions).
The historical local `master` and recovery branches are not automatic merge
sources. Follow the [publication safeguards](docs/decisions/2026-10-18-private-github-publication.md).

This is an independent, unofficial project. Project-authored code is available
under the [MIT license](LICENSE). Game assets, third-party dependencies and
contributed research retain their respective owners' terms; MIT does not
relicense those materials. Proprietary game assets and runtime binaries remain
excluded from this repository.
