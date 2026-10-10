# Codex Run Record — M1 bounded visual-control analysis

- Run ID/date: `CODEX-20260919-M1-VISUAL-CONTROL-ANALYSIS`, 2026-09-19.
- Gate/question: M1 CONTINUES after semantic-integration sub-gate PASS. Can one
  safe, reversible, unmistakable, owner-specific visual modification be
  implemented from the proven seam with current evidence?
- Starting baseline: commit `b115260`; only `docs/HANDOFF.md` was untracked.
  It was preserved. The current sponsor prompt authorizes this bounded visual
  proof investigation; it does not authorize formal TRL 4 PASS.
- Sources reviewed: `docs/HANDOFF.md`, approved M1 plan, latest M1 stutter run,
  risk register, integration contract, M0 semantic ownership/function maps,
  `tools/m1_component/m1_component.cpp`, and exact-build retained dumpbin
  disassembly under ignored `artifacts/pre-m0/raw/`.
- Tools/parameters: `git status`, `rg` on exact addresses/fields, read-only
  PowerShell PE-section/vtable lookup for manager vtable `0x007B8D4C` slots
  `+0x48/+0x50/+0x58/+0x140`, `Get-FileHash -Algorithm SHA256`, process and
  temporary-loader checks. No helper, gameplay, injection, hook, or capture.
- Result: semantic targeting remains **CONFIRMED**. The manager mode path
  `tModel0+0x1C → 0x006A96E0 → manager+0x1ECC → polygon flag handling` is a
  **STRONG HYPOTHESIS** visual control, but its visible effect and owner-local
  restoration are unproved. Material/tint field interpretation, transform
  copy lifetime, and LOD visual distinctness are unresolved. The selected
  disposition is **ADDITIONAL BOUNDED ANALYSIS REQUIRED**; no visual component
  was implemented or enabled. Exact evidence and next experiment are in
  `docs/m1/m1-b-visual-control-analysis.md`.
- Rejected for this run: generic `0x006AB410` mutation (downstream and hot),
  persistent mesh/model mutation (possible sharing), speculative color field,
  and unverified transform alteration. Geometry diagnostic hook remains off.
- Files created: this record and `docs/m1/m1-b-visual-control-analysis.md`.
  `docs/HANDOFF.md` receives a new checkpoint; no source or original asset is
  changed.
- Runtime/debug state: no `StarFleetOP`, `SFCLauncher`, or `m1_controller`
  process observed; no game-directory `winmm.dll` or `m1-component.ini` found.
  No probe is armed. Client SHA-256 remains
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
- Validation: read-only source/disassembly cross-check and original client
  hash passed. All handoff Markdown links resolved; the three changed files
  passed a trailing-whitespace check; `git diff --check` passed (noting it does
  not inspect untracked files). Analyzer unit tests passed 3/3 with the bundled
  Python runtime. No build or gameplay test was run because no code changed.
- Final repository: `?? docs/HANDOFF.md`,
  `?? docs/m1/m1-b-visual-control-analysis.md`, and
  `?? docs/runs/2026-09-19-codex-m1-visual-control-analysis.md`.
  No files staged or committed; baseline remains `b115260`.
