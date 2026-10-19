# Remix appearance controls

## Current temporary appearance baseline

Sponsor approved the current four tuning files on2026-10-19. Exact copies,hashes
and restoration instructions:
[temporary appearance baseline revision2](../../../docs/reconnaissance/evidence/baselines/20261019-sponsor-temporary-appearance-r2/README.md).
Use this checkpoint for future comparisons;older tentative snapshots and factory
examples are not the current sponsor baseline. No physical/native-SFC parity claim.

## Separate quality controls and suggested comparison profile

Use [quality.toml](quality.toml), independently of image/lights/materials. The
suggested starting file is enabled:anisotropic16x,mip bias0,temporal AA OFF,
denoising ON,native1x resolution. Your existing three tuning files are preserved.
This is a conservative comparison profile,**not a verified match to SFC**.
The accepted Community Edition's DirectX wrapper already forcesFiltering=16 and
Antialiasing=8x. Remix temporal AA is a different method,not an8x MSAA switch.
We leave it OFF initially to isolate temporal softening,not because SFC lacks AA.

Save while the existing light-tuning runner is active. QUALITY CONFIG_ACCEPTED
means validated;QUALITY_APPLIED in host.log confirms native application. Changes
apply at a safe output boundary,usually about500ms plus the next completed image.
No compilation needed. Bad values keep the last accepted profile.

| Setting | Use |
| --- | --- |
| enabled | true uses this profile;false restores pre-quality Remix defaults:anisotropic8x,mip0,AAoff,denoisingon,native1x. |
| texture_filtering | "anisotropic" for angled surfaces;"trilinear" disables anisotropic filtering. No unverified nearest/bilinear selector is offered. |
| max_anisotropy | 1,2,4,8,16. This is texture filtering,NOT the materials.toml stretched-highlight control. |
| mip_bias | -1..1;0neutral. Negative requests sharper mip selection but may shimmer;positive requests softer mips. Native option acceptance confirmed;visible effect on our SDK meshes is still weak/unresolved. |
| anti_aliasing | "off" or "temporal". Temporal AA can smooth jaggies but soften detail or leave motion trails. Native-resolution TAA,no DLSS/NIS/Ray Reconstruction enabled. |
| denoising | true keeps ray-tracing noise under control. false is a diagnostic view of noisy samples,not what the old SFC renderer did. |
| supersampling | Currently1.0ONLY. Larger values are rejected and leave settings unchanged. Correct larger-than-screen rendering/downsampling remains separate work. |

Restore with [quality.example.toml](quality.example.toml) or enabled=false. The
example restores previous Remix behavior,not the suggested16x comparison profile.
It never resets your image exposure,gamma,lighting or material settings.

The enabled profile explicitly selects each SDK material's LINEAR filter field
(filterMode1,the pinned SDK C++ default). Our previous zero-initialized C record
left that field0(point). Global anisotropy options alone were therefore not a
complete filtering setup. Quality edits safely recreate the host material/mesh
bindings after GPU completion;captured geometry/images remain unchanged. Disabling
quality restores the previous field0 as well as global defaults. Image-only edits
do not recreate geometry;material/quality recreation shares the existing256-change
safety ceiling—restart a long tuning session if it is reached.

Try ONE change at a time with fixed ship/camera:temporal AA on/off first,then
denoising briefly off/on. Filtering tests can follow,without adding image sharpening.
Actual filtering/mip changes were small relative to stochastic variation in the
bounded synthetic probe before selecting the SDK material filter;do not assume
that global16x alone caused the original softness. The explicit linear-vs-point
material field,temporal AA and denoising produced stronger measured differences. Do not lower
roughness to try to sharpen textures—it controls reflected highlights instead.

Supersampling is intentionally not faked with resolutionScale>1:the pinned SDK's
output-copy helper uses nearest sampling. A real GPU downsample/coverage resolve,
resource-budget checks and new spatial proof are required before enabling it.
No game-camera/transport redesign is needed merely to test the controls above.
Bounds and evidence:[quality probe](../../../docs/reconnaissance/probes/REMIX-QUALITY-CONTROLS-001.md).

## Separate image controls

Use [image.toml](image.toml) for the returned Remix image, independently of
lights.toml and materials.toml. This does **not** adjust original SFC drawing,
HUD, menus or the whole combined screen. Current output is still an added ship.

Start the existing `start_light_tuning_session.ps1` launcher. In image.toml set
`enabled=true`, change one value and SAVE. Reload is about half a second plus the
next completed render; initial asset/shader setup can take longer. Invalid edits
keep the last accepted settings. IMAGE CONFIG_ACCEPTED means validation/relay;
IMAGE_APPLIED in host.log confirms the native host applied it. No recompile needed.

| Control / default | What it does |
| --- | --- |
| enabled=false | Leaves startup image unchanged. After tuning, false restores the tested local/automatic baseline and bypasses the extra grading pass. |
| tone_mapping="local" | Existing default; balances different image regions. "global" uses Remix's whole-image tone curve and can look different even with neutral sliders. |
| automatic_exposure=true | Existing default; adapts exposure to the image. Set false for steadier manual comparisons, especially with a ship on a mostly black background. |
| brightness=50 | 0..100 slider; 50 neutral. Lower dims, higher brightens through native exposure. 0/100 correspond to -1.5/+1.5 stops relative to 50. |
| exposure_ev=0.0 | -4..4 stops added to brightness's exposure bias. +1 doubles the input exposure factor; -1 halves it. Final displayed RGB is not necessarily doubled because tone mapping compresses it. |
| contrast=1.0 | 0..2; below1 flattens differences, above1 strengthens them. 0 makes a grey image; not an ambient-light control. |
| gamma=1.0 | 0.25..4; above1 brightens displayed midtones, below1 darkens. Black/white endpoints stay fixed. Not a monitor calibration or a replacement for correct colour-space conversion. |
| saturation=1.0 | 0..2; 0 grey, 1 unchanged, above1 stronger colour. |

To restore the entire image configuration, copy [image.example.toml](image.example.toml)
over image.toml and SAVE, or simply set enabled=false. Lighting/material files are
not reset. Turning automatic exposure off or switching tone mapper is an intentional
appearance change; neither happens by default. Returned output is already8bit:
gamma/grade cannot recover clipped highlights or missing texture detail.

Tuning tip: turn automatic_exposure=false when comparing light strengths or
manual exposure; otherwise adaptation can partly counteract your changes. This
is optional, not a changed default. Brightness and exposure_ev deliberately feed
the same native exposure factor; gamma is the separate midtone adjustment.

### Which implementation actually works

Pinned Remix1.5.2 accepts native `rtx.tonemappingMode`, `rtx.autoExposure.enabled`,
`rtx.tonemap.exposureBias` (global) and `rtx.localtonemap.exposure` (local).
Local native exposure starts at0.75; our combined EV multiplies it by2^EV.
The nominal `rtx.userBrightness` option from associated public source is rejected
by this DLL (SDK error1). We therefore map the slider's documented3-stop-span
formula through the two working exposure controls. There is no pretend slider.

Global contrast/saturation are native `rtx.tonemap.*` controls and require
colorGradingEnabled=true. They are unused by the LOCAL mapper. In local mode only,
a small host-owned GPU pass supplies contrast/saturation after decoding the
returned sRGB-like display values to linear RGB, then re-encodes them. Its0.18
contrast pivot/BT.709 luminance follow the native global grading convention;
8bit quantization and different tone curves mean the two modes are not identical.
Gamma is a narrowly scoped display-midtone GPU adjustment in either mode. Never
apply both native and fallback contrast/saturation to the same image. Source
assets, lights, materials, output picking/depth and alpha are unchanged.

The extra pass runs only in the separate64bit host, after Remix completion and
before output publication. The game callback does no configuration/file work.
Default/disabled settings bypass pixel adjustment exactly. Native option failure
stops only the optional host after attempting rollback; original SFC still draws.

Bounds:16KiB config, at most256 accepted revisions per session,16 retained config
snapshots plus latest,100 console messages, no per-frame image dumps. Restart after
256accepted edits. One private1920x1080 scratch texture adds8,294,400bytes of GPU
storage, no extra shared surface or CPU screenshot loop. Existing session/output
caps and normal-exit cleanup remain in force. For proof and source references see
[image-control probe](../../../docs/reconnaissance/probes/REMIX-IMAGE-CONTROLS-001.md).

## Separate material controls

### Optional texture-derived roughness

New `roughness_map_enabled=false` preserves your current uniform surface.
Enable it in materials.toml to derive an artistic roughness map from the original
colour image. This is NOT recovered SFC surface data and does not alter that image.
`roughness_map_strength`0..1 blends uniform roughness with the derived result;
start0.25. `roughness_map_black`/`white`0..1 set input levels (white>black).
White produces rough/matte areas; `roughness_map_invert=true` reverses that.
`roughness_map_gamma`0.25..4 changes map midtones:above1 rougher,below1 smoother.
Save to reload; turn enabled=false to restore uniform roughness. No game restart.
Generation happens only in the host worker and may take longer than the usual
half-second reload. Existing128MiB image/256-edit limits apply. Old derivatives
are reclaimed only after the host confirms safe material retirement;current and
one pending revision stay protected. Missing/stale confirmation pauses further
material publication rather than risking an in-use file. A cache-budget message
is NOT machine RAM exhaustion. If current+pending images cannot fit or files stay
locked,a genuine budget rejection still retains last good settings.

**Independent opaque specular strength/reflectivity is not available in the pinned
SDK material interface.** No fake control has been added. Metallic, thin film,
translucent IoR and ray-sampling probability are not equivalent substitutes.
No normal/clearcoat/specular maps are invented in this increment. Current colour,
light and emission tuning remain independent. See
[roughness probe](../../../docs/reconnaissance/probes/REMIX-ROUGHNESS-MAP-001.md).

Use [materials.toml](materials.toml) for the extra ship's surface and illuminated
markings. Keep lights.toml for light sources. Save while the **light-tuning** runner
is active;reload is about half a second plus the next completed render. Invalid
edits retain last good values. Restart after256 accepted material changes.
Ordinary non-tuning textured runs read settings only at preparation.

Baseline: `roughness=1.0` is matte;lower toward0 for sharper reflections.
`illumination_strength=1.0` enables the provisional recovered illumination;
0turns it off,2doubles it. Start small;this is not an SFC-calibrated physical unit.
The map is primary colour multiplied by the associated secondary image,NOT all
the diffuse texture emitting light. Original images remain untouched.

Optional controls,in suggested order:

|Setting/default|What changing it does|
|---|---|
|metallic=0|Toward1 changes painted/dielectric response toward metal:less diffuse,more coloured reflections. Not recovered native material data.|
|anisotropy=0|Nonzero -1..1 stretches highlights directionally. Experimental without qualified tangent data;leave0 for baseline comparisons.|

Texture tints are deliberately absent:the pinned SDK's colour constants only act
when the corresponding texture is missing,not as texture multipliers. Offering
those as tint knobs would be misleading.

Ranges/comments are also beside each setting. These are Remix-only choices,not
changes to SFC assets or rules for a future backend. They affect the selected extra
ship globally,not the original ship. No opacity/normal/height options are offered:
those need their own evidence rather than guessed settings. Strong illumination,
metallic response and light changes can mask each other;change one control at a time.

## Separate dome to experiment with

The last `[[lights]]` entry, `id="project_fill"`, is a SEPARATE project light.
It does not replace either SFC light. To try it, set its `enabled=true` and SAVE.
It starts as `type="dome"`, `intensity_multiplier=0.05`, white colour, and an
empty environment_image (uniform fill). Adjust its intensity independently.
Your existing SFC light settings are unchanged. You can disable the second SFC
light separately if you prefer this dome's fill. Only one enabled dome at a time.

This project entry can change to any listed light type too. Unlike the two native
entries, its intensity is direct Remix radiance scaling: it is NOT multiplied by
SFC strength, conversion_scale or master_multiplier. Use its own intensity and
color_multiplier. It is recorded as project-added illumination, not captured GI.

## Choose the type of either light

Each existing entry now has `type`. Keep its `id` unchanged: the ID identifies
the captured SFC source, not the type we choose to render in Remix. For example,
under `id = "native_directional_1"`, change `type = "directional"` to
`type = "dome"` and SAVE. No extra light entry is required. Both lights remain
directional initially; your conversion/brightness settings are preserved.

|type|Use|Settings it uses|
|---|---|---|
|directional|Distant sunlight|direction_override (optional), angular_diameter_degrees|
|dome|Surrounding fill/environment|environment_image, environment_rotation_degrees|
|sphere|Local light emitting in all directions|position, space, radius|
|spot|Local cone of light (SDK shaped sphere)|position, space, radius, direction_override, cone_angle_degrees, cone_softness, focus_exponent|
|rectangle|Rectangular emitter|position, space, width, height, direction_override, roll_degrees|
|disk|Oval/circular emitter|position, space, width, height, direction_override, roll_degrees|
|cylinder|Tube-shaped emitter|position, space, radius, length, axis|

All use enabled/intensity_multiplier/color_multiplier. Native entries also use
existing conversion/master ratios; project_fill is independent as described above.
This is a deliberate Remix reinterpretation of the captured source;
it does not turn the native SFC light into a different type or prove native GI.
`enabled=false` removes that light entirely. At most one enabled dome is supported
by this adapter. The other light can use any listed type or be disabled.

The active file includes the shape fields for BOTH lights. Fields irrelevant to
the selected type are dormant so changing type does not require deleting settings.
`space="ship"` places local lights relative to the displayed extra ship, using
its model transform and diagnostic offset. `space="world"` uses absolute Remix
world coordinates. Space affects position only: directions/axis remain world-space.
Distances use the existing captured model/world units, not calibrated metres.
`direction_override=[x,y,z]` is optional; without it the captured direction is used.
Width/height are full dimensions (disk uses half of each as its two radii).
Roll rotates the rectangle/disk around its direction.

For a dome, `environment_image=""` uses a generated uniform white environment;
color_multiplier supplies its tint. Optional PNG/JPEG/DDS image paths can be
absolute or relative to this config folder. Inputs are decoded to8bit RGBA DDS,
not an HDR-preserving workflow. Rotation is degrees about Remix world Y. Images
are processed only outside SFC, max4096 per dimension/32MiB source, within the
existing128MiB combined image-output budget. Prepared DDS/source hashes appear in
light-shapes-manifest.json. Re-save a changed setting to reload an edited image.
Unknown type/missing image/invalid config preserves the last accepted configuration.
Per-light shadow-only/raytracing disable remains unsupported by the pinned SDK;
the type selector does not create such a switch.

To start: try `type="dome"` on light1 with its existing enabled=true and an empty
environment_image. Adjust that entry's intensity_multiplier independently of the
main light. Exit SFC normally when finished.

**Active file:**`lights.toml`,only when using the prepared light-wiring or tuning launcher.
The ordinary textured-copy launcher keeps its previous lighting baseline.
No change here edits SFC's lights or original assets.

## First pass versus tuning

First pass uses the normal90second harness to check wiring. It is not the longer
tuning session. Exit when the runner gives its two-beep request.

The sponsor-approved second pass now has a separate low-recording tuning launcher
described below. It ends when you exit the game normally, with a30minute safety
ceiling. The sponsor confirmed light alignment in the first pass.
Do not try to extend this test by editing hidden time limits.

## Editing while playing

Save `lights.toml` after an edit;the worker checks for changes about twice a
second. Invalid or partly saved files keep the previous valid settings. Check
the runner's LIGHTS CONFIG_ACCEPTED / CONFIG_REJECTED messages afterward;no need
to leave the game just to watch the console. No restart is required.

| Setting | Meaning |
|---|---|
|master_multiplier|All mapped lights:0.5=half,1=unchanged,2=double|
|intensity_multiplier|Same ratio,for the light in that section only|
|enabled|true=on,false=remove that light from Remix|
|color_multiplier|Red/green/blue channel ratios;[1,1,1] leaves colour unchanged|
|angular_diameter_degrees|Remix directional source size;provisional,not recovered from SFC|
|conversion_scale|Unit-conversion factor,initially1 and NOT physically calibrated|
|raytracing|renderer_default only;the current SDK has no per-light shadow-only switch|

Effective output=native RGB × native strength × conversion_scale ×
master_multiplier × that light's intensity_multiplier × color_multiplier.
The observed SFC strengths1.5/.25 therefore initially map to.75/.125 with
master_multiplier=.5. This is not a claim that SFC1.5equals physical Remix1.5,
or that two differently aimed lights will look exactly half as bright as the
old one-light diagnostic. Use multipliers for tuning,not native-memory changes.

`native_directional_0` and `_1` identify the two qualified native type0slots,not
proven engine names or a universal sun/ambient classification. Directions and
native strengths come from fresh observations,not the old saved run. This first
pass does NOT render transient native type5weapon/effect lights;their specialised
native behaviour still needs mapping. Do not add invented IDs or set
raytracing="off" expecting shadow-free illumination—it is rejected.

## Longer tuning session

Use `start_light_tuning_session.ps1` from the same elevated parent. Play and edit
this folder's `lights.toml`, then SAVE. Changes apply live; invalid edits keep
the last valid settings. Exit SFC normally when finished (30minute safety limit).
This mode records only small summaries/latest light state, not a continuous trace.
Raise `angular_diameter_degrees` for softer shadows; try1 or2 before larger jumps.
Use `master_multiplier` for both strengths or per-light `intensity_multiplier`.
Keep `conversion_scale` separate from artistic adjustments. Current settings persist
between runs. Both lights are directional; weapon/effect lights are not wired yet.

Bounds:config64KiB;intensity0..1000,master0..16,RGB0..16,conversion0..1000,
angular size0..180. Invalid edits apply nothing. Initial source dimensions and
radiance mapping are Remix-only policy,not a future-backend requirement.
