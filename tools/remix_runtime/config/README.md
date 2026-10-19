# Light controls

## Separate material controls

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
