---
title: "M1 — TRL 4 Integrated Component Validation Plan"
milestone: M1
target_maturity: CTE-1-oriented component validation; aggregate TRL tracked separately
status: technical-validation-complete-pending-sponsor-closure-review
date: 2026-09-04
governing_authority: "CDD v1.0 plus approved SFC-GATE-20261014"
---

# M1 — TRL 4 Integrated Component Validation Plan

## Current execution disposition — 2026-10-14

[M1 closure report](m1-component-integration-closure-report.md) recommends technical
PASS for the amended component gate; sponsor acceptance pending. No further
runtime test identified as necessary for this scope. Historical title does not
imply aggregate TRL4; approved gate amendment below still governs. No M2
implementation or commit authorized by this disposition.

## CURRENT APPROVED DISPOSITION — 2026-10-14

[SFC-GATE-20261014](../decisions/2026-10-14-m1-m2-gate-allocation-amendment.md)
is the approved authority for the revised M1/M2 allocation. The filename and
original title remain stable for existing links; **M1 is now semantic component
integration validation, not an aggregate TRL 4 claim**. Original allocation
language retained below is historical wherever it conflicts with this amendment.

M1 closes on semantic sub-gate plus sustained integration reliability, >=30-minute
representative mission, repeatable frame-time/system/graphics-memory evidence,
usable tactical UI/control, reproducible setup/disable/removal and reviewed risks.
Beneficial enhancement and three-class modernization move to M2's combined
CTE-1/2/3 TRL 4 checkpoint, before unchanged TRL 5 validation. No capability
Threshold/Objective/REQ ID changed; overall maturity remains least-CTE bounded.

## 1. Milestone purpose

M1 will determine whether the semantic rendering seam proven in M0 can host a
stable, observable, removable project-controlled component while preserving the
original SFC tactical render path and gameplay behavior.

The first proof is intentionally behaviorally neutral:

```text
SFC semantic render-owner state
  -> project-controlled observation/pass-through component
  -> original SFC rendering path
  -> 0x006AB410
  -> IDirect3DDevice3::DrawIndexedPrimitive
```

M1 does not select the final renderer, define a production rendering API, or
implement visual modernization. Its immediate technical question is:

> Can a project-controlled component observe and pass through the proven
> semantic render-owner path across representative tactical conditions while
> preserving correct original rendering, object identity, transforms, and
> tactical operation?

## 2. Requirements authority and traceability

The approved *Starfleet Command Rendering Modernization Capability
Requirements* v1.0 remains authoritative. This plan derives verification work
from it and does not change any Threshold, Objective, or stable requirement ID.

| Authority | M1 relevance | Planned evidence |
|---|---|---|
| CTE-1 — Legacy Render Access | Primary technical subject: turn the proven seam into a repeatable integrated component boundary. | Component manifest, static hook justification, enabled/disabled runtime runs, semantic-to-downstream correlations. |
| CTE-2 — Modern Rendering Enhancement | Deferred to M2 under SFC-GATE-20261014; no M1 visual-benefit claim. | Separately approved enhancement integration and combined TRL 4 evidence in M2. |
| CTE-3 — Scene/UI Composition and Temporal Integrity | M1 checks original rendering/UI non-interference only. | Modernized composition/temporal proof at the combined TRL 4 checkpoint in M2. |
| REQ-BAS-001 | Keep the supported executable/build and configuration explicit. | Exact executable hash and launch/configuration manifest for every formal run. |
| REQ-BAS-002 | Preserve a modernization-disabled comparison. | Paired disabled and enabled baseline captures for the selected fixtures. |
| REQ-BAS-003 | Make every formal result attributable. | Game, component, dependency, driver, and fixture identifiers in each run record. |
| REQ-REN-001 | Exercise sufficient access to the render path. | Stable semantic-owner observation correlated to `0x006AB410`. |
| REQ-REN-002 | Prevent intentional gameplay changes. | Neutral component behavior and focused tactical-control checks. |
| REQ-REN-003 | Provide repeatable enable/disable operation. | Documented load, disable, removal, and restoration procedures. |
| REQ-REN-004 | Preserve 3D content and required tactical overlays. | Paired scene evidence plus HUD/cursor checklist. |
| REQ-GAME-001 | Preserve required tactical controls and cursor interaction. | Sponsor-executed minimal gameplay actions during representative runs. |
| REQ-GAME-002 / REQ-GAME-003 | Avoid save/campaign conversion and preserve baseline restoration. | No game-data conversion; disable/remove demonstration. |
| REQ-PERF-001 / REQ-PERF-002 | Make frame-time and memory effects measurable. | Repeatable frame-time, system-memory, and graphics-memory capture for formal integrated runs. |
| REQ-STAB-001 | Separate baseline failures from component-induced failures where evidence permits. | Paired disabled/enabled runs and explicit failure attribution. |
| REQ-DEP-001 / REQ-DEP-002 | Keep the development configuration reproducible. | Build/run instructions and dependency/configuration manifest. |
| KSA-1 | Avoid modernization-induced unrecoverable failure. | Repeated representative mission records; the Threshold count remains three. |
| KSA-2 | Preserve tactical UI and information integrity. | Required HUD/cursor/target/status checklist. |
| KSA-3 | Preserve deployment reproducibility. | Clean recreation and enable/disable documentation. |

REQ-VIS-* and the full KPP-1 visual-quality evaluation remain governing
requirements, but a neutral pass-through produces no honest visual-modernization
claim. Enhancement and three-class modernization evidence are allocated to M2 by
SFC-GATE-20261014, not required to close M1's component integration gate.

## 3. Confirmed starting evidence

M1 begins from the following M0 results; they are not reopened absent a specific
contradiction:

- **CONFIRMED:** two distinct runtime `tEntityShip` owners converged through
  `t3DVisual_Model`, `tModel0`, the graphics manager, `0x006AB410`, and native
  `DrawIndexedPrimitive`.
- **CONFIRMED:** the mainline semantic path is:

  ```text
  tEntityShip::render              0x004162B9
    -> t3DVisual_Model::render/LOD 0x0042FD3F
      -> selected-child call       0x0042FDD2
        -> tModel0::render          0x0042E4B2
          -> manager source        0x006ABF80 / 0x006ABFB0
            -> polygon preparation 0x006ABFC0
              -> accumulation      0x006AB410
                -> batch flush     0x006AB380
                  -> native draw   0x006AB3C0
  ```

- **CONFIRMED:** ship owner, visual-model, mesh/LOD, source, and transform-handoff
  identities exist above the manager handoff.
- **CONFIRMED:** `0x006AB410` is a generic geometry boundary and reliable
  downstream correlation anchor, not the semantic modernization seam.
- **CONFIRMED:** M0 bounded probes preserved tactical responsiveness, exited
  normally, and did not alter the client executable.
- **CONFIRMED:** exact supported client evidence used by M0 is MD5
  `2BE8F713F81B1C68D50EAD6088C32886` and SHA-256
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
- **CONFIRMED:** a third `tModel0` return path at `0x00509843` was observed 131
  times and remains a finite unclassified exception.
- **STRONG HYPOTHESIS:** the cooperating owner/model/mesh chain, rather than one
  isolated function, is the practical integration boundary.

Primary evidence references:

- [M0 critical-function proof](../m0/m0-trl3-critical-function-proof.md)
- [M0 semantic ownership map](../m0/m0-semantic-ownership-map.md)
- [M0 semantic function map](../m0/m0-semantic-function-map.csv)
- [M0 bounded-capture runbook](../m0/probes/m0-probe-capture-runbook.md)
- [M0-RT-003 semantic-owner probe](../m0/probes/M0-RT-003.md)

## 4. M1 technical questions

1. Can a project-controlled component observe the owner/model/mesh chain and
   return control to the original path without corrupting state or behavior?
2. Are per-process owner identities stable enough to distinguish simultaneous
   visible ships and to track appear/disappear behavior without stale reuse?
3. Can model, selected mesh/LOD, source, and transform-handoff identity be
   represented in an explicit experimental contract?
4. Can semantic events be correlated reproducibly with downstream activity at
   `0x006AB410` without logging every draw indefinitely?
5. Is the unclassified `0x00509843` path a bounded exception, or does it expose
   a category that invalidates the proposed component boundary?
6. What measurable performance, stability, or UI/control cost does the enabled
   neutral component add relative to the disabled baseline?

## 5. Scope

M1 includes only work required to answer those questions:

- freeze an exact development manifest and disabled baseline;
- specify a temporary semantic event/identity contract;
- implement a reversible neutral observation/pass-through component;
- validate component enable, disable, removal, and original-flow continuation;
- correlate owner/model/mesh events with bounded `0x006AB410` activity;
- distinguish multiple owners and test object lifetime behavior;
- measure frame-time and memory effects with the component disabled and enabled;
- inspect required tactical rendering, HUD, cursor, and controls for regression;
- inventory only exceptions actually observed in the selected conditions;
- preserve probe, configuration, evidence, and Codex run documentation.

## 6. Explicit non-scope

M1 will not:

- select or integrate a final renderer;
- replace DirectDraw, D3D3/D3D7, the confirmed downstream path, or presentation;
- begin RTX, neural rendering, upscaling, ReShade, dgVoodoo, or model replacement;
- modernize the 2D UI or redesign controls;
- infer material, texture, camera, hardpoint, lighting, shield, or effect contracts
  unless a specific observed failure makes one necessary for seam validation;
- reconstruct unrelated engine systems or exhaustively classify every renderer
  caller;
- broaden supported game builds, configurations, or mods;
- polish the experimental contract into a production API;
- change CDD requirements or treat technical difficulty as a waiver;
- create detailed M2 work.

`local-coder-helper` remains parked and is not part of M1 planning or execution.

## 7. Candidate integration concept

### 7.1 Boundary

Treat the seam as a cooperating boundary with observation points at the confirmed
ship owner, visual model/LOD owner, and `tModel0` mesh/source owner. Retain
`0x006AB410` only as a downstream validation event.

The exact interception mechanism is an M1 implementation choice to be selected
after a short, evidence-based comparison of reversible techniques. Selection
criteria are: exact-build safety, known calling convention, deterministic
enable/disable behavior, minimal changed instructions/state, original-flow
continuation, bounded logging, and clean removal. This comparison must not become
a general architecture study.

### 7.2 Temporary semantic contract

The experimental record should contain only fields proven or required by M1:

- schema and component-build version;
- monotonic event sequence and high-resolution timestamp;
- event kind and originating function/address;
- per-process opaque owner ID plus observed raw pointer for evidence correlation;
- visual-model and `tModel0` opaque IDs/raw pointers;
- selected mesh/LOD identity where observed;
- source/resource identity where observed;
- transform-handoff identity and a bounded transform snapshot only where the
  calling context supports it safely;
- lifetime state (`first_seen`, `observed`, `not_seen`, `retired`) derived with an
  explicit rule;
- bounded downstream correlation count/token for `0x006AB410`;
- exception/rejection reason when a record cannot be normalized.

Raw addresses and pointers are evidence within one process, not stable identities
across launches. The component must assign new opaque IDs per process and must not
carry identity across a pointer retirement/reuse without corroboration.

### 7.3 Behavioral neutrality and reversibility

- Preserve registers, stack, floating-point/SIMD state, arguments, return values,
  and original call order required by the intercepted ABI.
- Forward every accepted mainline event to the original code path.
- On logging saturation or internal analysis failure, stop detailed capture and
  preserve original rendering; do not fail the game merely to preserve evidence.
- Provide documented disabled and removed states.
- Record and verify any touched executable bytes in memory before installation,
  during activation, and after removal. Never alter the on-disk client.

## 8. Work packages and sequence

### M1-01 — Freeze the development test manifest

Record the exact client hash, launcher/configuration, component revision,
dependencies, driver/OS, fixture, instrumentation, and output limits. Capture a
modernization-disabled baseline for the selected conditions.

**Completion evidence:** manifest, hash record, disabled run record, and baseline
telemetry.

### M1-02 — Define the integration/probe contract

Adjudicate the minimum observation points, calling conventions, preserved state,
semantic fields, lifetime rules, failure behavior, and downstream-correlation
method. Create a versionable probe/component definition before runtime use.

**Completion evidence:** reviewed contract/schema, hook-site evidence packet,
probe definition, and risk notes. Decompiler names alone are insufficient.

### M1-03 — Build and offline-validate a neutral component

Implement the smallest reversible pass-through that emits the contract and
continues original flow. Add mechanical tests for configuration parsing, bounded
buffers, saturation behavior, opaque-ID allocation/retirement, and disable/remove
paths. Validate binary architecture and import/dependency expectations.

**Completion evidence:** versioned source/configuration, build record, tests, and
component manifest. No gameplay is required until offline checks pass.

### M1-04 — Prove one-owner integration

Run the component disabled and enabled in the same minimal one-visible-ship
condition. Demonstrate semantic events, downstream correlation, correct original
rendering, control responsiveness, normal exit, and bounded output.

**Decision:** if original flow cannot be preserved, diagnose one evidence-backed
alternative mechanism. Do not proceed to volume testing on an unstable hook.

### M1-05 — Prove differentiation, motion, and lifetime

Use the minimum combined scenario capable of distinguishing two ship/model
owners, exercising camera and object motion/orientation, and observing an object
enter, leave, or become no longer rendered. Add a genuine LOD transition only if
it can be induced repeatably without broad scenario exploration.

**Completion evidence:** semantic timelines, paired scene evidence, downstream
counts, lifetime/reuse analysis, and an adjudicated exception list.

### M1-06 — Stability, telemetry, and reproducibility

Perform the formal repeated runs required by the relevant CDD criteria, including
at least one representative 30-minute integrated tactical mission. Capture
repeatable frame-time, system-memory, and graphics-memory telemetry. Exercise
disable/removal and recreate the documented development configuration without
interactive debugging or source modification.

**Completion evidence:** repeated run records, telemetry, HUD/control checklist,
recreation record, and failure attribution.

### M1-07 — Evaluate the formal TRL 4 completion gap

**Superseded allocation:** use SFC-GATE-20261014. Assess M1 reliability against
the revised component gate; record the combined TRL 4 gap for M2. The original
decision paths below are preserved historically, not current execution authority.

After the neutral component is proven, compare the evidence with the unchanged
CDD TRL 4 exit criteria. A neutral pass-through cannot by itself demonstrate
CTE-2, integrated CTE-3 modernization, or three VMES scene classes showing
repeatable modernization.

Do not declare TRL 4 PASS on pass-through evidence alone. Either:

1. keep the milestone at **M1 CONTINUES** and obtain sponsor authority for a
   narrowly bounded CTE-2/CTE-3 integration increment; or
2. if the sponsor separately changes milestone interpretation through the proper
   requirements/governance process, record that decision without editing or
   silently reinterpreting the approved CDD.

Any CTE-2/CTE-3 increment must be planned before implementation, remain
architecture-neutral where practical, and include the required three VMES scene
classes. This document does not choose that visual technique.

## 9. Minimum discriminating runtime conditions

| Condition | Why it is required | Minimum observation |
|---|---|---|
| Disabled one-ship baseline | Separates baseline behavior and cost from component effects. | Original rendering/control, hashes/configuration, frame-time and memory. |
| Enabled one visible ship | Proves the simplest integrated pass-through and correlation. | Stable owner/model/mesh identity and downstream `0x006AB410` activity. |
| Enabled two distinguishable ship/model classes | Rejects a singleton/global-owner hypothesis and detects cross-association. | Two stable owner chains with distinct model/source identity in one process. |
| Combined camera plus object movement/orientation | Tests transform handoff while avoiding separate redundant captures. | Owner association remains correct while view/object state changes. |
| Object enters/leaves the rendered scene | Tests lifetime, retirement, reappearance, and stale pointer/ID handling. | Explicit first/last observation and no cross-associated reuse. |
| Representative 30-minute mission | Required by the approved TRL 4 exit criteria and exposes accumulation/resource failures. | Continuous operation, telemetry, UI/control checks, bounded logs, normal exit. |
| Genuine LOD transition (conditional) | Directly tests selected mesh/LOD identity, but only if reproducible. | Same owner/model with an evidence-backed LOD change and correct downstream continuation. |

The two-ship, movement, camera, and enter/leave observations should be combined
into as few sponsor-operated sessions as practical. Additional ship classes,
effects, or missions require a specific unresolved hypothesis.

## 10. Test and instrumentation strategy

Each runtime activity follows:

```text
static evidence
  -> one stated hypothesis
  -> versioned probe/component definition
  -> bounded disabled/enabled run
  -> automated summary
  -> Codex evidence adjudication
```

Before execution, each M1 probe definition must record: probe ID, question,
hypothesis, exact target addresses, tool/version, build and launch method,
privilege behavior, start/stop gates, filters, numeric time/event/file limits,
expected output path and size, cleanup, analysis method, hazards, and evidence
mapping.

Routine privilege must be inherited from a narrowly scoped already-elevated
parent workflow. Sponsor activity is not to include UAC confirmation. The
explicit elevation fallback may remain for recovery; UAC and other Windows
security controls must not be weakened or globally disabled.

Corroboration targets:

- static call/field evidence plus runtime execution;
- stable differentiated owner identities plus matching model/source data;
- semantic event counts/timing plus bounded downstream `0x006AB410` activity;
- disabled/enabled scene evidence plus gameplay/UI observation;
- component telemetry plus baseline telemetry.

## 11. Bounded capture and raw-output policy

Detailed per-event logging must be gated and finite. The initial safe envelope is:

- no capture before explicit tactical-scene gating;
- maximum detailed burst of 120 rendered frames or 10,000 semantic events,
  whichever occurs first;
- no more than eight simultaneously detailed owner IDs unless a probe definition
  justifies a different bound;
- 16 MiB warning threshold and 32 MiB hard per-file stop for component event logs;
- maximum 35-minute formal runtime, with only summary counters after detailed
  capture saturates;
- bounded in-memory queue/ring behavior; producer activity must not wait
  indefinitely for evidence output;
- downstream `0x006AB410` correlation by counters/sampled windows rather than an
  unbounded per-call transcript;
- output written below ignored capture/artifact locations, with only curated
  summaries promoted into version control.

The frame, event, and file limits are initial engineering controls, not CDD
requirements. A probe may tighten them. It may increase them only in its reviewed
definition with expected volume, storage safeguard, and a reason the smaller
capture cannot answer the question.

Tools capable of rapidly generating multi-gigabyte output must be identified as
such in their runbooks. Their safe procedure must disable unrestricted tracing,
apply target/function and time/event filters before launch, verify free space,
and stop at the documented limit. Unbounded capture is prohibited where a
bounded alternative can answer the question.

## 12. Sponsor/test-pilot interaction

Codex or maintained tooling prepares builds, elevated parent context, component
configuration, capture gates, telemetry, log collection, cleanup, and automated
summaries. The sponsor is asked only to:

1. launch the prepared SFC Launcher workflow;
2. enter the named tactical fixture;
3. perform a short scripted gameplay action such as select/rotate/move ships,
   move the camera, or cause an object to enter/leave view;
4. continue the representative mission for the stated duration when required;
5. report visible rendering, HUD, cursor, or control anomalies; and
6. exit normally.

The sponsor is not asked to inspect assembly, decompiler output, pointers, call
graphs, raw traces, or administrative dialogs.

## 13. Entrance and exit criteria

### 13.1 Entrance criteria

- M0 / TRL 3 PASS evidence and semantic maps are versioned and reviewed.
- Exact supported client hash/configuration is available and verified.
- The unmodified original path can be launched through the SFC Launcher.
- A disabled baseline fixture and expected tactical actions are documented.
- Candidate observation points have static and runtime support; ABI/state
  preservation assumptions are explicitly reviewed.
- Probe/component definition, numeric capture bounds, cleanup, and rollback are
  approved before runtime execution.
- Offline tests and build checks pass.

### 13.2 Semantic integration sub-gate

The pass-through sub-gate succeeds when all of the following are **CONFIRMED**:

- the project-controlled component operates at the intended semantic level;
- original control flow and downstream rendering continue through `0x006AB410`;
- at least two simultaneous owners remain distinguishable;
- model plus mesh/LOD or source identity, and transform handoff, are represented
  without cross-association;
- object retirement/reappearance does not leave stale identity;
- disabled/enabled/removed states are repeatable and leave on-disk SFC artifacts
  unchanged;
- selected tactical conditions render and operate correctly;
- output remains within documented bounds; and
- the observed mainline and exception set are sufficiently bounded to continue.

### 13.3 Current M1 component integration exit criteria

Use the approved amendment's M1 exit checklist in addition to section 13.2:
>=30-minute representative semantic-component mission, repeatable frame-time and
system/graphics-memory comparison, usable UI/control, repeatable setup and
disable/removal, unchanged client, bounded output and reviewed lifetime/exception
risks. No beneficial enhancement required and no aggregate TRL 4 PASS implied.

### 13.3-H Historical combined TRL 4 criteria — now scheduled within M2

Formal **M1 PASS / TRL 4 demonstrated** requires both the semantic integration
sub-gate and every unchanged CDD TRL 4 exit criterion:

- CTE-1 through CTE-3 operate together in one repeatable configuration;
- a representative tactical mission operates at least 30 continuous minutes;
- at least three VMES scene classes show repeatable modernization;
- required HUD and cursor functions remain usable; and
- repeatable frame-time and memory telemetry are captured.

Required formal evidence remains: integrated-build manifest, run log, VMES
samples, telemetry, and updated risk/deficiency register.

### 13.4 Decision logic

**Current:** M1 PASS = component integration/reliability criteria confirmed;
CONTINUES = bounded evidence remains; BLOCKED/FAIL = component unsuitable or
different approach needed. None implies aggregate TRL 4. The original combined
gate logic below remains applicable to M2's overall TRL 4 checkpoint only.

- **M1 PASS / TRL 4 demonstrated:** semantic integration and all formal CDD TRL 4
  exit criteria pass; no unresolved issue invalidates the seam.
- **M1 CONTINUES:** evidence is promising and remaining questions are bounded and
  answerable in M1. This includes a successful neutral pass-through when the
  CTE-2/CTE-3 and three-VMES completion evidence has not yet been authorized or
  produced.
- **M1 BLOCKED / FAIL:** the seam cannot support a practical component, semantic
  state is unstable/insufficient, integration breaks normal operation, the
  exception set is unbounded, or progress requires a qualitatively different
  technical approach.

Failure is preserved as an engineering result; it does not change requirements.

## 14. Expected versioned artifacts

- this active-milestone plan and its sponsor disposition;
- integrated development-build/configuration manifest;
- experimental semantic contract/schema and field evidence table;
- component source, build scripts, configuration, and focused tests;
- M1 probe definitions and safe capture runbook;
- automated log analyzer and curated summaries;
- disabled/enabled comparison records and runtime evidence index;
- semantic owner/downstream correlation and lifetime timelines;
- bounded mainline/exception inventory;
- frame-time and memory telemetry summaries;
- HUD/cursor/tactical-control checklist;
- updated risk/deficiency register;
- M1 evidence report and Codex run records.

Raw traces, binaries, dumps, and bulk telemetry remain ignored unless a small,
reviewed artifact is deliberately promoted as durable evidence.

## 15. Known risks and uncertainties

| Risk/uncertainty | Current class | M1 control |
|---|---|---|
| Hook/ABI error corrupts original flow. | STRONG HYPOTHESIS until implementation evidence exists. | Review exact prologue/calling convention, preserve machine state, offline tests, one-owner gate first, immediate disable path. |
| Pointer reuse creates false owner identity. | SPECULATIVE. | Per-process opaque IDs, explicit retirement rules, enter/leave scenario, raw pointer evidence retained only for the run. |
| `0x00509843` represents a material tactical category. | CONFIRMED path, purpose unresolved. | Count/classify only in selected scenarios; escalate only if frequency or visible ownership affects the seam. |
| Per-event instrumentation changes timing or output volume. | STRONG HYPOTHESIS. | Bounded buffers, sampling/counters, disabled/enabled telemetry, fail-open logging. |
| Launcher/elevation workflow interrupts sponsor testing. | Previously observed; mitigated. | Already-elevated parent, regression-tested policy, no routine sponsor UAC. |
| Neutral pass-through is mistaken for full TRL 4. | CONFIRMED governance gap. | Separate semantic sub-gate from formal CDD exit; require sponsor disposition before a CTE-2/CTE-3 increment. |
| Material/effect/UI paths are not on the mainline owner chain. | SPECULATIVE and deferred unless observed. | Record bounded exceptions; do not broaden analysis without a failed M1 criterion. |

## 16. Deferred beyond M1

Unless required to complete the unchanged TRL 4 criteria through a separately
approved bounded increment, defer final renderer choice, production API design,
visual-quality optimization, full 3D-state inventory coverage, asset replacement,
UI modernization, packaging/updater polish, broader hardware support, and detailed
M2 planning.

The next milestone remains coarse: validate the accepted integrated approach in
the relevant target environment and against a broader verification set. Its plan
will be created only after M1 evidence is reviewed.

## 17. Sponsor disposition

**Current approval 2026-10-14:** SFC-GATE-20261014 explicitly reallocates beneficial
enhancement and three-class modernization to M2. It supersedes the prior
requirement to finish that work within M1; no final capability waiver is granted.
The earlier approval below remains historical, not the current allocation.

Approved 2026-09-04: execute the neutral pass-through as the first M1 increment.
Successful completion satisfies the semantic integration sub-gate only and leaves
M1 in **CONTINUES**. Formal TRL 4 PASS remains prohibited until the remaining
CTE-2/CTE-3 and three-VMES evidence required by the approved CDD is completed
through a separately planned and sponsor-approved M1 increment. No requirement
change or waiver was authorized.
