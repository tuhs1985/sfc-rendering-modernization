# Isolated Remix API scene proof

**PARKED — sponsor direction,2026-10-24 Run165.** Preserve this experiment;
current work is the metadata-only rendering-family survey. Resume only when
sponsor returns to API/backend readiness. Exact restart: qualify API camera/
viewport placement against the captured projection oracle before gameplay.

Experimental, offline-only backend. It is **not** selected by the normal SFC
launcher and does not qualify ordinary D3D9 indexed-draw submission. See
[probe](../../docs/reconnaissance/probes/REMIX-API-SCENE-001.md) and
[Run164](../../docs/runs/2026-10-24-codex-api-scene-proof.md).

The accepted capture/parser/retained registry, camera observations, image
preparation, light adapter and GPU return connection are reused. Only this
backend registers group materials/meshes and submits instances through the
pinned NVIDIA C API. A registered D3D9Ex device still provides presentation and
output-copy interoperability. No Toolkit, saved ship template or game-folder
model conversion is used. No watched USD publication is required on this route.

## Prepare and exercise

Requires the existing project-controlled Remix1.5.2/API0.6.4 dependency and
accepted four-owner/three-content offline fixture inputs. This is not a fresh
checkout dependency installer. Do not download different headers or DLLs.

1. Use `material_packet.prepare(asset_folder)` on one completed, accepted
   `gpu/assets/1` folder containing `scene.bin`, `scene.json`,
   `material-binding.json` and its generated DDS files. It adds only
   `api-materials.bin`; original scene and images remain unchanged.
2. Run `build.ps1 -TestScene <repository-relative asset-folder>` using the
   configured modern PowerShell/VS x64 tools. Strict host build, actual-input
   native mock tests and an independent source/config/binary lock are required.
3. Run `python -B tools/remix_api_proof/run_fixture.py`. No game is launched.
   `--emission-off` changes only the API material emission scalar for a negative
   control. `--late-asset` uses the existing withheld-third-content fixture.
4. Inspect `api-scene-control.json`, receiver/native logs, bounded-job receipt,
   result, and FIRST/settled returned BMPs in the reported evidence directory.
   Never interpret a successful API handle or generic fixture exit as image
   parity, per-owner pixel visibility, readiness or a gameplay pass.

Python packet tests: `python -B -m unittest discover -s
tools/remix_api_proof/tests -p 'test_*.py'`. Use a writable temporary directory
if the sandbox's redirected Windows temp cannot be written.

Native tests use a mock API table, checking the actual vertex/index/normal/UV,
material and matrix arguments; they explicitly make **no GPU claim**. GPU
controls exercise the real runtime/return compositor separately.

## Contract and lifecycle

`api-materials.bin` version1: little-endian four uint32 fields (magic0x314d5041,
version1, group count, row bytes256), ten existing material scalars, then one
256-byte row per group (`group,index,uint64 provenance,3x80-byte DDS names`),
followed by FNV1a64 over all preceding bytes. Total64+256*groups bytes. Names
must be64lowercase hex plus `.dds`, padded with zeroes; actual files remain
under that asset's generated policy textures directory. Group identity/order
must match the captured scene. Native counts/checksum/finite/path checks remain.

Each group supplies one explicit material handle. Each unique retained asset
has one SDK mesh containing group surfaces; separate owner poses reuse it.
Geometry/normals/UVs are copied unchanged, with group-local index rebasing.
Native model3x4 arithmetic remains unchanged; view/projection arrays are
transposed for the SDK and the captured viewport is folded into projection.
The source-pixel algebra is tested; actual parity with the intercepted camera
path remains unresolved. Do not silently compensate with an arbitrary scale.

Destroy meshes before materials, enqueue one unpublished retirement PresentEx,
wait for GPU completion, retire the output receiver and existing fences, then
use the accepted registered-device ownership/Shutdown sequence. No guessed COM
reference adjustments or vendor patches. Initial experiments with the SDK
Present wrapper failed teardown; current device PresentEx controls exit cleanly.
The existing vendor common-device-object warning remains a separate limitation.

Keep existing session/owner/asset/image/transport/log/watchdog limits and20GB
governed evidence cap. The generic inherited fixture console still says
ordinary-D3D9 in one line; the explicit API backend manifest/counters are the
authority. Never refresh normal D3D9 qualification from these runs.

## Current disposition

**PARKED by sponsor direction after Run164.** The restart action below is for a
future authorized resumption, not current work. Rendering-family characterization
and the authoritative repository handoff take precedence.

Run164 demonstrates direct material/mesh submission, first-image emission
response, shared assets, delayed asset delivery and clean owned-process exit.
It does **not** demonstrate sub2s startup, camera parity, seamless delivery,
in-game API backend integration, original-ship replacement or milestone PASS.
Next action: qualify API camera placement/scale against the existing captured
projection oracle before preparing an opt-in gameplay backend.
