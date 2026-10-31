# Run216 — registry repair confirmed; shield ordering remains open

2026-10-27 America/New_York. Sponsor completed the prepared Run215 checkout:
registry markings solid, no other HUD/control/game issues reported; grid crosses
the ship correctly, but replacement draws over shields that should cover it.
These are confirmed sponsor observations, not guesses about ship height.

[Evidence](../reconnaissance/evidence/20261027-registry-live-shield-review.json).
UTC run `20261028-025849-923300-in-game`: error=null, normal game exit,
controlled hook unload/controller0, renderer0, critical hashes/settings unchanged.
4911suppressed submissions,4893matching commits,rejected0,13cumulative repeats,
peak2,3reactivations,4recoveries including shutdown. NativeFallback presentations3
counts only that state, not total recovery time. Do not claim zero delivery gaps.

## Focused review

No implementation, source settings, builds, general regression suite or new GPU
fixtures. Read completed-run JSON, existing compositor/depth/frame-buffer code,
and a bounded region of existing pinned-client disassembly. Nine explicit byte
anchors, vtable entry and resource string checked against the hash-pinned EXE.

**CONFIRMED implementation:** replacement uses the saved complete pre-ReShade
native picture at Present; original effects are already in that picture.
The opaque replacement shader tests returned hull depth against saved native
depth, then overwrites covered colour. Correct opaque depth does not preserve
a transparent foreground contribution that did not write depth.

**CONFIRMED static relationship with known manager:** loader0x00426116 acquires
`assets/textures/shields.bmp`, stores its resource ID at0x008F522C. Candidate
draw0x00426563 selects that ID at0x004265DF through manager slot+134 when
the textured branch is enabled. It requests manager slot+C4 with0 at0x0042660C
before submission and restores1 at0x00426839. Known runtime manager vtable
0x007B8D4C maps+C4 to0x0069EC60, which requests device render-state14.
That is depth-write enable in the established Direct3D state numbering.
Blending is enabled through+B8; exact translated blend/depth state for this
latest live shield invocation was not recorded.

[Microsoft depth-write state documentation](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3drenderstatetype)
explains that disabled depth writes can still allow depth testing. Thus a
visible foreground shield need not appear in the depth buffer at all.

**STRONG HYPOTHESIS for this live defect:** late opaque insertion overwrites the
already blended shield because its foreground contribution is absent from saved
native depth. This matches static shield depth-write behavior and sponsor report.
The exact latest-live texture/draw/state/order join remains unverified. Do not
mislabel every blended draw as a shield, infer the shell geometry from artwork,
or claim an image-only height adjustment fixes transparency ordering.

## Next bounded action

Qualify the shield/transparent-effects drawing boundary and its relationship to
the opaque ship pass, using existing survey call-origin/state records and the
identified static shield path first. The eventual insertion must put the solid
replacement before foreground effects while retaining source-frame pairing and
native UI. Simply moving the current asynchronous Present compositor earlier
does NOT establish matching output availability or synchronized effects.
No whole-scene renderer rewrite, depth bias, forced shield depth writes or
unqualified effect replay. If existing captures lack the needed join, prepare
only shield-resource/state/order counters, not another broad/full-geometry run.

Registry repair is sponsor-confirmed. Full replacement visibility remains PARTIAL
because shield composition is unresolved. Settings and implementation remain
Run215; source/binary qualifications stay valid. Updated run/evidence,HANDOFF and
STATUS only; no staging/commit/push. No extra sponsor test requested now.
