# Run205 — directional light angle controls

Date: 2026-10-26 America/New_York (UTC artifacts 20261027).

Sponsor reports current tuning stable and enjoyable; requested editable light elevation
while retaining focus, plus a possible three-point arrangement. No SFC launched by Codex.

## Implementation and evidence

Added `angle_mode`, `azimuth_degrees`, `elevation_degrees` to the existing light
reader. Offset follows the captured source bearing; absolute sets a world-Y-up
bearing. Positive elevation raises the SOURCE; Remix ray direction is its inverse.
Elevation clamps at +/-90. Zero offsets return the original direction unchanged.
Native lights and the project light share this conversion. Directional only;
nonzero angles on other shapes reject rather than silently misbehave.
Position/focus and original SFC observations, assets, hooks and packet layouts unchanged.
No positional orbit or ship-relative directional rotation is claimed.

Files: tools/remix_runtime/{light_controls.py,live_lights.py,light_shapes.py,
config/lights.toml,config/README.md}; tests/test_light_angles.py; this run record,
probe, evidence JSON, docs/HANDOFF.md and docs/STATUS.md. Earlier dirty work preserved.

All previous TOML settings compared identical before/after adding neutral defaults:
artifacts/light-angles/run205/config-preservation.json. Rendering settings untouched,
including sponsor's newer exposure/saturation edits. R3 remains a historical rollback
snapshot, not a replacement for current settings. No dome automatically disabled.

572 Python tests passed, including independent translation-free direction conversion,
source/ray sign, 25-degree elevation, absolute bearing, normalization, pole clamp,
zero-preservation and invalid inputs. Actual candidate build and GPU/launcher
qualifications are recorded separately in this run's evidence JSON.

## Latest sponsor tuning observation

20261027-012701-716626-in-game lasted 417.969 seconds. Sponsor says stable/fun.
Top-level error null, normal_game_exit true, renderer_exit 0, original critical
hashes and launcher settings unchanged, broad proxy restored. This is NOT a clean
hook-unload proof: controller exit8, gate_clean_unloaded false, cleanup explicitly
process-exit reclamation. Missing optional PERSISTENT-SCENE-001.json remains a
reporting limitation; result.json labels the run PARTIAL. Do not rewrite that
result or interpret it as a newly demonstrated persistent-scene/shadow gate.

## Limits and next action

Restart the current tuning launcher once, then set an existing directional light's
`elevation_degrees = 25.0`, save and observe. Defaults remain zero. For a fixed
three-light rig use absolute angles and optionally convert project_fill dome to
directional; this does not disable all indirect lighting. Original SFC models
cannot receive Remix shadows; retained Remix instances can occlude each other's
light, but controlled cross-ship shadow confirmation remains pending.

No new renderer architecture, baseline promotion, staging, commit or push.
