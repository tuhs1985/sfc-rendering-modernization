---
decision_id: SFC-TECH-GATE-20261018-RENDERER-BOUNDARY
decision_status: sponsor-directed
gate_status: OPEN
date: 2026-10-18
authority: Sponsor / Owner
---

# Technical gate — renderer-independent scene boundary

## Sponsor intent and authority

Sponsor directs:"make note of this a tech gate we need to cross. I want us to
be able to use future tech because we designed that in mind".

Record this as an **implementation/architecture engineering gate**,not a new
capability requirement or amendment to CDD v1.0,stable requirement IDs,Thresholds,
Objectives or approved TRL/milestone exits. No future renderer choice,DX12 rewrite,
second full renderer implementation or new milestone work is authorized here.
The [approved gate allocation](2026-10-14-m1-m2-gate-allocation-amendment.md)
remains unchanged.

## Decision

2026-10-19 Run70 progress:normal D3D9 interception captures complete FCA/KFF
geometry and exact primary-image assignments without SDK mesh registration.
[Evidence/limitations](../runs/2026-10-19-codex-normal-d3d9-remix-proof.md):camera
export omits vertical field,current native D3D9 revalidation fails before drawing,
and runtime disposal warnings remain. Gate stays OPEN;no live presentation,
depth/coverage/timing or final-source multi-backend qualification claim.

Preserve SFC capture as a reusable game-facing adapter. Separate its recovered
scene meaning from Remix-specific registration/rendering and platform image-return
details. Future renderer technology should require a new backend adapter,not
rediscovery of SFC ownership/geometry/camera or a rewritten game-facing probe.

Intended separation:

```text
SFC-specific capture
    -> versioned renderer-independent scene contract
        -> Remix adapter today / another renderer adapter later
            -> explicit output/synchronization contract -> game compositor
```

DX12 is a possible future backend API,**not a universal scene interchange format
or a required intermediate feed for Remix**. Retain the working public Remix SDK
integration while defining this boundary. No claim that an arbitrary future
renderer will accept data unchanged,or that all future technology is guaranteed.
Adapters and capability-specific work will remain necessary.

## What crossing the gate must demonstrate

1. **Explicit scene contract.** Versioned,documented meanings for currently
   supported mesh/corner/group data,asset/image identity,owner epoch/lifetime,
   transforms,camera/viewport and frame provenance. State coordinate systems,
   units,matrix conventions,limits and supported optional fields. Do not guess
   lighting/material fields still unproven;mark unavailable/unsupported explicitly.
2. **Dependency separation.** SFC capture and neutral scene definitions do not
   depend on Remix SDK structs or renderer-specific GPU objects. Backend handles,
   material creation,resource layouts and API-specific synchronization stay in
   adapters/platform transport,not become SFC object identity. Existing experimental
   SDK/native fields must be inventoried,not declared neutral by renaming them.
3. **Reusable evidence.** Feed the same bounded captured/replayed scene through
   the Remix adapter and an independent validation consumer,without editing the
   SFC capture. Check geometry,owner identity,lifetime,transforms/camera and frame
   association against common fixtures. A lightweight consumer is enough to test
   separation;do not build a second complete renderer solely for this gate.
4. **Output/lifetime contract.** Define valid image/depth/coverage metadata,
   ownership/completion tokens,dimensions/color conventions and failure behavior
   separately from any particular DX/Vulkan handle mechanism. API-specific sharing
   remains explicit,not assumed portable. Unsupported/late/disconnected output
   must preserve original SFC rendering;no stale/cross-owner substitution.
5. **Bounded extension path.** Show where another renderer adapter could attach,
   which current data it could reuse,and which missing capabilities would require
   new evidence. Version/capability checks reject incompatible payloads safely.
   Do not promise unknown future features or expand into unrelated engine RE.

These are gate evidence checks,not a detailed future milestone implementation
plan. Reuse existing packets/tests where sound;avoid a speculative general-purpose
engine/framework or needless scene serialization/conversion layers.

## Disposition / scheduling

2026-10-19 Run69:[plain D3D9 proof](../runs/2026-10-19-codex-plain-d3d9-proof.md)
and [neutral offline view](../reconnaissance/scene-contract-v1.md) now exist.
Two genuine captured assets render through plain system D3D9 without Remix,with
independent projection/texture tests. This is evidence of a second consumer,NOT
gate closure:the SDK adapter does not yet consume this exact neutral view,and
live frame/output integration remains unqualified. Normal Remix interception is
the next separately reviewed bounded gate. Historical scheduling below preserved.

2026-10-19 sponsor clarification:D3D9 proof first,D3D12 adapter afterward against
the same scene boundary. [Updated transition plan](../reconnaissance/d3d9-adapter-transition-plan.md)
and [Run68](../runs/2026-10-19-codex-d3d9-transition-planning.md) supersede the
immediate Run67 SDK-cadence-fix next action. SDK path retained as reference;
first implementation target is offline plain-D3D9 scene replay,not another game
test. Presentation/timing architecture must be qualified before live replacement.
This records direction/planning,not proof,requirements change or gate closure.

**OPEN — not demonstrated.** Existing semantic capture/live bridge and public
Remix SDK integration are useful starting evidence,but renderer independence
has not been formally validated. [Run28](../runs/2026-10-18-codex-offset-copy-runtime-review.md)
proves a visible additive fresh-ship return,not this gate.

Cross this gate **before freezing the durable renderer-replacement architecture
or claiming a reusable renderer-independent integration baseline**. Current
bounded Remix return/stability experiments may proceed while it is open;do not
let their provisional formats silently become the permanent contract. Include
the gate in the next sponsor-reviewed relevant integration planning increment;
do not retroactively reopen settled M0 or delay work merely to invent abstractions.

Closure requires a curated contract,dependency/adaptation map,repeatable tests
and reviewed evidence distinguishing CONFIRMED behavior from hypotheses and
unsupported extensions. Record the evidence here and obtain sponsor review.
If reusable separation cannot be supported,report the precise coupling/blocker
instead of quietly waiving the gate or changing requirements.

## References

### Adapter isolation example — 2026-10-18 texture origin

Run37 measured a Blender/Remix image-origin mismatch. Run38's correction lives
only in the Remix SDK vertex adapter (`remix_texture_coordinates.h`),not captured
UVs,asset files or shared scene transport. A future D3D9/D3D12 backend must qualify
its own texture convention;it must not inherit `v=1-v` from this experiment.
This is one concrete separation safeguard,NOT closure of this technical gate.

- [Current return contract](../reconnaissance/ship-live-return-contract.md)
- [Public SDK design](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/main/documentation/RemixSDK.md)
- [Authoritative handoff](../HANDOFF.md)
