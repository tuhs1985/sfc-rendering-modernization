# SFC Rendering Modernization

An experimental rendering-modernization project for **Starfleet Command: Orion Pirates**, tested against the Community Edition client **2.5.6.4**.

The aim is to improve tactical 3D rendering while preserving gameplay, controls, tactical information, missions, campaigns and save continuity. This is not a rebuild of the game engine.

**Current result:** fresh ship geometry, original textures, movement, camera state and selected native lights can reach a separate NVIDIA RTX Remix runtime. Its rendered output can be composited into the actual SFC game window. The current in-game proof adds a textured copy beside an original ship; **it does not replace that ship or the entire scene**.

This is a research/development workspace, not a ready-to-install graphics mod.

## What works today

- **Semantic capture:** observe ship/model ownership before the engine reduces it to generic draw calls.
- **Fresh assets:** capture supported rigid triangular meshes and their texture associations from the running game, rather than substituting a prepared ship model.
- **Live scene connection:** multiple observed ships, including fighters in a tested scenario, can be constructed in the separate preview with live movement and camera updates. This does not establish universal model coverage.
- **In-game return:** a separate 64-bit Remix host renders a selected fresh ship; a project ReShade add-on composites the returned GPU image into the copied game's D3D11 presentation path.
- **Lighting and materials:** two qualified native directional-light sources drive Remix lighting. Editable configuration controls light types, brightness, source size, surface roughness and recovered illuminated markings.
- **Safety and evidence:** bounded capture, identity/lifetime checks, fallback to original rendering, executable-hash checks and documented test/cleanup procedures.

These are demonstrated capabilities within the recorded test conditions—not claims of complete compatibility, visual parity or final renderer architecture. The semantic integration proof is established; that alone is not an overall TRL 4 or finished-modernization claim.

## How it fits together

```text
SFC ship/model render state
    → 32-bit semantic observer
    → bounded scene/state bridge
    → 64-bit RTX Remix runtime host
    → shared GPU output
    → project ReShade compositor in the test copy
    → SFC's displayed frame
```

SFC continues its original rendering and gameplay. The modern-rendered copy is additive and deliberately offset for comparison. Missing or invalid replacement output must not stop the original renderer.

The **Remix runtime** produces the returned image. The **Remix Toolkit preview** was an earlier inspection tool and is not required in this return path. ReShade currently provides the in-game insertion point; a final renderer-independent interface remains an [open technical gate](docs/decisions/2026-10-18-renderer-independent-boundary-gate.md).

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

The repository is currently private. Sharing this link does not grant access.

### To build or try the in-game experiment

**There is no portable, one-command installation yet.** The existing runners include development-machine paths, exact dependency hashes, and source/binary qualification receipts. A fresh clone intentionally lacks the game, downloaded dependencies and generated receipts. Do not bypass a failed preflight to make it launch.

Before any runtime test:

1. Obtain a legitimate supported game installation. Preserve the accepted installation and archival originals.
2. Review the [dependency manifest](docs/reconnaissance/remix-return-dependencies.json) and [runtime probe/runbook](docs/reconnaissance/probes/REMIX-TEXTURED-RETURN-001.md). The tested stack includes Remix **1.5.2 / SDK 0.6.4**, the recorded dgVoodoo/ReShade setup, and Microsoft Detours. Use the pinned matching versions—not whichever SDK header or DLL is newest.
3. Review the local paths in the preparation/build scripts under `tools/remix_runtime/` and `tools/m1_component/`. The current build scripts target Visual Studio **2026 Community**, C++20 and the Windows SDK, with separate x86 and x64 tools. The runners use PowerShell **7** and Python **3.12**.
4. Prepare and verify an **independent test installation**, dependency hashes, native builds, regression tests and GPU qualification. The preparation entry points include `prepare_test_install.ps1`, `prepare_runtime.ps1`, `prepare_reshade_sdk.ps1` and `prepare_detours.ps1`; they are controlled development steps, not a general installer. Preserve their manifests and review the runbook before using them.
5. Complete the non-executing preflight before launching gameplay:

```powershell
python tools/remix_runtime/run_return_game.py --light-tuning
```

Without `--execute`, this checks local prerequisites and qualification; it does not start the game or renderer. A new machine will need setup and qualification before it can pass.

**Only in an already prepared and qualified workspace**, launch the current tuning experiment from an appropriately elevated PowerShell parent:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\tools\remix_runtime\start_light_tuning_session.ps1
```

The execution-policy override is process-scoped; do not disable UAC or globally weaken Windows security. The runner builds/checks the required tools and launches the verified test-copy workflow. Enter the familiar two-ship skirmish, compare the added ship with the original, and exit normally when finished. Tuning mode ends on game exit with a **30-minute safety ceiling**; ordinary diagnostic captures use shorter limits.

If setup fails, retain the generated evidence and inspect the reported condition before retrying. Never copy experimental DLLs into the accepted installation or manually delete active-session files to work around an error.

## Adjusting the returned ship

- [`lights.toml`](tools/remix_runtime/config/lights.toml): mapped native lights and an independent project fill light.
- [`materials.toml`](tools/remix_runtime/config/materials.toml): roughness, illuminated-marking strength and supported optional surface controls.
- [`image.toml`](tools/remix_runtime/config/image.toml): separately enabled live brightness, exposure, contrast, midtone/gamma and saturation controls; restore defaults with image.example.toml.
- [`quality.toml`](tools/remix_runtime/config/quality.toml): separate filtering, temporal AA and denoiser controls; supersampling remains at the qualified1× setting.
- [Control reference](tools/remix_runtime/config/README.md): units, ranges, live reload, light types and unsupported options.
- [Current temporary appearance baseline](docs/reconnaissance/evidence/baselines/20261019-sponsor-temporary-appearance-r2/README.md): the sponsor's recorded settings and attribution caveats, not physically calibrated conversion factors; older checkpoints remain historical.

Save valid configuration changes while the tuning session is active to apply them live. Invalid edits retain the last accepted settings. These settings affect the Remix-rendered copy, not the original game assets or native lights. Per-light shadow/ray-tracing disable is not exposed by the pinned SDK.

## Important limitations

- Original-ship suppression/replacement, full-scene visibility and correct interaction with retained weapons, shields, explosions and UI are not established.
- The additive path is asynchronous; its documented freshness policy is not an exact synchronized replacement contract.
- Supported mainline rigid meshes do not imply arbitrary deformation, damage updates, every LOD or every game object is covered.
- Transient weapon/effect lights are observed but are not yet mapped as qualified live Remix lights.
- Native lighting parity, physical brightness conversion and appearance quality remain provisional.
- Runtime cleanup warnings and prior renderer-exit classification issues remain recorded in the handoff/evidence. Successful short tests do not erase those open issues.
- Supersampling, DLSS integration and a final graphics backend are not delivered capabilities.

## Repository map

| Location | Purpose |
| --- | --- |
| `tools/m1_component/` | Native semantic observer, capture/transport and supporting runners |
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
