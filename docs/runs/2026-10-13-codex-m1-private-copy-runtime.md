# Codex run — 2026-10-13 RT-007 runtime adjudication

- ID: 2026-10-13-codex-m1-private-copy-runtime. Active M1/C-01; M1 CONTINUES.
- Question: did the one-use neutral private polygon copy reach the original
  renderer under the selected semantic owner while gameplay remained normal?
- Baseline: HEAD fee152f, existing dirty work preserved (72 pending paths before
  this documentation). No staged changes; no project implementation changes in
  this adjudication. Read current HANDOFF, RT-007 definition and preparation run.
- Source/tooling: component 0.10, existing PowerShell runner/controller, Python
  3.12.14 analyzers, PowerShell/.NET ZIP/SHA256, Git. Native/ABI offline tests and
  40 Python tests were completed in the linked preparation record; not falsely
  claimed as rerun here. Fuel Guard attach already performed; no daemon spawned.
- Runtime entry: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File
  "C:\Project\SFC-Modernize Engine\tools\m1_component\start_m1_private_copy_session.ps1"`.
  [RT-007](../m1/probes/M1-C01-RT-007.md) specifies cue, gate, privileges, bounds
  and cleanup. Run 20261013-223631-enabled, 90 seconds, 20-second setup,
  one substitution, 20,512-byte pinned slot; geometry/tint/shading off.
- Reproduction analysis: Python tools/m1_component/analyze_m1_private_copy.py,
  analyze_m1_wrapper.py, analyze_m1_rejections.py and
  analyze_m1_corner_snapshot.py, each with the run directory as argument.
  All rerun successfully; analysis issue lists empty. Independently checked
  installed client SHA256, process/proxy absence, summary and exit records.
- Preservation: compressed all 18 raw files, verified each ZIP entry SHA256
  against its source. Raw 1,136,545 bytes; ZIP 134,641 bytes; raw retained ignored.
  Archive path, hash, runtime binaries and client hashes in
  [evidence](../m1/evidence/M1-C01-RT-007-20261013-private-copy.md).
- Result CONFIRMED: one application, two preparation receipts, one parent return,
  intact payload, no copy failure. Sponsor reports expected gameplay. Hooks
  restored, normal process exit; pin ends at exit, not hook stop. No reusable-slot
  lifetime claim. New excluded caller 00413B2D remains unclassified; finite bypass
  without selected-owner match, not evidence of a failed selected handoff.
- Rejected overclaims: this is not replacement of the renderer, complete model
  copying, continuous substitution, early-free proof, or formal TRL 4 PASS.
- Files changed here: docs/HANDOFF.md, RT-007 probe status; created this record
  and RT-007 runtime evidence. No source/configuration changes or cleanup/deletion.
- Final validation: local documentation links and Git whitespace/staged-state
  checks; existing pending work retained. Nothing staged or committed. No active
  game/controller/session assumed. Exact next action: sponsor review and approval
  of a bounded repeat-use/lifetime proof before further implementation.
