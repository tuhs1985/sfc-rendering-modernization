# Codex run — read-only repeat budget/instruction correction

- Run ID/date: `2026-10-12-m1-c01-expanded-budget`; preparation began late
  2026-10-11 and continued across midnight, America/New_York.
- Authority: sponsor requested correcting directions/probe and increasing budget;
  then requested readiness/instructions for second run. Preparation only so far,
  no gameplay launched by Codex. M1 CONTINUES/C-01, no enhancement or commit.
- Starting baseline fee152f; prior uncommitted source/tests/evidence preserved.
  Sources: HANDOFF, RT-002 definition/partial packet, corner helper/analyzer,
  native/cue tests, existing launcher/runner. No settled seam/ABI reanalysis.
- Fuel Guard trusted recent hook verified/direct denied; no daemon/helper/agents.
- Acknowledgment: sponsor-facing directions omitted explicit both-ships-visible
  condition. Do not attribute missing windows to sponsor error; visibility cause
  remains unconfirmed. New instructions require small camera movement, both ships
  visible, low speed/gentle turn and late observation. Monitor issue remains parked.
- Changed read-only count ceiling65,536 to accept observed6,370 model while
  retaining64 actual sampled polygons/eight corners. Tint guard4,096 unchanged.
  Budget90s,18 windows/owner36 attempts,5s intervals/min1s spacing,3MiB packet;
  semantic120 epochs/10,000 events/eight owners/16–32MiB unchanged, geometryoff.
  Cue thresholds0/15/30s; latest sample85s gives actual turn response time.
- Component0.6, schema corners.v2; analyzer keeps legacyv1 limits/readability.
  Runtime metadata now identifies M1-C01-RT-003 and explicit corner budget.
  Fixed arrays/copy guards and original-data nonmutation unchanged; no new hook.
- Tools/commands: MSVC14.51.36231 x86/VS18.7.3 C++17 /W4 /WX via existing
  build_m1_component.ps1; bundled PS7.6.5/Python3.12.14, WindowsPS5 shim, Git.
  Process-local TEMP/TMP artifacts/m1/test-temp for tests.
  `python -m unittest discover -s tests -p 'test_*.py'`:23 pass;
  full native build/exports and allsix groups pass. Cue AST test now15s thresholds,
  new entry PS5→PS7 shim and17 PS source parses pass. Native fixture specifically
  accepts6,370 while reading64, refuses65,537, and verifies tint limit unchanged.
- Production serializer/parser fixture run:
  `artifacts/m1/bin/m1_corner_snapshot_tests.exe "C:\Project\SFC-Modernize Engine\artifacts\m1\test-temp\corner-synthetic-rev2"`;
  `python tools/m1_component/analyze_m1_corner_snapshot.py artifacts/m1/test-temp/corner-synthetic-rev2`.
  All36 records coherent, packet772,016/analysis25,517 bytes, explicitly synthetic.
  No live input-space or gameplay PASS. Files ignored, no material deletion.
- DLL SHA256234ED32DF9C6F57C204092FACAB27CA15BFE5C8B4FC2B14EECAA8A4418AB3BCA;
  controller93F8D3AAA2B48E07866E4E3AD137F2EA3A93737F066AB4B7C5F7B777B33EC2D8.
  Reference/installed client SHA unchanged4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
  Rebuild hashes frozen again by future runtime metadata.
- Files changed in this correction: m1_corner_snapshot.h, m1_component.cpp,
  run_m1_increment_a.ps1, start_m1_enabled_session.ps1,
  start_m1_corner_snapshot_session.ps1, analyze_m1_corner_snapshot.py,
  m1_corner_snapshot_tests.cpp, test_analyze_m1_corner_snapshot.py,
  test_m1_corner_action_cues.ps1; newest HANDOFF/probe cross-reference.
  Created M1-C01-RT-003 definition and this record. Prior work/history preserved.
- Validation: native/Python/cue/shim/parser tests, synthetic bounds, client hashes,
  final Markdown links/Git whitespace/status. No game launch, runtime queue or
  persistent elevated session assumed. All changes unstaged/uncommitted.
- Result READY FOR SPONSOR RUNTIME TEST. Exact next action: invoke revised entry
  from existing elevated parent and follow RT-003 instructions, preserving views.
