# TEXTURE-EXPORT-001 — fresh capture and textured Remix preview

Result: **PARTIAL — primary images recovered and displayed; sponsor placement
comparison and secondary-image role remain unresolved.** No TRL/gate change.

## Confirmed association

Fresh run `artifacts/m1/runs/20261016-010112-enabled`, component0.15,
90s automatic tactical gate. Sponsor: **“done no issues.”** Normal exit, unchanged
client and restored hooks recorded. Geometry hook OFF. One accepted mesh/texture
snapshot at frame3/79ms, owner epoch1, ship0x1682AD88, visual0x17B8E8E0,
Model00x17ACC518, source0x04AB365C. Packet57744bytes/452triangles/1356corners.
SHA256 `d1e666c5339debc021de71191b2f1125df7bb6b5005ce93af50a74cbbd42742c`.
Texture snapshot status1, same packet FNV2966573461, textures-enabled1; native
source words, STRS references, registry filenames and manager bindings corroborate
the static relationship in [the probe definition](probes/TEXTURE-EXPORT-001.md).

Model filename is **`assets/models/kff/kff.mod`**, directly observed, not guessed
from appearance. All files below are in `assets/models/kff/`.

| Group | Primary ID / original | Secondary ID / original |
|---|---|---|
|0|170 / `kff_1_2.bmp`|171 / `kff_1_2i.bmp`|
|1|172 / `kff_1_1.bmp`|173 / `kff_1_1i.bmp`|
|2|174 / `kff_1_4.bmp`|175 / `kff_1_4i.bmp`|
|3|176 / `kff_1_3.bmp`|177 / `kff_1_3i.bmp`|
|4|178 / `kff_1_5.bmp`|179 / `kff_1_5i.bmp`|

IDs are **this run only**, not pointers or reusable identifiers. Ten originals
decode as256×256 paletted BMP,66614bytes each, no decoded alpha channel. Original
disk hashes, copied originals and lossless PNG derivatives independently rechecked.
Original+PNG image bytes1177434, below64MiB warning/128MiB stop. Association
manifest contains per-image hashes/dimensions/formats and exact group assignments:
`<run>/textured/association-manifest.json`. Raw snapshot:
`<run>/TEXTURE-EXPORT-001.json`. No original game image modified.

CONFIRMED: original image identity and primary group bindings. Secondary
association also confirmed, **emission/glow purpose NOT confirmed**. All secondary
images preserved separately, not applied as glow. No decoded alpha is not proof
that the engine never uses colour keys or other transparency; none is invented.

## Actual consumer validation

Toolkit1.6.0-dev job `C:\Project\RemixJobs\20261016-050350Z-6dffd5be`:
vendor validation PASS,4.625s, exit0/no remaining owned processes.452triangles,
no missing/extra faces, source group bindings match. Corner comparison abs1e-6:
max position delta4.98e-9, UV1.91e-9, derived unit normal2.98e-8. No UV/image
flips, axis/model rotations, reverse faces or normal repairs introduced. Original
grey asset remains available. Five diffuse shader image bindings point to
`output/textures/resource_0170/172/174/176/178.a.rtex.dds`; emission disabled,
opacity constant1. DDS conversion is the vendor's derived output, not a claim
of byte-identical texture filtering or original shading.

Bounded NRC-off preview smoke:
`C:\Project\RemixJobs\preview-20261016-050403Z-9003afa9`,16.203s,
exit0/no remaining owned processes/source USD unchanged.11 mesh prims/452triangles;
actual Remix renderer. `above.png`, `angled.png`, `front.png` show green hull
panels and contrasting markings; analyst inspected `above.png`. This confirms
visible image application, **not sponsor-confirmed correct placement**. Synthetic
lights and previously documented dark/open-face/shading problems remain separate.
No live game renderer change or glow demonstration.

## Bounds, cleanup and retained evidence

5361 rendered frames observed;1180 detailed events/339469-byte event CSV, no
owner/thread overflow.5365 known0x00509843 exceptions counted, not re-investigated.
Generated semantic analyzer remains review-required:1702 bounded exclusions in
the last10.4s (851 ship-vtable,851 missing-owner), selected-address flags0,
no rejection-signature overflow. Do not describe this as zero rejections or
universal semantic coverage. The frozen frame3 association completed before these
exclusions; owner later retired, no texture recapture or retarget. Snapshot QPC
0.0945ms is not a whole-frame latency measurement.

Client installed/reference SHA256 unchanged:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Owned game-directory proxy/config absent; no SFC/controller active. Renderer job
scratch peaks2209405/1229079bytes; consoles114848/24448bytes, both below limits.
All retained image files across capture/import/preview2829304bytes, including
three comparison PNGs and duplicate staging copies. No multi-GB output generated.

Verified122-file ZIP (portable caches excluded, raw files retained):
`artifacts/remix-ingest/evidence/20261016-texture-recovery.zip`,2439928bytes,
uncompressed4752494bytes; SHA256
`98215728799ad370beaf542e79ea32ef9ac9b7cdf5dc0eff7ab6c3867abc9e45`.
Contains capture, manifests/original copies/PNGs, import outputs/logs, preview and
`TEXTURE-EXPORT-001-review.json` with image hashes/formats/dimensions for every
stage. Archive is ignored local evidence, not guaranteed in another checkout.

Next smallest action: sponsor compares the saved preview's hull markings/panel
placement with SFC. Then qualify only the secondary-image rendering role; do not
substitute textures, fix geometry, repeat broad reconnaissance or claim full PASS.

## Newer sponsor comparison / direct pixel audit

Sponsor recognizes the ship but notes softness. Supplied ModelBrowser1.0.7.2
LOD1 screenshots (emissive ON/OFF, Fix issues OFF) are useful reference, not actual
SFC runtime screenshots. Panel detail remains sharper with emissive OFF, so do not
attribute our softness simply to missing glow or original256² resolution.
[Direct pixel audit](../runs/2026-10-16-codex-texture-pixel-comparison.md): all ten
copied BMPs and PNG decoded pixels match originals exactly. Five primary DDS
base images remain256², BC7 compression/nine mip levels; preview staging exact.
Mean channel compression error0.819–1.386/255, max38, unchanged orientation strongly
better than flipped alternatives. Compression is not lossless, but these results
do not establish the cause of the displayed softness. Mip/filtering/lighting and
existing surface differences remain unresolved. No renderer changes made.

## Newer controlled mip-availability test (historical diagnostic)

[Approved A/B](../runs/2026-10-16-codex-base-mip-comparison.md) preserved base pixels/
geometry/UV/lights/camera but removed lower mip levels in five NEW scratch DDS
copies only. Preview `preview-20261016-052216Z-f60dc2ed/above.png` visibly restores
wing panel detail. Strong evidence that lower-detail sampling contributes to the
softness; actual sampled mip/algorithm and production filtering policy unproven.
No global/default/game fix, sole-cause claim, brightness/face repair or glow added.
Original/import files remain unchanged. Overall texture result still PARTIAL.

## Newest — offline preview softness resolved without removing mips

**Later runtime update:** [0.16 texture-path review](2026-10-16-texture-path-runtime-result.md)
confirms fallback-family selection (+3D58=511/+8009=0), same kff geometry/UV/
normals/groups and same ten original images, now correctly joined to IDs174–183.
No capture/import loss or client change. Exact eligible fallback pass sequence
still unobserved;0.17 extension prepared for a future convenient run. Provisional
lighting remains a hypothesis; no full fidelity/role PASS or preview-default change.

[Residency resolution](../runs/2026-10-16-codex-texture-residency-resolution.md):
two fresh bounded previews restore panel detail with the **unchanged full nine-mip
DDS chains**, Linear material filtering and child-only
`rtx.texturemanager.neverDowngradeTextures=True`. Both effective native configs
confirmed; source/asset/client hashes unchanged, no active process. An explicit
full-detail textured launcher is available; grey/streaming controls preserved.
Operational offline-preview fix CONFIRMED. Low-detail streaming residency was
responsible is STRONG HYPOTHESIS, not exact per-pixel/GPU-residency telemetry.
Nearest filtering was tested and rejected (blocky low-detail panels); no global
settings, light/geometry/UV/normal/face repair or glow added. Overall texture
fidelity remains PARTIAL for separate unresolved image-role/appearance questions.
Next smallest unresolved relationship: captured secondary-resource binding and
render operation; do not assume it is glow from filename or ModelBrowser alone.
