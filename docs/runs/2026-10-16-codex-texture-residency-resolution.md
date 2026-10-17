# Codex run — TEXTURE-RESIDENCY-20261016

Date2026-10-16. Active task: approved offline texture-recovery preview, within
current M1 work; no new rendering integration/milestone advancement. Sponsor
requested autonomous continuation without progress reports/input unless blocked.
Question: restore recovered panel detail without discarding the original mip chain.
Starting HEAD `fee152f137a55a3efeb47a5c236ebf9e3e1951cb`,167 short-status paths,
index empty; inherited dirty work preserved. Fuel Guard exact-thread hook verified,
direct access sandbox-denied/quota health unknown; no daemon spawned.

## Baseline and sources

Read current HANDOFF, latest mip-config/bias/base-only/sampling/pixel-audit records,
texture-recovery result and MESH-PREVIEW-001. Accepted textured import:
`C:/Project/RemixJobs/20261016-050350Z-6dffd5be/output/ship.usda`, SHA256
`5c08f217b36ef9056c3a1940931ff2fd463286ca67e120d7bd80269b997634b2`.
Existing controls: `preview-20261016-051922Z-c8fef267` full mip chain;
`preview-20261016-052216Z-f60dc2ed` sharp base-only diagnostic. Minus1 startup
acceptance is settled; did not repeat it. Original texture/PNG exactness settled.

Installed AperturePBR_Model.mdl128–141 declares Nearest=0, Linear=1;
AperturePBR_Opacity.mdl241 defaults Linear. Read-only installed material inspection.
Primary NVIDIA public **main**, consulted2026-10-16 (not exact installed source):

- [Scene manager](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/main/src/dxvk/rtx_render/rtx_scene_manager.cpp)
  createSurfaceMaterial1476–1507 suggests explicit sampler overrides may bypass
  generic sampler patching. That explanation remained SPECULATIVE for our viewer.
- [Texture manager](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/main/src/dxvk/rtx_render/rtx_texture_manager.cpp)
  addTexture871–895: neverDowngradeTextures requests MAX_MIPS, rather than ordinary
  feedback-driven loading. This supplied a materially different residency test.

Installed native log revision `remix-main+f337894d`; exact short-commit raw source
URL unavailable (404). Public main is guidance, not proof of matching binary code.
No broad engine RE, source download/build, new wrapper or cache deletion.

## Experiments / adjudication

Documented configurations in MESH-PREVIEW-001 **before** runs. All three use
Python3.12.14/Pillow12.3.0, Toolkit1.6.0-dev+main.30229.3f23f80a.gl/Kit110.1.1,
existing bounded_job.exe; child NRC off/bloom off. Same saved source/UV/geometry/
camera/lights. No SFC run, elevation dialog or sponsor action. Scoped execution
exception needed only for sandbox GPU initialization, not Windows security changes.

Reproduction (bundled Python executable, arguments):

```
tools/remix_ingest/run_mesh_preview.py --job C:/Project/RemixJobs/20261016-050350Z-6dffd5be --textures --smoke --nearest-filter
tools/remix_ingest/run_mesh_preview.py --job C:/Project/RemixJobs/20261016-050350Z-6dffd5be --textures --smoke --resident-textures
```

Scratch root `C:/Project/RemixJobs/`; results:

| Job suffix | Single variable | Duration | Console / peak scratch bytes | Result |
| --- | --- | --- | --- | --- |
| preview-20261016-162603Z-e74e87de | five shader filter_mode=0 session requests |16.281s|24448 /1238934|Coarse/blocky panels; not a useful fix|
| preview-20261016-162721Z-8c65dee6 | native neverDowngradeTextures=True |16.281s|24594 /1282767|Sharp wing panels restored, full mip chains retained|
| preview-20261016-162835Z-449d98d4 | repeat residency, fresh process |16.110s|24594 /1239107|Sharp result repeats|

All exit0, stop_reason0, READY452triangles/11prims, zero remaining owned processes,
source USD unchanged. All five scratch DDS hashes in all three runs equal original
import DDS (nine mips intact); scratch USD equals original import. Original
installed/reference client SHA256 both rechecked:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
No game/controller/Kit process remains. No game artifacts generated or removed.

First attempt `preview-20261016-162553Z-fe969678` stopped in preparation before
GPU launch: exclusive JSON writer refused existing scratch config (File exists).
Corrected to rewrite only its just-created owned scratch config; no source affected.
Nearest mode authored/read back five USD values (`preview-filter-test.json`), not
GPU sampler state. Its blockier output supports actual material-filter response,
not a better normal appearance; rejected as solution. No nearest default adopted.

Both residency logs137–143 list
`rtx.texturemanager.neverDowngradeTextures = True` in **effective native values**.
Thus config activation and repeated sharp output CONFIRMED; precise GPU resident
levels/per-pixel sampling are not directly read back. Low-detail streaming residency
as cause is STRONG HYPOTHESIS, supported by source-guided independent intervention
and original/base-only/full-chain comparison. Do not claim exact internal defect,
all filtering correctness or universal production policy.

Analyst viewed both residency above.png and nearest above.png: panel lines restored
in residency, resembling sponsor-accepted base-only result. Whole-image RGB RMS
versus base-only was0.388/0.395/0.375 first residency,1.026/1.035/0.994 repeat;
nearest6.961/6.240/6.251. Images are not pixel-identical; path-traced variation exists.
These are difference measures, not sharpness/fidelity scores or new sponsor approval.
Brightness, dark/open faces and unproven secondary/glow role remain separate;
overall texture-recovery fidelity remains PARTIAL. **Softness work is resolved
operationally for this offline selected-mesh preview.** No input blocker.

## Implemented disposition / validation

New explicit `--resident-textures` available for smoke or interactive textured
preview, child config only. All original mip levels retained; Linear default
retained. Separate `start_textured_preview.cmd` pins accepted textured job and
residency option; original grey launcher/default and streaming textured control
remain unchanged. No global/vendor config, renderer architecture, client, asset,
UV, rotation, winding, normal, light, glow or game hook change. Full residency is
appropriate to five small256² images here, not generalized to a full game scene.
Nearest/bias/base-only modes are mutually excluded from residency. Each fresh job
records launch, hashes, request, limits, outputs; gpu_residency_readback unavailable.

Files changed this run:

- tools/remix_ingest/run_mesh_preview.py
- tools/remix_ingest/kit_mesh_preview.py
- tools/remix_ingest/test_mesh_preview.py
- tools/remix_ingest/start_textured_preview.cmd (new)
- docs/reconnaissance/probes/MESH-PREVIEW-001.md
- docs/reconnaissance/2026-10-16-texture-recovery-result.md
- this run record (new), docs/HANDOFF.md

Validation:29 remix/preview unittest cases PASS,81 project Python cases PASS;
syntax/guard regression coverage includes session-only five-shader requests,
refusal before preparation for unsafe combinations, residency preparation with
unchanged source/DDS, grey launcher preserved. git diff --check PASS (existing
LF/CRLF warnings only); reference paths checked. No C++ rebuild needed for this
Python/Kit-session-only change. Repeated real residency smoke PASS as above.

Limits unchanged:180s wall/120s interactive,256MiB scratch stop/128MiB warning,
8MiB console,three smoke PNGs <=8MiB each,64KiB reports. No warning/stop reached;
no continuous output, multi-GB trace, shared cache cleanup or driver edit.
Useful evidence archived (portable caches excluded, no raw deletion):
`artifacts/remix-ingest/evidence/20261016-texture-residency-resolution.zip`,
2057430bytes/128entries, each reopened and SHA256 matched against source file.
ZIP SHA256 `8608c268ee453ae2179f456221ba83d5d4d22bd5349aaaed6496b272452edea9`.
Contains three job records/images/config/scripts and existing control/base-only
above images. All older archives remain. No full project backup required for
reversible additional preview tooling; existing uncommitted work never cleaned.

Final HEAD unchanged,168 short-status paths/index empty, inherited changes preserved; nothing staged or
committed. No active server/process/session to assume survives restart. No helper.
Next smallest action, only in a subsequent texture task: trace the already captured
secondary resource binding/operation to establish its actual role before emitting
glow. Do not recapture original textures or reopen the now-resolved softness test.
