# Tentative sponsor-selected Remix appearance baseline

HISTORICAL / SUPERSEDED:see [current revision2 and attribution correction](../20261019-sponsor-temporary-appearance-r2/README.md).
The quote below records the original observation;its illumination-map-specific
causal attribution was NOT isolated. Sponsor subsequently identified possible
metallic/material interaction. Do not carry the older CONFIRMED wording forward
as proof that illumination maps alone caused the observed light contribution.

Recorded2026-10-18 at22:56:25-04:00. **TENTATIVE**,not a physical calibration or
claim that native SFC lighting/material response has been reproduced exactly.
Full [lights.toml](lights.toml),[materials.toml](materials.toml) and source hashes/
observation in [manifest.json](manifest.json) preserve this checkpoint independently
of later tuning. Active files stay in tools/remix_runtime/config;not changed here.

|Setting|Tentative value|
|---|---|
|Roughness|0.9|
|Illumination strength|0.35|
|Metallic|0.15|
|Anisotropy|0.5|
|Native-light conversion scale / master|0.15 / 1.0|
|Native directional0|Enabled,multiplier1.0,angular diameter17degrees|
|Native directional1|Enabled,multiplier1.0,angular diameter15degrees|
|Separate project dome|Enabled,intensity0.005,uniform white environment|

Both native colour multipliers and project dome colour are white. Full snapshots
also retain dormant type/shape/space/position/rotation/raytracing settings;the table
does not replace those files. Do not turn this tentative choice into factory defaults.

## Sponsor-observed emergent behaviour

Sponsor reports: “illumination already adds a new feature without having to do
anything special! it acts as a light source!”

**CONFIRMED — sponsor visual observation:**the restored illumination contribution
acts as a light source in the returned Remix scene. The implemented mapped
emissive material is consistent with that observation,not merely a painted-bright
region. No additional explicit light was created by this documentation task.

Not independently measured here:which surfaces received how much light,physical
emitted strength,performance cost,or native-equivalence. This is not a discovery
of another native SFC light,nor evidence that emitted light affects retained
original SFC geometry. The separate project dome is still a separate added light.
No milestone advancement or full-scene/original-ship replacement claim.

Next exact action:use these values unchanged as the starting point for the next
sponsor-approved comparison;do not reset to Run49 defaults or retune automatically.
