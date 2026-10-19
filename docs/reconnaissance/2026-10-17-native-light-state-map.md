# Native light state — narrow static recovery

## Current live corroboration — 2026-10-18

[Run42](../runs/2026-10-18-codex-native-light-runtime-review.md) captures641snapshots
over89.937s,twoowners/samebank. Slots0/1 persistent white native type0,directions
(0.98893636,0,-0.14834046)/(0,0,1),multipliers1.5/.25. Local directions match
transposed supplied3x3 within3e-8 across1282comparisons. Slots2/3 transient type5,
orange/green,effect association STRONG HYPOTHESIS,exact physical mapping unknown.
Two steady sources,not three confirmed;GI not established. Runtime final result
file absent,reporting defect OPEN;raw capture,logs/cleanup/hash checks independently
retained. Historical "no live values" statements below superseded for this run.

Historical first offline continuation2026-10-18:[native lights and Remix controls](native-lights-and-remix-controls.md)
records sponsor's two approved goals and first offline core. Earlier minimum
snapshot proposal below is historical;new NATIVE-LIGHTS-001 defines bounded5Hz
discovery intended to observe transients. At that earlier checkpoint no live light
values had been captured;the Run42 corroboration above supersedes that limitation.

2026-10-17;[Run18](../runs/2026-10-17-codex-light-state-investigation.md).
Sponsor requests finding game lighting while away. No new gameplay,rendering
implementation,light override or changes to prepared calibration component.

## Result

**CONFIRMED static:**the proven graphics manager stores64native light records,
their enables and object-local derivatives. We can identify exactly where to
observe the light inputs already used to shade a selected ship. **NOT CONFIRMED:**
which slots the current mission enables,which is the main environmental light,
their actual values or a faithful Remix intensity/coordinate conversion.

Original client SHA2564D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Source ignored dumpbin artifacts/pre-m0/raw/StarFleetOP-2.5.6.4.dumpbin-disasm.txt;
41instruction/vtable/jump-table anchors independently match original PE bytes
via tools/m1_component/verify_light_state_bytes.py. Existing runtime RT-001/RT-010
proves native lighting affects the selected ship,not the current slot values.

## Storage and consumers

| Manager-relative data | Supported meaning | Evidence |
| --- | --- | --- |
|+0778 + i×40h,64bytes each|Original native light records,0<=i<64|006A9AB0 setter,006A9BA0 getter;16DWORD copies;capacity006A9AA0 returns40h|
|+1778 + i,64bytes|Enable bytes|setter006A9C40/006A9C4D;both transform and response consume|
|+17B8 + i×0Ch|Object-local point-like triple|006AA63F/649 or006AA65C/666 use supplied M with0069CBC0|
|+1AB8 + i×0Ch|Object-local direction-like triple|006AA650/657 or006AA66D/674 use0069CC40|
|+1DB8 + i×4|Reciprocal of record+28h for selected nonzero types|006A9B6C..8B;not an independent light intensity|
|+1EB8 byte|Global lighting-response gate|setter006A9C20;getter0069F190,existing preparation gate evidence|

Manager vtable007B8D4C slots+7C/+80/+84/+90/+98 point respectively to
006A9AA0/006A9AB0/006A9BA0/006A9C20/006A9C40. These are internal methods,
NOT IDirect3DDevice SetLight;do not impose DirectX light enums/layouts on them.

Transform handoff006AA550 uses supplied manager+6F4 object transform,not composed
projection+6B0,to derive light coordinates.0069CBC0 subtracts translation and
uses transposed3×3;0069CC40 uses transposed3×3 without translation (dispatchC74058).
Model-local lighting interpretation is STRONG HYPOTHESIS supported by existing
geometry/transform evidence;normalization,inverse assumptions and world units
still require numeric checks. Do NOT reinterpret17words as a conventional matrix.

## Native64byte record

| Offset | Static use | Confidence/qualification |
| --- | --- | --- |
|+00 DWORD|Type/branch selector|CONFIRMED static;native enum,not DirectX enum|
|+04..0C float3|Direction-like input to reverse-vector transform|CONFIRMED arithmetic;direction interpretation STRONG HYPOTHESIS|
|+10..18 float3|Position-like input to reverse-point transform|CONFIRMED arithmetic;position interpretation STRONG HYPOTHESIS|
|+1C..24 float3|Three-channel contribution scaled and summed by response|CONFIRMED math;RGB interpretation STRONG HYPOTHESIS pending live values|
|+28 float|Type0 response multiplier;type1 distance limit/falloff scale|CONFIRMED arithmetic;NOT one universal intensity field|
|+2C..3C|Copied/gettable payload|Unknown here;do not guess spot cone/attenuation names|

Response006A9790 reads type from record+0,dispatches via table006A9A7C:

- Type0→006A97FD:negative dot of transformed direction and supplied corner/face
  vector,multiplied by record+28;negative contributions discarded. Directional-like.
- Type1→006A9816:position-dependent,axis distance guards,Euclidean distance and
  normalized light-position-minus-vertex vector;falloff uses1-distance/record+28.
  Point-like. Dot/cull behavior remains original,not a new physical light model.
- Type5→006A98F3:additional position-dependent response involving a constructed
  up-vector and absolute dot product. Leave exact physical classification UNKNOWN.
- Types2/3/4/6→zero-contribution006A99CB in THIS software response. They may have
  other consumers;not globally unsupported or absent from the game.

At006A99DD..9EE the response multiplies record+1C triple by scalar and accumulates;
006A9A0E..55 clamps each accumulated channel above1 before returning float3.

**Important:**006A97E4 jumps to006A9A0E at the FIRST disabled slot. It terminates
this response loop,not merely skips a hole. Transform loop006AA62D instead skips
disabled slots and continues. A future observer must retain all64enable bytes
and describe the active contiguous prefix actually consumed;do not infer64active
lights from capacity or count arbitrary enabled slots as contributors.

## What has not been found/proven

- Actual live primary light slot(s),colors,strength,direction,position and lifetime.
- Whether scene lights are world-fixed,camera-related,ship-relative or temporary.
- Which scene object populates the light bank. Generic calls through vtable+80
  on unrelated objects are NOT sufficient caller evidence. A few inspected examples
  were rejected as one-argument object traversal or DirectDraw COM,not light setters.
- Full ambient/emissive behavior;secondary image contribution is separate from
  a spatial light. Existing source self-light scalar and brightness-like controls
  are not automatically a recovered ambient light.
- Faithful physical intensity/color space/range and shadow-casting policy in Remix.

## Smallest next lighting observation — not implemented here

After current calibration run,design default-off read-only snapshots at existing
validated semantic wrapper (same owner/model/manager/engine frame),not another
high-volume hook. Copy bounded64records (4096B),64enables,derived point/direction
triples1536B,reciprocal256B,global gate and existing M/V once at a few meaningful
samples. Stable double-read,finite/range/status checks,session/owner/sequence
identity;skip on inconsistency. Worker serialization only,no render-thread I/O.
At most3snapshots/2owners is <40KiB raw lighting payload;not continuous dumps.
Define/version probe and limits before adoption. Do not add fields to calibration
quietly or invalidate its qualified build while sponsor is preparing to run it.

Compare raw vs object-local light transforms using native arithmetic,object motion
and camera-only change. Determine directional/point-type membership by observed
type,not name. A separate runtime value check is required before saying "the sun
is at X" or feeding these values to production Remix lighting. No gameplay needed
for this static result;existing return-path/calibration remains next test.
