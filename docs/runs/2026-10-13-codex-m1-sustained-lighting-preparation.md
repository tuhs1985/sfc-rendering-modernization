# Codex run —2026-10-13 approved sustained diagnostic preparation

- ID2026-10-13-codex-m1-sustained-lighting-preparation; M1/C-01 diagnostic, not
  C-02 enhancement. Sponsor approved larger next test and corrected marker to
 20seconds to find/observe the right ship. Actual runtime not authorized/launched
  by this preparation; return ready runner after validation. No commit authority.
- Startfee152f/85pending entries, all unstaged; prior dirty work preserved.
  Fuel Guard attach via trusted recent hook, direct sandbox access denied; no
  daemon/helper/subagent. Read HANDOFF, current approval boundary, scoped copy/
  source/ABI code and RT-009 evidence. Wrote approved contract before new code.
- Decisions:20s marker from actual activation,5s normal,15s altered,original after.
  Same owner; abort on retirement/mismatch, no silent retarget. Complete <=512
  primary mesh, not old64prefix. Reverse only finite corner-vector sign bits,
  preserve non-unit magnitude/face vectors/culling/positions/UV/unknown bytes.
  Initial referenced vertex-light bit and non-unlit manager mode required.
- Bounded memory decision:two immutable full graphs332,336bytes<1MiB, retained
  pinned until process exit. Before **every** publication compare original full
  payload to neutral baseline; altered graph differs only by prescribed signs.
  Repeat publication does not overwrite/recycle memory. No aggressive free-point
  assumption, large per-frame fresh bank, new hook/ABI or final renderer.
- Legacy marker10s/detail-saturation restriction not silently changed: new explicit
  surface mode uses proven source lease machinery with its own20s schedule.
  Existing RT-007/008/009 behavior defaults remain. All capture bounds unchanged.

## Exact changed/created files

- tools/m1_component/m1_surface_graph.h (new):full graph pair, expected-byte/current
  input checks and20/5/15 phase scheduler; no live writes by itself.
- tools/m1_component/m1_component.cpp:0.13, explicit mode/identity/eligibility,
  continuous graph publication, marker/source lease, phase events/counters,
  per-call receipts/parents, abort/stop/pinning and bounded summary.
- tools/m1_component/build_m1_component.ps1:full-graph and production-surface tests.
- tools/m1_component/run_m1_increment_a.ps1, start_m1_enabled_session.ps1,
  start_m1_corner_snapshot_session.ps1:mode forwarding/config,20s instructions,
  component-driven cues and analysis selection; new entry
  start_m1_surface_lighting_session.ps1.
- New analyze_m1_surface_lighting.py; wrapper/rejection/corner analyzers preserve
  RT-010 identity and new action labels; no reinterpretation of old evidence.
- New tests/m1_surface_graph_tests.cpp, tests/m1_surface_component_tests.cpp,
  tests/test_analyze_m1_surface_lighting.py, fixtures/m1_surface_lighting_unload.ini;
  updated tests/test_m1_corner_action_cues.ps1 for event-driven phases.
- Docs:approved contract, RT-010 probe, this record; HANDOFF/current C-01 checkpoint.
  Requirements, originals, earlier probe decisions and archives remain untouched.

## Tools / reproduction

VS2026 18.7.3/MSVC14.51.36231 x86 C++17 /W4 /WX /O2 /MT /arch:SSE2;
bundled PS7.6.5/Python3.12.14, WindowsPS5 shim. Set process-local TEMP/TMP to
existing ignored absolute artifacts/m1/test-temp before offline fixtures.

```text
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/m1_component/build_m1_component.ps1
python -m unittest discover -s tests -p test_*.py
artifacts/m1/bin/m1_surface_component_tests.exe artifacts/m1/test-temp/surface-component
python tools/m1_component/analyze_m1_surface_lighting.py artifacts/m1/test-temp/surface-component
pwsh -File tests/test_m1_corner_action_cues.ps1
pwsh -File tests/test_m1_private_copy_unload.ps1 -FixtureName m1_surface_lighting_unload.ini
pwsh -File tests/test_probe_elevation_policy.ps1
pwsh -File tests/test_m1_process_image_path.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/test_m1_visual_entry_runtime.ps1 -EntryName start_m1_corner_snapshot_session.ps1
python tools/m1_component/verify_m1_c01_shading_bytes.py "Game Assets/StarFleetOP.exe"
git diff --check
```

Initial production negative fixture failed because VisualExit intentionally clears
thread semantic fields, and the synthetic next-call setup restored only part of
them. Corrected fixture to restore full current tuple, not production guards.
Final validation/results/hashes below. No runtime/gameplay/capture/deletion or
staging/commit. Phase/input/identity failures are not relabeled as success.

## Final validation / ready checkpoint

- Full native build/exports and eight test groups pass (original six plus complete
  graph and production surface sequence). Full452polygon/1356vector fixture:
  all prescribed sign-bit changes only,1200 immutable checked accesses, unknown
  bytes/positions/indices/UV/originals preserved. Nonfinite/count/pointer/input
  changes rejected. Pair332,336bytes; no growing or fresh-per-frame bank.
- Production sequence/source-lease/private-list receiver/parent/actual M1Stop
  fixture passes, then changed-original input leaves original argument intact
  and aborts overrides. Synthetic summary5010bytes; surface analyzer empty issues,
  LEAD_REVIEW_REQUIRED. Not live proof. Marker samples0..19990ms, baseline
 20010..24990ms, altered25010..39990ms, restored41000ms; no early marker timer.
-51Python tests pass. Cue regression checks old modes unchanged,20s identification
  instructions, completed two-tone release and component-event-driven third/fourth
  cues (not guessed from runner clock). New-mode forced unload refused before
  process access. Elevation, process path/exit and WindowsPS5->PS7 shim pass;
 18PowerShell scripts parse,42exact-client byte anchors match.
- Builder creates ignored test-temp parent and supplies absolute fixture output,
  avoiding CWD-dependent failure from sponsor's C:\Windows\System32. Direct
  production fixture run from System32 with absolute output succeeds, analyzer
  empty issues. No files written into System32. This is a scoped test-runner fix.
- Prior runtime M1-C-RT-001 recorded source0x23/mode5 with observed vertex-light
  suppression; supports the selected lighting gate, not proof of reversal's
  eventual visible strength. Live effect remains STRONG HYPOTHESIS until RT-010.
- Reference/installed client SHA256 unchanged:
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
  Prepared component SHA256
  `8D4CFAD7F4174D183F270896517CFA0548902075CFF8D79CFFE6F047E9A803F3`;
  controller`B3C963A56D7A6E29DBFA610742059F395C58B357E1B460BA56BDC5FF8FD1352A`.
  Entry rebuild will record actual hashes; no active game/controller or runtime
  launched. No new raw gameplay/archive/deletion. Small ignored offline fixtures
  retained; original captures/ZIPs and requirements untouched.
- **READY FOR SPONSOR RUNTIME TEST**, not visible PASS/quality improvement or
  fullTRL4. All pending work unstaged/uncommittedfee152f. Exact next action: provide
  the prepared RT-010 command and collect sponsor's marked-ship lighting/restore
  observation. No automatic run or further visual implementation before review.
- Final Gitfee152f:94pending path entries (13modified tracked/81untracked,
  including pre-existing work), staged0. Documentation links/whitespace pass
  (line-ending notices only), final runner parses, generated binaries/fixtures
  confirmed ignored. Nothing committed.
