# Codex run — C-01 corner/transform static qualification

- Run ID/date: `2026-10-11-m1-c01-corner-transform`, America/New_York.
- Authority: sponsor "continue, assume its the monitor... troubleshoot later".
  Parked display issue by sponsor decision; exact cause stays unconfirmed.
  Continued bounded C-01 analysis, no new effect/runtime/C-02 or commit.
- Starting HEADfee152f, three modified docs/four untracked runtime/preflight/
  baseline records/evidence preserved. Sources: latest HANDOFF, C-01 plan and
  analysis/runbook, approved M1 sponsor disposition, M0 ownership map, exact
  client/dumpbin, existing component input contract and latest shading evidence.
- Fuel Guard recent trusted hook verified/direct denied; no daemon spawned.
  Tools: bundled Python3.12.14/existing extract_disasm_ranges.py, PowerShell
  read-only PE words/hash, rg, bundled Git. No helper or game/process probe.
- Material commands: `python tools/recon/extract_disasm_ranges.py
  artifacts/pre-m0/raw/StarFleetOP-2.5.6.4.dumpbin-disasm.txt <ranges>`.
  Inclusive windows:004162B9..00416360,00416360..00416435,
  0041645F..0041651A,00416528..00416562,0042E4B2..0042E585,
  006ABF80..006ABFC0,006ABFC0..006AC100,006AC190..006AC210,
  006AC279..006AC2A0,006AC2A0..006AC350,006AC3D6..006AC435,
  006A9790..006A98B0,006A98B0..006A98ED,006A9A0E..006A9A79,
  0069CA30..0069CAC0,0069CAC5..0069CB13,0069CB10..0069CB62,
  0069CBC0..0069CCBC,0069BAF0..0069BBDF,006AA550..006AA705,
  0069F190..0069F1D0. Immediate data/transform callees only; no broad enumeration.
  Output to tool response only, selected windows finite/no new raw dump.
- Read-only PE word lookup: DOS e_lfanew, PE32 imagebase, section raw RVA mapping;
  addresses007B8E30→006AA550 and007B8DE0→0069F190. QueryC69FF0 correctly
  refused as not file-backed: its live value is not assumed zero. rg initially
  used nonexistent tools/pre_m0/docs/pre-m0 names; actual tool tools/recon found
  via rg --files, no directories created or project cleaned to accommodate it.
- Findings/classification in [qualification note](../m1/m1-c01-corner-transform-qualification.md).
  CONFIRMED static:28-byte corner records, separate indexed positions, vector+4,
  68-byte supplied-transform copy, scalar affine/transpose arithmetic and light
  remapping. Model-local normal/lighting-space interpretation STRONG HYPOTHESIS;
  active dispatch/orthonormality/sharing/runtime numeric changes unresolved.
- Rejected unsupported mapping source entry==one normal, shared-state writes,
  guessed matrix convention/inverse, adding redundant lighting or hot geometry
  hooks. Proposal is small read-only existing-Model0 snapshots, not an armed probe.
- Modified tooling: verify_m1_c01_shading_bytes.py extended from15 to29 exact
  corner/transform/vtable anchors. Executed against exact client, all matched;
  reference SHA256 unchanged4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
- Validation: all16 Python regressions pass with process-local TEMP/TMP at
  artifacts/m1/test-temp; static verifier pass; doc links/whitespace/status.
  No native component change so no native rebuild. No bulk capture/cleanup.
- Files created: qualification note, this record. Modified: byte verifier,
  HANDOFF, C-01 plan/current analysis status, risk sponsor disposition and C01
  offline runbook supplemental evidence. Earlier proof/historical text retained.
- Result M1 CONTINUES, live input qualification needed; neither failure nor
  modernization success. No active runtime/session assumed, no sponsor gameplay
  needed until prepared probe. Final changes unstaged/uncommitted, HEAD unchanged.
- Exact next action: prepare/offline-validate the bounded read-only corner/
  transform snapshot probe at existing Model0 seam; no C-02 implementation.
