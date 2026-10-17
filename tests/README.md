# Verification placeholder

This directory is reserved for repeatable tests and legally trackable fixtures.
Game binaries and proprietary assets must remain outside Git.

## M1 offline checks (no gameplay)

Complete selected mesh export: the normal build also runs
`m1_mesh_export_tests.cpp` and `m1_mesh_component_tests.cpp` (synthetic native
objects, no game/hooks installed). Python regressions are
`test_analyze_mesh_export.py`; workflow validation is
`pwsh -NoProfile -File tests/test_mesh_export_workflow.ps1`. The PS5 shim fixture
accepts `-EntryName start_mesh_export_session.ps1`. Probe definition:
`docs/reconnaissance/probes/MESH-EXPORT-001.md`. Never execute the actual export
entry as an offline test: it starts the gameplay workflow.
The same capture now also runs `export_mesh_obj.py` to prepare OBJ/MTL/manifest
for a separate Remix Toolkit ingest. `test_export_mesh_obj.py` verifies derived
attributes, source labels, provenance, overwrite refusal and bounds. See
`docs/reconnaissance/probes/MESH-EXPORT-001-remix-ingestion.md`; actual Toolkit
consumption must be recorded separately from a successful file conversion.

Use the bundled PowerShell 7/Python runtimes recorded in the probe definitions.
`tools/m1_component/build_m1_component.ps1` builds x86 binaries and runs contract,
WINMM forwarding, source-copy, production tint lifecycle and shading-off tests.
Generated binaries stay under ignored `artifacts/m1/bin/`.

Python: `python -m unittest discover -s tests -p 'test_*.py'`.
In the restricted Windows sandbox set process-local TEMP and TMP first to the
existing ignored `artifacts/m1/test-temp` absolute directory; default sandbox
temporary directories may reject fixture writes. Do not change system settings.

Windows PowerShell 5.1 runtime shim tests are harmless and do not launch SFC:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/test_m1_visual_entry_runtime.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/test_m1_visual_entry_runtime.ps1 -EntryName start_m1_shading_off_session.ps1
```

Runtime and visible-behavior claims require the separate versioned probe and
sponsor observation; these synthetic tests cannot establish them.

M1 closure measurement: `python -m unittest discover -s tests -p test_m1_frametimes.py`
and `pwsh -NoProfile -File tests/test_m1_closure_telemetry.ps1` cover bounded
capture, parser PID/swap-chain separation, output caps and memory attribution.
Use the process-local TEMP/TMP convention above. Actual native SFC PresentMon
coverage needs `M1-CLOSE-MEASURE-001`; synthetic success is not measurement proof.

Endurance preparation: `pwsh -NoProfile -File tests/test_m1_endurance_workflow.ps1`
tests the production neutral-policy/gate blocks with a synthetic event (no SFC).
`tests/test_m1_measurement_cancel.ps1` exercises cancellation/result preservation
with a fake child; frame Python regressions exercise real owned-child stop.
PS5 runtime shim fixture also accepts `-EntryName start_m1_endurance_session.ps1`.

The build also runs `m1_corner_snapshot_tests.cpp` (read-only header/production
budget/serializer fixture). `tests/test_m1_corner_action_cues.ps1` exercises the
production cue block with synthetic event/clock and physical sound mocked; no
SFC launch. Run shim fixture with `-EntryName start_m1_corner_snapshot_session.ps1`
for the new entry. Corner analyzer regressions remain read-only synthetic inputs.

# Texture-reference recovery addition (2026-10-16)

`test_export_mesh_textures.py` checks same-epoch association, all five source groups/
ten image resources, original hashes, lossless decoding, unchanged geometry/UVs,
explicitly unproven secondary roles and bounded PARTIAL failures. Native mesh tests
also exercise registry resolution, retirement/change rejection and the ten-resource
stop; production config tests require default-off/exclusive mesh mode. Run
`test_texture_export_workflow.ps1` and `test_mesh_export_workflow.ps1` for policy/
forwarding without SFC. `test_m1_visual_entry_runtime.ps1 -EntryName
start_mesh_export_session.ps1 -EnableTextureReferences` checks the PS5-to-PS7
handoff using a harmless fixture, not the real runner.

