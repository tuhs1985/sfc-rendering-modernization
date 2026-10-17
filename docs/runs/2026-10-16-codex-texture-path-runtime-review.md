# Codex run — TEXTURE-PATH-REVIEW-20261016

Final offline review extended only0069EA19–98 and corrected an initially
unsupported "previous_blend" name: +3F54 setter writes ALPHATESTENABLE15 and
ALPHAFUNC25, so final0.17 field is manager_previous_alpha_test_flag. No0.17 game
run used the temporary name. Preliminary path reports retain historical naming
with null value; final docs/reconnaissance/evidence/20261016-texture-path-review.json
uses corrected name and is current/versionable. Raw53-entry archive predates this
small final report, but contains all original inputs.

Active task: inspect sponsor-completed0.16 texture-path runtime, follow through
bounded ambiguity; offline follow-up only. Sponsor: "ok, ran the game, do you thing".
Starting HEADfee152f137a55a3efeb47a5c236ebf9e3e1951cb,174 short-status paths/index
empty; inherited dirty work preserved. Fuel Guard exact-thread hook verified,
direct sandbox access denied/quota health unknown; no daemon spawned.

Read HANDOFF, approved probe/role/surface/provisional records, both new run folders,
receipt/packet/metadata/results, reference JSON, current resource manifest, summary/
semantic analysis/controller logs. Compared old accepted kff OBJ field records and
ten original image hashes. [Evidence adjudication](../reconnaissance/2026-10-16-texture-path-runtime-result.md)
contains exact fields, addresses, confidence and remaining gap; no chat-only claim.

## Result / follow-through

Authoritative165955 completed normally; snapshot/mesh associations validated,
two coherent owners/zero semantic rejections/zero overflow, cleanup/unload evidence
and unchanged client confirmed. Geometry diagnostic hook remains OFF; no visual
intervention.4792frames/1180detailed events/339458-byte CSV,1.177MB image derivative.
Snapshot0.1215ms QPC is not whole-frame latency. Source2.5.6.4 remains exact.

Recorded +3D58=511/+8009=0 disproves selection of combined mode0 at that snapshot:
fallback family selected CONFIRMED by runtime inputs + static branch. Exact
fallback pass count UNOBSERVED: +800C validation mask/+3F54 previous alpha-test state
were absent. Static conditional two-pass operation supports the provisional
primary*secondary contribution, but no promotion to active emission/fidelity PASS.
Do not use wrapper secondary-list count8 as texture-pass evidence.

Targeted static follow-up only:006AC63F–754,0069F270,0069E9C0,0069DCD0–DDE6,
0069E6AC–6F8,0069E700–8DE and their two small blend jump tables. Existing
tools/recon/extract_disasm_ranges.py used on exact-build dump. PE32 section
mapping independently decoded engine blend(1,4) ->ZERO/SRCCOLOR; installed
Windows SDK10.0.26100.0 d3dtypes.h corroborates states19/20/27 and factors1/3.
No wider scene/engine reconstruction. One inline inspection command had a
parenthesis typo, corrected without writes/runtime activity.

Own instrumentation gap addressed before any further sponsor run: component0.17
adds5bytes read/recheck to existing reference snapshot (mask/old-state), ten bytes
total twice, fixed <8KiB storage/no added hook or ABI/control-flow changes/native
calls/writes. Probe definition updated first. Exporter preserves optional fields;
old missing values remain null. New read-only analyzer validates packet/receipt/
source-group/same-epoch linkage and reports conditional request predictions, not
GPU state or completion. No gameplay started in this Codex turn. Prepared0.17 is
UNEXECUTED; successful sponsor run remains0.16, do not conflate them.

Earlier165819 startup aborted OpenThread87/M1StartW5, rollback resume failures0,
no capture. Possible thread-enumeration race STRONG HYPOTHESIS, not diagnosed
conclusively. Successful retry is sufficient current evidence; failure preserved,
no unrequested concurrency/security redesign or repeated runtime loop.

## Reproduction / validation / files

Tools: Python3.12.14/Pillow12.3.0; PowerShell7.6.5; VS2026/MSVC14.51 x86 C++17.
Sponsor runtime used existing start_texture_export_session.ps1,90s auto tactical
gate,120detailed frames/10000events/8owners,16MiB log warning/32MiB stop,
ten image resources/4096²/64MiB warning/128MiB image limit; one snapshot, geometry
hook OFF. All limits retained for0.17. No unbounded/multi-GB output.

Executed:

```
python -m unittest discover -s tests -p test_*.py
python -m unittest discover -s tools/remix_ingest -p test_*.py
python tools/m1_component/analyze_texture_path.py artifacts/m1/runs/20261016-165955-enabled --output docs/reconnaissance/evidence/20261016-texture-path-review.json
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/m1_component/build_m1_component.ps1
```

89 project tests/36 preview tests PASS; full x86 build/native contract/tint/
shading/corner/copy/surface/mesh/configuration/stop/proxy tests and exports PASS.
New tests cover branch classification, missing historical data, bool/invalid
input rejection, exact group/epoch matching, no evidence mutation, capability
and prior-state branch prediction, native snapshot mutation detection. Predicted
requests still explicitly UNOBSERVED execution. No new Remix render required:
fresh geometry/UV/normals/groups AND ten original assets equal accepted preview.

Changes this turn:

- new tools/m1_component/analyze_texture_path.py, tests/test_analyze_texture_path.py;
- tools/m1_component/m1_texture_references.h, m1_component.cpp(version0.17),
  export_mesh_textures.py; tests/m1_mesh_export_tests.cpp,
  tests/test_export_mesh_textures.py;
- docs/reconnaissance/probes/TEXTURE-EXPORT-001.md; new runtime-result document;
  secondary-role and texture-recovery result updates; preview-surface sponsor-note
  addendum; this run record and docs/HANDOFF.md.

Only generated path reports added inside completed capture; original logs/packets/
refs untouched. Own initial analysis JSON preserved as .initial.json before
confidence-schema clarification, later canonical JSON preserved too; final
capture-folder path-review.json preliminary; curated versionable JSON above is
authoritative. No external/current game evidence overwritten.

Installed/reference hashes rechecked:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Normal exit true; component AND controller hooks-restored true. No active SFC/
controller, owned winmm.dll/m1_component.dll/m1_gate.dll/m1-component.ini absent
from game directory. Current0.17 build stays ignored under artifacts, not installed.

Both run folders archived/53 entries SHA256-verified:
artifacts/remix-ingest/evidence/20261016-texture-path-runtime.zip,
870797bytes, SHA16a201328f1b5fee0bc397db0ab276378fbb167263c141b624da514b71a1971d.
Older archives/raw files retained, no cache cleanup/deletion. Final diff/reference
checks PASS; HEAD unchanged/179 short-status paths/index empty, nothing staged or committed. No helper,
server, new process/session or requirements change. Current texture result PARTIAL.

Next exact action: when another normal game fixture is convenient, use prepared
0.17 reference capture to resolve the fallback eligibility inputs; do not repeat
0.16 unchanged or claim an exact pass count now. Existing provisional preview
remains valid as a hypothesis; no new sponsor visual-recognition request needed.

Final unexecuted0.17 build hashes: m1_component.dll
A62303B34A0BD5673DAC2A75E2B344F1D0205DD73E71C5D7E486FA826EB5F401;
winmm.dll2E93A2CC5E12D30FBF014E29277C6A1B3683D8F1353A720B13606AA6E5E1EFEB.
These are future-probe binaries, NOT the0.16 binaries used in sponsor's run.
Final curated JSON docs/reconnaissance/evidence/20261016-texture-path-review.json
is an additional deliberately versionable evidence file in this run's change list.
