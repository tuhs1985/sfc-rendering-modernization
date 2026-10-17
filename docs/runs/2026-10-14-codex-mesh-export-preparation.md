# Codex run — bounded read-only mesh exporter preparation

- ID/date: `2026-10-14-mesh-export-preparation`, America/New_York. Sponsor "Go"
  authorizes the next stated task: implement/offline-test packet exporter. No
  gameplay run or renderer integration authorized/executed in this preparation.
- Baseline: HEAD `fee152f`; 131 inherited pending Git paths, none staged. Prior
  changes preserved; no cleanup/rebase/reset/commit. M1 technical closure still
  awaits sponsor acceptance; this work does not promote aggregate TRL or change
  requirements, gates, supported builds or rendering technology.
- Fuel Guard attach confirmed recent trusted hook; direct sandbox connection
  denied, quota health unknown; no daemon/helper/subagent started.
- Read authoritative HANDOFF, complete-selected-mesh contract, actual component/
  graph/corner/source interfaces, build/tests and runner/elevation/entry workflows.
  Hypothesis: bounded complete primary mesh can be saved independently through
  existing proven wrapper without altering native rendering arguments/data.

## Implementation / adjudication

- Added fixed-storage `m1_mesh_export.h`: complete position array, full ordered
  primary polygons/corners/raw UV/vector/opaque bytes, sparse referenced source
  records, raw supplied/composed transforms, dispatch and semantic/LOD identity.
  Versioned little-endian serializer uses portable corner ordinals and provenance
  values (never consumer pointers), exact lengths and FNV-1a integrity check.
- Added default-off `EnableMeshExport` in component **0.14**. Existing owner-scoped
  primary wrapper only; original ABI/thunks/state preservation unchanged, no
  additional hook. Guard actual selected child/override, current manager source/
  positions, live owner/thread/depth/list/count; reject all mutation modes.
  QPC records each attempt's capture duration for later hitch adjudication.
- Final source traversal found the existing depth counter was activated only by
  private-copy mode, which would have prevented read-only capture. Corrected its
  activation condition to include mesh mode, without changing thunks. Extended
  production fixture to call actual Model0 entry/parent-exit recorders and assert
  depth establishment/drain and unchanged arguments. Final full rebuild PASS.
- One immutable target epoch, <=2 attempts on different frames, <=90s, one
  accepted packet. No geometry hook, no shared-state writes, no graph substitution
  or module pin/native lease. Read/compare twice, reject changed inputs. No
  atomicity/physical identity continuity claim. Serialize only on drained stop
  thread after hook restoration; fail-open native path on capture/output failure.
- Analyzer independently reads bounded file/checksum/lengths/topology/source/LOD
  relationships and optional cleanup receipt, reports bounds/normals/UV/degeneracy
  without silent repair. Nontriangles retained but not fan-triangulated; source
  index not promoted to texture/material ownership; transforms not external camera.
- Prepared exclusive runner/launcher switch and entry; reuse existing automatic
  tactical gate, temporary proxy lifecycle, client hashes and normal-exit logic.
  No old camera/action phases. Inherit elevated parent, PS5->bundled PS7 shim;
  refuse routine UAC escalation. Two exit beeps plus console request; no gameplay
  action except entering ordinary two-ship fixture/normal play/normal exit.
  Packet analysis rejection is deferred until exit/hash evidence is preserved.
- Probe definition: [MESH-EXPORT-001](../reconnaissance/probes/MESH-EXPORT-001.md).
  Capture limits: <=512 primary polygons, 3..8 corners, <=65,536 positions,
  source indices <256; static packet <1 MiB, file hard cap 2 MiB, summaries
  <=64 KiB; existing 120-frame/10,000-event detail and 16/32 MiB log caps unchanged.

## Exact files changed in this execution

New:

- `tools/m1_component/m1_mesh_export.h`
- `tools/m1_component/analyze_mesh_export.py`
- `tools/m1_component/start_mesh_export_session.ps1`
- `tests/m1_mesh_export_tests.cpp`
- `tests/m1_mesh_component_tests.cpp`
- `tests/test_analyze_mesh_export.py`
- `tests/test_mesh_export_workflow.ps1`
- `docs/reconnaissance/probes/MESH-EXPORT-001.md`
- this run record.

Modified (including files already dirty from inherited work):

- `tools/m1_component/m1_component.cpp`
- `tools/m1_component/build_m1_component.ps1`
- `tools/m1_component/run_m1_increment_a.ps1`
- `tools/m1_component/start_m1_enabled_session.ps1`
- `tests/README.md`
- `docs/reconnaissance/2026-10-14-single-ship-export-contract.md` (prep update only)
- `docs/HANDOFF.md` (new checkpoint, older entries preserved).

## Reproduction / validation

Tools: Visual Studio 2026 Community Developer Prompt 18.7.3, MSVC 14.51.36231,
x86 vcvars32;
bundled PowerShell 7.6.5, Windows PowerShell 5.1 shim, Python 3.12.14, bundled Git.
Build flags `/std:c++17 /EHsc /W4 /WX /O2 /MT /arch:SSE2`; compiler errors/warnings
are fatal. Set process-local TEMP/TMP to existing ignored absolute
`C:\Project\SFC-Modernize Engine\artifacts\m1\test-temp`; Python
`PYTHONDONTWRITEBYTECODE=1`. No system policy/environment changes.

Executed (all offline, no SFC launch/injection):

1. `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/m1_component/build_m1_component.ps1`
   — PASS including DLL/proxy/gate/controller, prior native contract/tint/shading/
   graph/lifecycle/forwarding checks and both new mesh tests. Rebuilt after final
   C++ changes. New tests cover scope/config/stop writer, byte nonmutation,
   UV/vector splits, LOD override, sparse groups, WORD boundary, max counts,
   read fault/overflow/nonfinite/index/count failures, changing inputs/identity,
   same-frame/retry/epoch/time budgets, corrupt packet and failed output stream.
   Production fixture injects a fake read only for three dispatch globals; tests
   actual collector/selection/writer and recorder's completed pass-through. No
   installed-hook or full live-ABI claim from synthetic fixtures.
   Also rebuilt the mesh unit test directly with the same cl flags after adding
   a maximum-size actual-stream assertion; subsequent full rebuild includes it.
2. `python -m unittest discover -s tests -p 'test_*.py'` — **67 PASS**, including
   seven parser/receipt tests. No hidden skips used for the new tests.
3. `pwsh -NoProfile -File tests/test_mesh_export_workflow.ps1` — PASS: parsed real
   script policy blocks and entry forwarding; no actual workflow invocation.
4. Existing `tests/test_m1_endurance_workflow.ps1` — PASS: unchanged endurance
   policy still excludes diagnostics. Its printed start message is synthetic.
5. `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/test_m1_visual_entry_runtime.ps1 -EntryName start_mesh_export_session.ps1`
   — PASS: actual PS5 runtime shim re-executes harmless test in PS7, not the entry.
6. `python tools/m1_component/analyze_mesh_export.py artifacts/m1/test-temp/mesh-synthetic.bin --output artifacts/m1/test-temp/mesh-synthetic-analysis.json`
   — PASS on native-generated two-polygon/sparse-source packet, **612 bytes**.
7. Same analyzer on `artifacts/m1/test-temp/mesh-component/MESH-EXPORT-001.bin`
   with matching `--receipt .../MESH-EXPORT-001-receipt.json` and
   `--output .../MESH-EXPORT-001-analysis.json` — PASS, production writer packet
   **452 bytes**, receipt **301 bytes** on observed build. Timing is synthetic,
   not SFC performance evidence.

Measured x86 packet storage **930,052 bytes**. Maximum exercised synthetic packet
(65,536 positions/512 eight-corner polygons/one source) **919,848 bytes**. Full
256-source schema maximum calculated **930,048 serialized bytes**, not measured
live. No raw-output firehose, multi-GB output, source/client modifications or
raw deletion. Generated fixtures/binaries/analyses remain ignored in artifacts.

Reference and installed client SHA256 verified unchanged:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
No SFC/controller process was launched by this run. No active elevated/debug
session needed to resume; do not assume administrative state survives restart.

## Result / remaining uncertainty / repository state

**READY FOR SPONSOR RUNTIME TEST** — final offline/documentation checks complete;
gameplay remains unexecuted.
CONFIRMED offline implementation and bounded synthetic serialization/readback;
actual complete SFC mesh/UV snapshot remains STRONG HYPOTHESIS awaiting one run.
Potential one-time full-copy hitch remains; QPC attempt durations are not complete
frame-time telemetry. Material texture ownership, full physical-ship coverage,
camera/space conventions and renderer connection remain unqualified/deferred.
No repeat tint test, architecture selection, requirements change, helper use,
game installation/config change, staging or commit.

Final checks: all 16 changed/new task paths exist, all local Markdown references
resolve, modified/new PowerShell scripts parse; tracked and no-index new-file
whitespace checks PASS (line-ending notices only). Final Python/native packet
readback repeated after the depth correction PASS; existing 42 client byte anchors
PASS. Generated binaries/packet fixtures confirmed ignored. CDD SHA256 unchanged:
`BF5384D2586601AAA28DB36970937A3B40F598E12002B3450BF2E7D9562FA352`.
Final component DLL SHA256:
`9BA522362AA988547288F92C4E8488C722B54175079F3B339594FEA98B70EADE`.
No game-directory `winmm.dll` present on final read-only check.
Final Git: HEAD `fee152f`, **140 pending paths**, empty staged diff, no commits;
131 inherited paths plus nine new paths. No persistent runtime/helper/session.
Exact next action: on sponsor readiness, run only MESH-EXPORT-001's prepared
90-second normal two-ship capture and adjudicate the complete packet/receipt.
