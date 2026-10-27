# Run206 â€” correct light angles to SFC world Z up

2026-10-26 America/New_York; UTC artifacts 20261027.

Sponsor reports the tool stable and useful, but Run205 azimuth acts like elevation,
and positive values lower the source. This runtime feedback supersedes Run205's
world-Y-up interpretation. The controls were implemented in the wrong basis.

## Verified cause

20261016-223535-enabled/LIVE-SCENE-001-updates.jsonl supplied matrix:
[-1,0,0,300; 0,0,1,200; 0,1,0,0; 0,0,0,1]. Local mesh Y-up maps to WORLD +Z.
The first two ship translations have world Z=0, not world Y=0. Checking mesh-local
bounds alone in Run205 did not establish world up. Current code submits the
world light vector directly to Remix; no later axis exchange corrects it.
The user observation matches rotation about the wrong Y axis.

## Change

light_controls.angled_direction now uses source azimuth atan2(y,x), elevation
atan2(z,hypot(x,y)); the submitted ray is the negative source unit vector.
Positive elevation raises the source toward world +Z; horizontal azimuth rotates
in world XY. Zero offsets still return the original vector exactly. At a vertical
pole azimuth deterministically uses zero, avoiding signed-zero atan2 ambiguity.
No wire, hook, model, image or native light changes. Existing focus remains.

Files: tools/remix_runtime/light_controls.py, config/lights.toml, config/README.md,
tests/test_light_angles.py, this record, probe/evidence, HANDOFF and STATUS.
Prior dirty work preserved. No staging, commit or push.

## Current appearance preservation

Original current TOML backed up at artifacts/light-angles/run206/lights-before.toml.
Offsets native0 -10/0 and native1 +10/0 translated to azimuth0/elevation+10 for both.
Checked old versus new output vectors against qualified native bank
20261019-211853-736917-in-game/gate/native-light-latest-1.bin: errors <1e-12.
This is a REFERENCE-BANK match, not a universal migration proof: the latest
performance run intentionally retains no raw native bank. A scenario with other
incoming directions can differ. Keep that limitation explicit; visually confirm
on restart. Rendering TOML and all other light values preserved. No dome removed.
R3 remains the saved historical rollback baseline; do not restore it over tuning.

## Validation and next action

575 Python tests PASS, including the actual captured matrix basis, positive
source-Z elevation, azimuth preserving height, independent absolute angles,
zero preservation, poles and saved-look migration. Initial restricted test run
hit Windows temporary-file access errors; rerun with normal access passed.
Actual build/GPU/qualification outcomes and exact fixture paths are in evidence JSON.
Completed Run205 offline bulk archived with per-file decompressed SHA verification;
receipts and JSON/logs remain, no gameplay evidence deleted.

Latest sponsor run 20261027-030239-393268-in-game: error null, normal game exit,
renderer exit0, client critical hashes unchanged. Sponsor says stable and liked
raising the light. No controlled new nonzero corrected-angle run was launched.

Exact next action: restart the tuning launcher, confirm the saved look, then
increase elevation_degrees (positive now means up). Do not swap geometry axes,
reverse native direction globally or re-run camera discovery to fix this control bug.


Storage note: the late fixture initially declined to start because its 1024MiB
reservation would exceed the existing 20GB aggregate cap. No limit was weakened.
Completed sponsor run030239 raw/generated binary/image files were archived
recoverably with decompressed SHA verification, preserving JSON/logs and a
run206-archive.json receipt. Restore that archive before requesting old raw files.


Qualification note: first current-profile GPU fixtures rendered successfully, but
the frozen material comparison correctly rejected their USD because the sponsor
has changed metallic/anisotropy/emission and roughness-map settings since R3.
The comparison was NOT weakened. Renewed frozen tests use exact R3 temporarily,
with byte-exact current rendering.toml saved/restored in a finally block; the
live-tuning qualifier deliberately permits current valid appearance settings.
This does not promote R3 over the current user profile or claim fresh visual
validation of every artistic setting. Logs preserve the initial failed checks.
