# Run90 — returned texture origin and tactical viewport scale

2026-10-21 America/New_York. Sponsor reports last run fairly stable,asks restore
texture flip and verify apparently larger returned ship. Read HANDOFF/Run89 and
earlier Run37texture-origin evidence,actual loader/material/compositor/camera code.
Fuel Guard attached through trusted hook,no daemon. HEADd29111f7,index empty,prior
dirty work preserved. No helper/agents/SFC launch/stage/commit/push. M1 CONTINUES.

## Actual improved-worker run

artifacts/remix-runtime/runs/20261021-041259-542370-in-game:5290/5402eligible
observer matches(~97.93%)vs Run84~91.27%.112old/different and1no-completion audit,
1ineligible.5292actual image draws,75stale pool rejections,zero invalid/resource/
depth/busy failure. Different callbacks/counters,not interchangeable denominators.
5384host outputs through last displayed frame5695:median10.720ms,p9513.959ms,
max39.000ms. Do not claim all flicker/tail latency eliminated from sponsor's fairly
stable report. No new explicit full HUD/control checklist attestation.

Normal game exit,renderer0,accepted/copied client+launcher settings unchanged,
proxy restored. Controlled component unload NOT CONFIRMED:controller8/log says
"Target exited before controlled component removal." Result error:
"Semantic component removal/unload not confirmed; exit normally". This is process
exit reclamation,not controlled live unload. Does not erase valid image/timing
evidence or imply corrupted client. Do not attribute early exit to a user action
without evidence. Preserve actual run uncompressed;CompletedGame archival guard
requires controlled unload. Relay13.375s preparation_seconds includes workflow
waiting,not isolated asset-conversion timing. Run86stage timing remains distinct.

## Confirmed sizing defect / correction

Native captured viewport[200,30,1720,1020];Remix output full-frustum1920x1080
per existing actual-output qualification. Compositor nativeScreen path had forced
origin0,scale1 and identity scene-depth mapping. It treated full-frustum pixels as
already-native-screen pixels. Source output therefore magnified width1920/1720
=1.116279,height1080/1020=1.058824,and displaced image coordinates. Not a deliberately
enlarged ship or world-depth offset.

New native_viewport_mapping.h restores sampling origin[200,30],scale[1920/1720,
1080/1020]and corresponding native-depth lookup. Scissor still confines tactical
viewport;immediate graphics-state restoration remains. Only D3D9 nativeScreen mode
uses this correction;legacy SDK compositor path unchanged. No mesh/model scale,
camera matrices,geometry,UV,normals or raw positions modified.

analyze_viewport_scale.py compares all3493used positions over64sampled rows from
99qualified current-owner records against independent captured native composed
matrix. Corrected maximum error.000134391pixels;first-row old placement error
~109.981pixels. Camera-left displacement produces zero camera-depth change over
these samples. CONFIRMED numerical projection agreement,NOT an actual-game pixel-
silhouette comparison. Off-axis perspective can change apparent shape naturally;
do not adjust model scale by eye to compensate. Real-game visual confirmation pending.

## Remix-specific texture-origin correction

Earlier SDK path had v=1-v only in backend-owned vertex copies. Ordinary D3D9 now
correctly preserves raw UVs,but replacement materials bind top-row-first DDS
derivatives. Current sponsor observation plus accepted Run37bottom/top-origin
comparison motivates restoring the equivalent conversion AT THIS REMIX boundary,
not contaminating neutral scene data or every future DirectX backend.

material_binding.encode_remix_material_dds vertically reverses derivative image
rows once before encoding. Color,emission,roughness share the same rule. Original
image files,captured mesh/UVs,ordinary D3D9primary upload bytes/hash and SDK path
remain unchanged. No double V flip or altered physical material/light values.
Runtime keeps cheap layout/byte checks only;full pixel verification stays offline.
Source asset identity unchanged;derived DDS hashes intentionally change. Manifest
annotates origin policy. Extra conversion is one-time preparation,not per frame.

New default-off qualify_texture_origin.py draws asymmetric synthetic two-triangle
plate through ACTUAL ordinary D3D9+Remix replacement material pipeline. No SDK
geometry,no SFC asset substitution. Small synthetic control is diagnostic only,
not a replacement for real gameplay proof. Final64x64quadrants:
unflipped TL/TR/BL/BR red/green/blue/yellow;
corrected blue/yellow/red/green. Actual returned RGB samples support all four
labels. Case records/PNG comparisons in material-runs/20261021-042301-317933.
Normal jobs/API shutdown0;vendor disposal warning40remains unresolved.

Two earlier control attempts retained as PARTIAL:041952malformed compact USDA
syntax produced black ship;042128correct USDA with2x2bilinear/wrap mixing made
nearest-palette labeling ambiguous. Corrected generator to known-good USDA layout
and64x64constant quadrants;neither failure is promoted or blamed on SFC/Remix
capability. Final actual replacement-layer origin control PASS. Native appearance
parity of corrected real ship remains sponsor visual check,not asserted from quad.

## Reproduction / validation

Bundled Python,modern PowerShell,VS2026 x86;existing pinned runtime/header/proxy.

```powershell
python tools/d3d9_proof/analyze_viewport_scale.py artifacts/remix-runtime/runs/20261021-041259-542370-in-game
python tools/d3d9_proof/qualify_texture_origin.py --execute
pwsh -NoProfile -File tools/remix_runtime/build_return_probe.ps1
pwsh -NoProfile -File tools/d3d9_proof/build_receiver.ps1
python tools/remix_runtime/run_return_fixture.py --d3d9-additive --graceful
python -m unittest discover -s tests -p 'test_*.py'
python tools/remix_runtime/light_discovery.py
```

376Python tests PASS,including asymmetric channel/alpha-preserving flip,unchanged
input/no-runtime-readback,independent projection mismatch/invalid viewport tests.
Native pool/mapping44checks PASS,wire29,source timing18,deferred logs PASS;
returnwire37,expanded13,broad14,present calibration22checks PASS. Build-return
also compiled depth GPU fixture. No claim every compiled-only test was executed.
Actual-proxy corrected fixture20261021-042218-536774:599/600display window,
152363changed pixels,border untouched,state_errors0,resize/recreation,normal
owned exit. Synthetic depth and replayed lights,not SFC gameplay. Native-light
qualification refreshed. Additive source/binary/config receipt refreshed from
corrected fixture;CheckOnly preflight PASS,no launch. Known /O2/private-timer
worker implementation unchanged. Current four appearance TOMLs unchanged.

## Evidence preservation / final state

All three small controls'generated inputs/raw images recoverably compressed with
archive_material_fixture.ps1;decompressed hashes checked before exact-file removal.
Result.json,scene data,material layers,logs andquadrants.png retained,including
partial attempts. Corrected standalone compositor fixture199generated copies
82,187,512B ->6,861,548B ZIP,receipt binary-archive.json;raw source rows/logs kept.
Archive SHA2560102BE7BC58D5030E98238F79B0E4B81AC688D7E989865B53CBCF42F0962B1AE.
No game files removed. Aggregate9,877,923,768B/20GB;per-run caps unchanged.
Accepted/copied client SHA256 both unchanged:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.

Files:material_binding.py,test_normal_material_binding.py,qualify_texture_origin.py,
analyze_viewport_scale.py,test_native_viewport_scale.py,native_viewport_mapping.h,
ship_triplet_compositor.h,d3d9_game_output_tests.cpp,this record,curated evidence,
HANDOFF,contract/probe status notes. No unrelated cleanup. Index empty,all prior/
current work unstaged/uncommitted. No active owned process/session,commit or push.
git diff --check and record/JSON/path checks at close.

Exact next action:sponsor SAME Federation-cruiser two-ship fixture,observe saucer
markings and returned/native apparent size across a couple camera views,then normal
movement;exit only at runner cue to permit controlled cleanup. SAME launcher:
tools/d3d9_proof/start_d3d9_offset_ship_session.ps1. Extra ship remains left,original
retained. No all-model expansion or milestone completion claim.
