# Codex run — add Remix asset ingestion to first mesh test

- ID/date: `2026-10-14-remix-first-test-preparation`, America/New_York.
  Sponsor: "Let's make the first test incorporate that" — capture -> validated
  portable OBJ -> actual Remix Toolkit ingestion, not live game integration.
- Start: HEAD `fee152f`, 140 inherited pending status paths, none staged. Read
  authoritative HANDOFF and mesh-export runbook, converter input schema/analyzer,
  tests and runner/entry. Existing component 0.14 and capture ABI/limits unchanged.
  No new requirements/gates/renderer selection or M1 closure acceptance inferred.
- Fuel Guard attach verified recent trusted hook; direct sandbox connection
  denied, current quota health unknown. No daemon, helper or agents started.

## Evidence / engineering decisions

- Official NVIDIA ingestion guide checked2026-10-14: OBJ input and USD-family
  output, UI/CLI procedures documented. Exact link in Stage B runbook. CONFIRMED
  documentation only; no local Toolkit ingestion/compatibility claim.
- Narrow read-only directory checks: `C:\Program Files\NVIDIA Corporation`,
  `C:\Users\rober\AppData\Local\NVIDIA Corporation`, legacy local `ov/pkg`.
  No obvious Toolkit directory located. Not a machine-wide absence claim.
  Asked sponsor asynchronously for shortcut/install path; no install/download,
  launch or vendor configuration change. Tool/version remains UNVERIFIED.
- New `export_mesh_obj.py`: validate packet + required runtime receipt first,
  verify second read SHA256 unchanged, derive triangle-only OBJ with independently
  expanded corners, unchanged position/UV/winding, unit-normal derived vectors,
  neutral-grey source-group-labelled MTL and provenance/polygon mapping manifest.
  Raw packet untouched; no texture pointer interpretation, axes/world transforms,
  material recovery, welding, smoothing/face reversal or guessed n-gon conversion.
- Reject zero vectors/degenerate triangles/nontriangles before derivative files;
  retain raw data for offline adjudication, not automatic new gameplay. Conversion
  outcome separate from raw packet validity. Protect existing packet/receipt/
  outputs; exclusive creation, manifest last; partial I/O outputs retained and not
  ready for ingestion. No automatic deletion/overwrite.
- Automatic post-capture conversion added to existing runner, no new gameplay
  phases. It prints OBJ path and defers pipeline failure until normal exit/hash
  evidence is collected. `run-result.json` separates packet vs OBJ failures.
- Derived caps checked before writing: OBJ2MiB, MTL/manifest64KiB each. Existing
  2MiB packet/16MiB warning/32MiB log caps and geometry-hook-off policy unchanged.
  No new runtime component/native changes, so no native rebuild required this run.
- Stage B has explicit separate acceptance: real Toolkit job/report/output mesh
  and preview/count/provenance correlation, not "OBJ exists". Installed CLI/schema
  must be checked and its bounded wrapper prepared before execution; proposed
  one job/120s conversion/128MiB warning/256MiB scratch stop/8MiB log cap are NOT
  implemented or measured by the packet runner. Do not edit installed vendor
  schemas or install Remix into SFC. Keep a separate scratch workspace.

## Files created / modified

New: `tools/m1_component/export_mesh_obj.py`, `tests/test_export_mesh_obj.py`,
`docs/reconnaissance/probes/MESH-EXPORT-001-remix-ingestion.md`, this run record.
Modified: `tools/m1_component/run_m1_increment_a.ps1`,
`tools/m1_component/start_mesh_export_session.ps1`,
`tests/test_mesh_export_workflow.ps1`, `tests/README.md`,
`docs/reconnaissance/probes/MESH-EXPORT-001.md`, `docs/HANDOFF.md`.
Prior capture/export/run records preserved, not overwritten to imply runtime PASS.

## Tools / reproduction / evidence

PowerShell7.6.5/Windows PowerShell5.1 runtime shim; bundled Python3.12.14; bundled
Git; apply_patch. Process-local TEMP/TMP set to ignored absolute
`artifacts/m1/test-temp`; `PYTHONDONTWRITEBYTECODE=1`. No global setting changes.

- `python -m unittest discover -s tests -p 'test_*.py'`: final result below.
  New tests compare independent OBJ text/face indices/MTL/manifest to raw fields,
  UV/vector seams, raw nonmutation, output caps (including maximum admitted
  triangle/source counts), unsupported data and overwrite refusal.
- `pwsh -NoProfile -File tests/test_mesh_export_workflow.ps1`: PASS real parsed
  policies/forwarding, including required receipt/output forwarding to converter.
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/test_m1_visual_entry_runtime.ps1 -EntryName start_mesh_export_session.ps1`:
  PASS harmless PS5->PS7 fixture, no gameplay entry executed.
- `python tools/m1_component/export_mesh_obj.py artifacts/m1/test-temp/mesh-component/MESH-EXPORT-001.bin --receipt artifacts/m1/test-temp/mesh-component/MESH-EXPORT-001-receipt.json --output artifacts/m1/test-temp/OBJ-PREP-001/ship.obj`:
  PASS native-produced synthetic packet/cleanup receipt -> OBJ454bytes,
  MTL150bytes, manifest1011bytes. Generated files retained ignored. This synthetic
  triangle is a legitimate offline regression fixture, not real SFC evidence or
  a substitute for the requested ship test. Real capture remains NOT EXECUTED.
- No multi-GB output, screen recording or cleanup needed. No runtime tracing,
  Toolkit output, game changes or original/reference writes in this run.

## Result / final state

Stage A capture/validation/automatic OBJ conversion prepared; Stage B ingestion
explicitly included in first test but **PENDING TOOLKIT LOCATION/VERSION AND
BOUNDED RUNNER**. CONFIRMED offline conversion; actual SFC packet and actual
Remix consumer result remain unproven. No live SDK/renderer integration selected.
Final validation: **73 Python tests PASS**, workflow/PS5 shim checks PASS; local
Markdown links and modified PowerShell parsing PASS; tracked/new-file whitespace
checks PASS (line-ending conversion warnings only). Native component unchanged:
`9BA522362AA988547288F92C4E8488C722B54175079F3B339594FEA98B70EADE`.
Reference and installed client unchanged SHA256:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
New derivative fixture confirmed ignored. Final Git HEAD `fee152f`, **143 pending
status paths**, empty staged diff. No staging or commits; inherited work preserved.

Exact next action: capture the ship once when sponsor is home, then process that
same packet through the isolated Toolkit after resolving its installation and
preparing the documented bounded ingestion runner. No second gameplay capture
merely to convert the already saved data.
