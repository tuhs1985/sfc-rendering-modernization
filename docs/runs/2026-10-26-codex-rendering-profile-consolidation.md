# Run203 — One readable rendering profile

## Authorized scope

The sponsor superseded Run202's proposed split-file layout and requested one
organized TOML with readable spacing. This authorizes configuration consolidation,
not new per-layer image processing or a different rendering architecture.

## User-facing result

- Authoritative editable profile: `tools/remix_runtime/config/rendering.toml`.
- Factory restore: `tools/remix_runtime/config/rendering.example.toml`.
- Numbered sections: surface material/emission; texture filtering and quality;
  whole-image adjustments; exact native Remix bloom options.
- Existing independent light sources remain in `config/lights.toml`.
- Former material/image/quality live profiles and examples were removed after
  exact local backups in `artifacts/config-consolidation/run203`. Historical
  accepted run snapshots and versioned baselines remain evidence.
- The current tuned values are preserved. Factory restore is deliberately a
  separate example, not another live profile. Copy one section to reset only it.

## Implementation

`rendering_config.py` supplies one path, bounded TOML parsing, allowed sections
and deterministic section projections. Material, image and quality workers read
only their relevant controls. Comment/spacing edits do not trigger material
regeneration; image/bloom changes do not rebuild roughness maps. Invalid edits
retain each subsystem's last accepted values. Existing reload cadence, revision
bounds, preparation snapshots and short-run profile freeze remain in force.

All startup/preparation paths now use the same profile: `multi_scene_relay.py`,
`live_owner_timing.py`, `material_binding.py`, the material qualifier and both
launcher messages. Qualification locks track the canonical rendering profile and
lights. `live_return.py` includes the new shared parser in its source lock.
Root README and the configuration README point to the new authority.

Run202's pending native controls are included: image wire v2 is64bytes, legacy v1
remains48; native bloom is independent of the image-grading enable switch.
`remix_image_controls.h` passes four exact native option names and individual
values; `ship_live_host.cpp` retains rollback on native rejection. The material
input now accepts native USD `emissive_intensity`; legacy `illumination_strength`
remains compatible, but both together reject. The existing value5 is preserved.
No illumination-map math, captured UVs, original images or geometry changed.

## Scope and evidence limits

Native bloom is whole-image processing, including other bright surfaces and
reflections. File organization does not make it illumination-only. No native
per-layer brightness/contrast/saturation was found in the pinned path, and no
custom replacements were added. `rtx.emissiveIntensity` is deliberately omitted:
API acceptance did not establish meaningful primary textured-emission control in
the strict test. Existing per-material strength is the supported dimmer.

Pinned NVIDIA reference:
[RtxOptions](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/RtxOptions.md).
Exact bloom names: `rtx.bloom.enable`, `rtx.bloom.burnIntensity`,
`rtx.bloom.luminanceThreshold`, `rtx.bloom.steps`.

## Validation and repository discipline

The byte-for-byte migration comparison is recorded in
`artifacts/config-consolidation/run203/migration-validation.json`: effective
material56/image64/quality48 packets are identical before and after consolidation.
The full Python regression suite passes564tests. Native x86/x64 image controls
pass40checks each, including malformed packets, bounds and restoration. Native
material, quality, light and return contracts pass their existing builds/tests.
Normal and candidate D3D9 hosts compile with the existing strict build policy.

Final rendering and launcher gate results are recorded in the Run203 evidence
manifest and authoritative handoff. A first private GPU check hit its existing
five-second completion timeout and is retained as partial evidence; retry results
must be assessed independently. No timeout or output limit was increased.

No SFC gameplay was launched for this configuration task. Existing accepted
Run201 gameplay evidence remains historical, not a new runtime PASS. Original
client/assets, diagnostic-geometry policy and runtime dependencies are unchanged.
No staging, commit or push; pre-existing dirty work based on `93e8dba` is preserved.

## Final offline result

The final source-matched SDK matrix passes all14private fixtures plus image and
quality pixel probes. Native bloom enable, intensity, threshold and steps change
the expected halo pixels; global emission visibility remains unproven and omitted.
Normal and isolated async D3D9 fixtures pass their existing qualifiers, including
the late-asset case and381selected exact content comparisons. Actual read-only
normal, candidate and tuning launcher preflights pass. This is offline readiness,
not a new gameplay or milestone claim.

The fixture timeouts exposed an existing isolation error: a textured private test
could prepare the sponsor's tuned maps before installing its own factory profile.
`qualify_live_return.py` now freezes that private profile before first capture.
The focused light/capture checks and final full matrix pass. Production asset
preparation, sponsor values and timeouts were not changed to make tests pass.
The legacy fixture's preparation deadline still failed intermittently after that
isolation fix; a bounded retry passed. The textured native wait is30seconds,
despite its older `fixture seed10s` error label. Do not claim the consolidation
resolved that timing variability or use those fixture times as gameplay loading
measurements. One orchestration preflight also used mutually exclusive flags;
the actual supported `--light-tuning` preflight passed after its existing native
light/calibration prerequisites were renewed through actual offline tests.

Exact fixtures, result labels and limits are in the
[Run203 evidence](../reconnaissance/evidence/20261026-rendering-profile-consolidation.json).
Detailed logs and migration backup are under `artifacts/config-consolidation/run203`.
Completed private-fixture textures are recoverably compressed; restore from each
run's `run203-texture-archive.json` before image-file reinspection. Logs, packets,
manifests and pixel evidence remain. No evidence was discarded to claim a pass.
To satisfy the unchanged aggregate reservation, generated images from the older
normal105940 and accepted Run201 were also SHA-verified archived. Raw geometry,
logs, manifests and the user's FCA image-review folder remain intact. Forty
reviewed older fixture BMPs are recoverably archived separately. Per-run receipts
and the three archive inventories in the evidence manifest give exact restoration
paths. Restore archived files before reopening those older image comparisons.

The current-source normal fixture is222812; candidate initial222951 and late223020.
All three remain available for their current qualification. No qualification
receipt was renewed by editing hashes or suppressing a failed condition.

## Exact next action

Use the existing light-tuning session to edit `rendering.toml`, starting with one
control at a time. Do not resume illumination staging or appearance tuning on the
sponsor's behalf merely because the configuration layout is now consolidated.
