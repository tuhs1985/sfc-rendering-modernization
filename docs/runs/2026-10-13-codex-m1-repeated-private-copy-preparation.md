# Codex run — 2026-10-13 bounded fresh-copy preparation

- ID: 2026-10-13-codex-m1-repeated-private-copy-preparation. Active M1/C-01;
  sponsor "ok, continue" after RT-007 review authorizes the next bounded proof.
  Runtime not executed; formal M1 remains CONTINUES.
- Starting baseline: HEAD fee152f; 74 pending paths, all unstaged. Preserved all
  prior work. User-supplied AGENTS instructions apply; no physical AGENTS.md at
  repository root. Fuel Guard attach succeeded through recent trusted hook;
  direct connection sandbox denied, no daemon started. No helper/subagents.
- Read HANDOFF and operating convention, approved M1 plan, current C-01 increment,
  copy-lifetime review, RT-007 probe/evidence/runtime/preparation record and scoped
  C++/PS/Python/tests. The old lifetime proposal is historical; live RT-007 is the
  newer authority for one-use receipt. No settled math/ABI or requirements reopened.
- Question: can repeated fresh private inputs preserve the same semantic owner
  across multiple frames without assuming safe buffer reuse? Chose 32 immutable
  process-lifetime slots, >=1-second spacing, same epoch/model/source/count/list,
  previous receipt/parent prerequisite. Old copies never overwritten or freed.
  No new hook sites or visual changes. Rejected premature free/recycling, per-frame
  unbounded allocation, full-rate firehose, shallow Model0 clone and C-02 work.
- [Probe RT-008](../m1/probes/M1-C01-RT-008.md) specifies target sites, ABI/state
  preservation inherited from RT-007, explicit flags, launch/UAC/cleanup, limits,
  failure behavior, expected outputs and evaluation. Component 0.11; fixed bank
  <=700 KiB, copy attempt cap32, 90 seconds, same 16/32 MiB event and 3 MiB corner
  limits. Extra bank allocation is static even in one-use/disabled modes.

## Implementation files changed in this execution

- tools/m1_component/m1_component.cpp: bank, scoped pending-slot receipt/return,
  fixed rate/cap/fail-open and summaries; unchanged interception sites/thunks.
- tools/m1_component/start_m1_corner_snapshot_session.ps1,
  start_m1_enabled_session.ps1, run_m1_increment_a.ps1: explicit opt-in forwarding,
  manifest/INI/probe ID and plain-language instructions. Existing one-use entry
  retains its default; all other entries leave repeated mode off.
- tools/m1_component/analyze_m1_private_copy.py: independent repeated-record
  checks; analyze_m1_wrapper.py, analyze_m1_rejections.py,
  analyze_m1_corner_snapshot.py: RT-008 provenance/neutral-action labels.
- tests/m1_corner_snapshot_tests.cpp: production fresh-slot, spacing, epoch/source,
  pending parent, exhaustion, nonmutation, malformed input and stop fixtures.
- tests/test_analyze_m1_private_copy.py: positive/negative repeated evidence;
  tests/test_m1_private_copy_unload.ps1: configurable harmless fixture name.
- Created tools/m1_component/start_m1_repeated_private_copy_session.ps1 and
  tests/fixtures/m1_repeated_private_copy_unload.ini.
- Documentation: created this record and RT-008 definition; updated HANDOFF and
  current C-01 status, preserving older checkpoints/evidence. No binaries tracked.

## Tools, commands and validation

Bundled Python3.12.14, PowerShell7.6.5; VS2026 18.7.3/MSVC14.51.36231 x86
C++17 /W4 /WX /O2 /MT /arch:SSE2. Set process-local TEMP/TMP to the existing
`C:\Project\SFC-Modernize Engine\artifacts\m1\test-temp` before fixture tests.
No system policy/security changes. Material commands:

```text
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/m1_component/build_m1_component.ps1
python -m unittest discover -s tests -p test_*.py
artifacts/m1/bin/m1_corner_snapshot_tests.exe artifacts/m1/test-temp/repeated-copy-good
artifacts/m1/bin/m1_corner_snapshot_tests.exe artifacts/m1/test-temp/repeated-copy-failure --failure
python tools/m1_component/analyze_m1_private_copy.py artifacts/m1/test-temp/repeated-copy-good/private-copy
python tools/m1_component/analyze_m1_private_copy.py artifacts/m1/test-temp/repeated-copy-good/repeated-private-copy
python tools/m1_component/analyze_m1_private_copy.py artifacts/m1/test-temp/repeated-copy-failure/repeated-private-copy
pwsh -File tests/test_m1_corner_action_cues.ps1
pwsh -File tests/test_m1_private_copy_unload.ps1
pwsh -File tests/test_m1_private_copy_unload.ps1 -FixtureName m1_repeated_private_copy_unload.ini
pwsh -File tests/test_probe_elevation_policy.ps1
pwsh -File tests/test_m1_process_image_path.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/test_m1_visual_entry_runtime.ps1 -EntryName start_m1_corner_snapshot_session.ps1
python tools/m1_component/verify_m1_c01_shading_bytes.py "Game Assets/StarFleetOP.exe"
git diff --check
```

Initial strict compiler rejected a shadowed local `index`; renamed to `copy_index`.
Initial three-argument failure fixture did not create its output root, causing
synthetic stop-output failure; fixture root setup now accepts argc>=2. Neither
was a gameplay defect; no game launch occurred. Final results recorded below.

## Result / next checkpoint

Implementation and offline validation only. Runtime repeat-use remains a
**STRONG HYPOTHESIS** until RT-008; reusable-buffer lifetime remains unqualified.
No source/geometry/lighting modification and no final renderer choice.
Exact next action: offer the prepared RT-008 runner to the ready sponsor, then
adjudicate captured results before any further implementation. No automatic run,
staging or commit. Preserve dirty baseline; latest final validation/state below.

## Final validation — 2026-10-13 22:54 EDT

- Full final native build, required DLL/proxy/gate exports and six test groups
  pass. Actual production RecordHook/thunks and M1Stop exercised offline; 32 fresh
  slots span synthetic 31+ seconds/distinct frames, every receipt/return observed.
  Source changes between copies do not mutate earlier private slots. Guards for
  setup/nesting, owner epoch/source mismatch, subsecond call, missing prior
  completion and exhausted bank preserve original arguments. Malformed second
  copy halts new substitution and preserves the first published slot.
- Synthetic one-use and 32-slot private-copy analyses: empty issue lists,
  LEAD_REVIEW_REQUIRED, not runtime success. Malformed-copy fixture correctly
  ADDITIONAL_BOUNDED_EVIDENCE_REQUIRED with explicit incomplete/halted-slot issues.
  Good repeated summary 13,905 bytes, fixed storage **657,004 bytes**; no growth
  beyond 32 slots. Small ignored fixture files retained, not gameplay evidence.
- 43 Python tests pass. Cue/gate ordering (20-second setup and completed two-tone
  cue before release), original and repeated forced-unload refusals, elevation
  policy, process path/exit classification, Windows PowerShell5-to7 shim pass.
  All 16 relevant PowerShell scripts parse. 42 static client anchors match.
- Reference and installed client SHA256 unchanged:
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
  Prepared DLL SHA256
  `97C502D6FEDB039F844A9EA2F55A8761BFE23149389C32782F416ACC219D3CE3`;
  controller `E965CFB97DDE40FE4AC830BE22592CFBD628AFF027D7423C21AF4D67B1F1B173`.
  The sponsor entry rebuilds and records actual runtime hashes, which may differ.
- No game/controller observed. No runtime launch/capture or client patch performed.
  No files deleted; previous RT-007 ZIP/raw preserved. Documentation links/Git
  whitespace/staged status checked at final handoff; all changes remain unstaged,
  HEAD fee152f. Final disposition **READY FOR SPONSOR RUNTIME TEST**; no commit.
  Final Git status: 13 modified tracked paths and 64 untracked path entries
  (77 total, including pre-existing work); staged list empty. Generated DLL and
  fixture summary confirmed ignored. Documentation links and diff whitespace pass
  (Git line-ending conversion notices only).
