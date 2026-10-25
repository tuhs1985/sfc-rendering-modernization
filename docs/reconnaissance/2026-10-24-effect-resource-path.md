# Effects resource path — Run167 bounded static characterization

Current scope: SFC2.5.6.4, offline investigation of Run166's captured native
callers. No effects renderer, new runtime hook, game run or backend change.
API experiment remains parked. This document supersedes UNKNOWN static linkage
for the one concrete path below, not the remaining effects inventory.

## Confirmed path

One concrete object on global list0x0092F470 has vtable0x007AA050. Slot+4
is0x004EFA4A, which is in both gameplay sample chains through0x004ED080.
Its constructor0x004EF0BD calls list insertion0x004ECD72, installs that vtable,
loads `assets/models/missile/missile.mod` through0x0042F39A and stores the
returned model at object+0x350. The constructor proves a missile-model resource
relationship; it does not identify every instance's weapon or owning ship.

The same draw routine has separate branches for the model and a textured
four-corner effect. Flags+0x3D/+0x3C control branch participation. An optional
early branch invokes object slot+0x3C (its full role is not characterized here);
the model at+0x350 is called through its render slot+0x18. Do not assume the
entire method is just one billboard.

The concrete four-corner resource route is:

`effect object -> draw0x004EFA4A -> live ID[0x0092F5FC] -> manager+0x134
 -> manager resource-selection field+0x1F24 -> native mode7/End -> polygon submission`

### Resource identity and selection

-0x004ECE2A–55 initializes seven resource IDs at0x0092F5FC through0x0092F614
 from a seven-entry table starting0x007A9818. Names are `fx0` through `fx6`.
 The first entry is fx0, flags0/0; fx5 has a different byte flag. No image roles
 inferred from those names or flags.
-0x004ECE80 builds `assets/textures/%s.%s`, tries `bmp` then `pcx`, and calls
 established registry0x008CC620 acquire slot+8. The acquired ID is stored by
 0x004ECE44. Thus this path selects fx0.bmp with pcx fallback; **actual successful
 runtime filename and resource epoch are not yet captured**. IDs are not pointers.
-0x004EFC8F passes the current fx0 ID to manager slot+0x134. Actual manager
 vtable0x007B8D4C resolves this to0x006AD3E0: it stores a bounded ID at+0x1F24
 (values above4096 become0). This is a deferred selection, not an immediate
 Device3 SetTexture and not necessarily the texture of a batch flushed earlier.
-At0x006AC900 the primitive finalizer reads that same ID into EBX. Mode7's
 jump-table entry resolves to0x006ACE58, which consumes four corners at a time
 and calls0x006AC830 with resource ID and count4. Existing low-level binders
 route through0x006A8860 where needed; the method eventually becomes ordinary
 native graphics submission, not the retained-ship semantic contract.
-0x004ECF3F–62 releases each nonzero global ID through registry slot+4 and
 zeros its table entry. This is resource shutdown, not per-effect retirement.

### Per-instance state needed

CONFIRMED reads in the concrete routine: object+0x20/24/28 supply translation
input to a locally constructed transform; +0x2C/30/34 contribute another vector;
+0x44 selects a16-byte UV-coordinate record at0x009339F8. The constructor sets
+0x44 from an input type. Therefore call it **UV variant**, not a proven animation
frame. UV setters slot+0x124 alternate with four position setters+0x114 before
End+0x110; mode7 is explicitly selected. Color slots+0x130 receive1/1/1 here.
The code sets and restores several manager depth/blend controls around the
effect. Exact effective state still comes from the graphics-state observations;
never replace that evidence with a guessed state name from a vtable slot.

Object orientation, complete transform convention, effect size/velocity and
ownership field semantics are not qualified. No payload array/image read was
needed for these static relationships. Resource identity and UV variant must
remain separate from object identity and future transient primitive payloads.

### Lifetime

Global-list base constructor0x004ECD72 initializes links+4/+8 and inserts the
object at0x0092F470.0x004ECDD6 unlinks it; concrete destruction eventually uses
that base removal path. Other flags can stop drawing while the object remains
linked. List disappearance, explicit unlink, visibility and GPU resource release
are different facts. Proposed tracking needs constructor/unlink epochs; a recycled
pointer or shared fx0 ID alone cannot identify a living effect.

## Attached effects: an important qualification

0x004103E2 is a generic attached-trait dispatcher; observed return0x0041043B
follows virtual slot+8. Separate0x00410447 walks slot+0x0C. In the
explosion-related vtable0x007978FC these resolve respectively to0x0041F5F5
and0x00413AC3. The former performs time/state/child-effect work; the latter can
render the model at trait+0x88 using a supplied manager. The constructor writes
this vtable at0x0041E078; surrounding factory calls reference tETrait_Explosion.
This establishes static separation of update/side-effect and model-render
routes, not the concrete trait type observed in Run166's late burst.

**Do not promote0x0041043B to a dedicated explosion-draw hook.** A stack captured
while updating a trait can occur because its changes cause older queued drawing
to flush. The observed native alpha-state return0x0069E61B is not an effect
resource or type label. Run166's explosion interpretation remains a strong
hypothesis, not confirmed by this static inspection.

## Smallest next observation

[EFFECT-RESOURCE-JOIN-001](probes/EFFECT-RESOURCE-JOIN-001.md) defines a small
default-off metadata observation of this concrete global-list path. Obtain one
fresh object epoch/vtable, its selected resource/UV variant and primitive-submit
scope before assigning a downstream graphics family. Do not add effects support,
capture all geometry or repeat the broad observer unchanged. Sprite archive,
beam, shield, damage, grid and tactical UI joins remain open.

## Reproduction and confidence

`tools/recon/verify_effect_resource_path.py <verified-test-client>` checks38
explicit byte/string/vtable anchors after exact client SHA validation, read-only.
All38PASS against the unchanged client. It checks a static path, not execution
of each branch in a captured instance. The actual disassembly is the existing
ignored pre-M0 dump; selected ranges only were inspected. PE section mapping
uses existing inspect_pe.py. No broad asset search or new external dependency.

CONFIRMED: static code/data relationships and Run166 sampled draw context.
STRONG HYPOTHESIS: missile-related model plus associated textured visual branch
is a useful first transient-family join. SPECULATIVE: which specific weapon,
trail/explosion component or owner produced any particular sampled draw.
