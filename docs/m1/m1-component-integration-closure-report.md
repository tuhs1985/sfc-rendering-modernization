---
title: "M1 — Semantic Component Integration Closure Report"
date: 2026-10-14
status: technical-pass-recommended-awaiting-sponsor-review
milestone: M1
governing_authority: "CDD v1.0 plus approved SFC-GATE-20261014"
---

# M1 — Semantic Component Integration Closure Report

## Executive decision

**Recommended disposition: M1 PASS — semantic component integration validated.**
Sponsor closure acceptance is pending. This is **not overall TRL 4**, proof of
beneficial modernization, or permission to begin M2 implementation.

A reversible project-controlled component can occupy the proven ship/model
render path, retain useful identity, and continue original rendering without
observed tactical regression in the supported Community Edition setup. Neutral
operation survived a single >=30-minute tactical session, with bounded frame-time
and process/graphics-memory measurements, clean hook restoration/unload, normal
exit and unchanged executable. Prior targeted tests independently demonstrate
two-owner differentiation, epoch retirement/reappearance, downstream correlation
and owner-specific reversible input substitution.

No further gameplay or cosmetic microtest is needed to support this scoped
closure recommendation. Existing limitations are explicit below, not waived or
converted into unsupported success claims.

## Authority and exact scope

- [Approved M1/M2 amendment](../decisions/2026-10-14-m1-m2-gate-allocation-amendment.md)
  controls the project milestone allocation; [M1 plan](m1-trl4-integrated-component-validation-plan.md)
  section13.2 supplies the existing semantic sub-gate.
- [Accepted baseline/manifest](m1-a-development-manifest.md): existing Community
  Edition client2.5.6.4 and launcher2.1.0.22, including its installed dgVoodoo2.8.6.5
  and ReShade6.7.1. Sponsor directs leaving that shipping setup intact until needed.
  Their presence is not a project architecture selection or modernization result.
- Client SHA256
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
  Exact dependency hashes/configuration snapshots in manifest and runtime records.
- Native-launch wording in historical reports means launcher-created process,
  not wrapper-free presentation. Historical no-external-renderer statement is
  superseded. Source-package provenance is sponsor attestation, not a ZIP audit.
- KPP/KSA/REQ IDs and Threshold/Objective boundaries unchanged. Capability-quality
  and all-CTE maturity obligations remain; this milestone is no longer shorthand
  for aggregate TRL 4. M2 receives combined CTE-1/2/3 modernization integration
  and three VMES-class evidence before any overall TRL 5 claim.

## Exit-criterion adjudication

CONFIRMED below means supported within the tested scope, not universal coverage.

| Revised M1 criterion | Evidence and adjudication | Confidence |
| --- | --- | --- |
| Semantic integration sub-gate | [RT-001](probes/M1-A-RT-001.md) confirms two owners/model/source/selected-child and12,632 correlated006AB410 events; [RT-002](probes/M1-A-RT-002.md) confirms distinct lifetime epochs under motion; [RT-003](probes/M1-A-RT-003.md) confirms practical semantic-only operation without observed stutter. [RT-005](evidence/M1-C01-RT-005-20261012-attribution.md) independently records retirement/new epoch without stale sampler reuse. Reuse completed sub-gate; do not require fresh geometry logging in endurance. | CONFIRMED |
| >=30 continuous tactical minutes with component active | [Endurance](evidence/M1-CLOSE-ENDURE-001-20261014.md): controller1830s duration after automatic tactical gate, independently observed1831.265s including shutdown/polling,109,688 gated frames. Sponsor confirms same mission/no pauses/no issues. Process uptime alone was not used as mission proof. | CONFIRMED |
| Repeatable frame-time/system/graphics-memory method and disabled comparison | [Qualification](evidence/M1-CLOSE-MEASURE-001-20261014.md):596 frame records/10 memory samples, component disabled after gate unload. Endurance:107,951 frame records/1,800 memory samples, exact PID/start-time identity. Same versioned bounded methods repeat successfully. Descriptive comparison shows no observed degradation; controlled causal overhead remains unmeasured and disclosed, not silently inferred. | CONFIRMED method/evidence; causal estimate NOT ESTABLISHED |
| Usable HUD/cursor/targeting/camera/controls | Explicit sponsor attestations in disabled qualification, endurance and prior scoped interventions. Endurance same session and no issues confirmed separately. Human observation, not exhaustive UI automation/gameplay equivalence proof. | CONFIRMED observed non-interference |
| Repeatable enable/disable/removal, configuration recreation, client preserved, bounded capture | Multiple prepared entries rebuild/start on this host without debugger/manual RE. Disabled qualification unloads gate before capture; enabled endurance restores/unloads at duration, normal exit, independent client/reference hashes unchanged. Actual installed dependency inventory/snapshots retained. This establishes on-host reproducibility, not fresh-PC deployment. | CONFIRMED tested workflow |
| Identity/lifetime/exception risks dispositioned | Epochs stay separate, no raw-address identity merge. Endurance no owner/thread/signature overflow. Known00509843 and three exclusion signatures bounded/reconciled; unclassified paths continue original rendering. No automatic intervention retarget/recovery claim. See limitations/risk register. | CONFIRMED policy/observations, category meanings unresolved |
| Review package complete | Plan/amendment, manifest, source/probes/tests, run/telemetry logs and archives, sponsor observations, this report and [risk register](m1-a-risk-deficiency-register.md). | CONFIRMED package available |

Traceability retained: CTE-1; REQ-BAS-001/002/003, REQ-REN-001/002/003/004,
REQ-GAME-001/002/003, REQ-PERF-001/002, REQ-STAB-001, REQ-DEP-001/002 and
relevant KSA-1/2/3 verification support. This report does not declare their full
final capability Thresholds passed, e.g. complete campaign/save verification,
all-state coverage, three final mission demonstrations or fresh-machine deployment.

## What the component actually controls

```text
tEntityShip::render              0x004162B9
  -> t3DVisual_Model              0x0042FD3F / selected child 0x0042FDD2
    -> tModel0                   0x0042E4B2
      -> source/positions        0x006ABF80 / 0x006ABFB0
        -> wrapper/preparation   0x006AC5A0 / 0x006ABFC0
          -> generic geometry    0x006AB410
            -> original drawing/presentation, including installed CE add-ons
```

Component0.13 uses existing state-preserving thunks; neutral endurance installs
only five semantic/lifetime hooks. No geometry/wrapper/corner/private-copy or
visual intervention active in endurance. The diagnostic geometry hook remains
disabled because prior32.4-million-call instrumentation coincided with3–5s
stutter; semantic-only comparisons support that cause as STRONG HYPOTHESIS.

[RT-010](evidence/M1-C01-RT-010-20261013-surface-lighting.md) additionally confirms
selected-owner copied452-polygon data can drive a visible lighting change and
restore originals:299 neutral/899 altered handoffs with matching native preparation
receipts/parent completion. That is controllability, **not improved quality**.
Ship/model/source/mesh and transform-handoff identities survive above the seam;
generic006AB410 alone lacks sufficient owner/model/material meaning. Full camera,
texture/material and output-composition contracts are not established.

## Measurements and preservation

Endurance mean frame interval16.67375ms, nearest-rank p9518.4722ms, max64.4624ms;
six5-minute-window p95s18.43–18.54ms. Disabled10s mean16.67132/p9518.479ms.
Observed consistency supports this scoped reliability result, not a causal
overhead percentage or compliance with later performance gates.

GPU provider memory initially rises then plateaus around675MiB late in the run.
No runaway growth evident here; not leak-freedom proof. Detailed semantic output
stops intentionally at120epochs/10,000events, summaries continue. Endurance
semantic CSV342,073bytes, frame CSV26,193,972bytes, memory580,097bytes; no caps
or queues exceeded, no uncontrolled multi-GB capture.

Main endurance archive4,036,052bytes,22 entries, all entry hashes verified:
`artifacts/m1/archives/M1-CLOSE-ENDURE-001-20261014-005117.zip`, SHA256
`2380E4A9C905EC7550621F7E02C377531424739D273428B1EC1EFBB1095E7220`.
Postexit configuration archive12,872bytes separately retained with source/copy/
entry hashes. Raw27,345,757bytes retained ignored, nothing deleted. Exact runtime
component/controller hashes, collection bounds and archive references are in the
linked evidence/run records; build-time hashes are not substituted for run hashes.

## Known limits and deficiency disposition

- Historical disabled-run dependency/config hashes absent. Sponsor accepted CE
  shipping baseline resolves scope discrepancy, not missing historical evidence.
  No wrapper-free or precisely matched causal-overhead claim. Future intervention
  comparisons must record actual dependency/configuration state before changes.
- Full-duration per-owner history was not logged. Initial two chains are coherent;
  summary9 retirements and prior independent epoch tests support bounded policy.
  Do not equate owner epochs with physical ships across gaps or assert every
  draw category follows this mainline.
- Known00509843 occurs109,692 times;101,922 classification exclusions reconcile
  to existing004EFC49/00413B2D/0042FDD5 signatures, no capacity overflow. Categories
  remain partly unknown. They bypass observation, not native rendering. This
  finite fail-open exception set does not invalidate tested mainline integration.
- Generic semantic analyzer's `PARTIAL_OR_REVIEW_REQUIRED` and rejection analyzer's
  lead-review flag remain intact. They do not auto-adjudicate this composite gate;
  absent fresh geometry samples is intentional, not a reason to enable the hot hook.
- Selected-epoch intervention recovery, safe recyclable/early-freed private buffers,
  all-model coverage, beneficial enhancement and modernized composition unproven.
  Current diagnostics pin immutable copies until process exit and abort on changed
  eligibility. No requirement to invent those capabilities just to close neutral M1.
- Reproducibility demonstrated on this host/installation, not clean install or
  independent second tester. No campaign/save conversion performed. No final
  capability/gameplay assurance inferred from sponsor's normal-operation reports.

These are bounded limits or later integration questions, not observed failures
of the approved M1 component gate. An actual contradictory result must reopen
the relevant conclusion; do not reinterpret it as a requirements change.

## Review decision and stop boundary

Recommend sponsor accept **M1 PASS — semantic component integration validated**
under SFC-GATE-20261014. Approval of this report does not itself stage/commit or
authorize M2 execution. Repository remains atfee152f with uncommitted work pending
review. Preserve Community Edition setup unchanged.

After closure acceptance, request separate authority for bounded M2 planning:
integrate one genuine enhancement using the proven semantic boundary. No detailed
M2 tasks, backend/renderer choice or implementation are created here. Exact next
action: sponsor reviews this closure recommendation and disclosed limitations.
