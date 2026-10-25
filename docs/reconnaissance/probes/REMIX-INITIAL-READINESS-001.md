# REMIX-INITIAL-READINESS-001 — Run163 initial material readiness

Research against normal commit fd79ce5 / pinned Remix1.5.2/API0.6.4. No SFC,
Toolkit, vendor patch, source-identity relaxation or appearance tuning. Initial
investigation uses isolated native-host source/binary copies under artifacts;
the gameplay host and normal qualification must remain unchanged until a fix is
qualified. Retain exact captured geometry and all432 generated images/materials.

## Documentation and test hypothesis

Exact pinned NVIDIA source b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4:

- [Initializer](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_initializer.cpp)
  loads mods during device initialization; asynchronous shader finalizing is
  separate from asset loading.
- [USD loading](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_mod_usd.cpp)
  watches file changes and reloads on a later frame boundary.
- [Texture manager](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_texture_manager.cpp)
  supports rtx.alwaysWaitForAsyncTextures; this changes texture scheduling, not
  mod-reload completion. Do not assume it solves library readiness.
- [Initializer options](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_initializer.h)
  documents rtx.initializer.asyncShaderFinalizing=False as a startup compilation
  wait; it is not a general material-ready query.

CONFIRMED project starts with an empty mod then atomically publishes initial
layers. STRONG HYPOTHESIS first-frame incompleteness and later initial stall
include asynchronous file-watch reload; exact packaged-runtime sequence remains
to be tested, not attributed solely to textures or shader compilation.

## Bounded controls

Use existing isolated FIRST matching-frame fixture (not standard delayed sample).
Run four owners/three contents, same lights/materials/settings, same early host
startup and return path. Native host copies differ only in bootstrap Present
count (accepted24 versus experimental1). All subsequent frames stay one Present.
Apply only child-local explicit vendor config/environment; never global settings.

Controls: accepted24; experimental1; experimental1 with texture wait enabled;
experimental1 with synchronous shader finalizing. Add a combined control only
if evidence warrants it. Keep actual supplied values and source/binary hashes
in each run. The texture-wait control is diagnostic, not a new steady-state
recommendation. Existing shader-prewarm and asset-loading policies otherwise stay.

Additional causal controls: explicitly disable material replacements for an
experimental1 run to distinguish temporal lighting history from absent mappings.
If the ready controls fail, test the existing non-prewarmed launch path with the
complete library present before device creation and documented synchronous initial
asset loading (child-only DXVK_ASYNC_ASSET_LOADING=0). That ordering control gives
up early device initialization for diagnosis; it must not silently replace it in
production or be advertised as a startup speed improvement without measurement.

Compare first and settled pixels in fixed ship ROI150..1899/700..999, returned
owner IDs, initial publication count, full image SHA multisets, existing QPC
stage timings and early600-frame delivery. Report both first output and actual
matching consumer appearance; transport ACK is not material readiness.

Bounds: existing20GB aggregate,32MiB supervisor output, existing startup/fixture
deadlines and owned-process cleanup. Two bounded screenshots per run, no
continuous capture. Preserve failed/partial results distinctly. No gameplay
launcher or production receipt may select experimental host copies.
