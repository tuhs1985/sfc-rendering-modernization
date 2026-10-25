# SFC executable rendering inventory

Newest:2026-10-25 Run173. **Targeted static inventory complete; runtime behavior
and exact effect/resource ownership remain partial.** No game launch, renderer
change, asset extraction or milestone claim. API remains parked.

[Versionable metadata](evidence/20261025-offline-render-inventory.json),
[run/validation/provenance](../runs/2026-10-25-codex-offline-render-inventory.md),
[family map](rendering-family-map.md).

## What the executable now tells us

| Selected category | Qualified native classes |
| --- | ---: |
| Effects | 38:37derived effect types plus tFx_Base |
| Attached explosion/debris traits and creators | 4 |
| Light creators | 2 |
| Semantic model/visual classes and manager | 5 |
| Sprite/UI-related classes | 6 |
| Tactical camera/manager types | 8 |
| Dust-cloud entity | 1 |
| Total | 64 |

65structurally qualified vtables contain908executable virtual-method entries.
This is NOT908distinct render functions; aliases/shared functions and non-render
virtual methods remain. Camera types include managers/view implementations, not
eight simultaneous scene cameras. A class named AmbientLightBar is not proof of
a recovered physical ambient light.

Ten of the37derived effects have actual global-list membership evidence from
Run172. The other27are static possibilities, not observed gameplay coverage.
All type-descriptor/vtable/base-chain addresses and method counts are in the
versionable metadata. Full method lists and bounded code-reference graphs remain
in the ignored, hash-addressed generated inventory.

### Effects draw-slot inventory

These are slot+4 candidates in the tFx_Base family, corroborated by the known
global-list dispatcher. Runtime column means observed LIST MEMBERSHIP, not proof
the draw passed visibility or generated a particular translated pixel.

| Native class | Slot+4 target | Run172 membership |
| --- | --- | --- |
| tFx_ADDBlast | 0x004EC5F0 | not observed |
| tFx_Corpses | 0x004ED999 | not observed |
| tFx_Disruptor | 0x004EE864 | not observed |
| tFx_DisruptorMuzzleFlash | 0x004EEA2D | Romulan fixture |
| tFx_Drone | 0x004EFA4A | both |
| tFx_ESG | 0x004F0F3D | not observed |
| tFx_ESGImpact | 0x004F1E81 | not observed |
| tFx_ESGLance | 0x004F28E3 | not observed |
| tFx_Explosion | 0x004F2C50 | Federation fixture |
| tFx_Explosion_Debris | 0x004F3066 | not observed |
| tFx_Fissure | 0x004F3C84 | not observed |
| tFx_FusionCannon | 0x004F4719 | not observed |
| tFx_HeavyDisruptor | 0x004F5427 | Romulan fixture |
| tFx_HeavyPhaser | 0x004F5BAA | not observed |
| tFx_HeavyPhoton | 0x004F63E3 | not observed |
| tFx_Hellbore | 0x004F6F1D | not observed |
| tFx_HellboreBlast | 0x004F7D32 | not observed |
| tFx_Hypermass | 0x004F82C6 | not observed |
| tFx_IonStorm | 0x004FC806 | not observed |
| tFx_Mauler | 0x004FD2D0 | not observed |
| tFx_MaulerMuzzleFlash | 0x004FD90E | not observed |
| tFx_MineBlast | 0x004FE513 | both |
| tFx_NatExplosion | 0x004FEF80 | not observed |
| tFx_Organian | 0x004FFB42 | not observed |
| tFx_Phaser | 0x00500312 | both |
| tFx_Photon | 0x00500C30 | Federation fixture |
| tFx_Plasma | 0x00501FED | Romulan fixture |
| tFx_PPDWave | 0x00502C54 | not observed |
| tFx_PPDPulse | 0x00503570 | not observed |
| tFx_Probe | 0x0050413E | not observed |
| tFx_ProximityDetonation | 0x00504AF2 | not observed |
| tFx_Pulsar | 0x00505182 | not observed |
| tFx_Shockwave | 0x00505C97 | not observed |
| tFx_Shockwave2 | 0x00506E94 | not observed |
| tFx_Tractor | 0x005070FE | both |
| tFx_Transporter | 0x00507FAB | both |
| tFx_TRBeam | 0x0050878D | not observed |

tFx_Base's slot points to a shared stub outside the effects module. It is kept in
the type inventory but excluded from effects-graph range selection; it is not a
newly discovered effect renderer.

## Texture/resource findings

**CONFIRMED static:**41direct literal registry-acquire sites covering38distinct
literal filenames in the bounded effects/adjacent-rendering code window. A literal
request is not proof the file loaded successfully at runtime or is the currently
bound resource. No images were opened/copied. Directory spelling/case preserved.
The common fxN loader's formatting template is NOT misreported as a direct image.

### Shared atlas references found in bounded draw/helper paths

| Initialized resource slot | Classes whose paths reference it |
| --- | --- |
| fx0 | Drone, Probe, Shockwave |
| fx1 | Phaser, HeavyPhaser, ProximityDetonation, Shockwave, TRBeam, Tractor |
| fx2 | ESG |
| fx3 | Explosion, Explosion_Debris |
| fx4 | Hellbore, HellboreBlast |
| fx5 | no reference in this bounded graph set; NOT proof unused |
| fx6 | FusionCannon |

These names come from the already-qualified seven-entry initializer and actual
code references, not texture artwork. The common resolver tries BMP then PCX;
actual successful filename/ID for a new resource still needs runtime provenance.
An atlas can contain unrelated artwork, be shared and be used only on one branch.
This table does not identify each UV region or prove exclusive ownership.

### Manually qualified important paths

**Phaser:**slot0x00500312 ->0x00500306 ->0x004FFE39. At0x004FFFD8 the
code can push the fx1 resource ID; alternative branch0x004FFFE0 pushes0 before
the same manager texture-selection call0x004FFFE4. The manager is sourced from
the supplied argument at0x004FFF6E. Mode7 begins at0x004FFFF0. Thus it is a
quad-based beam path with a textured/untextured choice, not a fixed ship mesh and
not proof that every phaser always uses fx1. Exact beam UV/width/branch-state
contract remains to extract. The bounded graph explicitly stops one deeper
width-helper call0x004F24DF at its configured direct-call depth.

**Photon:**initializer0x00500862 acquires
`assets/textures/photons-2.bmp` into0x00857FC4; the draw path selects that slot
at0x00500D6B. This is separate from the generic fx sheets. Heavy-photon has its
own literal `assets/textures/heavy-photon.bmp`; do not substitute based on names.

**Plasma:**constructor0x00501BD3 stores its incoming resource variant at+3C,
installs vtable0x007AA944 and invokes initializer0x00501B0E. Seven acquire/store
pairs populate0x00966ACC..0x00966AE4:

1. assets/textures/red-plasma.bmp
2. assets/textures/orange-plasma.bmp
3. assets/textures/yellow-plasma.bmp
4. assets/textures/green-plasma.bmp
5. assets/textures/violet-plasma.bmp
6. assets/textures/FastPlasma.bmp
7. assets/textures/PlasmaSnare.bmp

At0x0050212F the draw loads `table[owner+3C]` before the qualified manager
selection at0x00502144; mode7 at0x0050216F,UVtable0x00966B38. The separate
owner virtual slot+3C resolves to0x00501C5E; helper0x00501E80/0x00501E9A also
selects from the same indexed resource table. Core and auxiliary geometry must
not be flattened into one unchanged cached model. Resource variant is separate
from animation/UV selection; seven initializer entries do not independently
prove all possible caller indices are within0..6 or which was used in Run172.

**Organian:**the constructor at0x004FFAF3 calls0x004FFAC8, which requests
`assets/textures/Organian.bmp` at0x004FFAE3 and stores the returned ID at
0x00857F40. Its draw selects that slot at0x004FFC04 before mode7/per-corner UV/
position emission. This supersedes the tentative suggestion that fx4 names the
Organian effect. The examined Organian path has its own image; fx4 is statically
referenced by Hellbore code. No claim that Organian appeared in the two captures.

Other literal leads include disruptor-burst.bmp, esg-impact-long-1/2.bmp,
space-rift.bmp, debris1.bmp, fx_Mauler_beam.bmp, mauler-flash_2.bmp,
mine-boom2.bmp, natesplosion1/2.bmp, ppd-beam.bmp, ppd-wave.bmp,
ppd-wave-hit.bmp, pulsar_1/2.bmp and explosion animation/ring sheets. Adjacent
rendering code requests sky backgrounds and light/heavy space-dust images.
Their exact per-class binding/UV roles are not all adjudicated yet.

## Lighting findings from the same executable/captures

All21recorded native light-call return sites match byte-verified original calls:
slot+80light records,slot+98enable,slot+90global response gate, or the explicit
global-effects dispatcher for initial snapshots. This joins recorded operation
kind to real code, not a guess that every virtual+80 is a light setter.

- 0x004BA652/0x004BA696 set the scene setup's slot0 and slot1 records, followed
 by their enables. Native scale constants include1.5/conditional2.0 and0.25.
- 0x004B9CB7 changes the slot0 record,0x004B9CDD disables slot1, then
 0x004B9CEC calls the global-effects dispatcher. This directly explains why
 recording every setter sees lighting states change between passes.
- tFx_Drone,MineBlast,Tractor and Transporter have observed paired global-gate
 calls.0x006AC6DC/0x006AC739 are another common paired global-gate context.
 These change native lighting RESPONSE state; they are not physical point lights
 appearing/disappearing. Do not feed them to Remix as new scene lights.
- Two additional qualified type names,tLightPhaser_Creator and
 tTRBeamLight_Creator, provide bounded future creator/ownership leads. Their
 exact allocation/attachment behavior is not established merely by those names.

Slot2+ transient positional/contribution changes remain useful runtime evidence,
but exact weapon attachment and physical light conversion are still open. No GI
identity is inferred. Unknown native tail fields and per-type-unused values must
remain uninterpreted.

## Smallest interface implications — recommendation only

The existing retained rigid-ship asset contract cannot describe all these paths.
The first useful extension is a bounded transient quad/ribbon submission for the
qualified phaser/plasma cases, retaining positions, per-corner UV/color, optional
texture/variant and observed blend/depth/order. Preserve camera/frame provenance,
explicitly qualified lifetime and distinct lighting roles. The adapter may split
quads into triangles; do not change original geometry or UV convention silently.

This is not an approved new protocol, renderer architecture choice or implementation.
Complete exact UV/animation/state/lifecycle field definitions first. UI/background
functions without relevant RTTI, indirect calls, dynamically supplied assets and
unobserved branches still require targeted evidence. Do not request a gameplay
run merely to rediscover class names or these static filenames.

**Exact next action:** extract the byte-backed phaser/plasma UV, width, state and
variant rules from these named paths into a small renderer-neutral transient-
primitive contract proposal. Use existing captures for branch/caller comparisons;
request another run only for a specific remaining live value/association.
