# Run279 — first effect-light gameplay run: submissions work, visible contribution unresolved

Sponsor reports no visible new illumination in a standard two-ship test and suggests internal/hardpoint placement, shadowing or overly brief lifetime. Investigated existing run `20261103-041835-978830-in-game`; no rendering/configuration changes or new gameplay capture.

## Confirmed

- K-FF and F-CA both loaded and rendered. Complete run, normal game exit, controlled unload, renderer exit0 and original client hashes unchanged.
-5,353effect-update observations,1,046active slot observations,0invalid or unavailable frames,1,072handle changes and remaining0 at close. Actual successful SDK draw-submission recorder observes every one of those5,353frames, with0gaps/invalid/unstable reads or omitted records. File1,021,429bytes; limit4MiB. No source-to-SDK detection/forwarding failure established.
- All1,046active submissions are native type5 in slots2/3/4. Four submitted RGB values: orange[0.88,0.55,0],green[0,0.2,0],magenta[1,0,1],orange-red[1,0.25,0]. No exact weapon names inferred from those colours.
-26continuous active-slot periods, measured using native capture QPC and on/off transitions: shortest0.0158s,median0.7660s,longest1.6840s. Slot reuse/repeated effects can occur without an intervening OFF; these are slot-active durations, not individual projectile lifetimes. Most are long enough that an overall one-frame-only explanation is unsupported. This does not prove they were visible in the camera.
- Native range varies0.007058–20world units,median3.000826. In a representative sequence it decreases5→4.6665→4.3347 while RGB remains unchanged. Current Remix sphere radius stays1; emitted radiance follows RGB/settings. Native range is recorded but its SFC spatial response is not reproduced by the sphere adapter.

## Rechecked spatial falloff in the original code

Used existing accepted-client disassembly, not another live run or guessed field naming. At006A97C5,EDI is manager+0x7A0 = bank+0x28 for slot0. Type5 at006A98F3 reads `[edi]`, then006A990E–9954 compares this value with absolute vertex-to-light coordinate differences. Beyond the threshold it returns zero contribution. The remainder computes position/normal response with vector subtraction and dot products(0069B190/0069B250). It is spatial range in this lighting calculation, not a duration in seconds. A separate animation/lifetime process may vary this range over time; that update mechanism is not identified here.

This native per-surface response contains no geometry-visibility ray query and differs from a physical sphere source. An internal native source could therefore produce a visible SFC response while the corresponding Remix source is blocked by geometry. That mechanism is plausible, not yet demonstrated for this run's lights.

Local extracted ranges: `artifacts/player-replacement/run279/type5-response.txt`. Original accepted executable and full listing are unchanged; no executable or bulk disassembly is added to Git.

## Unknowns and next diagnostic direction

- Do not claim hardpoint linkage or inside/outside placement: this performance run preserves raw light positions but not a full contemporaneous per-frame ship-pose history for all the relevant flashes. Its rolling final scene table cannot prove earlier light/ship intersections. Initial static transforms are not an acceptable substitute for moving ships.
- Successful SDK submission is not proof of visible lighting in final pixels. Need distinguish an occluded emitter, insufficient point-light radiance, adapter/runtime rejection/culling after submission and a light outside the visible scene.
- Brightness units and spatial falloff remain provisional. Native RGB is a contribution to the old surface calculation; copying it as physical Remix sphere radiance does not establish equivalent brightness. No evidence supports reinterpreting native range as a standalone intensity or seconds.
- Smallest useful follow-up: a bounded visible-contribution check that separates position/occlusion from brightness, with same-frame ship transforms joined to raw light data. Use retained geometry, a known exterior source reference and the unmodified scene-light baseline;compare completed pixels with effects off/on in an isolated fixture before changing native lifetimes or guessing offsets. Do not permanently extend lights or move hardpoints based solely on this first observation.

This is a partial integration result: capture and actual API submission demonstrated in gameplay; useful visible effect illumination remains unproved. Source/config unchanged. Per-slot periods and compact analysis are retained under `artifacts/player-replacement/run279/` with the read-only analyzer `artifacts/player-replacement/analyze_effect_run279.py`. Existing implementation changes remain unstaged/uncommitted; no new stage/commit.
