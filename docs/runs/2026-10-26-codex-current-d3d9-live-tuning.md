# Run204 — Current D3D9 live tuning and protected appearance baseline

## Result

**READY FOR SPONSOR RUNTIME CHECKOUT.** The familiar
`tools/remix_runtime/start_light_tuning_session.ps1` now selects the established
ordinary-D3D9, persistent multi-ship, asynchronous-material **Remix1.6.1 checkout**.
It does not start the older SDK/ImGui ship renderer or rebuild binaries on every
launch. The normal short1.5.2 diagnostic remains independently available; this
does not promote a new runtime across unrelated workflows.

This resolves the implementation portion of pin SFC-17. Actual extended SFC
gameplay and the visible result through the sponsor's ReShade preset remain to
be checked. No new gameplay, replacement, universal coverage or milestone PASS.

## Preserve the sponsor's new baseline

[Appearance baseline revision3](../reconnaissance/evidence/baselines/20261026-sponsor-appearance-r3/README.md)
is authoritative for the saved tuning preset, superseding the older appearance
snapshots. Its manifest contains exact SHA-256 values and copies of rendering,
lights and both placement profiles. No factory values were substituted.

Key values include emission1.2, roughness0.4, metallic0.2, anisotropy0.5;
generated roughness strength0.9/gamma0.4; brightness70, exposure-0.5, contrast1.3,
gamma0.7, saturation0.9; bloom intensity10, threshold0.95, steps2. The complete
files, rather than this abbreviated list, control restoration.

An independent backup outside Git was created and verified byte-for-byte:
`C:\Project\SFC-Modernize Engine Backups\20261026-appearance-r3.zip`.
SHA-256: `A6B8D015F5135ECDCD419B9AC6422345118EF07FAD50BDCD481B86AE5E78E498`.
Do not delete it as generated test output. Never automatically restore a snapshot
over newer user edits. The active profiles are still `config/rendering.toml` and
`config/lights.toml`; snapshots are restoration evidence, not extra live inputs.

## Implementation and safety

- Image, native bloom and quality controls use the existing bounded packets.
  A backend file-reader thread caches valid changes; native options apply on the
  renderer thread between completed frames, with rollback on rejection. No new
  file access, waits or processing inside SFC's render callback.
- Native lights retain the existing fresh shared-memory observations. The worker
  reloads light policy, publishes matching shape/packet revisions and retains the
  last good configuration after invalid edits.
- Material changes use supported USD/MDL inputs and the existing flat library
  publisher with distinct-second OpenUSD revision notification. Shader constants
  reuse prepared images. Changes requiring derived maps reuse the established
  image-processing functions outside rendering. Original geometry, UVs, images
  and emission math remain unchanged. Identical materials remain shared.
- New asset publication retains active tuning overrides; unqualified assets are
  not replaced with another model. Future late-asset tuning behavior still needs
  extended live observation; the frozen late-asset regression passed.
- Current D3D9 composition stays at the existing pre-ReShade-effects insertion
  point. The active ReShade preset's contribution was not newly measured, and
  these identical saved values do not guarantee identical appearance to the old
  later overlay path. Do not silently retune to compensate.
- The tuning controller/capture window is1800seconds, total workflow1980seconds.
  The renderer guard, native live-input worker, output receiver and control host
  all accommodate that duration. Short diagnostic limits stay unchanged. The
  launcher stops on normal SFC exit; this is not an unlimited session. Initial
  preparation/activation watchdogs remain. No timed motion or on/off experiment.
- Performance-mode recording retains existing bounded queues/counters, limited
  scene details and five-second supervisor samples. Existing20GB aggregate,
  output-surface and per-asset image limits remain. Immutable material images
  stay available until renderer exit because no per-material retirement ACK has
  been established; no claim of unlimited edit/cache capacity.
- The dedicated tuning qualifier locks code, binaries, dependencies and placement
  while permitting the two appearance files to change. Frozen diagnostic gates
  remain strict. No receipt hashes were edited to bypass testing.

## Files changed in this increment

Launchers: `start_light_tuning_session.ps1`, `start_return_image_session.ps1`,
`tools/d3d9_proof/start_d3d9_multiship_session.ps1`.

Runtime workers: `run_return_game.py`, `return_host.cpp`, `multi_scene_relay.py`,
`async_material_checkout.py`, new `d3d9_tuning.py`, `material_library.py`, and
`tools/d3d9_proof/live_light_binding.py`.

Native host/limits: `d3d9_direct_host.cpp`, `visual_controls.h`,
`live_owner_input.h`, `output_channel.h`, `output_receiver.cpp`,
`tools/remix_ingest/bounded_job.cpp`. Files without a folder above are under
`tools/remix_runtime`; the native host/limits are under `tools/d3d9_proof`.

Validation: `run_return_fixture.py`, `qualify_async_material.py`, new
`qualify_d3d9_tuning.py`, `tests/test_d3d9_tuning.py`,
`tests/d3d9_output_wire_tests.cpp`. Baseline, readmes, evidence, tracker and handoff
updated. Prior accumulated uncommitted work is preserved separately in history.

## Validation

- 568Python tests PASS, including original-image preservation, shader-only
  shared-image reuse, required-light rejection/last-good behavior and launcher
  duration wiring.
- Strict native normal/candidate host builds, x86 receiver/wire tests, bounded
  job, return host and native-light observer tests PASS. The receiver's native
  lifetime checks cover a window greater than ten minutes; no actual ten-minute
  SFC soak was performed by Codex.
- Actual current-source normal, candidate initial and candidate late fixtures
  pass their respective gates.381selected content comparisons remain exact,
  with explicitly recorded sponsor-baseline material constants and the existing
  geometry/Remix-origin exceptions. No image differences were waived.
- Live-control GPU fixture passes native image application, material publication,
  final emission0.25 definition, zero rejected controls and **zero regenerated
  image bytes** for the scalar edit. The private fixture config is separate from
  sponsor files. Native scene/HUD exactness, state preservation, resize/recreate
  and owned shutdown checks pass.
- Actual read-only current-tuning preflight PASS; original/copied client checks
  retained. No SFC gameplay launched or installed game files modified by Codex.
- All four active profile files were checked against the revision3 manifest;
  byte hashes remain unchanged.

Logs, fixture paths and build receipts: `artifacts/d3d9-tuning/run204`.
Completed older evidence and preliminary fixtures were recoverably compressed
with decompressed SHA checks to retain the20GB allowance. Restore through each
run's `run204-archive.json` or `run204-preliminary-archive.json` before inspecting
archived images/raw survey packets. Results/logs and archive inventories remain.

## Repository state and exact next action

Parent `93e8dba`; all accumulated changes remain unstaged/uncommitted, no push.
The previous SDK tuning route is historical and its old source qualification is
stale; both PowerShell tuning entry points route to current D3D9 instead. No
persistent tool server is needed for this launcher.

Close the old tuning game normally, launch the same dedicated tuning command,
enter the familiar skirmish and tune for5–10minutes. Save rendering/light edits,
then exit normally. Review that run's behavior, cleanup and client hashes before
claiming extended gameplay success or changing the saved baseline again.
