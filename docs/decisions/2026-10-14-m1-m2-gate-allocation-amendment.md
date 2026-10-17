---
status: approved
date: 2026-10-14
decision_id: SFC-GATE-20261014
authority: Sponsor / Owner
---

# Approved amendment — M1 integration reliability / M2 enhancement

## Authority and precedence

Sponsor approved the proposed allocation with: "agreed. make changes" after
discussion of M1 as integration/controllability and M2 as enhancement integration
and visual benefit. This is an explicit milestone-gate amendment, not an inferred
waiver or a declaration that diagnostic effects meet visual requirements.

Governing authority is approved CDD v1.0 **plus this approved amendment** for the
M1/M2 allocation only. Original CDD remains unmodified at:
`C:\Users\rober\OneDrive\Documents\Obsidian Vault\02 - Projects\Project Requirements\Starfleet Command Rendering Modernization Capability Requirements.md`.
Original SHA256:
`BF5384D2586601AAA28DB36970937A3B40F598E12002B3450BF2E7D9562FA352`.
This versionable amendment controls over conflicting M1 allocation language in
the prior plan/increment and historical records. It does not amend KPP/KSA or
REQ IDs, Thresholds, Objectives, supported baseline, or final capability scope.

## Replacement project milestone allocation

### M1 — semantic component integration validation

Purpose: validate a stable project-controlled access/intervention boundary while
preserving the original renderer and tactical behavior. No beneficial visual
enhancement, three-class modernization demonstration, or CTE-2 enhancement
implementation is required to close this project milestone.

M1 entrance: existing M0 proof, supported client/configuration and reviewed
ABI/probe contract. M1 exit requires:

- the existing semantic integration sub-gate (plan section 13.2) is CONFIRMED;
- a representative integrated tactical mission operates for >=30 continuous
  minutes, with the semantic component active and original rendering preserved;
- repeatable frame-time and system/graphics-memory telemetry, including a
  disabled comparison, supports an explicit overhead/deficiency assessment;
- HUD/cursor/targeting/camera/control operation remains usable/correct;
- enable/disable/removal and recreation of the configuration are demonstrated,
  client hashes preserved and capture bounded;
- relevant identity/lifetime/exception risks are dispositioned; fail-open is an
  acceptable explicit policy, not proof of untested retarget/recovery behavior;
- integrated manifest, run logs, telemetry, control checklist and updated risk
  register support sponsor review.

Short diagnostic intervention evidence may support controllability; neither
reversed lighting nor tint is counted as visual modernization. No requirement to
repeat passed microtests or make new visual effects just to close M1.

M1 PASS means **semantic component integration validated**, not overall project
TRL 4. M1 CONTINUES if bounded reliability/measurement evidence remains; BLOCKED /
FAIL if the component cannot meet those criteria without a different approach.
This amendment does not retrospectively declare M1 PASS.

### M2 — enhancement integration and relevant-environment validation

Coarse scope only: connect the proven boundary to a bounded enhancement capable
of genuine visual benefit, then validate the integrated result on the target PC.
Do not assume internal color/shading adjustments can meet the capability goal.
Candidate selection and detailed planning require separate sponsor approval.

The original combined CTE-1/2/3 integration and three VMES-class modernization
evidence move from the M1 project exit to an **overall TRL 4 checkpoint within
M2**, before any overall TRL 5 claim. Preserve the original 30-minute integrated
mission, HUD/cursor and telemetry clauses for that checkpoint with enhancement
active; M1's neutral 30-minute run cannot substitute for it.

After that checkpoint, original CDD TRL 5 criteria remain unchanged: complete
representative mission, >=60% VMES cases scoring >=2, no Critical Visual Regression
preventing completion, p95 tactical frame time <=50ms, critical gameplay smoke
subset passes, and no modernization-induced unrecoverable gate-mission failure.
Existing VMES definitions and final KPP thresholds remain unchanged.

## Maturity accounting / affected authority

CDD section 11.2's least-mature necessary CTE rule is unchanged. Milestone order
is no longer shorthand for aggregate TRL. M1 validates the CTE-1-oriented
component boundary; do not infer CTE-2 or modernized CTE-3 maturity from it.
CDD TRL 4's combined proof remains required, but is scheduled in M2. TRL 5 entry
still requires that combined proof. The CTE-3 risk mitigation requiring
composition evidence by TRL 4 stays in force at the aggregate checkpoint.

Superseded for project scheduling: the old M1 plan sections 2, 8/M1-07, 13.3–13.4
and 17, and Increment C's beneficial-enhancement-as-M1-completion assignment.
Historical approvals/results stay preserved, with this later disposition taking
precedence. No new rendering implementation or final technology is authorized.

## Current evidence and next boundary

CONFIRMED: RT-010 owner-specific input substitution reaches native preparation,
changes visible lighting, restores original flow and exits cleanly. It does not
prove improved quality, complete material/camera contracts or all-model coverage.
M1 still needs formal sustained reliability, measurements and reproduction
evidence adjudication. Next action: prepare a bounded M1 closure evidence/test
checklist from existing runs before scheduling additional gameplay. M2 remains
coarse; no enhancement implementation begins under this amendment.
