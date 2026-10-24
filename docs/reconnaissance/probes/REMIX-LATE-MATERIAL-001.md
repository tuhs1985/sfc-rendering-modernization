# REMIX-LATE-MATERIAL-001 — initial versus incremental material application

Status: completed isolated Run150 diagnostic; NOT a normal game flag.
See [run/adjudication](../../runs/2026-10-24-codex-initial-loading-material-workaround.md)
and [curated receipts](../evidence/20261024-late-material-controls.json).

## Definition

Use existing offline captured FCA/RCA/FDD fixture, four owner instances including
shared FCA owner31, normal maps, camera, lighting and materials. Start candidate
stock1.6.1, preserve working1.5.2 comparison. Never launch SFC or Toolkit.

Normal `tools/remix_runtime/return_fixture.cpp` saves its first image only after
all owner assets arrive. For this probe only, copy it into ignored
`artifacts/material-transition-fixture/return_fixture.cpp`, retain normal source,
and add one-shot `scene.shipSample(...)` when:

- lateAssetFixture is true, asset_ready==3;
- drawn frames>=60 and<120, and same-frame source correspondence holds;
- rename completed sample to `fixture-ship-initial.bmp` and log
  `INITIAL_MATERIAL_SNAPSHOT` with frame, asset count, draws and QPC.

The existing late fixture withholds its late owner until120draws; validate the
snapshot precedes the second layer publication using QPC/perf_counter timestamps.
Keep the existing two post-arrival snapshots. Build isolated x86 fixture using
the established VS18Community vcvars32, `/std:c++20 /EHsc /W4 /WX`, normal
d3d11/d3dcompiler/advapi32/ole32/user32/dbghelp libraries. Use absolute normal
include paths in this copy. Copy supporting normal return-bin DLLs/executables
without overwriting the isolated rebuilt fixture or normal binaries.

Diagnostic source SHA256:
`905FF07838F2A11EAB75F74B7D9E55AEF3DBC3426E160B8A997184BE28A22110`.
Diagnostic executable SHA256:
`2751ED5564BE9AFC0EDCEF2CC06C6A70DCE1EB92EC05AD0D75BD81A9AB8AD97A`.

## Supervisor controls and reproduction

Existing ignored `artifacts/trace_late_materials.py MODE` imports the normal
fixture module but overrides its BIN to the isolated folder. It invokes:

```
--multi-ship --multi-ship-resources --multi-ship-late-asset
--prewarm --startup-profile --pipeline-mode performance
```

All modes except `normal` add `--runtime-candidate 1.6.1`. Modes:

- `candidate`: unchanged candidate loading/materials.
- `disabled`: exact candidate child receives DXVK_DISABLE_ASSET_REPLACEMENT=1.
- `emission-off`: only generated stage emissive_intensity becomes0.
- `normal`: unchanged pinned1.5.2 positive control.
- `async-off`: exact candidate child receives DXVK_ASYNC_ASSET_LOADING=0 and its
  own DXVK_CONFIG_FILE gets rtx.initializer.asyncAssetLoading=False.
- `async-off-emission-off`: combines the preceding one-option policy with
  generated emission0, preserving all image/map contents.

Never set either override globally or in production tuning. Log actual effective
candidate option plus generated master/layer hashes/publication timestamps in
late-material-probe.json and async-control-input.json. Library interception must
assert standalone fixture and restrict stage writes to that run's gpu/assets.
No production shader/material scalar changes or vendor patch.

After native closes the initial BMP, supervisor converts only it to PNG and
verifies decoded RGBA equality before deleting its own BMP. This keeps the
unchanged32MiB envelope; initial uncompressed three-BMP attempt is partial and
excluded. No rendering-thread conversion or continuous screenshots.

## Analysis and acceptance

`artifacts/analyze_late_materials.py` compares true initial, post-arrival and
settled images with fixed ROI x150..1899/y700..999, excluding banner/markers.
Derive background from each ROI first pixel; use union non-background masks.
Read432generated image/native SHA multisets directly or via verified archive
receipts. Record per-model response, four ACKs/three contents, state/device/
shutdown checks, native process/job cleanup and option logs. First async-off
and its repeat must remain separate cases, not overwritten mode results.

Bounds:100s native/285s owned job,32MiB supervisory envelope,20GB aggregate;
reserve storage before starting, archive only verified completed generated
outputs when needed. Do not raise limits to make tests pass. Do not count
incomplete/capped runs as performance or material success.

Success here proves repeatable returned material response across initial/late
publication, not full runtime promotion, GPU residency readiness, roughness,
all models, gameplay or a sub-two-second load. No active session is required to
resume. Next implementation should move the candidate-only option into the
standard harness and rerun normal fixtures rather than relying on monkeypatches.
