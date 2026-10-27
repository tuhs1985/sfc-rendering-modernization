# SFC Rendering Modernization

An experimental rendering-modernization project for **Starfleet Command: Orion Pirates**, tested against the Community Edition client **2.5.6.4**.

The aim is to improve tactical 3D rendering while preserving gameplay, controls, tactical information, missions, campaigns and save continuity. This is not a rebuild of the game engine.

**Current result:** we capture fresh ship geometry and scene state from the running game, submit it through our own **ordinary Direct3D 9 adapter**, and let NVIDIA RTX Remix render it. GPU-shared output is composited into SFC's actual game window. Persistent tracking and bounded presentation buffering retain supported ships across camera changes. The demonstrated in-game path adds textured copies alongside originals. A separate, default-off **player-ship replacement** checkout is now qualified offline and awaiting gameplay confirmation; full-scene replacement is not established.

The multi-ship diagnostic accepts fresh supported assets. The first replacement checkout deliberately selects a unique Federation heavy cruiser (`fca.mod`); it requires that player fixture against a different enemy model, rather than assuming a verified engine player flag. See the [current checkpoint](docs/HANDOFF.md).

This is a research/development workspace, not a ready-to-install graphics mod.

## Video — latest good in-game test

[![SFC Rendering Modernization — Live RTX Remix Rendering Test](https://img.youtube.com/vi/NCYvT6ypXLY/hqdefault.jpg)](https://youtu.be/NCYvT6ypXLY)

Click the preview to watch on YouTube. The test shows the original FCA alongside its live Remix-rendered copy, with a 360-degree camera pan to demonstrate the lighting response. This is the additive integration proof, not original-ship replacement.

## What works today

- **Semantic capture:** observe ship/model ownership before the engine reduces it to generic draw calls.
- **Fresh assets:** capture supported rigid triangular meshes and their texture associations from the running game, rather than substituting a prepared ship model.
- **Live scene connection:** supported fresh ships and fighters can be retained through the D3D9-to-Remix additive path. Tested coverage is recorded per run; it does not establish every model or rendering family.
- **Persistent tracking:** a bounded registry retains qualified ship identity, geometry revisions and simulation-derived transforms independently of camera visibility. A camera switch does not itself retire or reload a living ship.
- **Standard graphics input:** a separate 64-bit host builds D3D9 vertex/index buffers and texture bindings from the captured data, then submits ordinary indexed triangle draws that Remix intercepts.
- **In-game return:** a project ReShade add-on composites shared GPU output into the copied game's D3D11 presentation path. The opt-in buffer pairs the previous complete native frame, depth and returned ship rather than putting old ship pixels on a new camera view.
- **Lighting and materials:** two qualified native directional-light sources drive Remix lighting. Editable configuration controls light types, brightness, source size, surface roughness and recovered illuminated markings.
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
       → actual SFC game window (original ship + offset rendered copy)
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

Inside the copied game, the project ReShade add-on combines returned color/depth/owner coverage with the qualified native game depth at the before-effects presentation point. **ReShade is our present insertion mechanism**, not the source of the captured models or the ray-traced rendering. The result is in SFC's displayed frame, not a desktop window laid over the game.

The current default-off synchronized test retains **one adjacent complete native frame**, including its native HUD pixels and matching depth, and accepts only the returned ship image belonging to that saved frame. It does not attach stale pixels to the newest camera. Queued images cannot be overwritten before use, and an independent worker releases completed GPU reads without making SFC wait. Later ReShade UI and the OS hardware cursor are not deliberately delayed.

The copy remains additive and deliberately offset for comparison. Missing, late, disconnected or invalid output omits the extra ship rather than blocking original SFC rendering. Occasional omissions remain; this is not a synchronized original-ship replacement guarantee.

### Where to inspect this pipeline

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

The separate [`start_d3d9_player_replacement_session.ps1`](tools/d3d9_proof/start_d3d9_player_replacement_session.ps1) prepares one aligned player replacement, rather than an offset copy. Original drawing continues until paired output authorizes suppression. It stages SFC's background/HUD and matching Remix ship offscreen, then displays the complete picture. At most two additional complete-picture presentations bridge missing output; sustained failure restores intact native rendering and latches replacement off until restart. Use F-CA versus a different model and follow [Run209's checkout instructions](docs/runs/2026-10-27-codex-player-replacement-qualified.md). The background itself is **not** sent into Remix.

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

- Original-ship replacement is qualified offline for the first player checkout; in-game suppression, controlled unload and interaction with retained effects still need confirmation. Full-scene replacement is not established.
- The current multi-ship checkout accepts fresh supported ship assets; the older single-FCA diagnostic remains separate. The32-owner/64-asset limits and tested models do not establish universal object, geometry or mission coverage.
- The established additive buffer pairs one adjacent frame with a 50 ms input limit. The new replacement transaction separately retains up to two earlier source frames, checks exact output/receipt identity, and can repeat a whole completed picture twice before latched native recovery. No motion prediction or indefinite stale overlay is used. Actual replacement playability remains to test.
- The qualified buffered output extent is 1920×1080. Resize/device recreation can omit the extra ship until a fresh supported session; automatic recovery at arbitrary resolutions is not established.
- Supported mainline rigid meshes do not imply arbitrary deformation, damage updates, every LOD or every game object is covered.
- Transient weapon/effect lights are observed but are not yet mapped as qualified live Remix lights.
- Native lighting parity, physical brightness conversion and appearance quality remain provisional.
- Runtime cleanup warnings and prior renderer-exit classification issues remain recorded in the handoff/evidence. Successful short tests do not erase those open issues.
- Supersampling, DLSS integration and a final graphics backend are not delivered capabilities.

## Repository map

| Location | Purpose |
| --- | --- |
| `tools/m1_component/` | Native semantic observer, capture/transport and supporting runners |
| `tools/scene_bridge/` | Renderer-neutral scene representations, persistent identity and simulation pose |
| `tools/d3d9_proof/` | Ordinary D3D9 adapter, live host, GPU output receiver and diagnostic launchers |
| `tools/remix_runtime/` | Remix runtime host, GPU return/compositor, preparation, analysis and controls |
| `tools/remix_ingest/` | Earlier offline/Toolkit inspection workflow |
| `tools/recon/` | Focused inspection and publication-audit helpers |
| `tests/` | Python/native regression and protocol fixtures |
| `docs/m0/`, `docs/m1/` | Milestone plans, contracts and evidence |
| `docs/reconnaissance/` | Focused investigations, render/transport contracts and curated results |
| `docs/runs/` | Reproducible execution records |
| `docs/HANDOFF.md` | Current checkpoint and historical handoffs |

Game files, reference originals, SDK/runtime downloads, compiled binaries, extracted assets and bulk captures are excluded from Git. Generated evidence belongs under ignored `artifacts/` or other documented local work areas. A clone is source and documentation—not a game distribution.

## Working on the project

Keep experiments small, reversible and evidence-backed. Separate **CONFIRMED**, **STRONG HYPOTHESIS** and **SPECULATIVE** findings. Preserve client hashes, original assets and useful evidence; document probe configuration, output limits, cleanup and results. Do not broaden engine reverse engineering or change requirements just to make an experiment pass.

For a new development session, read the handoff, choose one bounded task, run the relevant tests and leave a durable run record/handoff. Future contributors should propose a focused change rather than assume every historical experiment is current.

The existing development workstation uses `codex/github-sanitized` to publish to GitHub `master`; fresh GitHub clones use remote `master` normally. Follow the [publication safeguards](docs/decisions/2026-10-18-private-github-publication.md); never merge or publish local-only recovery history.

This is an independent, unofficial project. Game assets and third-party dependencies remain subject to their owners' terms. Their omission from this repository is intentional; no redistribution rights or project source license are granted by this README.
