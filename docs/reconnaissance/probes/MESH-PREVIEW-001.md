# MESH-PREVIEW-001 — saved asset, isolated Remix-renderer preview

## 2026-10-16 offline surface / illumination discrimination

Bounded follow-on: `left-handed` authored/read back correctly but looked unchanged
(above RGB RMS~0.36 vs control), so no GPU facing effect established. One distinct
`two-sided` session test enables doubleSided on eleven mesh prims only, retaining
orientation/index/normal/UV arrays and original lighting. Same guards/reports;
no change to captured source or general rendering policy. This discriminates
backface visibility from simple brightness; no texture/face repair silently adopted.

Sponsor authorized brightness/odd-face investigation without altering captured
model. Read-only audit_mesh_surface.py reads accepted geometry.json <=2MiB,
<=16 mesh prims/512 triangles/8192 points per mesh, emits <=64KiB exclusive JSON.
Compare geometric face cross-products against corner normals; edge incidence
uses positions rounded6decimals for analysis ONLY (no welding/repair). Initial
inspection: dominant opposite normal/winding directions, no same-direction
shared edges. That does not prove whether winding, normal convention or consumer
interpretation is wrong. Preserve originals and finite exceptions.

Fourth bounded discriminator after both facing flags were visually ineffective:
`emissive-surface` enables intensity1 emission using each material's SAME primary
texture, in anonymous session only. No source/array/alpha/culling/lighting edits;
retain original diffuse and fixed synthetic lights. This intentionally nonphysical
visibility test asks whether the dark patches contain textured surface that can
emit independently of illumination. It is NOT recovered glow, normal repair,
appearance calibration or adoption of an all-emissive ship. Same single-job limits,
three PNGs/report/cleanup. Black screenshots alone cannot prove absent geometry.

Two isolated `--textures --resident-textures --smoke --surface-diagnostic MODE`
jobs, MODE `left-handed` or `quarter-light`; exclusive with provisional lighting
and all sampling diagnostics. Both use accepted textured input and same fixed
camera/geometry/UV/normals. `left-handed` changes only anonymous session orientation
from rightHanded to leftHanded on all captured mesh prims, NOT vertex/index order
or normals. This is an explicit temporary facing-interpretation hypothesis,
not a source repair/default adoption or proven game-axis contract. `quarter-light`
keeps original facing and scales synthetic dome/key0.7/2.0 to0.175/0.5; no texture,
material, exposure or color grading changes. Report authored original/test values.
Use existing no-emission residency control20261016-184126Z-4af65ccc for comparison.

Same Python/Pillow/Kit/Remix versions, NRC-off/bloom-off child,180s/256MiB scratch
(warning128MiB)/8MiB console/three fixed PNGs<=8MiB each/64KiB reports. Expected
<3MiB per ordinary job, no continuous/multi-GB output. Existing job-object cleanup,
source/texture hashes, cache-excluded verified archive retained. No SFC launch,
client/assets/vendor edits, additional runtime hook or security change. Do not
infer missing captured polygons from a black screenshot alone or silently fix
faces/lighting based only on appearance. Match all five provisional mask shader
assignments using existing manifests; retain matched emission-OFF/ON images as
separate comparison evidence, not live-game validation.

## 2026-10-16 sponsor-authorized provisional lighting-mask preview

Sponsor disposition: "Don't have access to computer. Do what the code suggests.
We can verify later". This authorizes a separate offline hypothesis preview, NOT
promotion of runtime branch/role/fidelity to CONFIRMED or a requirement waiver.
Question: can the already captured primary/secondary pairs drive a code-informed
unlit contribution on their own five saved groups? Use full-detail residency,
same cameras/lights/geometry/UVs, default OFF `--provisional-lighting` alongside
`--textures --resident-textures`. No other filtering diagnostic simultaneously.

Offline helper verifies capture/import packet identity, reference/manifest hashes,
five exact group pairs and ten lossless PNG hashes. In NEW scratch only, derive
per-channel round(primary*secondary/255), using encoded source values, no flips,
upscale, alpha invention or source edits. This isolates the unsaturated additive
term suggested by static legacy combiner; modern emission cannot reproduce its
intermediate saturation or establish legacy color space/physical strength.
Five256² RGB products -> lossless RGBA PNG and uncompressed RGBA DDS, decoder
round-trip exact; intensity1 is an explicit preview assumption, not measured SFC.
Bind emissive_mask_texture/enable_emission/intensity only in anonymous USD session
on the matching source_NNN shaders; read back authored paths/values. No Save or
mesh/primary-material change. Label UI and report PROVISIONAL / RUNTIME UNVERIFIED.
Default normal textured and grey previews remain unchanged.

Python3.12.14/Pillow12.3.0 and existing installed Kit/Remix versions. No new
converter/wrapper, SFC run, UAC or runtime probe; run with existing native owned
job guard. Same NRC-off/180s wall/120s viewing/256MiB scratch warning128MiB,
8MiB console, three smoke PNGs <=8MiB each/64KiB reports. Ten originals max,
five selected256² products only, total product output <=8MiB and still within
128MiB overall image envelope. Expected about1.5MiB derivatives plus screenshots;
no continuous dump or multi-GB mechanism. Compare to unchanged residency control,
inspect panels and manifest/shader/group match; no visual-fidelity success claim.
Verify original capture/import/client hashes, clean exit/zero owned processes;
archive useful evidence excluding caches, preserve originals and older evidence.
Later sponsor gameplay validates both missing branch predicates before a confirmed
reconstruction; absence of that validation does not block authorized preview.

## 2026-10-16 material filtering discrimination (authorized autonomous continuation)

**Newer verified preview-only disposition:** first residency smoke restored panel
detail with the full, unchanged nine-mip DDS chains and Linear filtering. Native
effective-option block confirms True. Permit the same explicit `--resident-textures`
with `--textures` in interactive mode too (same120s viewing/180s total guard).
`start_textured_preview.cmd` pins the accepted textured job and those flags;
`start_mesh_preview.cmd` remains the original grey baseline, ordinary textured
mode without the flag remains the streaming control. No global/default runtime
policy, final architecture, brightness, glow, face fix or SFC change. This selected
mesh has five tiny256² images; do not generalize residency to full scenes/assets.

Follow-on discrimination, only after nearest test: full-chain nearest result
has conspicuously coarse/blocky panels, unlike the sharp base-only result.
Public main texture-manager source `addTexture` requests MAX_MIPS when
`rtx.texturemanager.neverDowngradeTextures` is true, whereas ordinary streaming
uses feedback. Test `--textures --smoke --resident-textures` in one fresh child,
requesting only that native option True. Keep all original DDS/mips, Linear
material default, geometry/camera/lights unchanged; no nearest/bias/base-only
combination. Same limits/tool versions/cleanup as below. Expect config/launch,
`texture-residency-test.json`, three fixed PNGs, ordinary logs <3MiB. Require
effective native option confirmation and compare existing full-chain/base-only
views. No installed/global/game policy change. Source-guided residency hypothesis
is not actual GPU-readback evidence. No wrapper installation or live capture.

Question: does the material's explicit filtering request change the soft preview,
where global nativeMipBias=-1 loaded but did not visibly help? One isolated
`run_mesh_preview.py --job C:/Project/RemixJobs/20261016-050350Z-6dffd5be --textures --smoke --nearest-filter`
test. Installed AperturePBR_Model.mdl declares Nearest=0, Linear=1; material
defaults Linear. Author `int inputs:filter_mode=0` on exactly five primary-image
shaders in anonymous session only. Report paths/authored values; no GPU sampler
readback claim. No texture/DDS/USD file, geometry, UV, camera, light or global
settings changes; no other sampling diagnostic simultaneously. Compare existing
unchanged control and base-only views. This is a discrimination test, not adoption
of nearest filtering or a live renderer policy. Public NVIDIA main source suggests
material sampler overrides can bypass global mip patching; not verified against
installed f337894d and therefore SPECULATIVE for this preview.

Same Python3.12.14/Kit110.1.1/Toolkit1.6.0-dev, child-only NRC-off, bounded_job
180s/256MiB scratch (128MiB warning)/8MiB console, three PNGs <=8MiB each,
64KiB reports. Expected <=3MiB ordinary evidence; no continuous capture or
multi-GB trace. Scoped sandbox exception only for graphics initialization, no UAC
gameplay request/security change. Guard owns cleanup; require zero remaining
processes/source hashes unchanged. Preserve cache-excluded verified archive;
optional cleanup only exact owned scratch after archive, never shared caches.

2026-10-16. Sponsor authorized a one-click preview after installed Toolkit UI
offered only Save/Save As/Close Project and ingestion required a queued result.
Status: actual saved geometry visible in the separate viewer; sponsor recognized
the ship. Camera labels corrected after sponsor identified +X/front and +Z/side
for this mesh. No universal engine/world-axis contract inferred.
Purpose: recognize the already accepted452triangle mesh without another conversion,
SFC run, game-mod project or source repair. This is a small diagnostic viewer using
the **installed Remix Hydra renderer/Kit libraries**, not the normal Toolkit project
workspace, a new final renderer architecture or live integration.

## Source / configuration / launch

Sources under `tools/remix_ingest`: `start_mesh_preview.cmd`,
`run_mesh_preview.py`, `sfc_mesh_preview.kit`, `kit_mesh_preview.py`, tests.
Windows Explorer double-click `start_mesh_preview.cmd`; no PowerShell policy/UAC
required by design. It uses configured bundled Python3.12.14 and existing x86
bounded_job.exe (MSVC14.51), installed Kit110.1.1/Toolkit
1.6.0-dev+main.30229.3f23f80a.gl. No vendor installation edit, extension download,
new DLL in SFC or admin-service requirement. A restricted sandbox startup issue
remains separate from running the ordinary desktop launcher.

Input is pinned real ingestion `C:\Project\RemixJobs\20261015-231057Z-19b131ce`;
requires accepted nonfixture result and452triangle corner comparison plus USD SHA256
`59B9C57ADAD61BEF4244F34B631B833BD6C34416791D3108ADE0537A64592696`.
Copies USD into a fresh `C:\Project\RemixJobs\preview-<UTC>-<id>` folder. Never
reload/resave original evidence. Toolkit revision and exact launch/script/Kit/guard
hashes preserved per job. Generated portable cache/data/log root inside scratch;
shared driver caches remain outside full isolation, never delete them.

Launch by prepared CMD, or configured Python:

```powershell
python tools/remix_ingest/run_mesh_preview.py --prepare-only
python tools/remix_ingest/run_mesh_preview.py --smoke
python tools/remix_ingest/run_mesh_preview.py
```

First prepares only; second is no-window rendering validation; third opens the
separate interactive viewer. Each invocation gets fresh outputs. No unbounded
startup/shader warm-up or re-ingestion. No helper/agents. Other open Remix windows
are untouched; close only this preview using its button or window.

Final process-only renderer environment: DXVK_GRAPHICS_PRESET_TYPE=4,
RTX_INTEGRATE_INDIRECT_MODE=0 (reference importance sampling, **NRC off**),
DXVK_RTX_CONFIG_FILE points to the copied `preview_renderer.conf` (bloom off).
Installed bridge/source docs and actual log corroborate option values. No global
environment/preference change requested. Initial default NRC run produced black
output and VK_ERROR_DEVICE_LOST; do not repeat that baseline blindly. Vendor may
write shared caches/user config or automatically send crash telemetry; that is
outside portable isolation and is not proof of a pristine whole-machine state.

## Rendering / interpretation

Anonymous USD session layer holds synthetic perspective camera, neutral dome/key
lights only. No mesh positions/normals/winding/material/source attributes changed;
Final dome intensity0.7/key2.0, camera fStop0.0, no artificial face repair.
known100x importer parent transform retained. Camera fits **world** bounds; does
not "correct" scale/axes. Buttons Angled/Front/Side/Above reposition the camera,
not the mesh. Plain grey source-labelled material was already diagnostic, not
original SFC textures. Missing faces/inside-out appearance are findings to retain,
not permission for silent normal/handedness/back-face repairs.

Report renderer request/mesh count/bounds and verify source+scratch USD hashes.
Rendered screenshot demonstrates only this synthetic setup. Human recognizable
ship/face visibility still require observation; do not infer full Stage B/gate
PASS from a successful launch or PNG file alone.

## Bounds / evidence / cleanup

Explicit launcher start, auto-close120seconds after ready,180seconds total guard.
One Windows Job Object atomically owns only spawned Kit tree; failures/deadline
kill only its descendants. Console hard cap8MiB; scratch128MiB warning/256MiB
polled stop (25ms, may overshoot; not disk quota). Ready/config/result reports
<=64KiB; fixed1024x640 PNG:one interactive or three smoke, <=8MiB each checked
after write. No continuous screenshots/video or high-volume geometry hooks.

Outputs: copied input, script/config/launch metadata, portable/console log,
job-result/preview-ready/preview-result JSON, angled.png (and above/side for smoke).
Final smoke uses above/front images (historical jobs used above/side). Source
hashes rechecked after exit. Final smoke16.641s,647768polled peak scratch bytes,
24448console bytes; clean interactive run127.625s/exit0/no remaining owned process.
Early brighter diagnostic jobs reached ~2.75MB scratch, still far below limits.
Kit caches can grow substantially; existing guard bounds
portable scratch, not external global driver/system caches.

Retain useful evidence in a verified ZIP before optional exact-job-folder cleanup;
do not delete originals, accepted capture/ingestion, vendor install or shared
caches. No game cleanup needed because this workflow never launches/touches SFC.
Implementation/offline/runtime/visual results recorded in the execution run record.
# Sampling-settings observation addendum — 2026-10-16

Question: does the existing preview expose a mip/filter/upscaling override that
could explain softness? One prepared `--textures --smoke` replay of the accepted
textured import, not a game run or modified image/material. Existing tool/version,
launch, child-only NRC-off/bloom-off and180s/256MiB/8MiB limits retained.
New `preview_sampling_audit.py` reads published Kit settings after Remix readiness:
`/rtx`, `/rtx-transient`, `/renderer`, persistent renderer-settings extension.
Only relevant scalar keys;256 values/8192 visited nodes/depth16/string256chars;
`preview-sampling-audit.json` uses existing64KiB exclusive writer. No setters or
changes to installed Toolkit/global settings. Missing values remain unavailable,
not zero/default. Published settings do not prove actual native Remix options or
per-pixel sampled mips. Hardware feature support in logs is not active filtering.
Three PNGs remain <=8MiB each; no unbounded trace or multi-GB mechanism. Same
owned-process cleanup/source-hash verification and cache-excluded archive policy.
# Base-mip-only A/B addendum — 2026-10-16 sponsor approved

Question: is lower-mip availability responsible for the observed preview softness?
Run existing textured smoke baseline versus `--textures --smoke --base-mip-only`.
New opt-in helper changes only five DDS files in the newly owned scratch directory:
observed BC7/DX10/256²/single-array layout only; retain exact base compressed payload,
strip lower levels and update mip count/caps/header flags. Independently decode
before/after and require identical RGBA pixels. Never recompress, sharpen, flip,
upscale or change source/installed/import files. Geometry/UV/lights/camera/config
remain unchanged, except scratch dependency hashes and diagnostic metadata.
Existing Python/Pillow/Toolkit versions, NRC-off child environment,180s job/
256MiB scratch/8MiB console/three8MiB PNG limits and cleanup remain. Tool SHA,
each original/derivative hash and byte size recorded in new job. Compare fixed
above/angled/front PNGs against the previous unchanged baseline; capture-to-capture
variation can exist, so absence of broad improvement is not per-pixel mip telemetry.
No game run or UAC task; archive useful output without caches, no deletion/commit.
# Mip-policy candidate — 2026-10-16 sponsor authorized

One `--textures --smoke --sharper-mip` test requests `rtx.nativeMipBias=-1` in
the NEW scratch child config only; full original DDS mip chains/base pixels,
geometry/UV/lights/camera remain unchanged. Exclusive with base-mip-only mode.
Native option identifier present in installed x64 runtime; prior official option
documentation describes negative bias as higher-detail preference, not a guarantee
of applied value. No native getter: record requested setting, not false readback.
Retain existing NRC-off environment/180s/256MiB/8MiB/three-PNG guards and cleanup.
Compare existing baseline and base-only reference at fixed views. No default,
vendor/global/game config change; no continuous/moving-camera qualification claimed.
