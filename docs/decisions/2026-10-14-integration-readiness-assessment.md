# Integration readiness — 2026-10-14

Assessment only; no renderer/API/technology selection or M2 implementation
authorization. Read with [approved gate allocation](2026-10-14-m1-m2-gate-allocation-amendment.md).

## Answer

**Yes, enough to attempt a bounded integration prototype; not enough to promise
a complete replacement or modernized picture yet.** Stop treating native tint
and shading changes as the next visual milestone. A useful candidate experiment
would pass one identified ship's mesh/transform data to a project-owned rendering
consumer, initially separately from the live game picture, while SFC keeps
rendering normally. This tests whether data is usable outside the native path.
Only after that should in-game composition be qualified. This is a candidate
direction, not a requirement, architecture decision or approved task sequence.

## Evidence and limits

| Available input/control | Support | What it does not establish |
| --- | --- | --- |
| Ship/model/mesh/source association and transform handoff | CONFIRMED semantic probes and M0/M1 maps | Complete scene export or physical-ship continuity across opaque epoch retirement |
| Indexed positions, polygon/corner layout and UV field accesses | CONFIRMED exact-build static accesses plus bounded live samples/private graph receipts | A complete textured-mesh export, texture ownership contract, all mesh/model classes |
| Supplied transform rotation/translation interpretation | Numeric/static/runtime support; model-local interpretation STRONG HYPOTHESIS | Full external camera/view/projection and coordinate convention contract |
| Private whole-small-mesh substitution and normal-vector lighting control | CONFIRMED RT-010, visible selected ship change, matching native receipts/restoration | Independent rendering, beneficial lighting or safe recyclable/early-freed storage |
| Original flow preserved during scoped intervention | CONFIRMED short runs, clean restoration/exit | Formal long-duration stability, performance or replacement/composition correctness |

Sources: [RT-010](../m1/evidence/M1-C01-RT-010-20261013-surface-lighting.md),
[numeric adjudication](../m1/evidence/M1-C01-MATH-001-20261012.md),
[field/transform qualification](../m1/m1-c01-corner-transform-qualification.md),
[handoff feasibility](../m1/m1-c01-isolated-corner-handoff-feasibility.md),
[retention review](../m1/m1-c01-copy-lifetime-review.md).
Older preparation proposals in those references are historical where RT-010
provides newer runtime proof; their unresolved full-contract limits remain.

## Remaining integration questions

For an independent consumer, first qualify the smallest mesh/transform snapshot
contract, topology/conventions and lifetime. Camera/view/projection and output
composition become necessary for an aligned in-game replacement; material,
texture/resource mapping depends on the chosen enhancement. Investigate only
fields required by that selected proof. Existing normal reversal does not answer
them. No assumption that a translation wrapper alone recovers lost semantics.

M1 closure reliability/telemetry work remains separate. The immediate project
action is its bounded closure checklist; a later sponsor-approved M2 proposal
can select one real enhancement and its minimum integration inputs, without
committing to a final backend or beginning broad engine reconstruction.
