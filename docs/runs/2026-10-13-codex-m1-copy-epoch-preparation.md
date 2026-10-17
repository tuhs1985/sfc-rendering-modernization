# Codex run — 2026-10-13 fresh-epoch preparation

- ID2026-10-13-codex-m1-copy-epoch-preparation; active M1/C-01, sponsor "continue"
  after RT-008. Starting HEADfee152f /79 pending path entries, all unstaged.
  Prior source/evidence preserved; no cleanup/staging/commit authorized.
- Fuel Guard attach via recent trusted hook, direct sandbox connection denied;
  no daemon spawned. No helper/subagents. Read HANDOFF/operating convention, M1
  authority/current C-01 state, RT-008 run/evidence/probe and relevant owner table,
  wrapper/prep/parent paths, runner/analyzers/tests. No original artifacts modified.
- Question: can handoffs resume under an independently validated fresh owner epoch,
  without merging IDs or reusing old copies? Recorded
  [contract](../m1/m1-c01-fresh-epoch-copy-contract.md) **before implementation**.
  Evidence supports current vtables/link/table; no undocumented field/ABI inferred.
- Selected: same raw tuple as an experimental filter, explicit inactive predecessor
  and retirement record, fresh reads, >=3frames/250ms candidate, per-slot IDs and
  provenance; max2 requalifications/32 fresh slots, bank657,872bytes<=700KiB.
  Previous receipt/parent/rate and full-copy validation preserved; old slots remain
  pinned/immutable until process exit. No hook architecture/site or visual change.
- Rejected: merging same-address epochs, weakening retirement, relaxing old RT-008
  count acceptance, automatic retarget to another model/source, broad RE, recycling,
  full-rate copying, hot geometry and C-02 implementation. Live safety remains
  STRONG HYPOTHESIS pending RT-009; offline behavior is directly testable.

## Exact files changed this execution

- tools/m1_component/m1_component.cpp: component0.12, validated candidate contract,
  bounded retirement/dwell/current-epoch state, per-slot owner/provenance and
  receipt/parent accounting, prospective summary fields; existing thunks unchanged.
- tools/m1_component/run_m1_increment_a.ps1, start_m1_enabled_session.ps1,
  start_m1_corner_snapshot_session.ps1: explicit flag forwarding/INI/manifest,
  corrected prospective copy cue metadata and optional40s look-away cue.
- tools/m1_component/analyze_m1_private_copy.py: fresh-epoch evidence validation;
  analyze_m1_wrapper.py, analyze_m1_rejections.py, analyze_m1_corner_snapshot.py:
  RT-009 provenance/action labels, no reinterpretation of archived RT-008 results.
- tests/m1_corner_snapshot_tests.cpp: real synthetic ship/visual/model/table,
  live vtable/link rejection, production scene retirement, dwell/frame guards,
  independent IDs, immutable slots/receipt/return, two-transition ceiling and stop.
- tests/test_analyze_m1_private_copy.py and test_m1_corner_action_cues.ps1:
  qualified/fabricated identity evidence and third cue; old defaults still tested.
- Created tools/m1_component/start_m1_copy_epoch_session.ps1,
  tests/fixtures/m1_copy_epoch_unload.ini, contract/RT-009 definition/this record.
- Documentation updated: HANDOFF and current C-01 increment checkpoint. Older
  checkpoints/probe results preserved; no requirement or final renderer changes.

## Tools, commands and reproducibility

VS2026 18.7.3/MSVC14.51.36231 x86 C++17 /W4 /WX /O2 /MT /arch:SSE2,
bundled PS7.6.5/Python3.12.14, WindowsPS5 shim and existing elevation policy.
Set process-local TEMP/TMP to existing ignored absolute artifacts/m1/test-temp.
Material commands (no gameplay):

```text
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/m1_component/build_m1_component.ps1
python -m unittest discover -s tests -p test_*.py
artifacts/m1/bin/m1_corner_snapshot_tests.exe artifacts/m1/test-temp/fresh-epoch-good --epochs
artifacts/m1/bin/m1_corner_snapshot_tests.exe artifacts/m1/test-temp/fresh-epoch-default
artifacts/m1/bin/m1_corner_snapshot_tests.exe artifacts/m1/test-temp/fresh-epoch-failure --failure
python tools/m1_component/analyze_m1_private_copy.py artifacts/m1/test-temp/fresh-epoch-good/repeated-private-copy
pwsh -File tests/test_m1_corner_action_cues.ps1
pwsh -File tests/test_m1_private_copy_unload.ps1 -FixtureName m1_copy_epoch_unload.ini
pwsh -File tests/test_probe_elevation_policy.ps1
pwsh -File tests/test_m1_process_image_path.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/test_m1_visual_entry_runtime.ps1 -EntryName start_m1_corner_snapshot_session.ps1
python tools/m1_component/verify_m1_c01_shading_bytes.py "Game Assets/StarFleetOP.exe"
git diff --check
```

RT-009 definition documents exact launch, sponsor free-camera action,20s setup /
two-tone start /40s three-tone look-away,90s run/capture limits, expected output,
pin/unload/cleanup and analysis. No runtime launched. Tiny ignored fixture outputs
may remain; no new gameplay raw/archive or deleted data. Final results below.

## Final offline validation and checkpoint

- Full native build/required DLL/proxy/gate exports and six test groups pass.
  New `--epochs` production fixture:32 fresh slots, two independent new owner IDs,
  actual scene retirements, copied-pointer receipts and parent closures; original
  and earlier copied payloads unchanged. Invalid Model0/visual vtables and ship
  link, unqualified ID, insufficient frames/time and third qualification refused.
  Old default and malformed-copy fail-open fixtures still pass. No compiler/test
  corrections were necessary in this preparation.
- Actual synthetic M1Stop retains all used slots and writes19,593byte summary;
  bank657,872bytes. Qualification records atslots8 and16:1->2 at28,250ms after
  retirement28,000ms, and2->3 at36,500ms after retirement36,250ms; four distinct
  qualifying frames each. This is synthetic evidence, not live behavior.
  Private analyzer for new/default positive fixtures has empty issue lists;
  failed-copy fixture correctly reports incomplete/halted-copy evidence.
-47Python tests pass, including forged retirement/dwell/frame/provenance, merged
  ID, spurious transition and missing live transition rejection. Read-only call
  against archived RT-008 summary retains its original count-only incomplete
  decision, without modifying raw files or archive.
- Cue tests cover old phases,20s setup/start completion, optional40s third cue and
  no repeated release; prospective metadata now agrees0/15/30,0/20,0/20/40 by mode.
  New-mode forced unload refused before process access; elevation policy,
  process image/exit classification and WindowsPS5->PS7 shim pass.17PS scripts
  parse and42exact-client anchors match.
- Reference/installed client SHA256 unchanged:
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
  Prepared component SHA256
  `2ED7554F6372A193F0AC1FA86399E527FD3D6E429C87FE6C3B4BF26B407EB9AA`;
  controller`B1E49093A483838D0EB18788BA4F116D835D597DD5BC3FA3EE5ACF975C4ADEBA`.
  Runtime runner rebuilds and records actual hashes; preparation hashes may differ.
- No active game/controller. One compound inspection returned shell exit1 because
  Get-Process found none; explicit follow-up confirms count0, not a failed test.
  No runtime launch/client change/raw capture/archive/deletion this execution.
  Tiny ignored offline fixtures retained; prior runtime archives unchanged.
- Final disposition **READY FOR SPONSOR RUNTIME TEST**. No formal TRL4, new
  enhancement, reusable-buffer or physical-identity-continuity claim. Final Git
  baselinefee152f,83pending path entries including prior work, staged0. Docs/link/
  whitespace checks at handoff; no commit. Exact next action: sponsor runs prepared
  RT-009 fixture; review evidence before further implementation.
