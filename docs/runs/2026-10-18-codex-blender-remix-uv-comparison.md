# Run37 — Blender/Remix texture-coordinate convention comparison

SFC-RETURN-20261018-37;2026-10-18 America/New_York. Current approved experimental
in-game return-path increment;no milestone advancement. Sponsor requests comparison
of working Blender capture with exact Remix inputs,not another game test.

## Baseline and sources

HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d;existing dirty/untracked work retained,
index empty. Read HANDOFF,M1 approved disposition,Run33/35,actual source exporter,
mesh/material host,texture preparation and existing audit/probe definitions.
FuelGuard attach verified actual thread hook;no helper/subagent/daemon.

Actual newly completed game run `20261018-210454-034369-in-game/result.json` records
normal_game_exit=true,gate_clean_unloaded=true,controller0,renderer0,unchanged
critical installation hashes/settings,error null. Prepared PNG1920x1080 captured
owner2/revision2/frame1551,sequence322,26.2677ms request age,SHA256
`a5eb8b82ca0e9361e333d53bba0e4750e1fcd92fb0ae04f562c49f27c82819df`.
It is the post-mask prepared layer before late AddImage,not raw SDK output. Sponsor
identifies reversed saucer here,so late insertion is not the first source of it.
Do not invent a new complete gameplay checklist from this image.

## Experiment and first demonstrated difference

Documented BLENDER-UV-COMPARE-001 before execution. Installed Blender5.0.1,
build a3db93c5b259,background/factory-startup/threads2;CPU Cycles1sample,128square,
emission-only asymmetric quad. No security elevation or game launch. Actual OBJ
importer reads existing fresh-capture export;dump per-corner local position,
material and UV,then clear scene and render independent coordinate control.

Installed importer preserves all19,110corner local positions/UV float32 bits and
group/material associations exactly (multiset permits importer ordering changes).
The source export's native mesh and current runtime's native mesh are byte-identical,
SHA256 `ef42faf540821e9ccc4e0a7e25dfe404e16bd2c6d705e6e210bbdeb63a8558dd`.
Read-only audits of BOTH captures pass58groups/81original+PNG+DDS image associations.
Saucer group45 uses same original top.bmp;no filename/group substitution.

Control uses top-left position UV(0,0),same numeric corner layout as retained
fence-completed Remix control. Source image TL/TR/BL/BR red/green/blue/yellow.
Actual Blender render blue/yellow/red/green;actual pinned Remix render
red/green/blue/yellow. **CONFIRMED:**opposite vertical texture origins for the
same numbers. Previous correct Remix control was not evidence of Blender parity;
that untested relationship is now measured. BMP file row storage alone was never
sufficient justification. **STRONG HYPOTHESIS:**our absent origin conversion
explains the saucer mismatch. Native SFC matched visual parity still unproven.

Smallest supported correction is Remix-adapter-only v=1-captured_v (or an
equivalent derivative-image row conversion,not both). Original packets,OBJ,
positions,normals,winding,textures must remain unchanged. No production correction
applied in this diagnosis;no qualification pins invalidated. Brightness/native
lighting and differing face rejection remain independent issues.

## Reproduction, bounds, limitations

From project root, use installed `C:/Program Files/Blender Foundation/Blender 5.0/blender.exe`:

```text
--background --factory-startup --threads 2 --python tools/remix_runtime/compare_blender_uv.py -- NEW_OUTPUT artifacts/remix-runtime/exports/20261018-202703-fca/ship.obj
```

Use absolute quoted paths for launch. Caller owned-process watchdog90s/8MiB,
100ms polling;actual~4seconds,4small outputs2,219,877B. Tool refuses overwrite.
Sandbox denied Blender extension cache compat.dat writes;normal quit/import/render
completed;no installed configuration changed. Deprecation warning use_nodes is
nonfatal. Earlier Remix control shutdown remains PARTIAL,not silently promoted;
only retained fence-completed image corners used here.

Bundled Python3.12.14,existing Pillow/numpy;analysis command:

```text
python tools/remix_runtime/analyze_blender_uv.py artifacts/remix-runtime/runs/20261018-uv-blender-compare artifacts/remix-runtime/exports/20261018-202703-fca/ship.obj artifacts/remix-runtime/runs/20261018-202703-589843-in-game artifacts/remix-runtime/runs/20261018-210454-034369-in-game artifacts/remix-runtime/runs/20261018-200014-459912-texture-control
```

Initial analyzer assumed an OBJ axis conversion;actual importer readback disproved
that local-array assumption. Corrected analyzer compares actual unchanged local
positions,not a guessed axis mapping. No production axes changed. Readback includes
UV-flip/wrong-material/changed-position rejection regression.

222Python regressions PASS4.467s;git diff --check PASS (existing LF/CRLF notices).
No native rebuild necessary:only diagnostic scripts/tests/docs changed.
Source client files read-only;hash continuity comes from actual game's retained
result,not a new unrelated live hash measurement. No persistent process/session.

Evidence [summary](../reconnaissance/evidence/20261018-blender-remix-uv-origin.json).
Archive raw retained,175,996B:
`artifacts/remix-runtime/archives/20261018-blender-uv-compare.zip`,SHA256
`8C02C2CA31E02F1EB2527CB85DD000B9CC827B0DF9CEDA1DA0E87B2A86D56011`.
No large continuous capture,source-asset changes,stage or commit.

Files added:compare_blender_uv.py,analyze_blender_uv.py,test_blender_uv_compare.py,
probe,evidence JSON,this record. HANDOFF updated;old checkpoints retained.

**Exact next action:**apply and offline-qualify only the evidence-backed Remix
texture-origin adapter conversion,then use a matched saucer visual check before
claiming native parity. Do not redo geometry capture or repair the Blender model.
