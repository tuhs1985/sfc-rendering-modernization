# Codex run — M1 validation gap assessment

- Run ID/date: 2026-10-14-m1-validation-gap-assessment; active milestone M1.
- Question: what remains before formal M1 / TRL 4 validation?
- Starting baseline: HEAD `fee152f`; existing tracked modifications and untracked
  implementation/evidence preserved. Nothing staged. This is an assessment only.
- Authority reviewed: approved `docs/m1/m1-trl4-integrated-component-validation-plan.md`
  sections 13–17; current `docs/m1/m1-c-cte23-increment-plan.md`; `docs/HANDOFF.md`;
  latest RT-010 evidence/run reviewed during this assessment session.
- Requirements original: `C:\Users\rober\OneDrive\Documents\Obsidian Vault\02 - Projects\Project Requirements\Starfleet Command Rendering Modernization Capability Requirements.md`,
  TRL 4 section, lines 676–696. SHA256 verified:
  `BF5384D2586601AAA28DB36970937A3B40F598E12002B3450BF2E7D9562FA352`.

## Result and remaining evidence

CONFIRMED: semantic integration and RT-010 diagnostic lighting control are
demonstrated. This does not establish beneficial modernization or formal TRL 4.
The unchanged CDD requires CTE-1 through CTE-3 together in one repeatable
configuration, a representative mission for at least 30 continuous minutes,
repeatable modernization across at least three VMES scene classes, usable HUD
and cursor, and repeatable frame-time/memory telemetry.

Remaining work: approve a bounded genuinely beneficial visual treatment; integrate
and demonstrate it across three justified scene classes; collect the sustained
mission, original/enabled comparisons, frame-time and memory measurements; verify
repeatable setup, disabling/removal and normal tactical operation; assemble build
manifest, logs, visual samples, telemetry and updated deficiencies for review.
Close integration/lifetime gaps where they affect that configuration: RT-010
stops on selected-owner retirement and does not prove new-epoch intervention
recovery. Auxiliary spare-owner coverage limits remain recorded, not waived.

Candidate scene classes (proposal only): close ship, multiple ships with camera
motion, and active combat with HUD. Final selection belongs in the approved
bounded enhancement/validation increment, not silently added requirements.

No final renderer, full remaster, broad reverse engineering or later TRL 5 numeric
quality/performance thresholds are required by this assessment. Diagnostic tint
and reversed lighting alone do not count as beneficial modernization. Existing
short-run observations cannot substitute for the 30-minute integrated evidence.

## Reproduction, validation and repository state

- Tools: PowerShell repository reads, Git status/HEAD, `Select-String` for CDD TRL 4,
  `Get-FileHash -Algorithm SHA256`, and `apply_patch` for this record.
- Material checks: `git status --short`, `git rev-parse --short HEAD`, read plan
  sections 13–17 and current increment/handoff, requirements hash comparison,
  `git diff --check`, referenced repository path existence and staged-state check.
- No runtime probe/capture/build was run or changed; capture limits not applicable.
  No client binary was touched; no fresh client hash claim made for this assessment.
- Files created: this record only. No existing evidence or handoff overwritten.
- Confidence: CONFIRMED requirements gap; proposed beneficial treatment and scene
  selection are not yet adjudicated or implemented. M1 CONTINUES.
- Final state: inherited dirty work retained; this record additionally untracked;
  nothing staged or committed. No active runtime/tool session established.
- Exact next action: prepare a bounded beneficial-shading proposal for sponsor
  approval before new enhancement implementation.

## Follow-up — sponsor questions M1/M2 allocation

Sponsor considers M1's improvement expectation too demanding and asks what M2
was intended to establish. Read the approved M1 plan's deferred-next-milestone
description and CDD TRL 5 gate (lines 700 onward). No standalone roadmap was
located by the filename search; M2 is discussed here as the next TRL 5 gate,
not as an invented detailed implementation plan.

CONFIRMED TRL 5 purpose: convergence toward Threshold in the designated target
environment. Criteria: complete representative tactical mission; at least 60%
of current VMES cases score >=2; no Critical Visual Regression preventing mission
completion; p95 tactical frame time <=50 ms; Critical Gameplay Fidelity smoke
subset passes; no modernization-induced unrecoverable gate-mission failure.
Evidence: mission recording/log, visual score sheet, telemetry, smoke-test results
and open deficiencies. These are maturation criteria, not replacement KPPs.

Clarification: the prior answer's phrase 'useful improvement' is explanatory,
not a new verbatim M1 requirement. M1 says repeatable modernization in three scene
classes; TRL 5 introduces quantified breadth/quality and performance gates.
Discussing a changed allocation does not authorize editing requirements or waive
the existing gate. Next action for this discussion: sponsor decides whether to
request a bounded M1/M2 gate-change proposal before further enhancement work.
Tools: Fuel Guard attach (recent hook verified), PowerShell CDD reads, rg filename
and content searches. Documentation-only; no runtime/build or staging/commit.
