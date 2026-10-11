# Codex run — bounded shading-off diagnostic preparation and approved commit

- Run ID/date: `2026-10-11-m1-shading-off-preparation`, America/New_York.
- Milestone: M1 CONTINUES, C-01 diagnostic/control qualification. Semantic
  integration sub-gate PASS retained; no CTE2/CTE3 or formal TRL4 claim.
- Sponsor authority: "approve and commit" after the owner-specific shading-off
  contract/build proposal. Prepared/validated diagnostic and committed reviewed
  pending related work; no SFC runtime launch/injection authorized or performed.
- Starting HEAD `1dca4526169501ef731e30c8cb6ae8150eeaa643`; HANDOFF modified and
  ten untracked CDD-reconciliation/C01 planning, harness, analysis/test/run files,
  nothing staged. No unexpected unrelated edits; preserved prior work/history.
- Question: can we responsibly prepare suppression of the two exact primary
  lighting selectors, identify the target, keep the off comparison observable
  for45s independent of log saturation, and guarantee copy-only/restoration?
- Sources reviewed: HANDOFF instructions, approved M1 plan, latest visual tint
  runtime/evidence and M1-B-RT-001, C01 exact-build shading analysis/runbook,
  four pending planning/analysis records, existing semantic contract, recorder,
  runner/bootstrap/build and source-copy tests. CDD external read-only source/hash
  retained; no requirement or approved baseline-plan edit.
- Fuel Guard attach verified trusted global hook; direct daemon access sandbox-
  denied. No sandbox daemon spawned, no guessed session. No helper or subagents.

## Engineering decisions and configuration

- Existing semantic hooks/thunks/ABI unchanged; no fresh calling-convention guess.
  Model0 mainline owner/thread and original source argument2 are retained. Source
  copy preserves all bytes except bits0x06 in **referenced** source DWORD flags.
  RGB-only magenta cue uses the prior mechanism, not a new render hook.
- Inspect manager+1ECC read only: mode3 already suppresses both lighting bits.
  Already-unlit/mode3 sources are no-op; eligible bits still do not prove active
  light slots/visible effect. Secondary source/00509843 remain untouched.
- Fixed gate sequence: 5s normal, 3s cue, 5s normal, 45s off, restore through75s.
  First validated mainline owner epoch, not assumed player; no retarget after
  retirement. Guarded reads, existing pointer release, active-scope drainage and
  hook restoration retained. DLL mapped until normal exit, no force-unload.
- Probe `M1-C-RT-001`: 75s after auto gate, gate wait600s, geometry hookoff,
  StopOnBurst0; semantic detail120 epochs/10,000 events/eight owners,16/32MiB
  limits. Fixed96 samples one per second/phase transition plus first eligible
  source; phase counters after saturation. Original/control flow never waits on
  disk I/O in a hook. Summary analyzer input safeguard256KiB.
- Entry always rebuilds before launcher, PS5 shim→bundled PS7, elevated token
  inherited/refused if absent. No new UAC or persistent execution-policy change.
- Deliberately rejected: shared manager mode mutation, guessed normal/matrix
  layouts, redundant added lighting, hot geometry hook, asset/backend/UI work,
  automatic runtime execution or treating this control diagnostic as enhancement.

## Tools, commands and validation

- VS2026 18.7.3, x86 MSVC14.51.36231, C++17 `/W4 /WX /O2 /MT /arch:SSE2`;
  bundled PowerShell7.6.5, Python3.12.14, bundled Git, Windows PowerShell5.1.
- Process-local TEMP/TMP = `C:\Project\SFC-Modernize Engine\artifacts\m1\test-temp`.
  `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File tools/m1_component/build_m1_component.ps1`:
  final build passed; contract, tint source copy, production tint lifecycle,
  production shading-off and WINMM forwarding groups passed. Export checks passed.
- `python.exe -m unittest discover -s tests -p 'test_*.py' -v`: final16 tests pass.
  One intermediate invocation omitted TEMP/TMP override and seven fixture tests
  failed sandbox-temp writes with PermissionError; no semantic/assertion failure.
  Corrected process-local environment and reran successfully, no security changes.
- Windows PowerShell production shim fixture executed for original tint and new
  shading entry; both pass without launching SFC. All15 PowerShell source/module/
  test files parsed; elevation-policy and image-query/exit regressions pass.
- `python tools/m1_component/verify_m1_c01_shading_bytes.py "Game Assets/StarFleetOP.exe"`:
  all15 exact PE prefixes match, read-only. No additional broad RE.
- `artifacts/m1/bin/m1_shading_off_component_tests.exe "C:\Project\SFC-Modernize Engine\artifacts\m1\test-temp\shading-off-synthetic"`, then
  `python tools/m1_component/analyze_m1_shading_off.py artifacts/m1/test-temp/shading-off-synthetic`:
  actual production serializer/parser coherent,8 samples, phase3 three eligible
  substitutions/releases; no issues. **Synthetic**, not actual 59s gameplay.
  CSV354 bytes, summary3,847, component log389, analysis893; small ignored output
  retained, no compression necessary, no material deletion. Native tests also
  exercise fixed sample capacity, saturated detail, late-window activation,
  other-owner/exception isolation, no-op, renderer replacement, stop drainage,
  bad reads, retired epochs and conflicting configuration.
- Markdown links checked (51 docs before this record), Git diff whitespace and
  ignored artifact checks pass; final links/status/staged diff rechecked at commit.
- Client reference and installed SHA256 both
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
  Launcher SHA256 `84D3A5F89A922C4BEE6815CF0614538C3565C4BDB7DB3AA187C552CB727EF890`.
  Approved CDD SHA256 `BF5384D2586601AAA28DB36970937A3B40F598E12002B3450BF2E7D9562FA352`.
  All unchanged; no originals/configuration assets written.
- Final prepared DLL SHA256
  `EC491C3C5BE67D8834FFFB40E94126281A350F449BF8133E4D1C5D1E188E4502`;
  controller `1A9FE6892A5F6EC14AA249798DC682BDEB446668EEFBFBBA249819E47DE47A38`.
  Link timestamps may change rebuild hashes; future runtime metadata freezes actual
  component/controller hashes. Binaries ignored, rebuild source authoritative.

## Exact committed files

Modified tracked in this run: `docs/HANDOFF.md`, `tests/README.md`,
`tests/m1_visual_tint_tests.cpp`, `tests/test_m1_visual_entry_runtime.ps1`,
`tools/m1_component/build_m1_component.ps1`, `tools/m1_component/m1_component.cpp`,
`tools/m1_component/m1_visual_tint.h`, `tools/m1_component/run_m1_increment_a.ps1`,
`tools/m1_component/start_m1_enabled_session.ps1`.

Created this run: `docs/m1/probes/M1-C-RT-001.md`, this record,
`tests/m1_shading_off_component_tests.cpp`, `tests/test_analyze_m1_shading_off.py`,
`tools/m1_component/analyze_m1_shading_off.py`,
`tools/m1_component/start_m1_shading_off_session.ps1`.

Previously untracked reviewed work included:
`docs/m1/m1-c-cte23-increment-plan.md` and
`docs/m1/m1-c01-existing-shading-analysis.md` (also updated with latest disposition),
`docs/m1/probes/M1-C01-OFFLINE-001.md`,
`docs/runs/2026-10-10-codex-m1-cdd-reconciliation.md`,
`docs/runs/2026-10-10-codex-m1-cte23-planning.md`,
`docs/runs/2026-10-11-codex-m1-c01-existing-shading.md`,
`docs/runs/2026-10-11-codex-m1-c01-harness-preparation.md`,
`tests/test_prepare_m1_c01_packet.py`,
`tools/m1_component/prepare_m1_c01_packet.py`,
`tools/m1_component/verify_m1_c01_shading_bytes.py`.

## Result and repository closure

**READY FOR SPONSOR RUNTIME TEST; M1 CONTINUES.** Offline mechanics CONFIRMED;
live eligibility, visible lighting change, candidate runtime overhead and
normal gameplay remain unconfirmed/STRONG HYPOTHESIS. Numeric normal/transform
space remains unqualified. No runtime process or persistent admin/server session.

Only these25 reviewed files staged/committed under user authority:
`Prepare bounded owner-specific shading-off diagnostic`, parent `1dca452`.
The commit containing this record identifies the final revision; post-commit
Git status verified clean. Raw/disassembly/binaries/test-temp remain ignored.
Historical records' old uncommitted/parked statements remain preserved as history.

Exact next action: obtain sponsor runtime readiness/authorization for the prepared
M1-C-RT-001 two-ship comparison; do not automatically execute from this approval.
