# UE wrapper foundation qualification

Development tooling, not part of the Remix alpha. The application source is
`src/ue_wrapper`; the original `src/ue5_proof` remains the comparison reference.
Use UE **5.8.4 CL 58902052**, the installed MSVC 14.44 toolchain and
Windows SDK 22621. The engine supplies its .NET 10 SDK. Runtime code has no
UnrealEd dependency; editor asset generation lives in `SFCBridgeEditor`.
Build logs record the exact compiler revision; the November 22 GPU checkpoint
uses MSVC 14.44.35230.

Build with `tools/ue_wrapper/build.ps1 -Configuration Development` or
`-Configuration Shipping`. The default installed engine path is development
configuration only. `-Engine` can select an identically pinned installation.
`-SkipEditor` is for an already-current editor/content build. Full repeated
content generation is supported. A build receipt records exact source hashes,
engine, configuration and local parent; source changes during a build fail
qualification. No game copy or original game file is changed.

Packages are under `artifacts/ue-foundation/<configuration>/package/Windows`.
Pass `-SFCScene=<absolute checked scene.json>` to the packaged executable.
The existing proof inputs remain valid. To prepare another saved packet, run
`prepare.py <replay-directory> <read-only-game-root>
<new-artifacts/ue-foundation/inputs-directory>`. This reuses the independent
inspector and verifies original images once. It writes only source inputs,
not a copy of the game or the previous proof project.

Normal inspection is untimed, with no image/receipt capture. Exit, Escape and
ordinary Windows close are available. Required loading/structural checks run
with assertions disabled. This is not a live-game launch or a UE mod release.

## Explicit qualification

Use the repository's Windows Python with Pillow/NumPy:

```text
python tools/ue_wrapper/qualify.py <package-exe> <scene.json> <new-output-directory>
```

The tool resolves the actual runtime process (including Shipping), bounds each
process to 120 seconds, checks source identity, constructed arrays and original
pixel references, and retains bounded output. `--shared` constructs two explicitly
distinct diagnostic owners sharing one mesh. `--procedural` selects the compact
comparison path. `--frame N` selects a recorded pose. `--reject` expects an
explicit admission rejection and no success receipt. `--close` checks normal
Windows close with diagnostics off. Python callers can additionally request
`world_restart=True` or `close_normally(..., escape=True)` for lifecycle tests.
Test receipt flags describe work actually performed, not assertions compiled out.

The packaged app's `-SFCDiagnostics -SFCOutput=<directory> -SFCExit` enables one
readback/comparison receipt. `-SFCWorldRestart` additionally recreates the world
once and proves the session asset is reused. `-SFCShadowCheck` is a synthetic
512-square paired lit-receiver fixture. It does not claim the captured SFC camera
or light state: its purpose is actual ray-traced-shadow capability. The normal
source camera and source units remain unchanged outside that fixture.

The standalone math fixture is `tests/ue_world_math_tests.cpp`; compile with a
Visual Studio developer environment (`cl /EHsc /std:c++20`) for x86 and x64.
It directly tests the production adapter's matrix header without an UE device.

See [qualification record](../../docs/runs/2026-11-18-codex-ue-worldspace-foundation.md)
and the [gated implementation plan](../../openspec/changes/ue-native-insertion/tasks.md).
GPU sharing, live source receipt and in-game insertion remain separate gates.
