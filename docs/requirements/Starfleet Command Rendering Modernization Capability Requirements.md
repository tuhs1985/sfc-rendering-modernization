---
title: "Starfleet Command Rendering Modernization Capability Development Document"
aliases:
  - "SFC Rendering CDD"
  - "SFC Modernization Requirements"
document_type: "Capability Requirements / CDD"
status: "Approved Requirements Baseline"
version: "1.0"
date: "2026-09-03"
sponsor: "Project Sponsor / Owner"
review_authority: "Sponsor / Owner"
baseline_status: "Approved 2026-09-03"
tags:
  - starfleet-command
  - sfc
  - rendering
  - modernization
  - requirements
  - cdd
  - kpp
  - ksa
  - trl
---

# Starfleet Command Rendering Modernization Capability Development Document

> [!info] Document Status
> **v1.0 — Approved Requirements Baseline**
>
> **Baseline approval:** Approved 2026-09-03
> **Review authority:** Sponsor / Owner
> **Primary framework:** [[Capability Requirements Template]]
>
> This document defines the capability requirements for substantially modernizing the tactical 3D presentation of *Star Trek: Starfleet Command* (SFC) while preserving the gameplay experience that makes the original game worth playing.

# 1. Executive Summary

The project will provide a visually modernized SFC tactical experience on a supported modern PC configuration while preserving normal gameplay behavior, tactical information, controls, mission progression, and save/campaign use.

The operational deficiency is visual rather than mechanical: SFC remains desirable to play, but its legacy rendering and presentation substantially limit the experience on modern hardware. Existing compatibility methods can make the game run; the desired capability is a meaningful remaster-level improvement to tactical presentation rather than compatibility alone.

Initial Threshold scope remains bounded to one supported SFC baseline and one supported target PC configuration, but modernization coverage includes all technically applicable 3D-rendered states of that baseline. Broad game-version compatibility, comprehensive 2D UI remastering, specific rendering technologies, public packaging, and content expansion are outside Threshold.

Four KPPs define success:

1. **Visual Modernization Effectiveness** — the improvement must be substantial and readily apparent.
2. **Gameplay Fidelity** — modernization must preserve SFC gameplay and trustworthy tactical information.
3. **Real-Time Rendering Performance** — the result must remain playable in representative tactical combat.
4. **Tactical Modernization Coverage** — modernization must survive complete tactical play rather than isolated screenshots.

Major technical uncertainty remains in legacy render access, modern enhancement of incomplete legacy render data, and correct composition of modernized 3D output with SFC's tactical UI. Because those uncertainties can prevent Threshold capability, the project uses CTE/TRL-style maturity gates.

# 2. Operational Need

## 2.1 Current State


SFC is a legacy PC title whose graphics pipeline, native rendering assumptions, and visual assets predate modern rendering techniques.

Modern systems can run the game through compatibility settings, community patches, display fixes, or rendering translation approaches, but successful execution alone does not provide a materially modern visual experience.

The tactical game remains compelling enough to justify preservation. The presentation does not currently match the desired experience on modern hardware.

## 2.2 Capability Gap


The current capability gap is:

> SFC can remain playable on modern hardware, but the tactical 3D presentation remains constrained by the legacy rendering pipeline and does not provide a substantial modernized visual experience.

A solution that only raises resolution, sharpens the image, adjusts color, or provides a modest cosmetic improvement does not close this gap.

## 2.3 Need Statement


> **Provide an SFC player with the capability to conduct normal tactical gameplay using a substantially modernized 3D presentation on a supported modern PC, while preserving gameplay behavior, tactical information, user control, and mission/campaign continuity.**

## 2.4 Desired Effect


After successful delivery, the user can launch the supported SFC configuration and play representative tactical missions normally while observing a clearly modernized presentation of ships, lighting, materials, weapon effects, explosions, environmental objects, and scene composition.

The user should experience a modernized SFC session rather than operate a rendering demonstration.

# 3. Intended User Experience / Mission Thread

1. User launches the supported SFC configuration.
2. The modernization capability initializes through the approved launch workflow.
3. User loads a representative mission or campaign battle normally.
4. Tactical 3D presentation is modernized while gameplay-critical overlays remain usable.
5. User rotates and zooms the camera, selects targets, maneuvers, fires weapons, observes shields/damage, and responds to combat normally.
6. Modernization remains active across representative ships, weapon effects, explosions, environmental objects, and scene complexity.
7. User completes the mission without disabling the modernization capability.
8. Mission completion, save state, or campaign state behaves consistently with the supported SFC baseline.
9. The accepted configuration can be identified and reproduced for continued use.

# 4. Scope

## 4.1 Threshold Scope


The first usable capability shall cover:

- one designated SFC executable/build and configuration baseline;
- one designated target PC configuration;
- all technically applicable 3D-rendered states of the supported baseline, exercised through representative tactical gameplay and other required coverage fixtures;
- representative player and non-player ships;
- normal camera movement and zoom;
- representative weapon fire;
- shield and damage-state presentation required for play;
- explosions and destruction events;
- representative planets or large environmental objects where applicable;
- starfield/background presentation;
- tactical HUD, cursor, targeting, and other information required to complete the Threshold mission set;
- complete representative tactical missions;
- normal save/load or campaign-state transitions exercised by the Threshold verification set.

## 4.2 Objective Scope


Objective capability provides stronger visual quality, improved performance, and a more mature deployment experience. Broader 3D-rendered-state coverage is not deferred to Objective because the sponsor directed it into KPP-4 Threshold.

## 4.3 Explicit Non-Goals


The following shall not block Threshold completion unless later traced to an approved need, validated deficiency, or explicit sponsor decision:

- comprehensive remastering of 2D menus or interface art;
- replacement of every ship model;
- replacement of every texture;
- audio replacement;
- gameplay-mechanics changes;
- mission-script changes;
- new ships, factions, weapons, missions, or campaigns;
- support for every SFC release, patch, community edition, or total conversion;
- support for every third-party mod;
- mandatory 4K output;
- mandatory HDR;
- mandatory frame generation;
- any named neural-rendering technology;
- any named upscaler;
- any named rendering wrapper;
- ray tracing as a required implementation;
- public distribution packaging;
- automatic installer/updater infrastructure;
- AI-generated replacement game content.

# 5. Requirements Governance

## 5.1 Anti-Requirements-Creep Rule

> [!danger] Baseline Rule
> A requirement, KSA, feature, integration, safeguard, compatibility target, or refinement shall not enter the active Threshold baseline merely because it appears useful, elegant, safer, interesting, or technically achievable.

Every proposed Threshold addition shall trace to at least one of:

1. a defined operational need;
2. an approved KPP Threshold;
3. a demonstrated deficiency against an approved requirement;
4. an explicit sponsor capability decision.

A proposal without traceability remains outside the active baseline.

## 5.2 Threshold Discipline

**Threshold defines done. Objective defines better.**

Once every approved KPP Threshold has been demonstrated in the supported operational configuration, unmet Objective values do not delay Initial Usable Capability unless explicitly promoted.

## 5.3 No Silent Threshold Growth

Any proposal to increase an approved Threshold shall record:

| Field | Required Entry |
|---|---|
| Existing Threshold | Current approved value |
| Proposed Threshold | New proposed value |
| Operational deficiency | Why the current value is inadequate |
| Expected impact | Cost, schedule, complexity, or risk effect |
| Authority | Sponsor approval |

## 5.4 Solution Neutrality

Rendering wrappers, graphics APIs, neural models, reconstruction techniques, shader systems, injectors, replacement assets, and vendor-specific features are implementation choices unless evidence demonstrates that one is necessary to satisfy an approved capability.

## 5.5 Evidence Before Mitigation

For non-catastrophic technical concerns:

1. identify the affected approved requirement;
2. reproduce or observe the deficiency;
3. determine whether Threshold is materially violated;
4. apply the narrowest correction that restores compliance;
5. verify that the correction does not materially degrade another KPP.

# 6. KPP Summary

| ID | KPP | Threshold Summary | Objective Summary | Current Status |
|---|---|---|---|---|
| KPP-1 | Visual Modernization Effectiveness | ≥80% of frozen visual evaluation cases score Substantial or better; median ≥Substantial; zero Critical Visual Regressions | ≥95% score Substantial or better; ≥50% score Remaster-Level; median Remaster-Level | Not assessed |
| KPP-2 | Gameplay Fidelity | 100% of Critical Gameplay Fidelity cases pass, with no known modernization-induced gameplay divergence or false tactical-state event across the complete maintained regression suite and normal sponsor operational play | No separate Objective; the sponsor-selected performance is the binding Threshold | Not assessed |
| KPP-3 | Real-Time Rendering Performance | 95th-percentile tactical frame time ≤33.3 ms; no sustained modernization-induced control-blocking stall or resource-exhaustion collapse | 95th-percentile frame time ≤16.7 ms where engine behavior permits, or ≤5% degradation from the validated practical ceiling | Not assessed |
| KPP-4 | Tactical Modernization Coverage | Modernization operates consistently across all technically applicable 3D-rendered states of the supported baseline without scene-specific user intervention or manual reconfiguration | No separate Objective; the sponsor-selected coverage is the binding Threshold | Not assessed |

# 7. Key Performance Parameters

## KPP-1 — Visual Modernization Effectiveness


### Capability

Provide a substantial, repeatable improvement in SFC tactical 3D presentation that is immediately distinguishable from simple resolution scaling, sharpening, or minor post-processing.

### Measures

#### MOP/MOE 1-A — Visual Modernization Score

A frozen Visual Modernization Evaluation Set (VMES) shall be scored using the following rubric:

- **0 — No Useful Modernization / Regression:** no meaningful improvement, or the result is materially worse.
- **1 — Minor Modernization:** visible improvement dominated by scaling, sharpening, color adjustment, or isolated detail enhancement.
- **2 — Substantial Modernization:** clear improvement beyond simple scaling/post-processing, with meaningful improvement in at least two defined visual dimensions and no material gameplay/readability regression.
- **3 — Remaster-Level Modernization:** broad modernized presentation with strong improvement across at least three defined visual dimensions and no material gameplay/readability regression.

Relevant visual dimensions include:

- material/shading appearance;
- lighting and local contrast;
- image reconstruction/detail;
- silhouettes and edge quality;
- weapon/effect presentation;
- environmental/background presentation;
- temporal stability during motion;
- overall scene cohesion.

#### MOP/MOE 1-B — Critical Visual Regression Count

A Critical Visual Regression is any modernization-caused error that:

- hides or materially misrepresents gameplay-critical information;
- prevents identification or tracking of a required target;
- makes required HUD/cursor information unusable;
- creates persistent false gameplay-state cues;
- corrupts a required scene class sufficiently that modernization must be disabled to continue.

### Threshold (T)

Using a frozen VMES containing at least 12 representative scenes or clips:

- at least **80%** of evaluated cases shall score **2 or greater**;
- the median modernization score shall be **2 or greater**;
- **zero** Critical Visual Regressions may occur.

### Objective (O)

Using the frozen VMES:

- at least **95%** of evaluated cases score **2 or greater**;
- at least **50%** score **3**;
- the median score is **3**;
- zero Critical Visual Regressions occur.

### Rationale

The project exists to create a substantial visual improvement. A pipeline that works technically but produces only modest cosmetic improvement does not satisfy the operational need.

### Verification

Sponsor/User Evaluation using matched baseline-versus-modernized captures and short clips from the frozen VMES.

### Current Assessment

**Not assessed.** No formal VMES or verified modernization build exists yet.

---

## KPP-2 — Gameplay Fidelity


### Capability

Preserve SFC gameplay behavior and trustworthy tactical information while modernization is active.

### Measures

#### MOP/MOE 2-A — Critical Gameplay Fidelity Pass Rate

Percentage of Critical Gameplay Fidelity cases that produce the expected functional outcome with modernization active.

Critical cases shall include, at minimum:

- game launch and mission entry;
- tactical camera control;
- ship selection and targeting;
- tactical cursor interaction;
- movement and maneuvering controls;
- weapon activation and visible weapon-state feedback;
- shield and damage-state feedback required for play;
- tactical UI interaction;
- mission completion;
- save/load or campaign-state transitions exercised by the Threshold mission set.

#### MOP/MOE 2-B — False Tactical State Events

Count of modernization-induced visual events that a reasonable player could interpret as authoritative tactical state when the underlying game state does not contain that event.

### Threshold (T)

- **100%** of Critical Gameplay Fidelity cases shall pass.
- No known modernization-induced gameplay divergence or false tactical-state event shall exist across the complete maintained regression suite and normal sponsor operational play of the supported baseline.

### Objective (O)

No separate Objective value is specified. The sponsor determined that the former Objective fidelity statement is necessary for useful capability and directed it to become the binding Threshold.

### Rationale

The modernization is only useful if SFC remains trustworthy as SFC. Incorrect tactical information or altered gameplay defeats the purpose of the project.

### Verification

Paired modernization-disabled and modernization-enabled regression testing, with deterministic comparison where practical and functional-outcome comparison where exact replay is unavailable.

### Current Assessment

**Not assessed.** No modernization-enabled regression baseline has been established.

---

## KPP-3 — Real-Time Rendering Performance


### Capability

Maintain adequate real-time tactical responsiveness while visual modernization is active.

### Measures

#### MOP 3-A — 95th-Percentile Tactical Frame Time

95th-percentile frame time measured during the frozen performance test sequence.

#### MOP 3-B — Control-Blocking Stall Events

Count of sustained modernization-induced stalls that prevent normal tactical control or targeting.

#### MOP 3-C — Resource-Exhaustion Failure

Occurrence of sustained graphics-memory or system-memory exhaustion that causes unrecoverable performance collapse or mission failure.

### Threshold (T)

On the designated Threshold system and render configuration:

- 95th-percentile tactical frame time shall be **33.3 ms or less**;
- **zero** control-blocking stall events may occur;
- **zero** resource-exhaustion failures may occur.

### Objective (O)

On the designated Threshold system:

- 95th-percentile tactical frame time is **16.7 ms or less** where SFC engine behavior permits 60 FPS operation; or
- where the engine imposes a lower practical ceiling, modernization remains within **5%** of the validated practical baseline ceiling without material frame-pacing degradation.

### Rationale

A visually impressive result that interferes with tactical control is not operationally useful.

### Verification

Frame-time and memory telemetry during repeatable low-complexity, representative-combat, and high-representative-complexity tactical sequences.

### Current Assessment

**Not assessed.** Baseline performance capture and modernization telemetry are pending.

---

## KPP-4 — Tactical Modernization Coverage


### Capability

Provide useful modernization through complete tactical gameplay rather than isolated scenes or screenshots.

### Measures

#### MOP/MOE 4-A — Threshold Scene-Class Coverage

The Threshold mission set shall exercise:

- player and non-player ships;
- normal camera rotation, movement, and zoom;
- representative beam/phaser-style weapon fire where available;
- representative projectile/torpedo-style weapon fire where available;
- shield effects;
- explosions/destruction events;
- a planet or equivalent large environmental object where available;
- starfield/background presentation;
- target changes;
- tactical HUD and cursor presentation.

#### MOP/MOE 4-B — Complete Mission Modernization Continuity

Percentage of complete Threshold missions completed without manually disabling modernization because of rendering failure or scene incompatibility.

### Threshold (T)

- modernization shall operate consistently across all technically applicable 3D-rendered states of the supported SFC baseline;
- **100%** of formal Threshold mission runs shall complete without requiring the user to disable modernization to continue; and
- no covered 3D-rendered state shall require scene-specific user intervention or manual reconfiguration.

### Objective (O)

No separate Objective coverage value is specified. The sponsor determined that the former Objective coverage is necessary for useful capability and directed it to become the binding Threshold.

### Rationale

A successful screenshot or narrow proof of concept does not provide the intended capability. The modernization must survive actual SFC play.

### Verification

Complete mission demonstration using a frozen coverage checklist tied to the VMES and gameplay regression set.

### Current Assessment

**Not assessed.** Threshold mission fixtures and the inventory of technically applicable 3D-rendered states are not yet frozen.

# 8. Key System Attributes

## KSA-1 — Operational Stability


**Threshold:** Three consecutive representative tactical missions complete without a modernization-induced unrecoverable crash, render-pipeline failure requiring game restart, or permanent corruption of the active session.

**Objective:** Ten consecutive representative gameplay sessions complete without a modernization-induced unrecoverable failure.

**Supports:** KPP-2, KPP-3, KPP-4

**Verification:** Repeated operational mission test in the supported environment.

---

## KSA-2 — Tactical UI and Information Integrity


**Threshold:** All HUD, cursor, targeting, ship-status, weapon-status, shield-status, and other 2D information required to complete the Threshold mission set remain legible and functionally interpretable with modernization active.

**Objective:** All supported SFC interface elements maintain correct compositing, scale, aspect, cursor behavior, and readability across the supported display configurations.

**Supports:** KPP-1, KPP-2, KPP-4

**Verification:** UI inspection checklist plus complete Threshold mission demonstration.

---

## KSA-3 — Deployment Reproducibility


**Threshold:** The accepted modernization configuration can be recreated from the designated supported SFC baseline using maintained instructions and an identified set of required dependencies without interactive debugging or source-code modification.

**Objective:** The accepted configuration can be installed, selected, disabled, restored, and updated through a packaged or automated workflow while preserving SFC game data and saves.

**Supports:** KPP-2, KPP-4

**Verification:** Clean-baseline deployment demonstration and dependency/configuration inspection.

# 9. Derived Baseline Requirements

| ID | Requirement | Trace |
|---|---|---|
| REQ-BAS-001 | Formal verification shall identify the supported SFC executable/build, patch/configuration state, and gameplay-affecting mods. | KPP-2, KPP-4 |
| REQ-BAS-002 | Formal visual comparison shall use representative baseline captures made with modernization disabled. | KPP-1 |
| REQ-BAS-003 | Every formal verification result shall identify the game baseline, modernization build/configuration, external runtime components, driver version, and test fixture. | KPP-1, KPP-2, KPP-3, KPP-4 |
| REQ-REN-001 | The modernization capability shall obtain sufficient access to the SFC render output or render pipeline to satisfy KPP-1 and KPP-4. | KPP-1, KPP-4 |
| REQ-REN-002 | Rendering modernization shall not intentionally modify SFC rules, mission logic, campaign logic, ship statistics, weapon statistics, or save-state semantics. | KPP-2 |
| REQ-REN-003 | The development configuration shall provide a repeatable method to enable and disable modernization for verification. | KPP-1, KPP-2, KPP-3 |
| REQ-REN-004 | The rendering chain shall preserve correct presentation of gameplay-critical 3D content and required 2D tactical overlays. | KPP-2, KPP-4, KSA-2 |
| REQ-REN-005 | The Threshold tactical view shall not exhibit unacceptable stretching, clipping, or loss of gameplay-critical screen area. | KPP-1, KSA-2 |
| REQ-VIS-001 | Modernization shall preserve clear identification of ships, targets, weapon fire, shield activity, destruction events, and gameplay-relevant spatial relationships. | KPP-1, KPP-2 |
| REQ-VIS-002 | Modernization shall not create persistent false gameplay-state cues. | KPP-2 |
| REQ-VIS-003 | Modernization shall not introduce persistent flicker, smearing, ghosting, or reconstruction instability that prevents normal tactical interpretation. | KPP-1, KPP-2 |
| REQ-VIS-004 | Normal camera angle, zoom, target, combat-effect, and covered 3D-rendered-state changes shall not require manual modernization reconfiguration during Threshold operation. | KPP-4 |
| REQ-VIS-005 | The project shall maintain a frozen inventory of technically applicable 3D-rendered states in the supported SFC baseline and shall verify modernization coverage for every inventoried state. | KPP-4 |
| REQ-GAME-001 | Modernization shall preserve required tactical controls and cursor interactions exercised by the Critical Gameplay Fidelity set. | KPP-2 |
| REQ-GAME-002 | Modernization shall not require conversion of SFC save or campaign data for rendering purposes. | KPP-2 |
| REQ-GAME-003 | Removing or disabling modernization shall not require conversion of SFC game-state files to restore baseline operation. | KPP-2, KSA-3 |
| REQ-PERF-001 | The development configuration shall support repeatable frame-time capture sufficient to verify KPP-3. | KPP-3 |
| REQ-PERF-002 | Formal performance tests shall record graphics-memory and system-memory behavior sufficient to identify resource-exhaustion failures. | KPP-3 |
| REQ-STAB-001 | Where evidence permits, verification failures shall distinguish baseline SFC failure from modernization-induced failure. | KSA-1 |
| REQ-DEP-001 | The project shall maintain instructions sufficient to recreate the verified Threshold configuration from the supported SFC baseline. | KSA-3 |
| REQ-DEP-002 | The project shall maintain an inventory of required external binaries, runtimes, models, patches, and configuration files used by the accepted build. | KSA-3 |

# 10. Verification Cross-Reference

| Requirement / Attribute | Verification Method | Primary Evidence Needed |
|---|---|---|
| KPP-1 | Sponsor/User Evaluation + Analysis | Frozen VMES, matched baseline/modernized captures, score sheet |
| KPP-2 | Test + Demonstration | Complete maintained gameplay-fidelity regression results, paired baseline comparison, and normal sponsor operational-use record |
| KPP-3 | Test + Analysis | Frame-time and memory telemetry |
| KPP-4 | Demonstration + Inspection | Complete mission recordings/logs and frozen 3D-rendered-state inventory with coverage results |
| KSA-1 | Test | Repeated mission-run record |
| KSA-2 | Inspection + Demonstration | UI checklist and mission evidence |
| KSA-3 | Demonstration + Inspection | Clean deployment record and dependency/configuration manifest |
| REQ-BAS-* | Inspection | Test configuration records |
| REQ-REN-* | Test + Demonstration | Render-path and A/B verification evidence |
| REQ-VIS-* | Evaluation + Demonstration + Inspection | VMES, mission evidence, and frozen 3D-rendered-state inventory |
| REQ-GAME-* | Test | Gameplay fidelity regression results |
| REQ-PERF-* | Analysis | Telemetry artifacts |
| REQ-STAB-* | Analysis | Failure attribution record |
| REQ-DEP-* | Inspection + Demonstration | Deployment documentation and manifests |

## 10.1 Verification Fixtures

### Visual Modernization Evaluation Set (VMES)

The initial VMES should contain at least 12 representative scenes or short clips covering:

- close ship view;
- medium ship view;
- distant ship view;
- multiple ships;
- camera movement;
- beam/phaser-style weapon fire where available;
- projectile/torpedo-style weapon fire where available;
- shields;
- explosion/destruction event;
- planet or equivalent large environmental object;
- starfield/background;
- busy tactical scene with HUD visible.

The VMES is a verification fixture. Its individual cases are not separate Threshold requirements.

### Critical Gameplay Fidelity Set

A complete maintained regression suite of supported gameplay-fidelity cases and expected functional outcomes shall be used for KPP-2 verification. The suite shall include the defined critical cases and evidence from normal sponsor operational play.

Where exact deterministic replay is unavailable, verification shall compare functional state and behavior rather than requiring identical random outcomes.

### 3D-Rendered-State Coverage Inventory

Before formal KPP-4 verification, the project shall freeze an inventory of all technically applicable 3D-rendered states in the supported baseline. Each inventoried state shall have at least one verification fixture or operational demonstration showing that modernization remains active without scene-specific user intervention or manual reconfiguration.

The inventory is a verification fixture used to bound the phrase “all technically applicable”; it does not add another game baseline, 2D UI remastering, or content expansion to Threshold.

### Performance Test Set

Performance testing shall include:

- low scene complexity;
- ordinary tactical combat;
- high representative Threshold scene complexity.

Formal results should record:

- average frame time;
- 95th-percentile frame time;
- observed major stalls;
- graphics-memory usage;
- system-memory usage where relevant;
- baseline comparison;
- modernization configuration.

# 11. Capability Maturation

The project uses formalized CTE/TRL-style gates because major technical uncertainty remains in the rendering path and can prevent Threshold capability.

## 11.1 Development Increments

### Increment 0 — Technical Risk Reduction

**Purpose:** Prove the highest-risk enabling rendering functions and establish repeatable evidence capture.

**Target maturity:** TRL 2–3

No KPP Threshold is required during Increment 0.

### Increment 1 — Threshold Capability

**Purpose:** Integrate the viable technical path and satisfy every approved KPP Threshold in the target operational configuration.

**Target maturity:** TRL 4–7

Passing TRL 7 and the Initial Capability Exit Criteria constitutes the first usable success.

### Increment 2 — Objective Expansion

**Purpose:** Pursue approved Objective visual quality and performance, plus improved operational convenience. KPP-4 coverage is already a Threshold obligation and is not deferred to this increment.

**Target maturity:** TRL 8–9 where continued maturation provides useful evidence.

### Future Increments

Future compatibility, packaging, additional game variants, UI remastering, content replacement, and other modernization ideas require traceability to an approved need or explicit sponsor prioritization.

## 11.2 Critical Technology Elements

### CTE-1 — Legacy Render Access

Ability to obtain a stable render path from the supported SFC baseline that exposes sufficient scene output for the required modernization.

### CTE-2 — Modern Rendering Enhancement

Ability to apply a modernization technique that can reach KPP-1 quality while remaining within KPP-3 performance limits.

### CTE-3 — Scene/UI Composition and Temporal Integrity

Ability to modernize tactical 3D output while preserving gameplay-critical overlays, tactical readability, and temporal stability during normal SFC motion and combat.

Overall technical maturity shall not be assessed above the least-mature CTE required for Threshold capability.

## 11.3 TRL Gate Rules

Each gate shall record:

- purpose;
- entry criteria;
- exit criteria;
- required evidence;
- known deficiencies;
- disposition: **PASS**, **CONDITIONAL**, or **FAIL**;
- requirement impacts, if any.

A failed gate may invalidate a technical approach. It does not automatically add, relax, or increase a capability requirement.

### TRL 2 — Credible Technical Concept Formulated

**Purpose:** Establish at least one credible end-to-end modernization concept.

**Entry Criteria:**
- capability need and KPP draft exist;
- supported SFC baseline is identified sufficiently for experimentation.

**Exit Criteria:**
- at least one candidate end-to-end render path is documented;
- required intercept points and external components are identified;
- major unknowns are recorded for each CTE;
- a test method exists for first-frame modernization proof.

**Required Evidence:**
- architecture concept note;
- CTE register;
- initial risk register;
- TRL 3 proof plan.

---

### TRL 3 — Critical Function Proof of Concept

**Purpose:** Prove that SFC rendering can be accessed and materially altered.

**Entry Criteria:**
- TRL 2 passed or conditionally passed;
- candidate render path is runnable.

**Exit Criteria:**
- SFC reaches tactical 3D gameplay through the candidate path;
- at least one live tactical scene is visibly altered beyond the native/compatibility baseline;
- the game remains interactively controllable for at least 10 continuous minutes;
- matched baseline/modified evidence is captured;
- basic frame-time measurement is available;
- no observed failure invalidates the concept outright.

**Required Evidence:**
- baseline/modified capture pair;
- short gameplay capture;
- configuration manifest;
- performance sample;
- deficiency list.

KPP-1 Threshold is not required at TRL 3.

---

### TRL 4 — Integrated Component Validation

**Purpose:** Demonstrate that the principal CTEs operate together in one development configuration.

**Entry Criteria:**
- TRL 3 proof exists;
- each Threshold-critical CTE has an identified implementation path.

**Exit Criteria:**
- CTE-1 through CTE-3 operate together in one repeatable configuration;
- a representative tactical mission operates for at least 30 continuous minutes;
- at least three VMES scene classes show repeatable modernization;
- required HUD and cursor functions remain usable during the demonstrated sequence;
- repeatable frame-time and memory telemetry are captured.

**Required Evidence:**
- integrated-build manifest;
- run log;
- VMES samples;
- telemetry;
- updated risk/deficiency register.

---

### TRL 5 — Validation in Relevant Environment

**Purpose:** Demonstrate credible convergence toward Threshold on the designated target environment.

**Entry Criteria:**
- TRL 4 passed;
- designated target PC and supported SFC baseline are available.

**Exit Criteria:**
- one complete representative tactical mission completes;
- at least **60%** of current VMES cases score **2 or greater**;
- no Critical Visual Regression prevents mission completion;
- 95th-percentile tactical frame time is **50 ms or less** during the gate test;
- the Critical Gameplay Fidelity smoke-test subset passes;
- no modernization-induced unrecoverable failure occurs during the gate mission.

**Required Evidence:**
- mission recording/log;
- VMES score sheet;
- telemetry;
- smoke-test results;
- open-deficiency list.

TRL 5 values are maturation criteria and do not replace KPP Thresholds.

---

### TRL 6 — Threshold-Capable Integrated Prototype

**Purpose:** Demonstrate an integrated prototype capable of meeting the approved Threshold capability.

**Entry Criteria:**
- TRL 5 passed;
- formal Threshold verification fixtures are frozen.

**Exit Criteria:**
- all four KPP Thresholds pass formal verification;
- every Threshold-critical CTE is assessed at TRL 6 or higher;
- no unresolved defect is known to invalidate a KPP Threshold.

**Required Evidence:**
- KPP verification report;
- VMES results;
- gameplay regression results;
- performance telemetry;
- complete mission coverage evidence;
- configuration/dependency manifest.

---

### TRL 7 — Demonstration Under Normal Operational Use

**Purpose:** Demonstrate that the Threshold-capable prototype remains useful during normal sponsor play.

**Entry Criteria:**
- TRL 6 passed;
- sponsor-operable configuration exists.

**Exit Criteria:**
- all KPP Thresholds remain satisfied;
- all KSA Thresholds pass or receive explicit sponsor waiver;
- at least three complete representative tactical missions are played under normal user conditions;
- no modernization-induced unrecoverable failure occurs during those missions;
- no unresolved defect invalidates a KPP Threshold;
- sponsor accepts the build as usable for ordinary SFC play.

**Required Evidence:**
- operational play log;
- defect log;
- sponsor acceptance note;
- verified configuration snapshot.

Passing TRL 7 constitutes Initial Usable Capability when Section 17 is also satisfied.

---

### TRL 8 — Stable Qualified / Reproducible Build

**Purpose:** Produce a stable, reproducible, qualified modernization build.

**Entry Criteria:**
- Initial Usable Capability has been accepted.

**Exit Criteria:**
- clean-baseline deployment is reproduced using maintained documentation;
- formal KPP/KSA verification passes on the release-candidate configuration;
- dependency/configuration versions are frozen;
- known limitations are documented.

**Required Evidence:**
- release-candidate verification report;
- clean deployment record;
- configuration manifest;
- known-limitations record.

---

### TRL 9 — Sustained Normal Use

**Purpose:** Demonstrate maturity through sustained ordinary play.

**Entry Criteria:**
- TRL 8 passed;
- qualified configuration is in routine sponsor use.

**Exit Criteria:**
- at least **10 hours** of normal sponsor gameplay across at least **five** sessions;
- no modernization-induced Critical Gameplay Fidelity failure;
- no modernization-induced unrecoverable failure that invalidates normal use;
- recurring visual/performance deficiencies are recorded and dispositioned.

**Required Evidence:**
- operational-use log;
- defect history;
- final maturity assessment.

TRL 9 does not require achievement of KPP Objective values.

# 12. Risks and Deficiencies

### RISK-1 — Legacy Graphics Translation / Interception

**Risk:** The legacy SFC render path may expose behavior that modern interception or translation approaches reproduce imperfectly.

**Potential Effect:** Missing or corrupted geometry/effects, cursor problems, aspect errors, crashes, or blocked modernization.

**Affected Requirement:** KPP-1, KPP-2, KPP-4; CTE-1

**Mitigation / Evidence Plan:** Evaluate candidate render-access approaches during TRL 2–4 and reject approaches that cannot converge on Threshold.

---

### RISK-2 — Missing Modern Render Data

**Risk:** Candidate modern rendering techniques may expect depth, motion vectors, material information, exposure data, or other inputs SFC does not provide.

**Potential Effect:** Weak visual improvement, temporal instability, or inability to use a preferred modernization method.

**Affected Requirement:** KPP-1, KPP-3; CTE-2

**Mitigation / Evidence Plan:** Use TRL 3–5 experiments to determine the minimum viable input set and substitute the modernization method if necessary.

---

### RISK-3 — False Detail / Temporal Artifacts

**Risk:** Aggressive reconstruction may invent, smear, or destabilize tactical visual information.

**Potential Effect:** Attractive still images but unreliable tactical interpretation.

**Affected Requirement:** KPP-1, KPP-2; REQ-VIS-002, REQ-VIS-003

**Mitigation / Evidence Plan:** Use moving VMES clips and gameplay regression evidence before adding mitigation beyond observed failures.

---

### RISK-4 — Performance / Memory Cost

**Risk:** Advanced rendering may impose disproportionate GPU, VRAM, CPU, or system-memory cost.

**Potential Effect:** Poor frame pacing, control interruption, resource exhaustion, or mission failure.

**Affected Requirement:** KPP-3

**Mitigation / Evidence Plan:** Begin telemetry at TRL 3 and use KPP-3 as the governing acceptance boundary.

---

### RISK-5 — Legacy Timing Coupling

**Risk:** SFC gameplay or input behavior may react poorly to unusually high, low, or inconsistent frame rates.

**Potential Effect:** Gameplay divergence despite successful rendering.

**Affected Requirement:** KPP-2, KPP-3

**Mitigation / Evidence Plan:** Evaluate gameplay fidelity whenever frame behavior materially changes.

---

### RISK-6 — 2D / 3D Composition

**Risk:** SFC may combine tactical UI/cursor elements with the 3D render path in ways that complicate scene modernization.

**Potential Effect:** Modernized 3D imagery with unusable or transformed tactical UI.

**Affected Requirement:** KPP-2, KPP-4, KSA-2; CTE-3

**Mitigation / Evidence Plan:** Require UI/composition evidence by TRL 4 before broad visual polish work.

---

### RISK-7 — External Component Availability

**Risk:** A successful prototype may depend on unstable, version-specific, proprietary, discontinued, or non-redistributable components.

**Potential Effect:** The accepted build becomes difficult to reproduce or maintain.

**Affected Requirement:** KSA-3

**Mitigation / Evidence Plan:** Maintain dependency/configuration manifests and preserve architecture substitutability where practical.

# 13. Design Constraints and Program Decisions

> [!warning]
> The items in this section are current program or implementation decisions. They are not capstone KPPs and may change if another approach better satisfies the approved requirements.

## 13.1 Current Program Baseline

- Initial verification hardware is the sponsor's Windows 11 PC with:
  - Intel Core i7-13700KF;
  - NVIDIA GeForce RTX 4070 Ti 12 GB;
  - 32 GB system RAM.
- Exact SFC executable/build and patch/configuration baseline remain to be frozen.
- Tactical 3D presentation is the initial modernization focus.
- Current candidate solution space may include legacy render translation, graphics interception, modern upscaling/reconstruction, neural rendering, shader/post-processing, replacement visual assets, or combinations thereof.
- No named rendering technology is required by the capability baseline.

## 13.2 Distribution Boundary

🛡️ Public project packaging shall not depend on redistributing proprietary or leaked third-party binaries without appropriate redistribution rights. Private technical experiments may reference separately obtained user-supplied components without making those binaries part of the distributable project baseline.

# 14. Decision Log

| ID | Decision | Basis | Requirement Impact |
|---|---|---|---|
| DEC-001 | End state is an Obsidian-compatible Markdown capability requirements document. | Sponsor direction | Governance |
| DEC-002 | KPP Threshold/Objectives define critical capability performance. | Sponsor direction / project reference | All KPPs |
| DEC-003 | Requirements creep is explicitly controlled. | Sponsor direction / project reference | Governance |
| DEC-004 | Formal CTE/TRL-style gates are used because rendering feasibility contains genuine technical uncertainty. | Sponsor direction | Section 11 |
| DEC-005 | The capability must substantially modernize SFC tactical visuals while preserving SFC gameplay. | Operational need | KPP-1, KPP-2 |
| DEC-006 | Minor cosmetic uplift is insufficient. | Sponsor intent | KPP-1 |
| DEC-007 | All technically applicable 3D-rendered states are within Threshold KPP-4 coverage; tactical 3D presentation remains the initial development focus. | Scope control + sponsor direction | KPP-4 |
| DEC-008 | Named wrappers, APIs, neural renderers, upscalers, and similar technologies remain candidate solutions. | Solution neutrality | Section 13 |
| DEC-009 | Development may iterate among technical approaches without sponsor intervention unless a requirement, scope, risk-acceptance, or major trade decision changes. | Development efficiency | Governance |
| DEC-010 | Objective performance does not block Threshold completion. | Threshold discipline | All KPPs |
| DEC-011 | Sponsor PC is the initial verification hardware baseline. | Current program decision | Verification environment |
| DEC-012 | Approve the v1.0 requirements baseline and use the former KPP-2 and KPP-4 Objective performance as binding Threshold, without redundant Objectives. | Sponsor review and explicit sponsor direction. | KPP-2, KPP-4; Sections 4, 6, 7, 9, 10, 14, 16–19 |

# 15. Open Sponsor Decisions

The following are intentionally deferred until evidence or a later gate requires resolution:

- exact SFC SKU/executable/build and patch/configuration state for Threshold verification;
- target display resolution and refresh rate;
- whether an existing HD/community compatibility configuration becomes part of the frozen baseline;
- which mission or missions form the Threshold gameplay fixture;
- which ship set or modded visual assets, if any, are included in the Threshold fixture;
- whether any 2D UI modernization becomes an Objective requirement;
- whether public distribution becomes a future program objective;
- whether SFC2, SFC2 Community Edition, SFC3, or other variants become future increments.

These decisions do not block TRL 2 concept work unless a specific gate entry criterion requires one to be resolved.

# 16. Requirements Traceability

## 16.1 Lightweight Traceability Summary

| Capability Need | Primary Requirement |
|---|---|
| Produce a substantial visual modernization | KPP-1 |
| Preserve gameplay and trustworthy tactical information | KPP-2 |
| Maintain real-time tactical usability | KPP-3 |
| Modernize all technically applicable 3D-rendered states rather than isolated scenes | KPP-4 |
| Avoid fragile one-off operation | KSA-1 |
| Preserve usable tactical UI | KSA-2 |
| Reproduce the accepted configuration | KSA-3 |
| Mature legacy render access | CTE-1 |
| Mature the visual enhancement path | CTE-2 |
| Mature correct 3D/UI composition and temporal behavior | CTE-3 |

## 16.2 Derived Requirement Trace Matrix

| Requirement | KPP-1 | KPP-2 | KPP-3 | KPP-4 | KSA-1 | KSA-2 | KSA-3 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| REQ-BAS-001 |  | X |  | X |  |  |  |
| REQ-BAS-002 | X |  |  |  |  |  |  |
| REQ-BAS-003 | X | X | X | X |  |  |  |
| REQ-REN-001 | X |  |  | X |  |  |  |
| REQ-REN-002 |  | X |  |  |  |  |  |
| REQ-REN-003 | X | X | X |  |  |  |  |
| REQ-REN-004 |  | X |  | X |  | X |  |
| REQ-REN-005 | X |  |  |  |  | X |  |
| REQ-VIS-001 | X | X |  |  |  |  |  |
| REQ-VIS-002 |  | X |  |  |  |  |  |
| REQ-VIS-003 | X | X |  |  |  |  |  |
| REQ-VIS-004 |  |  |  | X |  |  |  |
| REQ-VIS-005 |  |  |  | X |  |  |  |
| REQ-GAME-001 |  | X |  |  |  |  |  |
| REQ-GAME-002 |  | X |  |  |  |  |  |
| REQ-GAME-003 |  | X |  |  |  |  | X |
| REQ-PERF-001 |  |  | X |  |  |  |  |
| REQ-PERF-002 |  |  | X |  |  |  |  |
| REQ-STAB-001 |  |  |  |  | X |  |  |
| REQ-DEP-001 |  |  |  |  |  |  | X |
| REQ-DEP-002 |  |  |  |  |  |  | X |

# 17. Initial Capability Exit Criteria

> [!success] Definition of Done
> SFC Rendering Modernization reaches Initial Usable Capability when all approved KPP Thresholds have been demonstrated in the target operational configuration and no known unresolved defect invalidates those demonstrations.

Initial Usable Capability requires:

- every KPP Threshold passes its formal verification event;
- Threshold KSAs pass or receive explicit sponsor waiver;
- TRL 7 passes;
- the capability succeeds during representative sponsor operation;
- no unresolved defect invalidates a KPP Threshold;
- the accepted game/modernization configuration can be identified and reproduced sufficiently for continued use.

The following do not block Threshold completion unless explicitly promoted:

- unmet KPP or KSA Objective values where a separate Objective remains specified;
- minor cosmetic imperfections below Critical Visual Regression level;
- broader game-version compatibility;
- additional platform support;
- 2D interface remastering;
- easier packaging or updater work beyond KSA-3 Threshold;
- newer models, frameworks, wrappers, or vendor features;
- unapproved visual enhancement ideas.

The project may stop after Initial Usable Capability and still be considered successful.

# 18. Requirements Change Log

| Version | Date | Change | Authority |
|---|---|---|---|
| 0.1 | 2026-09-01 | Initial SFC rendering modernization CDD draft. | Draft |
| 0.2 | 2026-09-01 | Rewritten to conform to the project Capability Requirements Reference: added Executive Summary, formal Operational Need, standard KPP format with measures/current assessment, KPP summary, traced derived-requirement table, verification cross-reference, separated design decisions, tailored CTE/TRL model, explicit Definition of Done, and review/baseline structure. | Draft for Sponsor Review |
| 0.3 | 2026-09-03 | Added mobile-friendly sponsor review controls for second-level scope sections, KPPs, and KSAs. No requirement, Threshold, Objective, TRL gate, or scope value changed. | Draft for Sponsor Review |
| 0.4 | 2026-09-03 | Moved temporary mobile review controls from the end of the document to the applicable X.X, KPP, and KSA headings. No requirement, Threshold, Objective, or TRL value changed. | Draft for Sponsor Review |
| 1.0 | 2026-09-03 | Approved the requirements baseline; promoted the former KPP-2 and KPP-4 Objective performance to binding Threshold; added the minimum coverage-inventory requirement and verification updates needed to bound KPP-4; removed redundant Objectives and temporary review controls. | Sponsor approval |

# 19. Sponsor Review Notes

## 19.1 Baseline Review Disposition — 2026-09-03

| Review Item | Disposition |
|---|---|
| Sections 2.1–2.4 and 4.1–4.3 | Approved as written, subject to the KPP-4 coverage consistency update. |
| KPP-1 and KPP-3 | Approved as written. |
| KPP-2 | Approved with directed change: use the former Objective fidelity statement as the binding Threshold and do not retain a redundant Objective. |
| KPP-4 | Approved with directed change: use the former Objective 3D-state coverage as the binding Threshold and do not retain a redundant Objective. |
| KSA-1 through KSA-3 | Approved as written. |
| Baseline | Approved as v1.0 on 2026-09-03. |

After baseline approval, KPP/KSA identifiers remain stable and retired IDs are not reused.

# 20. Source / Evidence Basis

## 20.1 Governing Requirements Framework

This document is structured in accordance with the project's **Capability Requirements Reference v1.0**.

The governing principles applied here are:

- capability need precedes solution selection;
- KPPs are few, capstone, measurable, and independently verifiable;
- Threshold defines the minimum capability worth declaring usable;
- Objective represents meaningful additional utility without blocking Threshold completion;
- KSAs support capability without automatically becoming capstone requirements;
- derived requirements trace upward and do not independently expand scope;
- verification evidence is defined with the requirement;
- TRL/CTE gates are used only because genuine technical uncertainty exists;
- architecture and implementation decisions remain separate from the requirements baseline;
- evidence precedes mitigation for non-catastrophic hypothetical failures;
- successful Threshold verification establishes a legitimate stopping point.

## 20.2 Project Evidence Basis

This draft incorporates sponsor intent established during prior SFC discussions:

- preserve SFC gameplay;
- pursue substantial rather than minor visual improvement;
- use Codex/development automation to iterate on implementation approaches;
- use KPP Threshold/Objectives as the capability framework;
- use TRL gates because legacy-render modernization contains technical uncertainty;
- keep the eventual requirements artifact Obsidian-compatible.

Detailed technical feasibility remains to be established through the CTE/TRL evidence process. No candidate implementation technology is treated as proven by this document.
