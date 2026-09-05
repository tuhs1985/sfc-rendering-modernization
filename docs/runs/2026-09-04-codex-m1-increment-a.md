# Codex Run Record — M1 Increment A Neutral Pass-Through

## Run identity

- Run ID: `CODEX-20260904-M1-A-001`
- Date: 2026-09-04
- Active milestone/task: M1 / TRL 4, Increment A semantic integration sub-gate
- Starting commit: `51ab372 Approve M1 TRL 4 integrated component validation plan`
- Starting Git state after Phase 0: clean
- Current result: implementation and offline validation complete; runtime evidence
  pending prepared sponsor gameplay

## Sponsor authority and milestone boundary

The sponsor approved execution of the neutral pass-through as the first M1
increment. Success satisfies only the semantic integration sub-gate and leaves M1
in **CONTINUES**. No CDD requirement was changed or waived. Formal TRL 4 PASS,
CTE-2/CTE-3 modernization, three-VMES evidence, technology selection, and the
next increment remain outside this run.

## Technical question and hypothesis

Question: can a reversible project-controlled component observe the confirmed
`tEntityShip -> t3DVisual_Model -> tModel0` seam, correlate it to `0x006AB410`,
and return control to the original renderer without changing normal operation?

Hypothesis: exact-byte x86 trampolines with full EFLAGS/general/FX state
preservation can record a bounded per-process identity contract and be removed
with all original bytes restored.

## Starting evidence

- M0 / TRL 3 PASS report and semantic ownership/function maps.
- Exact retained dumpbin disassembly for the six chosen hook points.
- M0-RT-003 runtime register/pointer sequence and two-owner correlations.
- M0 shared bounded-capture and elevation-policy implementation.
- Approved M1 plan and sponsor disposition at commit `51ab372`.

## Work packages and decisions

### M1-01 — Development manifest

Created `docs/m1/m1-a-development-manifest.md`. It records client hashes,
launcher version evidence, host OS/GPU/driver, toolchain, dependencies, fixture
IDs, limits, and the outstanding exact launcher path. The client was rehashed:

- MD5 `2BE8F713F81B1C68D50EAD6088C32886`;
- SHA-256 `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.

### M1-02 — Integration contract and ABI adjudication

Created `docs/m1/m1-a-integration-contract.md`. Selected six exact observation
points: scene begin, ship entry, visual entry, Model0 entry, visual exit, and
`0x006AB410`. The visual-exit hook bounds mainline owner-to-geometry association
instead of assigning later generic geometry to the last observed ship.

Codex adjudicated the x86 ABI from exact prologues/epilogue, callee cleanup,
static parent/call relations, and M0 runtime registers. Hook thunks preserve and
restore EFLAGS, all general registers, and FXSAVE x87/MMX/XMM state. These remain
**STRONG HYPOTHESIS** until live non-interference is demonstrated.

### M1-03 — Neutral component

Implemented:

- `tools/m1_component/m1_contract.h`;
- `tools/m1_component/m1_component.cpp` and `.def`;
- `tools/m1_component/m1_controller.cpp`;
- build and elevated-parent runner scripts;
- bounded evidence analyzer;
- C++ contract and Python analyzer tests;
- M1-A-RT-001 probe definition and shared runbook.

The mechanism is an architecture-neutral observation component, not a renderer.
It validates exact live bytes, installs in-memory trampolines transactionally,
uses fixed event/owner/thread storage, performs no file I/O in hooks, stops detail
at 120 frames or 10,000 events, continues counters after saturation, restores
all hooks, and leaves the inert DLL mapped until process exit to avoid an unload
race. The on-disk client is never patched.

## Tools and material commands

- `rg`, PowerShell `Get-Content`, and retained dumpbin disassembly for targeted
  static evidence review.
- `Get-FileHash -Algorithm MD5/SHA256` for client preservation.
- Windows/CIM inventory for OS and graphics-driver manifest fields.
- `pwsh -NoProfile -File tools/m1_component/build_m1_component.ps1`.
- `python -m unittest tests.test_analyze_m1_log tests.test_analyze_probe_log -v`.
- PowerShell parser API for runner syntax.
- `dumpbin /headers`, `/imports`, `/exports`, and generated-object `/disasm`.

## Offline evidence and validation

- MSVC x86 builds passed with `/W4 /WX /O2 /MT`; DLL also uses `/arch:SSE2`.
- Pure C++ tests confirmed stable active identity, two-owner distinction,
  retirement/new epoch on raw pointer reuse, owner overflow fail-open behavior,
  and fixed event-buffer saturation.
- Python M1 analyzer synthetic test and existing M0 analyzer regression passed.
- DLL exports `M1StartW` and `M1Stop` confirmed.
- PE headers confirm x86/PE32 DLL; static runtime leaves Windows system imports.
- Generated hook disassembly confirms six occurrences each of
  `pushfd/pushad/fxsave/fxrstor/popad/popfd`; `cld` executes only inside saved
  EFLAGS scope.
- PowerShell runner parsed without errors.
- Generated `.dll`, `.exe`, `.obj`, `.lib`, and `.exp` outputs are ignored under
  `artifacts/m1`; three initial root `.obj` files were removed as disposable,
  reproducible build products after the build script was corrected.
- No runtime interception has yet occurred in this record.

## Probe and capture definition

- Runtime probe: `M1-A-RT-001`.
- Runbook: `docs/m1/probes/m1-a-component-runbook.md`.
- Gate: first exact-vtable ship/visual event.
- Detail limits: 120 frames, 10,000 events, eight owners.
- File limits: 16 MiB warning, 32 MiB hard stop.
- Runtime bounds: 300 seconds for enabled one-owner proof; 600-second launcher
  and normal-exit waits.
- Raw output: ignored `artifacts/m1/runs/<timestamp>-<mode>/`.
- Multi-gigabyte warning and safe procedure are documented; unrestricted traces
  are prohibited.

## Current confidence and blockers

- Component code/build/bounds and exact original bytes: **CONFIRMED** offline.
- ABI preservation sequence: **CONFIRMED** in generated code;
  live compatibility remains **STRONG HYPOTHESIS**.
- Neutral live pass-through, downstream correlation, visible non-interference,
  and controlled removal: **SPECULATIVE** until M1-A-RT-001.
- Blocker: none technical; prepared disabled/enabled gameplay runs require the
  sponsor to enter and operate the minimal tactical fixture.

## Repository state

- Phase-0 planning baseline committed as `51ab372`.
- All Increment-A implementation, documentation, tests, and this run record are
  unstaged and uncommitted for sponsor review.
- No implementation commit is authorized by the current instruction.
