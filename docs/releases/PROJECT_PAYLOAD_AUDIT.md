# Our alpha payload — continued audit, November 9, 2026

Sponsor priority: focus on excessive **project-authored** files/dependencies, not
vendor package trimming. This continues [the tools audit](PACKAGED_TOOLS_AUDIT.md).
**Static review only. No production changes, deletion, game/renderer launch or
refactor implementation.** The refactor remains parked.

## Count and meaning

118 project-authored files inside `SFCRemix`, 6.78 MiB:

| Current review classification | Files |
| --- | ---: |
| Development/offline/retired-mode modules already identified | 34 |
| Mixed runtime/development helper modules | 7 |
| Diagnostic placement/model-selection profiles | 2 |
| Newly identified isolation candidates below | 4 |
| Legacy native texture-hash helper | 1 |
| Retain current runtime pending further qualified separation | 70 |

Thus **48 files are now on the exclusion/separation review list**. That does not
mean 48 are safe to delete today or that the final runtime needs exactly 70
files: helper extraction may add files, and the retained 70 include mixed code.
The external `SFCRemix-Launch.cmd` is one additional convenience entry outside
this118 count. Settings/defaults/licenses/manifests are tracked separately.

Per-file accounting: `artifacts/alpha/project-payload-audit.csv` and `.json`.
Those are development evidence, not product payloads.

## New findings

### 1. Displaced asset-preparation implementation

`multi_scene_relay.Relay.__init__` creates
`asset_preparation.PreparationQueue(self.identify_asset,self.prepare_asset)`.
`progressive_scene_relay.Relay.__init__` then closes it and assigns
`parallel_assets.Pipeline(self)`. The active alpha class is
`async_material_checkout.Relay`, which inherits that progressive path.

The active Pipeline does its own capture decoding, geometry/image dependency
scheduling, base assembly and enhancement work; it does not dispatch through the
old `identify_asset`/`prepare_asset` queue. Therefore:

- Add `remix_runtime/asset_preparation.py` to isolation candidates.
- Separate the production constructor from the old queue/old methods before
  dropping its import. It is currently executed during initialization.
- The old `multi_scene_relay.prepare_asset` imports `run_direct64.resize_output`
  and the old material-binding preparation path. Removing that legacy seam can
  disconnect standalone replay tools and the subprocess texture hasher without
  changing current progressive geometry production.
- Do not claim this explains measurable startup delay. An executor constructed
  and closed before submitting jobs need not start worker threads.

### 2. Python buffer recorder is not native synchronization

`live_owner_timing.finish` imports `synchronized_buffer.save` for the old detailed
finish path. Installed untimed play instead calls `finish_play`.

Add `remix_runtime/synchronized_buffer.py` to production exclusion candidates
once the old finish branch is isolated. Keep the actual native buffered output,
frame/owner matching, readiness and leases. Removing a Python evidence recorder
must not disable synchronized delivery.

### 3. Offline loading experiments still live in normal startup

`multi_scene_relay.start_on_launch` calls `loading_policy.configure` with the
production-default `inherit` mode. Non-inherit policies are explicitly offline
experiments. Separate retained pinned runtime inputs from experiment selection
and `loading-inputs.json` receipts, then exclude
`remix_runtime/loading_policy.py` from the alpha.

Do not remove `async_material_checkout.configure_child`: it supplies the current
runtime's async material loading and real preparation behavior. Its historical
name/docstring does not make it an unused experiment.

### 4. Project evidence allowance file is no longer an installed-play policy

Add `remix_runtime/evidence_budget.py` to isolation candidates. Its sole constant
is the old development 20GB output allowance. Installed untimed play already
bypasses that quota, but imports and the existing guard CLI still consume the
argument. Decouple development capture budgets from production configuration
before excluding it. Keep actual free-space checks and per-asset/GPU bounds.

## Diagnostic work still enabled with retained reports off

These are **audit findings, not changes made**:

- `async_material_checkout.configure_child` unconditionally sets
  `SFC_D3D9_STARTUP_PROFILE=1`. `startup_profile.h` then gathers process/system
  memory and timing data and prints startup measurement lines. This is optional
  external-worker measurement, not required for rendering. It belongs in an
  explicit diagnostic mode, independently of whether reports are retained.
- `parallel_assets.Tasks._run` and `pump` collect begin/end/thread timing records
  into `spans`; pipeline preparation also appends stage timing details. Keep
  scheduling/frame/source timestamps used by real operations, but gate the
  measurement-only records separately. Do not blanket-remove clocks.
- `multi_scene_relay.finish_play` calls `native_cohort.save`, which writes the raw
  cohort `.bin` and `.json`, and then writes a separate play-session summary.
  The off-mode retention layer deletes these later. Those diagnostic dumps are
  not required to keep the running game working; distinguish reading required
  completion/error state from serializing full evidence. Minimal opted-in reports
  need only their documented small allowlisted fields.

Consequently **reports off currently means no retained run history, not that all
internal instrumentation has been disabled**. No claim of measured gameplay
impact or accumulating leak is made here. This is a production-boundary cleanup
item, not authorization to remove identity, matching, recovery or integrity work.

## Things that look disposable but currently are not

The four Relay modules form an actual inheritance chain:
`async_material_checkout → progressive_scene_relay → multi_scene_relay → live_owner_timing`.
The progressive poll explicitly calls `SingleRelay.launch` for activation; other
base methods implement current shared state, startup, light binding and shutdown.
Do not delete the older-looking base file wholesale. A focused production class
or helper separation is a refactor, not an unused-file deletion.

`SFC_DIRECT64_TIMING_ONLY=1` is misleadingly named: the current host uses it to
avoid CPU staging/readback allocation in live mode. Keep that behavior. Likewise
keep the real renderer/material warmup and output receiver startup. They are not
made optional merely because diagnostics used them originally.

## Native payload: eleven current components, one legacy candidate

| Component | Current alpha role |
| --- | --- |
| `launcher.exe` | Package entry, elevation, bundled interpreter startup |
| `return_launcher.exe` | Verified copied-game launch and preload |
| `return_host.exe` | Creates the actual current-user return mapping; validity/parent-stop lifecycle. Observe-only does not load another renderer. |
| `m1_controller.exe` | Semantic component installation/coordination and shutdown |
| `m1_gate.dll` | Native startup/attachment gate |
| `m1_light_component.dll` | Actual semantic mesh/state/light/damage/break capture component despite its narrow historical name |
| `SFCRemixReturn.dll` | Game-side return/insertion and graphics integration |
| `d3d9_direct_host.exe` | Actual retained D3D9/Remix rendering process |
| `output_receiver.exe` | Output resource transfer/import receiver; distinct process/bitness responsibility |
| `bounded_job.exe` | Owned-process containment and parent-death cleanup; installed recording quota does not terminate play |
| `mesh_checksum.dll` | Native mesh/material texture identity functions currently used by progressive preparation |
| `texture_hash.exe` | **Legacy candidate**: progressive materials use the DLL's `sfc_texture_identity`; old binding path and manifest role still require cleanup before removing EXE. |

Two launcher EXEs or several DLLs are not automatically duplicate work: their
process/bitness/lifetime roles differ. A smaller visible file count alone is not
proof of a simpler or correct interface. The tiny root CMD and optional
Troubleshoot CMD are user launch choices, not development toolsets.

## Repeated helpers and misleading names

The audit inventory locates `fnv`, `digest` and process-query wrappers across
modules. In particular, `owner_rebind.fnv`, `material_controls.fnv` and
`live_lights.fnv` implement the same wire-checksum family. Share their implementation
where useful, but each distinct packet still requires its checksum operation.
SHA256 helpers also differ in uppercase/lowercase receipt formatting; preserve
existing wire/manifest identities when consolidating. Native xxHash geometry/
texture identities are different algorithms, not redundant FNV checks.

`run_return_fixture` supplies production paths/hash helpers; `run_offline` supplies
storage/constants; `player_replacement` supplies native offsets; `light_discovery`
supplies an actual release component check. The prior seven mixed-module list
stands. Rehome necessary helpers before excluding development files. Renaming
`proof`, `fixture`, `calibration` or `checkout` alone would only conceal the coupling.

## Recommended priorities when the parked refactor is reopened

1. Disconnect eager inactive imports and the displaced preparation constructor.
2. Isolate the measurement-only work listed above from the normal runtime.
3. Rehome genuine shared helpers/wire definitions; remove legacy import chains,
   old hash subprocess dependency and diagnostic profile requirements.
4. Produce a production-module allowlist; keep the test/tool implementation in
   the development tree. Preserve one shared rendering/data path.
5. Test a freshly staged package with removed candidates physically absent through
   first assets, enhancements, new ships/fighters, lights, damage, breakup,
   camera changes, native fallback, exit/relaunch and interrupted recovery.

Read-only source/AST and package-role review only. No timing benchmark, new
runtime trace or gameplay test was performed, and no vendor trimming was pursued.
