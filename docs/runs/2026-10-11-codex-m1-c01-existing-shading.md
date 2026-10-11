# Codex run — C-01 existing shading investigation

- Run ID/date: `2026-10-11-m1-c01-existing-shading`, America/New_York.
- Authority: sponsor resumed with "start digging" after suggesting temporary
  shading-off. Executed offline qualification/analysis only; no live intervention.
- Starting HEAD `1dca4526169501ef731e30c8cb6ae8150eeaa643`; HANDOFF modification
  plus seven untracked C01/planning files preserved, nothing staged.
- Question: can the existing shading contribution be bypassed owner-locally
  without altering RGB/textures or shared lighting manager state?
- Sources: latest handoff/C01 draft/runbook, RGB analysis, M0 ownership map,
  existing component/contract, retained exact-build dumpbin, reference client,
  historical M1-B-RT-001 semantic CSV. CDD constraints unchanged.
- Tools: Fuel Guard hook attach (direct denied), bundled Python 3.12.14,
  existing extract_disasm_ranges.py, PowerShell hash/ZIP and bundled Git.
- Commands: `python -m unittest tests.test_prepare_m1_c01_packet -v` (five pass);
  prepared packet command exactly in M1-C01-OFFLINE-001 executed; temp environment
  process-local artifacts/m1/test-temp. Packet 49,473 bytes, SHA-256
  `5391285C0A33A6610CAD575738F4355FBF63199E1A5E97D507E3F4ADA7E2CBD5`.
- Narrow extraction windows: 006ABFC0..006AC400, 0042E4B2..0042E650,
  006A9790..006A9A90, 0069B250..0069B2B0, 006ABF80..006ABFC0,
  006AC400..006AC59B, ship handoff 004162E0..00416350, wrapper
  006AC5A0..006AC6A0, deferred mode read 006AC8C0..006AC990. Output reviewed
  in tool response only; curated addresses retained, no new bulk dump created.
- New reusable static helper `verify_m1_c01_shading_bytes.py`: 15 exact instruction
  prefixes mapped through PE sections against frozen reference SHA-256; executed
  twice with all matches. This corroborates instructions, not dynamic semantics.
- Findings: source DWORD flags bit4 selects polygon response, bit2 selects vertex
  response; both use 006A9790 and multiply source RGB. Clearing both avoids mode4
  promotion and direct source RGB survives. Dot-product math and source cache
  reset traced. Instruction relationships CONFIRMED static; lighting/normal
  interpretation and visible off effect STRONG HYPOTHESIS pending runtime.
- [Curated analysis](../m1/m1-c01-existing-shading-analysis.md) contains exact
  VAs/offsets and proposed flags & ~0x06 in owner-local copy. Shared mode rejected;
  source sharing does not prevent all-referenced-entry suppression but remains
  a constraint on future per-surface enhancement. No claim all shading disappears.
- Unresolved: live entries' active bits, baked texture shading, secondary passes,
  numeric normal/transform space, candidate-specific preservation/runtime proof.
  Next proposed test identifies target and gives 45 seconds, with originals/masked
  flag counts and matching source releases. No component/runner changed or armed.
- Files created: analysis, static byte helper, this run record. Modified: HANDOFF,
  C01 runbook execution/supplement and Increment C resumption disposition.
- Raw handling: packet compressed to ignored
  artifacts/m1/archives/M1-C01-OFFLINE-001-20261011.zip, 8,860 bytes;
  SHA-256 `EBC6D2B9F06668D358DDD3EE992734259303C5E6DAE26F8A47C45A82800C140B`.
  Archived JSON hash independently matches raw; small raw retained. No deletion.
- Validation: five packet tests, actual packet preparation, actual byte verification,
  JSON archive hash, doc links/whitespace and Git check. Client/reference never
  written; matching reference SHA required by both offline tools. No gameplay,
  injection, UAC, shading change, helper or formal TRL4 success claim.
- Result: **M1 CONTINUES**, credible bounded shading-off candidate. Exact next
  action: approve diagnostic contract/build preparation, not a new enhancement.
- Final repository: HEAD unchanged, HANDOFF modified and ten untracked curated
  files, all unstaged/uncommitted; generated packet/archive ignored. No active
  runtime/tool server/session. Previous parked restriction superseded only for
  the expressly resumed offline investigation; no automatic runtime authority.
