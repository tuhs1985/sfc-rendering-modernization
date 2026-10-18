# Run35 — Blender derivative of the actual captured cruiser

SFC-RETURN-20261018-35;2026-10-18 America/New_York.
Sponsor confirms emissionOFF result looks better,still bright,and requests the
model for Blender. Explicitly excludes conversion of an installed SFC MOD file.
Subsequent "proceede" authorizes finishing/checking the export,not new rendering.

## Baseline / source of truth

HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d;119starting porcelain entries,
prior edits retained,indexempty. Read HANDOFF,Run34,current exporters/mesh decoder,
latest actual runtime result/fresh-asset/texture manifests. FuelGuard attached
actual thread through hook;no daemon/helper/delegation. No staging/commit.

Source **only fresh runtime packet**:
`artifacts/remix-runtime/runs/20261018-202703-589843-in-game/assets/asset-2.bin`,
with its same-epoch JSON resource references. SHA256
`1f48e13793ea40ab51248c7c96573b2b38aef0f0c4f83203a484f42a0f72f5b4`.
GeometrySHA `16981bd6f5b84f8d9f17f1395a92b34011387ddba5e1a64fbff4b21bd81e65a5`.
Model label `assets/models/fca/fca.mod` is provenance only;that file is NEVER
opened by this exporter. No old imported model,USD or asset-folder geometry used.
Primary images are already retained verified PNG derivatives of originals linked
by live resource references. Export reads those cached PNGs,not guessed textures.

## Artifact / implementation

Added `tools/remix_runtime/export_live_obj.py`:decode/validate live packet and
image/geometry hashes;write isolated OBJ/MTL and56PNG files.19,110 independent
corner vertices,6,370triangles,58groups. Exact original positions,raw normals,
UVs and triangle order;no normal normalization,welding,axis/UV flip,rotation or
geometry repair. No model/world/camera transform,temporary light,whole-hull emission
or secondary glow exported. Blender may use its own import/view conventions;
actual Blender visual import not executed or claimed validated here.

New `--verify` reads OBJ arrays/groups/faces and MTL assignments back,compares
float32 values exactly with captured packet and verifies copied primary PNG hashes.
Refuses overwrite. Maximum16MiB OBJ/128MiB derivative;actual content4,145,609B
(manifest additional). Generated outputs ignored;source and run records versionable.

Prepared folder:
`artifacts/remix-runtime/exports/20261018-202703-fca/`
contains `ship.obj`,`ship.mtl`,`manifest.json`,`textures/`.
OBJ SHA `012f90ee8ea14d280262c812a1852a640084e5c0ca64922a3eb55d21d963b0d5`;
MTL SHA `d82c2ac0b555a08a44f0c9d83dbd7eeb59d75f69f4e97eb94525ebdb332c751b`.
Portable ZIP `artifacts/remix-runtime/exports/20261018-202703-fca-blender.zip`,
2,049,729B,CRC PASS,SHA256
`EAB8FCD3EA9A64E103C3D9FDFEEDB2E7566A3C915EAFC20172440822661F1630`.

Bundled Python3.12.14/Pillow;no new dependencies/native rebuild/game launch:

```text
python tools/remix_runtime/export_live_obj.py artifacts/remix-runtime/runs/20261018-202703-589843-in-game artifacts/remix-runtime/exports/20261018-202703-fca
python tools/remix_runtime/export_live_obj.py artifacts/remix-runtime/runs/20261018-202703-589843-in-game artifacts/remix-runtime/exports/20261018-202703-fca --verify
```

First command already executed;do NOT repeat over existing export. Second PASS:
LIVE_CAPTURE_OBJ_READBACK_PASS. `tests/test_export_live_obj.py`:synthetic export
works with NO installed MOD file;overwrite refusal;changed UV rejection. Full
regressions215PASS/4.489s,TEMP/TMP=ignored artifacts/test-temp. JSON/references/
archive CRC/git diff --check PASS. No production source qualification changed.

## Latest runtime receipt / limitations

202703actual run normal game exit,controller0,renderer0,hook removal/unload true,
original critical hashes unchanged. Sponsor screenshot copied unchanged to
`docs/reconnaissance/images/20261018-emission-off-sponsor.png`. Sponsor says
"better ... still bright ... looks good";this supports visible improvement,not
native-light fidelity,complete control checklist or proven sole brightness cause.
Record texture reversal still unresolved. Do not fix it silently in Blender export.

Latest raw run53,419,474B archived(raw retained,no deletion) at
`artifacts/remix-runtime/archives/20261018-emission-off-runtime.zip`,6,326,083B,
CRC PASS,SHA256 `6173D1A2B0F8B34E5076B6A68F0E2F80E21B2F0FE1E8618F0F2999F1119A0ADF`.
No continuous screenshots/repeated mesh dumps introduced;existing runtime probe
REMIX-TEXTURED-RETURN-001 bounds unchanged. This run is offline conversion only.

Files created/modified:new exporter and3tests,this run record,HANDOFF and curated
sponsor screenshot;ignored derivative/ZIPs as above. No source asset/client edits,
stage or commit. No active process/session needed. Capture is only this selected
rigid model/LOD,not all ship states or an improved replacement asset.

**Exact next action:**sponsor imports exported `ship.obj` via Blender's Wavefront
OBJ importer,keeps MTL/textures alongside it,and selects Material Preview to view
textures. Investigate saucer native-sampling relationship separately;no new game
test needed just to inspect this captured model.
