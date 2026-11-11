# Asset preparation separated from developer tools

November 10, 2026. Parent `7ae2c35`, branch
`codex/organize-repository-foundation`. Sponsor authorizes separation with
unchanged behavior, followed by a renderer/transfer ownership review. Sponsor
reports checkout complete and requests the commit. No push, merge, release or
SFC launch by Codex.

## Application and development boundary

Nine existing modules move to `src/assets` with stable runtime module names:

| Module | Runtime responsibility |
| --- | --- |
| `parallel_assets.py` | Existing task graph, image read/decode, bounded working caches, geometry/base/enhanced preparation |
| `scene_bundle.py` | Original-image resolution, geometry packing, existing scene packet serialization/reader and provenance |
| `material_binding.py` | Existing Remix DDS encoding, shader/material definitions and legacy preparation interface |
| `material_library.py` | Generated material composition, revision publication and qualified Windows file replacement |
| `roughness_maps.py` | Existing optional derivatives, receipt-aware generated-file reuse/reclamation |
| `mesh_checksum.py` | Existing native checksum/content identity helper; native DLL/source ownership unchanged |
| `damage_materials.py` | Existing faithful damage image/material preparation |
| `damage_mapping.py` | Existing damage projection arithmetic |
| `break_scene.py` | Existing qualified runtime debris decoding/admission |

New `src/assets/mesh_decode.py` holds the original neutral mesh decoder extracted
from `live_scene.py`. It does not import shared-memory transport. `live_scene`
continues exporting the same decoder and retains actual scene-channel transport.

Development-only `tools/asset_diagnostics/asset_capture_review.py` now owns:
snapshot selection from old capture updates; `ImageStore` with PNG/DDS comparison;
old preview `qualify_mesh`/`SceneConsumer`; offline break capture analysis;
streamed-material experiments; and explicit test-mode source/upload comparisons.
Normal play does not load that module. Existing explicit review APIs remain
available through lazy development access; those tools do not ship.

`scene_bundle.read_replay` stays in the application: current launch reads its
packet to obtain geometry span. Removing it based on its historical name would
break functional startup. Cheap generated-image layout checks, finite/count/index
checks, actual asset associations, budgets and immutable identities remain
functional. Test-mode comparisons retain their existing errors and semantics.

Legacy developer file paths forward to canonical application modules using the
established importlib compatibility pattern. Explicit spec-loader consumers also
retain helper attributes. Bootstrap/coordinator and standalone qualification add
the asset application path; the package allowlist excludes all forwarders and
review tools. Production grows from **60 to 61 Python modules** only because the
decoder is now independent of transport. It has **3,850 immutable manifest files**.

This is source/dependency separation, not a new generic renderer SDK. The task
graph still uses the established Relay context and wire packet. Remix-specific
material definitions and image-origin rules remain separate from original
geometry/images. Renderer/transfer code was reviewed, not relocated or redesigned.

## Unchanged behavior and verification

- **764 regressions pass**, plus four selected existing capture-review tests for
  mesh arrays, malformed associations, original image assignment and multi-owner
  lifetime/revision behavior.
- New isolated tests exercise legacy/application-first import identity and actual
  image/material task execution while review imports are blocked. Explicit review
  APIs still resolve to the development module when requested.
- AST comparison finds **45 existing function/class definitions unchanged**,
  including the full task graph, caches, image conversion/material arithmetic,
  neutral geometry decoder and moved review classes. Three intentional
  adaptations delegate scene snapshots and material comparisons or import the
  relocated decoder; their data operations and error semantics are preserved.
- Actual material revision/file-publication tests pass. An initial full-suite run
  encountered intermittent Windows error1175 in the existing rapid file-exchange
  test; its isolated rerun and the final complete suite pass without a runtime
  workaround or permission change.
- Actual native-light workers and 600-frame Strict/ExtraFrame multi-owner GPU
  fixtures pass with current lights/damage, owner receipts, independent pixels
  and native graphics-state restoration. Renewed qualification uses those results.
- New private package passes original, moved Unicode/space and final-path native
  preflights, plus installed normal coordinator preflight. An additional source
  CLI preflight was rejected by automatic approval review as a possible game
  launch; it did not execute and was not bypassed. Existing package preflight,
  unit tests and standalone qualification cover the required boundaries.
- Installed import guard resolves all ten asset modules to `code/src/assets`,
  creates/closes the actual IPC receiver, verifies decoder reexport identity and
  confirms review/compatibility files are absent from normal installed imports.
- Installed CPU preparation uses retained raw F-CA capture data, not an imported
  ship template: **19,110 vertices, 58 groups**, base/enhanced materials and actual
  light binding. No diagnostic task spans or review imports. Source images read
  only; no game source model conversion.
- Profiling-off installed GPU output and pre-output cancellation pass. Host and
  receiver colour/depth/owner planes match; both jobs leave zero owned processes.
  Standalone bootstrap readiness **3.422 s** is not first-ship timing or a
  performance improvement claim.
- No native `.cpp`/`.h` or appearance `.toml` changed. Renderer hash remains
  `1bf0045d64b2cb6283bb20e9476b64e16c436e45b1ccd6e860377d3e2e53c16b`.
  Package defaults and seeded rendering/light settings match the existing source
  exactly. Worker counts, task limits, cache behavior, publication order, native
  fallback and ExtraFrame/untimed play remain unchanged.

Local evidence, ignored: `artifacts/alpha/asset-separation-*.txt`,
`asset-separation-equivalence.json`, installed GPU/cancellation directories and
stager `preflight-fixtures/20261110-061835-405241/result.json` (paths there precede
the verified final move). Source originals/move map are retained locally for the
equivalence audit, not shipped. GPU fixtures:

- `artifacts/remix-runtime/runs/20261110-061600-689072-return-fixture` — Strict.
- `artifacts/remix-runtime/runs/20261110-061746-057533-return-fixture` — ExtraFrame.

## Renderer/transfer review and next action

[Completed ownership review](../reconnaissance/2026-11-10-renderer-transfer-ownership.md)
maps the actual Relay chain, scene IPC, texture payload ownership, renderer host,
x86 receiver, game-local output pool and native insertion leases. The smallest
next separation is functional scene receipt/input transport from calibration and
timing analysis, followed by normal renderer orchestration/backend selection.
Preserve paired native contracts and teardown; do not move whole proof folders.

New private gameplay copy: `artifacts/alpha/asset-preparation-game`, recording off,
current appearance. Previous accepted game copies/packages are untouched. This
directory contains game assets outside SFCRemix and is not public release input.

```cmd
cmd.exe /d /c call "C:\Project\SFC-Modernize Engine\artifacts\alpha\asset-preparation-game\SFCRemix-Launch.cmd"
```

**Sponsor gameplay checkout complete.** Sponsor reports completion and requests
the commit. No specific gameplay scenario coverage or measured timings were
reported. Keep visible startup-stage investigation and external tester graphics
preparation parked; no loader optimization here.
