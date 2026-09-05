# Codex Run Record — M0 Baseline Closure and M1 Planning

## Run identity

- Run ID: `CODEX-20260904-M1-PLAN-001`
- Date: 2026-09-04
- Active task: close completed M0 baseline and plan M1 / TRL 4
- Starting repository state: `master` at `38d57fd`; 10 reviewed pending files
  covering probe elevation policy, regression tests, and two local-helper IOC
  records; nothing staged. README status was found stale during baseline review.
- Result: baseline closed; M1 plan produced for sponsor review; M1 not started

## Technical question

Can the M0-proven semantic rendering seam support a stable, observable,
behaviorally neutral integrated component boundary, and what bounded evidence is
required to adjudicate M1 without changing the approved CDD?

## Sources reviewed

- approved external *Starfleet Command Rendering Modernization Capability
  Requirements* v1.0, including KSA-1 through KSA-3, derived requirement IDs,
  CTE-1 through CTE-3, and TRL 4 entry/exit evidence;
- `docs/m0/m0-trl3-critical-function-proof.md`;
- `docs/m0/m0-semantic-ownership-map.md`;
- `docs/m0/m0-semantic-function-map.csv`;
- M0 probe definitions and shared bounded-capture runbook;
- Pre-M0 subsystem map and runtime-question backlog where they intersect the
  proven chain;
- all staged/unstaged files present at run start.

## Baseline closure

Review found no unexpected or unrelated working-tree change. Generated probe
binary output remained ignored. The stale README statement that requirements
were not baselined was corrected to identify approved CDD v1.0.

Validation performed before commit:

- `git diff --check` — passed (line-ending notices only);
- `pwsh -NoProfile -File tests/test_probe_elevation_policy.ps1` — passed;
- `python -m unittest tests.test_analyze_probe_log -v` — 1 test passed;
- `pwsh -NoProfile -File tools/m0_probe/build_probe.ps1` — x86 build passed;
- ignored-output check — generated `artifacts/pre-m0/bin/m0_probe.exe` confirmed
  ignored;
- client MD5 — `2BE8F713F81B1C68D50EAD6088C32886`, unchanged;
- client SHA-256 —
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`,
  unchanged;
- M0 report — confirmed `PASS` and `M1 JUSTIFIED`; no M1 implementation present.

The completed semantic proof already existed as commit:

- `38d57fd Complete M0 TRL 3 semantic rendering seam proof`

The reviewed follow-on baseline was committed separately because it is probe
workflow/tooling hardening rather than the semantic proof itself:

- `d87c7bb Harden M0 probe workflow and document helper IOC`

## Planning decisions

- Use a neutral observation/pass-through component as the first integration
  proof; do not select a final renderer.
- Treat the owner/model/mesh functions as one cooperating semantic seam and
  retain `0x006AB410` as downstream validation only.
- Normalize only owner, model, mesh/LOD, source, transform handoff, lifetime, and
  downstream correlation needed to test the boundary.
- Combine two-ship, camera/motion, and enter/leave questions into the smallest
  practical number of sponsor-operated sessions.
- Make LOD transition conditional on reliable induction.
- Require paired disabled/enabled evidence, reversible removal, bounded buffers,
  numeric file/event/time limits, and frame-time/memory telemetry.
- Preserve the approved CDD distinction: a neutral pass-through can complete the
  semantic integration sub-gate but cannot alone prove CTE-2, integrated CTE-3,
  or three modernized VMES classes. Formal TRL 4 PASS therefore remains gated on
  a sponsor-authorized bounded completion increment or proper governance action.

## Deliberately rejected scope expansion

- no renderer replacement or final architecture choice;
- no RTX, neural rendering, upscaling, wrapper replacement, or UI modernization;
- no broad caller-tree or unrelated engine reconstruction;
- no material/effect/hardpoint/camera contract absent a failed seam criterion;
- no detailed M2 plan;
- no use or modification of `local-coder-helper`.

## Files created or modified during planning

- baseline correction committed in `README.md` as part of `d87c7bb`;
- created `docs/m1/m1-trl4-integrated-component-validation-plan.md`;
- created this run record.

No M1 source code, component, hook, probe, or runtime capture was created or
executed.

## Evidence and confidence

- **CONFIRMED:** M0 PASS baseline and two-owner semantic chain are versioned in
  `38d57fd`.
- **CONFIRMED:** follow-on probe workflow/tests are versioned in `d87c7bb` and
  passed the listed checks.
- **CONFIRMED:** the approved CDD TRL 4 exit requires CTE-1 through CTE-3, a
  30-minute mission, three modernized VMES classes, HUD/cursor usability, and
  repeatable frame-time/memory telemetry.
- **STRONG HYPOTHESIS:** a reversible neutral pass-through is the lowest-risk
  first M1 integration proof.
- **SPECULATIVE:** exact interception mechanism, runtime cost, pointer-reuse
  behavior, and materiality of the `0x00509843` exception remain for M1 evidence.

## Sponsor approval

Approved 2026-09-04 with this exact disposition:

> Execute the neutral pass-through as the first M1 increment. Successful
> completion satisfies the semantic integration sub-gate only and leaves M1 in
> CONTINUES. Do not claim formal TRL 4 PASS until the remaining CTE-2/CTE-3 and
> three-VMES evidence required by the approved CDD is completed through a
> separately planned and sponsor-approved M1 increment. No requirements change
> or waiver is authorized.

No blocker prevents execution of the approved neutral pass-through increment.

## Final repository state

- committed baseline: `master` at `d87c7bb`;
- planning artifacts approved for the dedicated M1 planning-baseline commit;
- no other staged or unstaged changes expected;
- nothing from M1 implementation was staged or committed.
