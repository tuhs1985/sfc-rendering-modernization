# Codex run — TEXTURE-RECOVERY-PREP-20261016

Date: 2026-10-16, America/New_York. Task: approved bounded texture recovery,
offline capture/review only. M1 amended semantic integration gate closure remains
pending sponsor review; no aggregate TRL4/M2 advancement claimed.

## Starting baseline and question

HEAD `fee152f137a55a3efeb47a5c236ebf9e3e1951cb`; 151 short-status entries,
empty index. Substantial inherited completed/ongoing work preserved; not a clean
checkout. No staging, commit, cleanup or baseline reset authorized/performed.
Question: join the selected mesh's five groups to original images using *fresh*
live resource identity, without interpreting IDs as pointers or guessing glow.

Reviewed authority/evidence: `docs/HANDOFF.md` and its operating convention;
`docs/m1/m1-trl4-integrated-component-validation-plan.md`; latest
`docs/runs/2026-10-16-codex-mesh-preview-launcher.md`; mesh runtime record
`2026-10-15-codex-mesh-export-remix-runtime.md`; single-ship export contract,
render-input gap assessment, semantic function/subsystem maps, mesh/preview probe
definitions and accepted `20261015-190310-enabled` packet/source records.
Read only narrowly relevant exact-build disassembly and installed model directory
examples. Matching file names/ship appearance were NOT used as assignments.

## Decisions and evidence

The **pre-implementation checkpoint** is in
[TEXTURE-EXPORT-001](../reconnaissance/probes/TEXTURE-EXPORT-001.md): exact addresses,
source offsets, STRS relationship, registry and manager resource tables, confidence,
ABI/nonmutation strategy, tool versions, limits, launch/stop and cleanup.
CONFIRMED static: source+0x14/+0x1C are resource IDs; +0x18/+0x20 are string
offsets, not pointers. Loader 0x0042F617–0x0042F68B writes those IDs; resource
registry 0x008CC620 / vtable0x00795C54 uses20-byte entries and resource+8 inline
filenames. Independent 0x006A07D0 string lookup and 0x006A0920 object lookup
corroborate it. 0x006A8860 binds the manager table's corresponding texture.
Manager+0x1ED0/source flag1 govern whether those IDs survive preparation.
Live readability/actual ship-image assignments remain STRONG HYPOTHESIS.
Secondary image has a conditional rendering relationship but **emission/glow,
alpha purpose and faithful placement remain unproven**. No suffix-based glow.

Implemented component0.15 default-off reference snapshot alongside successful
same-epoch mesh capture. No hook/ABI changes, native calls, COM access, image copy,
allocation or disk I/O added to the render thread. Fixed <8KiB reference storage,
ten unique IDs, <=255-byte printable strings; rechecks resource names, requested
names, source words, registry/manager identities, model filename and owner epoch.
One association attempt; failures preserve the accepted mesh and explicit status.
Stop serializes after recorder drain/hook restoration. Existing geometry hook OFF.

Offline recovery joins exact registry-relative Assets paths, hashes/decodes
original BMP/PCX images, writes lossless PNG copies, and generates separate primary
MTL bindings on the unchanged derived OBJ. No model rotation, UV flip, face/normal
repair or silent world conversion. Secondary originals/PNGs retained separately,
not emitted as glow; overall manifest stays PARTIAL. Missing/ambiguous images,
cross-epoch associations, disabled/unproven primary use and exceeded bounds fail
closed for the derivative, not the game. No GPU readback/wrapper installation.

Runtime entry preserves90s automatic tactical gate and normal-exit/client checks.
Image recovery runs **after normal exit**. Remix `--textures` is explicit and
requires derivative hashes/unchanged geometry, numeric corner/group comparison
before preview. Grey CMD/accepted USD remain untouched. Existing child-only
NRC-off configuration and owned-process guards remain; imported images, alpha
behavior and actual viewport fidelity still await fresh real evidence.

## Files changed in this execution

New:

- `tools/m1_component/m1_texture_references.h`
- `tools/m1_component/export_mesh_textures.py`
- `tools/m1_component/start_texture_export_session.ps1`
- `tests/test_export_mesh_textures.py`
- `tests/test_texture_export_workflow.ps1`
- `docs/reconnaissance/probes/TEXTURE-EXPORT-001.md`
- this run record.

Updated (some already inherited/untracked, not newly created by this execution):

- `tools/m1_component/m1_component.cpp`
- `tools/m1_component/run_m1_increment_a.ps1`
- `tools/m1_component/start_m1_enabled_session.ps1`
- `tools/m1_component/start_mesh_export_session.ps1`
- `tests/m1_mesh_export_tests.cpp`, `tests/m1_mesh_component_tests.cpp`
- `tests/test_m1_visual_entry_runtime.ps1`, `tests/README.md`
- `tools/remix_ingest/run_remix_ingest.py`, `run_mesh_preview.py`,
  `kit_mesh_preview.py`, `test_mesh_preview.py`, `README.md`
- `docs/HANDOFF.md` (new checkpoint; old evidence retained).

Generated DLLs/test executables remain ignored under `artifacts/m1/bin`; temporary
synthetic assets are explicitly fixtures, not actual recovered SFC textures.
No reference packet, accepted grey OBJ/USD, installed original image or game file
was modified. No game/runtime probe, Toolkit ingestion or GPU preview launched.
No helper/subagent invoked. Fuel Guard attach attempted for the supplied thread;
existing trusted hook verified, direct sandbox daemon access denied; no new daemon.

## Validation / reproducibility

Tools: VS2026 Community18.7.3, x86 MSVC14.51.36231 C++17 `/W4 /WX`; bundled
PowerShell7.6.5; Windows PowerShell5.1 entry; Python3.12.14/Pillow12.3.0.
For Python tests set process-only `PYTHONDONTWRITEBYTECODE=1`, and TEMP/TMP to
`artifacts/m1/test-temp` (existing sandbox-compatible directory).

- `tools/m1_component/build_m1_component.ps1`: DLL/proxy/gate/controller builds,
  all native tests/export checks PASS. New cases include live-table resolution,
  default-off/exclusive configuration, retirement/source-change rejection,
  unterminated strings and stopping at the eleventh resource without overflow.
- Bundled Python `-m unittest discover -s tests -p 'test_*.py'`:78 PASS.
  Five-group/ten-image fixture; exact original preservation, image decoding,
  lossless PNG roundtrip, geometry/UV/group preservation, cross-epoch/duplicate
  rejection, path/dimension/byte-limit failures and warning behavior.
- Bundled Python `-m unittest discover -s tools/remix_ingest -p 'test_*.py'`:
  21 PASS, including explicit textured-candidate hash gating; grey protections kept.
- `tests/test_mesh_export_workflow.ps1` and
  `tests/test_texture_export_workflow.ps1`: PASS; parse/policy/forwarding only.
- Windows PowerShell5.1 `-NoProfile -ExecutionPolicy Bypass -File
  tests/test_m1_visual_entry_runtime.ps1 -EntryName start_mesh_export_session.ps1
  -EnableTextureReferences`: PASS against harmless PS7 fixture; no game/elevation.
- Synthetic derivative -> installed-schema Remix **job preparation** PASS:
  input PNGs/MTL forwarded, schema points at copied textured OBJ.356 original+
  derived image bytes in that two-image fixture. Fixture directory automatically
  removed by its temporary-directory test; no material project evidence deleted.
- `git diff --check`: PASS; inherited LF/CRLF advisory warnings only.
- Installed and reference client SHA256 both unchanged:
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
  No SFC process or owned WINMM/M1 game-directory leftovers observed.
- Final prepared component SHA256:
  `370D31B8DEF52E440B2A4EDA4818FDD8FD0ECB0967F53137D63EBC20AD994155`;
  WINMM proxy:
  `2FA876876B512E1C9945FFA56832C477D4F7B7FFDB36D610C60A6FEC52502B34`;
  texture-reference header:
  `DB5A45B9397D4BAD98E6D7FCD25C251DC81A740EE3914639F55C719D2B73CB97`.
  Full final rebuild and78+21 Python tests re-passed after the enable-byte check.

## Result / remaining work

**READY FOR SPONSOR CAPTURE; texture-recovery result remains PARTIAL / untested
in SFC and the textured preview.** No actual association manifest or comparison
images can honestly be claimed before the fresh run. No old resource IDs reused.
Existing geometry/shading findings remain separate. Potential one-time snapshot
cost must be checked in runtime; QPC capture timing is not presentation latency.

No runtime bulk output this execution. New fixed capture cannot generate multi-GB
output. Image original+derived cap128MiB/warning64MiB, dimensions4096², ten unique
resources; semantic16/32MiB log bounds and90s runtime retained. Preview120s/180s,
scratch128/256MiB and8MiB console envelope retained. Archive useful real packets,
references, manifests, images and comparison PNGs after analysis; existing ignored
archives remain intact. No synthetic test image is evidence of correct SFC texture.

Exact next action: from the existing elevated parent shell, run
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\m1_component\start_texture_export_session.ps1"`.
Enter usual two-ship skirmish, keep both initially visible, play normally, exit
normally after the two exit cues/console request. Expect no visual game change.
Codex then adjudicates fresh registry associations and prepares the separate
textured preview/comparison, investigating only a specific missing role if needed.

Final repository: HEAD unchanged,158 short-status entries, empty index, inherited work plus the listed
unstaged additions/edits retained. Nothing staged or committed. No active game,
controller, debugger or new renderer process to resume; shell bindings are not
project authority. Recheck status/build hashes before runtime after any restart.
