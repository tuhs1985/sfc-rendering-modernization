---
decision_id: SFC-ALPHA-SCOPE-20261027
decision_status: sponsor-directed
date: 2026-10-27
---

# Alpha mod release — required additions

Sponsor direction: an alpha mod release needs the following in addition to
replacement. This records release scope; it does not declare these features
implemented, amend the preserved CDD snapshot or change formal TRL gates.

| Feature | Alpha disposition | Current qualification / remaining work |
| --- | --- | --- |
| Ship replacement | **Required** | First player-only checkout is prepared; in-game validation remains pending. That first checkout alone does not establish alpha release readiness or broader supported-ship coverage. |
| Weapon lighting | **Required** | Apply weapon-generated lighting to the replacement rendering. Existing light/effect observations are useful evidence, not proof this integration is complete. This item does not require rebuilding every weapon effect's geometry. |
| Damage textures | **Required** | Read and apply the ship's damage textures/state. Sponsor notes that the current path does not read these textures; no new implementation or discovery was performed to qualify them in this record. |
| Break model on destruction | **Required; loading speed is critical** | Transition to the destruction/break model. Sponsor flags this as difficult and requiring fast loading. Model acquisition, preparation and lifecycle handling remain to qualify; no new numeric timing threshold or loading mechanism is assumed. |
| LOD models | **Optional** | Supporting level-of-detail models is desirable, but is not an alpha release blocker under this direction. Existing active-LOD identity observations do not establish complete LOD rendering support. |

All required items must be addressed before calling the mod alpha-ready. Normal
gameplay, controls/UI, bounded resources, original-asset preservation and existing
cleanup/synchronization disciplines remain applicable. This list is not a claim
that it exhausts those existing obligations.

Immediate execution stays unchanged: finish the prepared player-replacement
checkout and review its result. Record follow-up implementation increments after
that review; do not silently expand the current test or start a full effects,
damage, destruction or LOD implementation from this scope note alone.

## Break-model clarification — bounded inspection, Run212

Sponsor identifies the `_brk.mod` asset. [Inspection](../runs/2026-10-27-codex-break-model-inspection.md)
confirms installed examples and the already mapped secondary-model request.
Existing successful FCA_BRK/KFF_BRK native loads occur during setup, before
tactical rendering, with the returned break visual stored at ship+0x8C.
Therefore preparation while the ship is alive is a supported opportunity to
investigate; starting every load only after destruction is not a necessary
assumption. Fresh capture/retention, breakup-piece transforms and transition
timing remain unqualified. No direct disk-model replacement or implementation
change is authorized by this inspection.
