# Run33 — washout and apparent saucer reversal diagnosis

SFC-RETURN-20261018-33;2026-10-18 America/New_York.
Sponsor asks to figure out washout and flipped texture. Diagnostic authority only;
no production material/UV/geometry correction or new gameplay run performed.

HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d;existing dirty work preserved,index
empty,no stage/commit. Read HANDOFF,current textured contract/probe,Run30–32,
native producer/material adapter,ImageStore,mesh decoder and earlier image/secondary
role evidence. FuelGuard attached real thread through hook;no daemon/helper.

## A — washout: established implementation cause, not measured sole contribution

`tools/remix_runtime/ship_textured_asset.h`,TexturedAsset::create,assigns every
primary hull bitmap to BOTH albedoTexture and emissiveTexture,white emissive
constant and intensity1. `ship_live_host.cpp` also adds a provisional sphere light
with radiance200. Thus ordinary hull markings are explicitly self-illuminated in
addition to reflected lighting. This was a diagnostic visibility shortcut,not
faithful native shading. **CONFIRMED configuration defect relative to normal
surface appearance;STRONG HYPOTHESIS major contributor to sponsor's washout.**
No matched emission-off GPU experiment measured its fraction,so exposure/tone
mapping/colour-space contributions are NOT ruled out. Do not promise merely
lowering a brightness slider establishes faithful native rendering.

Static native combiner evidence already documented in
[secondary role](../reconnaissance/2026-10-16-secondary-texture-role.md):configured
term primary*clamp(secondary+vertex_lighting),not all primary pixels emitting.
Remix public source carries emissive intensity>0 into an explicit emissive
material;shader adds emitted radiance. These are qualitatively different models.
Corrective direction:ordinary primary as surface colour,not unconditional emission;
keep proven secondary contribution separate and lighting explicitly provisional.
This run does not choose light strength,claim native-light extraction,or implement.

## B — reversal: data corruption and wrong group assignment ruled out;cause open

New reusable read-only `tools/remix_runtime/audit_texture_delivery.py` audits
actual fresh FCA run `20261018-193951-766949-in-game` against packet,resource
manifest,native mesh,material packet,original copies and copied-install originals.
Result:19,110 corner vertices,58groups,81unique images;all positions/normals/UVs
exactly equal packet;group indices and primary content hashes match;PNG/DDS pixels
match original decoded images exactly. Group45 uses original `assets/models/fca/top.bmp`,
1,980corners,1024-square,same SHA256
`7edff9804f13617c96d98991906ac8f6ba2e17a3734c029742c6128545ff4a18`.
Original-vs-DDS mean pixel error0;vertical-flip MAE13.695805,horizontal10.606157.
This proves conversion did NOT flip stored pixels. It does NOT establish how
native SFC or Remix samples them on a particular visible surface.

Initial audit required literal filenames and flagged wrpout/wrpin and reg_lft/
reg_rht aliases. Content hashes prove each pair byte-identical;ImageStore reuses
first filename for identical content. Corrected audit to compare resolved original
hashes,not misdiagnose valid deduplication as a mapping error. No image path changed.

Native static006AC2E2–2EF copies corner+10/+14 UVs unchanged into prepared geometry;
collector reads corresponding raw words4/5. SDK CreateMesh copies caller vertices
and exposes the same float2 buffer;external instance uses identity texture transform.
Inspected pinned shader loads float2 and applies surface texture transform,not
an unconditional V flip. These support ruling out an obvious exporter/API flip,
NOT ruling out image-loader origin,material/UV interpretation or face-selection
differences. SDK instances currently double-sided;native face rejection is not
identical. Do not rotate saucer,reverse faces,or apply global1-v from screenshot.

**CONFIRMED:**saved assets/UV/group association intact. **STRONG HYPOTHESIS:**a
native-versus-modern sampling/visible-surface convention difference. **Unresolved:**
which exact convention/face relationship explains the reversed saucer. Positive
BMP height1024 denotes bottom-up file storage,but Pillow correctly decodes it;
height alone does NOT prove SFC uploads raw rows or authorize a flip.

## Tools, commands, evidence and validation

Python3.12.14/Pillow/numpy already installed;no dependencies added.
`python tools/remix_runtime/audit_texture_delivery.py artifacts/remix-runtime/runs/20261018-193951-766949-in-game`:
PASS read-only;stdout small JSON,no new runtime capture or image dumps. At most
one original/PNG/DDS image triple decoded at a time,4096-square existing limits,
256resources/2MiB packet. Treat this as bounded offline evidence audit,not a probe.
Curated [audit result](../reconnaissance/evidence/20261018-washout-orientation-audit.json).

`tests/test_texture_delivery_audit.py`:intact synthetic fixture PASS,mutated UV
rejected,mutated DDS pixels rejected. FullPython regression210PASS/4.427s;
TEMP/TMP=ignored artifacts/test-temp. No native rebuild or source qualification
invalidation:only standalone audit/test/docs added. Existing launch readiness stays.
Client/texture inputs read-only;no game/client/config modifications;no new hash
continuity claim beyond retained runtime results. No screenshots/archives deleted.

Read-only research inspected pinned NVIDIA commit
`b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4`,not unverified current headers:
[UV loads/transform](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/shaders/rtx/concept/surface/surface_interaction.slangh#L462),
[emission evaluation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/shaders/rtx/concept/surface_material/opaque_surface_material_interaction.slangh#L872).
Pinned public source identity is supporting evidence,not proof every binary
instruction matches that revision. Local exact-build native disassembly unchanged.

Files added:audit script,three-test regression,this record,evidence JSON;HANDOFF
updated. No native production change,staging,commit,helper or active session.

## Exact next smallest action

The first proposed offline control was executed below. Next:trace only native
top.bmp row-origin/face selection before choosing an adapter conversion. No new
sponsor gameplay or blanket flip justified yet. Texture reversal remains PARTIAL.
Native ship replacement,appearance tuning and architecture selection stay out.

## Follow-through — asymmetric GPU control captured, shutdown PARTIAL

Prepared and documented
[REMIX-TEXTURE-CONTROL-001](../reconnaissance/probes/REMIX-TEXTURE-CONTROL-001.md)
BEFORE execution. Added standalone `texture_orientation_probe.cpp` and
`run_texture_orientation_probe.py`;no production host/fixture/header change.
Isolated x64 /W4 /WX compile PASS with exact pinned SDK;executed owned offline
process only. Run `20261018-200014-459912-texture-control` retained.
64frames,known-UV quad,64square asymmetric DDS,2fence-completed256-square BGRA
readbacks;runner60s/8MiB cap. Both native CAPTURE markers and complete262144B
outputs exist. Process failed after capture,before final shutdown PASS marker.
Initial runner did not preserve exact native exit code;corrected for subsequent
executions. Do NOT invent its code,claim normal shutdown,or equate it with SDK40.
No new helper investigation begun;this is an explicit new diagnostic-tool defect.

Read the retained fence-completed BGRA outputs directly with numpy and median
7x7patches centred at screen98/158 coordinates. RGB corners TL/TR/BL/BR:

| Mode | TL(red) | TR(green) | BL(blue) | BR(yellow) |
|---|---|---|---|---|
|emission OFF|87,13,13|13,92,13|12,12,82|91,90,13|
|emission ON|240,43,41|33,231,31|51,52,244|224,224,26|

**Direct captured GPU evidence:**known corners remain in correct positions;
SDK/DDS path does not globally invert this controlled image. Whole-primary
emission substantially brightens fixed-light colour samples,corroborating washout
configuration diagnosis. Not a universal native image-origin proof,complete source
colour-parity claim,or clean-shutdown gate PASS. The control changes emission after
32frames;automatic exposure/history is not fixed,so exact causation fraction or
physical light calibration cannot be derived from the numerical ratio.

Native SFC sampler-origin/face-selection relationship is still the smallest
missing fact for the saucer. Do not declare a1-v fix from this negative control.
No new production image,UV,light or material change;no source qualification reset.
Standalone diagnostic source/tool/probe added to file list above. Retain all small
raw captures with curated sample summary;archive after bounded analysis.

Final validation210Python tests PASS/4.261s;both accepted/test executable hashes
independently remain `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Parser/JSON/Markdown references/git diff --check PASS,indexempty. Partial control
archived with CRC PASS (raw retained,no deletion):
`artifacts/remix-runtime/archives/20261018-texture-orientation-control-partial.zip`,
59,033B,SHA256 `04E15874BF25FDF1DB6680CDD1D36969C352E7CD6467B51C4ECB5FB40A7A5882`.
Readback SHA256 OFF `DFDA53D859810EF33E8F2AECE5839A94BAD56FCA029F1E3621DBE40656A53BCD`,
ON `3B5FA83F8C33846C284FC780AD1CC7830702C5B1D2E52F5A7A3593EE97ACFF2C`.
