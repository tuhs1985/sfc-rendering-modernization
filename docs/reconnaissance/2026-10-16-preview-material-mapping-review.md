# Preview material mapping versus captured fallback selection

## Disposition

**Retain the separate provisional preview, unchanged.** Its five paired-image
products are supported by the captured branch and source algebra, but binding
them as modern material emission is an approximation, not an exact SFC shader.
No additional gameplay is needed to settle the already captured branch inputs.
Overall texture/appearance fidelity remains PARTIAL; no milestone advancement.

## Evidence and mapping

Fresh capture: `artifacts/m1/runs/20261016-171830-enabled`, component0.17.
[Eligibility analysis](evidence/20261016-texture-eligibility-review.json) records
textures1, secondary word511, multitexture0, validation mask3, previous alpha-test0.
These CONFIRMED inputs plus exact-build branches select mode2 then mode1 requests;
actual GPU pass completion is not directly measured. See
[runtime adjudication](../runs/2026-10-16-codex-texture-eligibility-runtime.md).

Existing imported preview job: `C:/Project/RemixJobs/20261016-050350Z-6dffd5be`,
based on original capture20261016-010112-enabled. Do not relabel that import as
having been made from the new run. Independent comparison confirms:

- all ten original filenames/SHA256 values match, joined by filename, NOT live ID;
- 4542 selected OBJ position/UV/normal/face/group/material records match exactly;
- group pairs remain 1_2,1_1,1_4,1_3,1_5, each primary plus corresponding secondary.

Current IDs170–179 happen to equal the first capture's IDs. This coincidence is
not evidence of persistent resource identity and is not used for the cross-run join.

`tools/remix_ingest/provisional_lighting.py` validates the preview job's own packet,
references, manifest, five groups, ten resources and source hashes before deriving
per-channel `round(primary_encoded * secondary_encoded / 255)` products.
`kit_mesh_preview.py` checks each group's primary material filename, binds its
product as emissive_mask_texture, sets enable_emission=true/intensity1, and authors
only an anonymous session layer. The primary remains the diffuse texture. Normal
grey/textured launchers and imported assets remain unchanged. The existing label
PROVISIONAL_RUNTIME_UNVERIFIED remains conservative: this preview uses the old
capture, and GPU execution/strength/fidelity are still unverified even though fresh
branch eligibility is now known. Do not rewrite historical manifests.

## Algebra: where the approximation stops being equivalent

For the statically configured eligible fallback, intended normalized RGB is:

`legacy = P * clamp(S + L, 0, 1)`

P is primary, S secondary, L legacy interpolated vertex lighting. Blend evidence,
addresses and enum corroboration are retained in the linked runtime/static records.
Framebuffer quantization/color space are additional qualifications.

Without intermediate saturation, this decomposes to `P*L + P*S`. Thus product
emission uses the appropriate primary-weighted image term; raw S as emission
would be wrong. But the actual preview uses modern synthetic illumination,
material response, exposure and emission transport, not legacy L. It does NOT
implement the full legacy equation or its clamp ordering. No physical light-source,
HDR brightness, bloom, alpha or modern PBR meaning follows from these masks.

Even an ideal additive stand-in `P*L + P*S` differs when S+L>1:
P=.5,S=.8,L=.4 gives legacy .5 versus stand-in .6 before final display treatment.
This demonstrates a mathematical mismatch, NOT a measured screenshot error.

Read-only numeric check over five recovered image pairs (983040 RGB channels):

| Assumed constant L | Channels where ideal additive stand-in exceeds legacy | Maximum normalized excess |
| --- | ---: | ---: |
|0|0|0|
|.25|26783|.2460784314|
|.5|50496|.4960784314|
|1|154476|.9960784314|

Calculated independently per channel as
`(P/255) * ((S/255)+L-min(1,(S/255)+L))`, tolerance1e-12 for nonzero.
These are synthetic constant-light diagnostics, NOT captured lighting values or
proof that all affected texels are visible. Product rounding max error is
.4980392157 of one byte; it is tiny compared with the demonstrated clamp mismatch.
Nonzero product RGB-channel counts by group:12145,7662,53266,39121,29474.
These are channel counts, not pixel/geometry counts. Source hashes unchanged.

## Confidence / remaining question

CONFIRMED: associations/identical preview inputs, encoded product calculation,
session-only assignment code and fresh branch selection inputs. STRONG HYPOTHESIS:
the current preview is a useful approximation of the ship's unlit markings.
Exact perceived strength, original color space, modern-material light transport,
normal/facing interpretation and matched visual fidelity remain unresolved.
Sponsor's modelling experience supports treating viewer brightness separately,
but does not identify the cause. No brightness/normal/UV/winding change justified.

**Next smallest action:** obtain a matched SFC/preview view at comparable angle and
scale during the next convenient gameplay session to localize the remaining
appearance difference before selecting any calibration change. No new diagnostic
game build or repeat branch-settings run is needed; no immediate sponsor action.
