# C-01 — existing shading control analysis, 2026-10-11

## Result

**Current qualification update:** [runtime](evidence/M1-C-RT-001-20261011-shading-off.md)
corroborates vertex-light suppression and visible return. Subsequent
[corner/transform analysis](m1-c01-corner-transform-qualification.md) identifies
the narrower read-only proof needed before an enhancement. Earlier unexecuted/
unconfirmed statements below are pre-runtime history, not current status.

**Update 2026-10-11:** sponsor approved diagnostic contract/build preparation
and commit. [M1-C-RT-001](probes/M1-C-RT-001.md) implements a fixed magenta
identification cue followed by a 45-second owner-local lighting-bit mask.
Offline validation passes; gameplay is unexecuted. Read-only manager mode
`+0x1ECC` is sampled: mode 3 already suppresses these bits, so it is ineligible
for the off intervention. Source-bit eligibility does not prove lights contribute
visibly. The following result/proposal is the preserved pre-build analysis.

**M1 CONTINUES — credible owner-local shading-off candidate identified.**
No intervention implemented, game launched or new runtime probe run. Existing
shading participation on the selected live hull remains unconfirmed.

Sponsor authorized digging after suggesting shading-off rather than adding
redundant shading. This resumes offline harness execution and targeted analysis;
it does not authorize C-02 visual implementation or redefine modernization.

## Evidence and exact path

Five offline packet tests passed. Packet
`artifacts/m1/c01/20261011-input-packet.json`: 49,473 bytes, SHA-256
`5391285C0A33A6610CAD575738F4355FBF63199E1A5E97D507E3F4ADA7E2CBD5`.
Its output correctly remains INPUT_QUALIFICATION_PENDING. Historical owner
chains are context only; they do not expose current flags, normals or matrices.
Retained exact-build dumpbin instructions were traced within the proven primary
path and one immediate lighting callee; no broad caller/engine enumeration.

| Address / data | Static observation | Confidence |
| --- | --- | --- |
| `006AC02A..006AC03F` | Polygon +4 selects source entry with 36-byte stride. | CONFIRMED instruction relationship, prior runtime source control. |
| `006AC0E0` | Source entry +0 DWORD loaded as flags in ECX. | CONFIRMED static. |
| `006AC16C..006AC188` | Mode 3 clears 0x06; mode 4 promotes 0x04 only when 0x02 set. | CONFIRMED static. |
| `006AC18C/18F` | Bit 0x04 selects polygon response block; clearing it skips to 006AC27D. | CONFIRMED static branch. |
| `006AC1B4..006AC1D0` | Uses polygon +8 vector and first indexed position, calls 006A9790. | CONFIRMED static arguments; face-normal interpretation STRONG HYPOTHESIS. |
| `006AC255..006AC279` | Returned RGB response plus source +8 scalar multiplies source RGB. | CONFIRMED static arithmetic. |
| `006AC28B/006AC2F8` | Bit 0x02 selects per-vertex response; absence skips to 006AC3D6. | CONFIRMED static branch. |
| `006AC310..006AC32E` | Uses current vertex-list record +4 vector, indexed position and same callee. | CONFIRMED static; vertex-normal interpretation STRONG HYPOTHESIS. |
| `006AC3D6..006AC3E8` | With vertex-light bit absent, normalized source RGB is copied directly to prepared vertex +34/+38/+3C. | CONFIRMED static. |
| `006A9790..006A9A78` | Position/three-component vector response with light-slot iteration, dot products, scalar color contributions/clamps. | CONFIRMED arithmetic/calls; lighting interpretation STRONG HYPOTHESIS until live corroboration. |
| `0069B250..0069B268` | Three-component dot product. | CONFIRMED static math. |
| `006ABF9F..006ABFA9` | Prepared vertex flags cleared per Model0 source initialization. | CONFIRMED static; prior copy/restore runtime supports mainline isolation. |

`verify_m1_c01_shading_bytes.py` independently mapped VAs to PE file offsets
and matched 15 control/call/helper byte prefixes against the SHA-256-verified
reference executable. This corroborates disassembly fidelity, not a second
dynamic semantic proof. No function label alone is evidence.

## Proposed diagnostic intervention (not implemented)

Reuse the proven bounded source-copy/argument-substitution/release mechanism.
For the selected validated mainline owner only, change each referenced copy's
flag DWORD from `flags` to `flags & ~0x06`. Keep original RGB, source +8 scalar,
alpha/other flags, resource pointers, textures, vertices/indices and transforms
unchanged. Do not alter original source memory or shared manager mode/lights.

Clear **both** bits: clearing only vertex bit leaves polygon lighting; clearing
only polygon bit can be undone by mode-4 promotion of vertex lighting. With
both absent, neither multiplication block is taken in the inspected path.
The already-proven source pointer release bounds ownership; reuse its guarded
copy, active-scope drain and original-flow continuation, not a new hot hook.

This is disabling a specific primary-path lighting contribution, **not all
shading everywhere**. Texture-baked shading and separate damage/shield/effect
passes may remain. Model0 secondary source at 0042E60E is renderer-authored and
must remain intact; known return 00509843 remains untargeted. Clipping/culling,
geometry transformation and textures are not bypassed by this proposed mask.
Source-entry sharing does not block this all-referenced-entry control experiment;
it still matters for future geometry-dependent enhancement.

## What remains unresolved and how to discriminate it

1. Current target entries may already have 0x06 clear, or legacy lights may be
   inactive: no visible difference then does not disprove the semantic seam.
2. Baked texture shading may dominate appearance; a flatter/brighter hull is
   STRONG HYPOTHESIS, not promised. It may be subtle in a particular fixture.
3. Numeric normal/transform space remains unqualified; shading-off does not
   need to synthesize lighting, but does not solve future enhancement inputs.
4. Mainline copy safety was proven for RGB; flag mask still needs its own
   offline preservation tests and runtime targeting/restore corroboration.

Smallest next test design: log original/masked flags and count **referenced**
entries with actual lighting bits, selected owner/model/source and matching
releases. Require before/off/after evidence, no untargeted modifications.
No original lighting bits => classify target ineligible/no-op, not proof of
successful shading suppression. No normal recovery claims from this experiment.

Sponsor visibility requirement: identify the selected ship before the off window;
do not assume first owner equals player or reuse last run's enemy ordering.
Plan a 45-second off window with automatic restoration and a clear ready/exit
message; any target-identification cue/control must be documented and validated
before launch. The 45 seconds is an engineering observation window, not a CDD
criterion. Detail logging must not end the effect early. No runner is armed.

## Next action / maturity

Request approval to prepare the bounded owner-specific **shading-off diagnostic**
contract/build, with target identification and longer observation window.
It remains a critical-control experiment, not CTE-2 modernization or formal
TRL4 success. Do not build a redundant directional-lighting enhancement from
this static finding or broadly reverse-engineer the light manager.
