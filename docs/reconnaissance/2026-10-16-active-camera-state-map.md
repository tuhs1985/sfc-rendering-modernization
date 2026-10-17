# Active tactical camera — renderer-facing state found

## Executive result

Renderer-facing view/projection/viewport state located at the existing graphics
manager. Existing0.18 live records also permit offline recovery of the combined
world-to-pixel homogeneous map for all1854 observations. No new gameplay or live
collector change was needed. This is not a reconstructed camera-mode subsystem.
No claim that the executable owns only one camera object: capture the current
state at selected ship submission, not a global assumption about other passes.

**CONFIRMED:** exact-build locations/static read-write/multiply/divide relationships,
recorded matrices, bounded numerical recovery/low-skew pinhole factorization.
**STRONG HYPOTHESIS:** recovered camera pose/projection interpretation suitable for
external alignment, supported by static perspective/viewport construction and
runtime factorization. **UNPROVEN:** independently matched projected vertex/pixels,
direct runtime view/projection/viewport fields, clip/depth/pixel-center conversion
for the external renderer and every camera mode. No success/TRL advancement claim.

## State and exact supporting functions

Addresses are client2.5.6.4, SHA256
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Offsets relative to the CONFIRMED manager instance/vtable007B8D4C, not global
live pointers or camera-control object offsets.

| Manager offset | Meaning in inspected path | Setter/getter/evidence |
| --- | --- | --- |
|+055C,68bytes|Stored projection P|006AA3F0 copies17words at006AA3F8–406; getter006AA490; slots+EC/+F0|
|+05A0,68bytes|Pixel viewport transform S times P|006AA408–470 builds scale/offset then calls0069B450 with P|
|+0628,68bytes|Supplied current viewing transform V|006AA4A0 copy006AA4A8–4B6; getter006AA4D0; slots+D8/+DC|
|+05E4,68bytes|S*P*V|006AA475–485 after projection set;006AA4B8–4C5 after view set|
|+06F4,68bytes|Supplied object transform M|Existing006AA550 copy, ship handoff00416323|
|+066C,68bytes|V*M|006AA572–57C|
|+06B0,68bytes|S*P*V*M|006AA581–58F; applied to model positions006AC2C9–2CF|
|+075C/+0760|Viewport x/y origins, float copies of integers|006AA000 entry args3/4 ->006AA004/00E|
|+0764/+0768|Viewport width/height, float copies of integers|006AA018/026; getter006AA080,slot+44|
|+076C/+0770|Half-width/half-height|006AA032/042, exact PE float.5 at007959C8|

Viewport setter slot+40 points006AA000. Projection setter builds S with x scale
half-width, y scale NEGATIVE half-height, translations x+half-width,y+half-height,
z scale1 and bottom row0,0,0,1. This is why +05E4 is not simply a view matrix.
006AA0E0 (slot+100) builds perspective-like P using tangent, aspect width/height,
near/far-like arguments and bottom row0,0,-1,0. Other projection builders exist;
this task does not infer which constructor was called solely from its presence.
Current runtime matrices independently fit a perspective/no-skew subset.

Multiplication order corroborated by scalar0069BAF0 instructions, not function
names: output=this*argument, output pointer first stack argument. In-place0069B450
likewise composes this with its argument. Existing dispatchC69FF4 controls alternate
math implementations; all analyzed live records dispatch0, not universal proof.

Scalar0069CA30 computes homogeneous x,y,z and reads byte+41 of native matrix
payload: affine flag1 outputs w=1, flag0 uses stored fourth float row. This metadata
is within seventeenth DWORD, not a seventeenth float. 006AB5B4–5DD uses exact
float1 at007959CC divided by cached w, then multiplies x,y,z into submitted
screen-coordinate fields. Thus recovery must preserve homogeneous divide; an
affine-only camera or direct use of+6B0 as a rigid pose would be wrong.

Thirty-six selected code/vtable/constant byte anchors match original PE via
verify_active_camera_bytes.py. Full exact disassembly remains ignored at
artifacts/pre-m0/raw/StarFleetOP-2.5.6.4.dumpbin-disasm.txt. Generic virtual calls
at the same slot on unrelated objects were NOT promoted into manager callers.
Camera mode/lock controls0048CA35–CC22 intentionally left alone.

## Recovery from the already completed game run

Input20261016-211253-enabled/LIVE-BRIDGE-001-updates.jsonl,646336bytes,
1854 complete active records over63–90000ms, owner1. The supplied M and composed C
were already guarded/read-rechecked by0.18; no new probe or old pointer dereference.

Use native effective4x4 matrices, honoring affine metadata, and compute:

`B = C * inverse(M) = S * P * V`

This removes the ship's own pose, not the camera. Double-precision general inverse
avoids assuming stored R transpose exactly equals its inverse. Recomposition
B*M versus recorded C max absolute error2.3283064e-10 (algebraic consistency,
NOT independent native output comparison). Pinhole factorization additionally
checks row directions, no skew, depth-row dependence; max factorization residual
3.0552926e-8. This second structure check is nontrivial but still not pixel proof.

Recovered pixel-space principal point ranges:
x1059.9998657..1060.0001479,y539.9999367..540.0000615.
Focal magnitudes x1903.3455912..1903.3462750,y1903.3457009..1903.3461785.
Stable intrinsics while recovered camera center changes:
x -376.174711..374.431789,y69.812357..201.750068,z26.493662..28.245331,
in native world units. These are inferred optical-center coordinates, not direct
camera-struct reads or independently measured player input.

Pixel projection/view factorization uses viewport Y-down and perspective negative-Z
conventions from inspected construction. It is explicitly a candidate, not an
arbitrary external API camera convention. Recovered Q still includes pixel scaling
and offsets; do not pass it directly as normalized external clip projection.

Installed sfc.ini currently says Width1920/Height1080 (read only). Principal x1060
is not full-width center960. Viewport offset/subregion or projection shift matters;
do NOT assume the whole1920 buffer is the tactical viewport, infer a rectangle
solely from principal point, or silently recenter to960. Exact rectangle not in
old stream. No FOV/near/far/clip-interval values guessed from that configuration.

## Tools, bounds and reproduction

```
python tools/m1_component/verify_active_camera_bytes.py "C:/Games/Taldren Software Inc/Starfleet Command Orion Pirates/StarFleetOP.exe" --output docs/reconnaissance/evidence/20261016-active-camera-bytes.json
python tools/m1_component/analyze_live_camera.py artifacts/m1/runs/20261016-211253-enabled/LIVE-BRIDGE-001-updates.jsonl --output docs/reconnaissance/evidence/20261016-active-camera-recovery.json
```

Bundled Python3.12.14; first script reuses exact-build/hash/PE bounds verifier
with scoped anchor table and restores original table. Second script read-only,
<=8MiB input/2700records/4096bytes per line; report<=128KiB, exclusive create,
never overwrites. Explicit excluded records retained; this run excluded0. No
GPU trace, process attachment, network, elevation or rendering-thread work.
Expected report volumes tens of KiB; cannot generate rapid multi-GB output.
Output evidence JSON versionable, existing raw input already archived/unchanged.
Cleanup: retain curated JSON/source/tests; no source/capture/cache deletion needed.

Tests cover known camera with independently constructed object pose/projection,
local-vs-world projection equivalence, native affine metadata, invalid/singular/
nonfinite/alternate-dispatch input, zero-w refusal, bounded read-only report and
nonmonotonic records.93 total project Python tests PASS. No runtime build changed.

## Smallest next integration action

Prepare camera-aligned live bridge increment using identified V/P/viewport fields
or the recovered combined map as a check; include same-frame viewport rectangle
and a few independently observed native projected vertices to qualify pixel/depth
mapping. Reuse existing semantic callback, bounded worker and matched owner/frame.
No new broad camera-control reconstruction, geometry firehose or repeated motion
exercise is needed just to find state. Do not implement that increment or change
the game/preview in this investigation. Light extraction and image return remain
separate unanswered integration pieces, not implied complete by finding camera.
