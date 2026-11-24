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

## Read-only copied-game checkout

After `run_source_session.py` passes read-only preflight, use an Administrator
CMD window:

```cmd
cmd.exe /d /c call "C:\Project\SFC-Modernize Engine\tools\ue_wrapper\start_source_session.cmd"
```

This development command uses the existing verified copy and transactional
startup/recovery parent. Enter the usual F-CA skirmish. SFC keeps drawing every
ship; a separate UE window shows original base textures and the recovered camera.
Move, turn, pan/zoom, switch away and return, then exit SFC normally. Exit/Escape
in UE also ends inspection. No UE image is inserted into SFC in this check.
The prepared workflow is bounded to five minutes, with no image/trace recording;
required definitions/images are working files. Existing evidence plus UE evidence
and the 544 MiB reservation must fit 20 GB. No new game copy is created.

Preflight is `python tools/ue_wrapper/run_source_session.py` without `--execute`.
The explicit end-to-end replay is `qualify_source_service.py EXE SCENE OUTPUT`;
passive cancellation/parent death/relaunch are `qualify_source_lifetime.py EXE OUTPUT`.
Both are standalone tools and never launch SFC.

## Additive native checkout — default off

After run_additive_session.py passes preflight without --execute, use the
existing Administrator CMD window:

```cmd
cmd.exe /d /c call "C:\Project\SFC-Modernize Engine\tools\ue_wrapper\start_additive_session.cmd"
```

Use the usual unique F-CA skirmish. The original stays visible, and UE inserts
one extra base-textured player with a fixed native-world X offset of
-15.897722721099854. Move/turn, pan/zoom, switch cameras, expose shields and
briefly pause. Exit SFC normally at the two-beep cue after 90 seconds of source
activity. The existing prepared-workflow ceiling is 285 seconds. No new game
copy is made. This is not the public Remix alpha or a replacement checkout.

The parent reuses transactional startup/recovery, exact native target/frame
admission and ExtraFrame synchronization. Gate records are bounded to 8MiB;
no continuous screenshots are recorded. Required asset definitions/images are
working files. Originals remain enabled, and no source image/UV is rewritten.
Known limitations: unique configured player fixture, base materials only,
no UE weapon lights/damage/break feature-parity claim. Live gameplay is pending.

Standalone qualification tools: qualify_live_output.py verifies actual fresh
source assets/registry and independently sampled pixels; --native-insertion
also draws native depth-tested effects/text in its explicit GPU fixture.
qualify_native_gate.py exercises the actual native Receiver Acquire/Commit with
packaged UE, while tests/ue_native_gate_fixture.cpp supplies synthetic source
cadence and native targets. Neither launches SFC. The generated qualification
hashes are required by the additive development launcher and never enter normal
shipping gameplay. See the [run record](../../docs/runs/2026-11-23-codex-ue-additive-insertion.md).
