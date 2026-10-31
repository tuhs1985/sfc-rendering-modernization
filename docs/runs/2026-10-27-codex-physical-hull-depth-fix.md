# Run215 — solid hull coverage independent of Remix reflections

2026-10-27 America/New_York; parent e4d1e33. Sponsor authorizes resolving the
Run214 lettering holes. Prior unstaged work preserved. No game launched by Codex.
Current lighting/material/image/quality profiles and original assets unchanged.

## Implementation

Pinned NVIDIA CopyRenderingOutput exposes colour, primary depth, normals,
picking and GUI, but no distinct physical first-hit depth. Run214 proved primary
depth may describe a reflected surface or reflection miss. Do not patch Remix,
disable mirror features, alter roughness or fill holes heuristically.

New `tools/d3d9_proof/physical_hull_depth.h` uses a standard D3D11 depth-tested
raster pass over the SAME captured triangles and current matrices. It writes
nearest physical hull depth into the existing R32 depth output; existing union
coverage and compositor consume that. Clear -1234 denotes genuinely uncovered
pixels. Colour still comes from ordinary D3D9 intercepted by pinned Remix1.6.1;
PSRR/PSTR and appearance settings remain unchanged. No ray-traced colour is
substituted, no RGB key and no guessed mask expansion.

One immutable auxiliary vertex/index pair is prepared per admitted resident
content. Shared owners reuse it. Geometry is not rebuilt across camera changes.
The external renderer stores at most32mesh/pose submissions and rasterizes only
the instances actually submitted for that returned colour frame. Player-only
replacement filters remain intact. The worker alone creates resources/submits
GPU work; no new SFC callback wait, allocation, file access, refresh cap or game
hook. Additional resident geometry is charged against existing256MiB asset cap.

Full returned-image viewport is essential: the receiver maps colour and depth
into the native tactical viewport once. Initial offline attempt double-applied
the native viewport, failed alignment, and is preserved as `fixed-replay`.
Corrected `fixed-aligned` has exact reference coverage. Canonical matrices/UVs
are unchanged; this is a Remix-output adapter convention, not a source-data fix.

The physical pass is queued after vendor colour-copy completion, before the
existing grade/coverage batch and existing worker fence. No additional shared
surface/lease or cross-process synchronization contract. One private D32 buffer
adds8,294,400bytes at1920x1080; conservative full controlled output accounting
is16four-byte planes=132,710,400bytes (126.5625MiB), below128MiB. No space for
another full-size surface should be assumed. Union coverage is still not
per-object picking. Current supported geometry is opaque rigid triangles;
translucent/skinned/unsupported geometry is not newly qualified. Current AA-off baseline is tested; temporal jitter/edge treatment is not newly qualified.

Supporting documentation: [pinned API](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/public/include/remix/remix_c.h),
[D3D11 depth testing](https://learn.microsoft.com/en-us/windows/win32/direct3d11/d3d10-graphics-programming-guide-output-merger-stage).

## Validation

[Versionable evidence](../reconnaissance/evidence/20261027-physical-hull-depth-fix.json).

- Captured FCA replay, reflections enabled: all65missing pixels restored.
  Coverage exactly matches all15,267pixels of the reflection-disabled diagnostic
  reference: zero extra/zero missing. Depth max difference1.61e-6, mean2.24e-7.
  Native lights were not replayed; not a live-colour duplication claim.
- Colour pipeline/settings unchanged. Independent runs' colour bytes are not
  identical (mean absolute byte difference0.0229/255); no deterministic exact
  colour equivalence claim. Physical output does not modify the colour texture.
- Actual GPU unit test60checks: translation,rotation,viewport convention,
  clipping,nearest overlap in either submission order,inactivity/retirement,
 32instance bound and immutable geometry reuse. Existing combined-post65checks
  and native host tests pass; normal/candidate strict builds pass.
-579Python tests pass. Actual replacement window600/600initially,599/600final repeat with the same compiled host; forced miss/source-gap
  tests rearm correctly and explicit stop stays off. Fault384/600includes the
  intentional stop at400, not a steady-delivery failure.
- Final-source normal591/600,initial596/600,late596/600,tuning596/600; all unchanged
  qualification gates pass. Frozen381file material comparison retained. Graphics
  state/resize/recreation,normal owned exits and API shutdown pass. Both actual
  replacement/tuning launch preflights pass. No receipts manually edited.
- FullHD GPU timing, captured19,110vertices/indices,9batches of32draws:
  median4.414microseconds per depth pass. Measures GPU-only steady cached pose,
  not CPU overhead,end-to-end latency or all-ship stress scaling. Benchmark
  commands/results under artifacts/player-replacement/run215.
- Existing vendor device-objects warning retained; process exits are verified,
  not proof of universal vendor GPU-resource teardown correctness.

One late fixture and a final-repeat initial fixture refused1024MiB scratch reservations before launch. Completed
initial evidence was SHA-verified archived, temporarily restored for comparison,
then returned to archived state. Retry passed unchanged limits. Closed second
game-run GPU derivatives and standalone bulk similarly archived with receipts;
original gate packets/results/logs retained. Closed older standalone DLL/rollback copies also archived with decompressed hashes checked;installed files untouched. Final-source gates were refreshed after a formatting-only fix;host binary hash identical. Aggregate18,888,917,604bytes at
evidence generation, below20GB. Restore archived raw inputs before reuse.

## Files / repository / next action

Implementation: new physical_hull_depth.h; d3d9_direct_host.cpp;
multi_scene_runtime.h; build_direct64.ps1; new physical_hull_depth_tests.cpp;
player_replacement.py (requires physical-depth exercise/native GPU evidence).
Documentation: this record/evidence, transaction/probe, STATUS and HANDOFF.
Existing Run211–214 unstaged changes retained; nothing staged, committed or
pushed. No original client binary/config/assets changed. Rendering/lights hashes
match Run213/current sponsor settings after temporary frozen comparisons.

Next sponsor runs the same player-replacement launcher, F-CA versus a different
model. Check black registry markings remain solid with a bright shield/effect
behind them, then ordinary camera/movement switches. Keep SFC open through
restoration and exit normally on cue. This is offline-qualified, not yet a new
gameplay PASS,alpha readiness or formal TRL completion. No discovery repeat,
material tuning,all-ship replacement or appearance change needed.
