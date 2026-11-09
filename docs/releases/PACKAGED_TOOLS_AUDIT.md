# Packaged tools audit — November 9, 2026

**Latest sponsor priority: our files, not vendor trimming.** The
[continued project-payload audit](PROJECT_PAYLOAD_AUDIT.md) covers all118 of our
files, expands the exclusion/separation review set to48 (not ready deletions),
and identifies measurement-only work still enabled during normal play. Refactor
remains parked; no runtime changes made.

Continued across the entire package in the
[whole-alpha file relevance list](PACKAGE_FILE_RELEVANCE_AUDIT.md): 2,555
additional candidate files/about29MiB, plus vendor dependency keep findings and a
Visual C++ clean-machine packaging gap. No deletions or refactor implemented.

Scope: the private alpha's `SFCRemix/code/tools`, not deletion from the development
repository. **Read-only audit: no product/source-runtime files removed or changed.**

There are **105 files: 103 Python modules and two TOML files**, about **785 KiB**.
The static staging/import walk includes every development branch; it is not a
production dependency allowlist. No entire installed tools subfolder can be
removed wholesale: each includes active runtime code.

## Result

- **34 modules (221.57 KiB):** development/offline/retired-mode candidates for
  exclusion from the distributed alpha after their inactive/eager imports are
  disconnected. This is not permission to delete those project tools.
- **Seven mixed modules (98.77 KiB):** separate retained runtime helpers or remove
  their transitive development imports first; do not simply delete the files.
- **Two diagnostic TOMLs:** removable after zero-offset/all-ship production
  behavior stops reading them and installed preflight no longer requires them.
- **62 files remain after those candidates**, provisionally. This is not a proven
  minimum or completed replacement allowlist. Gameplay/activation/recovery and
  fresh-asset delivery must validate any actual pruning.

The savings are mainly cleaner dependencies and maintenance. This audit does not
establish a significant loading-time benefit; Python/tool code is already small.

## Candidates to keep in development, exclude from the alpha

These functions are outside the fixed alpha bootstrap path (ExtraFrame,
performance, untimed native all-ship replacement, BRK, damage; no optional developer
capture, private SDK preview, offline fixture or live tuning mode). Some modules
are still imported despite their work not being requested. Remove those import
edges before exclusion.

### Offline fixtures and replay diagnostics — 5 files

- `tools/d3d9_proof/analyze_ingress.py`
- `tools/d3d9_proof/light_fixture.py`
- `tools/d3d9_proof/multi_scene_fixture.py`
- `tools/d3d9_proof/startup.py`
- `tools/d3d9_proof/synthetic.py`

### Development qualification/setup tools — 10 files

- `tools/remix_runtime/additive_qualification.py`
- `tools/remix_runtime/native_foreground_qualification.py`
- `tools/remix_runtime/prepare_full_reshade.py`
- `tools/remix_runtime/qualify_async_material.py`
- `tools/remix_runtime/qualify_d3d9_tuning.py`
- `tools/remix_runtime/qualify_lifecycle_capture.py`
- `tools/remix_runtime/qualify_multiship.py`
- `tools/remix_runtime/qualify_offscreen_position.py`
- `tools/remix_runtime/qualify_persistent_scene.py`
- `tools/remix_runtime/qualify_synchronized_buffer.py`

### Diagnostic and retired-mode code — 19 files

- `tools/remix_runtime/analyze_present_calibration.py`
- `tools/remix_runtime/d3d9_tuning.py`
- `tools/remix_runtime/depth_search_channel.py`
- `tools/remix_runtime/depth_snapshot_analysis.py`
- `tools/remix_runtime/effect_light_trace.py`
- `tools/m1_component/identity_census.py`
- `tools/remix_runtime/lifecycle_capture.py`
- `tools/remix_runtime/live_return.py`
- `tools/remix_runtime/native_insertion_probe.py`
- `tools/remix_runtime/offscreen_position.py`
- `tools/m1_component/prepare_m1_c01_packet.py`
- `tools/remix_runtime/run_coverage_probe.py`
- `tools/remix_runtime/run_image_probe.py`
- `tools/remix_runtime/scene_depth.py`
- `tools/remix_runtime/ship_image_snapshot.py`
- `tools/remix_runtime/source_timing.py`
- `tools/remix_runtime/texture_prefetch.py`
- `tools/remix_runtime/textured_asset.py`
- `tools/m1_component/verify_m1_c01_shading_bytes.py`

## Mixed dependencies: extract or untangle first

| Current file | Why it cannot just disappear |
| --- | --- |
| `remix_runtime/run_return_fixture.py` | Normal coordinator imports ROOT/BIN/DLL/TEST/ENV and hash/file-size helpers from this offline fixture. Move genuine runtime definitions to production helpers; exclude its standalone fixture main. |
| `d3d9_proof/run_offline.py` | Normal coordinator still imports `storage`/aggregate constants. Keep actual disk accounting where required; move oracle/negative-case/offline CLI out. Installed untimed play no longer needs its evidence quota. |
| `d3d9_proof/run_direct64.py` | Older preparation methods import resize/replay helpers from this standalone launcher. Confirm which methods the progressive production path actually calls; move any retained helpers or remove dead imports before excluding it. |
| `d3d9_proof/run_intercept.py` | Dragged in by `run_direct64` at module import for old runtime/replay constants and helpers. It is not the current native injection implementation. Remove this transitive dependency with that separation. |
| `remix_runtime/player_replacement.py` | Current cohort/gate modules import ROOT and OFFSET from this player-only diagnostic module. Retain the actual shared wire layout, not the old qualification campaign. |
| `remix_runtime/light_discovery.py` | Normal release calls `require_qualification`, whose release branch validates the shipped semantic component. Retain that release dependency check; keep offline observers/analyzers outside the package. |
| `d3d9_proof/owner_selection.py` | Old owner-fixture/model selection and camera-offset helpers are imported by inherited paths and bootstrap's scene-profile preflight. Native all-ship production must use actual owner identity, not require that diagnostic configuration. |

`d3d9_proof/multi_ship.toml` and `offset_ship.toml` are diagnostic placement/model
settings. They are **currently required by code/preflight**, even though the
release uses zero offset/all ships. Retire those reads/roles with focused tests;
do not reproduce the previous missing-profile launch failures by deleting first.

## Runtime code hidden behind misleading development names

Keep the live functions/classes in:

- `async_material_checkout`, `progressive_scene_relay`, `multi_scene_relay`,
  `live_owner_timing`, `parallel_assets`, `asset_preparation`, `recovery_service`:
  actual relay inheritance, persistent state, preparation scheduling and shutdown.
  Some old methods can later be split; these are not disposable test scripts.
- `present_calibration.Receiver`, `live_scene`, `break_scene`, `live_bridge`,
  `live_camera`, `m1_component/analyze_live_camera.native_matrix`/`inverse`:
  live IPC, fresh geometry/debris decoding and camera/transform arithmetic.
- `scene_bridge/scene_bundle`, `damage_mapping`, `mesh_checksum`, `owner_rebind`,
  `multi_scene`, `texture_memory`, `material_binding`, `material_library`,
  `remix_coordinates`, `damage_materials`: live data/material preparation and wire
  submission, even when files retain offline/proof-era names.
- `native_gate`, `native_cohort`, `synchronized_buffer`, `return_channel`,
  `light_transport`, `native_light_state`, `effect_lights`, `live_light_binding`,
  `light_shapes`, `live_lights`, `environment_resources`: current synchronization,
  output/lifecycle and light path. Keep safety/lifetime/resource contracts.
- `broad_capture` and `recover_broad_session`: actual proxy switching/restoration
  helpers are mixed with broad-capture utilities. Never remove transaction and
  recovery code by filename alone.
- `bootstrap`, `session_recording`, `runtime_context`, `release_manifest`,
  `game_profile`, `copied_preferences`, `session_exit`, `controller_shutdown`,
  `windows_processes`, `portable_reshade`, settings/control modules and required
  capacity/startup helpers: production startup, settings, process ownership and
  restoration. Trim development CLIs separately where present.

## Concrete eager-import defects

`run_return_game` imports `qualify_synchronized_buffer` and
`qualify_persistent_scene` before checking `if not args.multi_ship`. In the
all-ship alpha, the test functions are skipped but their modules/dependencies
still load. Move those imports inside the condition.

Its top-level `depth_search_channel` import and `run_return_fixture` import also
pull development concerns into normal startup. The latter supplies real runtime
constants, so it needs helper separation rather than a blind deletion.

## Recommended order

1. Separate the small production constants/file helpers and restrict development
   imports to their actual development branches. Preserve one renderer and shared
   interfaces; do not write another rendering pipeline.
2. Replace the all-branches staging superset with an explicit production-module
   allowlist. Exclude the 34 development modules and then the mixed modules whose
   helpers/dependencies have been separated. Keep the tools in the repository.
3. Remove the two diagnostic settings requirements only after proving production
   never reads them. Keep normal appearance controls in settings unchanged.
4. Validate a newly staged package with excluded files physically absent:
   isolated-Python startup, first fresh assets/materials/lights, damage/BRK,
   native insertion, normal exit/relaunch and interrupted recovery. A successful
   import or preflight alone is insufficient.

## Evidence and limits

Source/import/guard map: `artifacts/alpha/packaged-tools-audit.json`; exact candidate
counts/byte inventory: `artifacts/alpha/packaged-tools-candidates.json`. Literal
dynamic imports were checked too; no extra candidate references were found there.
Optional execution profiling was stopped after excessive instrumentation overhead.
A revised optional coordinator/preflight execution audit was rejected by automatic
approval review because its launch flags could start SFC; it was not retried.
The completed audit is static only, and makes no exhaustive live call-coverage
claim. No game/renderer was launched, no settings or package manifest changed.
