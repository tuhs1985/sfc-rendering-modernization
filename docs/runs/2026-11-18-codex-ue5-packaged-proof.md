# First packaged UE5 captured-scene proof

November 17–18, 2026. Local uncommitted work on
`codex/expand-rendering-interface`, parent `e07a025`. The accepted Remix alpha,
game installs, appearance settings and existing renderer remain unchanged.

## Result

A real Win64 Development package built and rendered captured SFC geometry,
original primary images and captured model/view/projection data with UE 5.8.4.
It runs without the editor, Remix or a D3D9 device. No `.mod` import or OBJ
conversion is involved. Source geometry comes from the independently checked
runtime packets and replay manifests. Original image files are read from the
verified local test game and verified against their captured associations.

The package is local at
`artifacts/ue5-proof/first-captured-scene/package/Windows`.
It contains 56 files, 1,011,799,909 bytes. Runtime executable SHA256 is
`84319fa7dcd19f3e48bb8361861cf17953e37d5ef137c12949a12b78fb5642d8`.
The complete proof workspace, including UE intermediate build/cook files and
local inputs, is 7.75 GiB. No new full game copy was made. All generated assets
and package files remain ignored, outside source Git.

## Implementation and conventions

- Authored project: `src/ue5_proof`. Preparation, build and independent pixel
  comparison: `tools/ue5_proof`. Build recipe was exercised end to end.
- UE `UProceduralMeshComponent` uses one vertex per captured corner and one
  section per group. Constructed positions, normals, UVs and triangle indices
  are read back and checked. No topology repair or source UV change is made.
- Captured column-vector model/view transforms are evaluated before adapting
  camera space to UE forward/right/up as `(-z,x,y)`. The captured projection
  is converted to UE row-vector reversed-depth form. The scene-capture axis
  swap is corroborated by the installed Epic source
  `Engine/Source/Runtime/Renderer/Private/SceneCaptureRendering.cpp`.
- Original top-row-first BGRA images feed an unlit, two-sided source-colour
  material with nearest filtering. No Remix UV correction, generated material,
  colour adjustment, emission, lighting or postprocessing is imported.
- Captured tactical output is 1720×1020 at offset (200,30) within the 1920×1080
  window. No camera repositioning is used to make the ship larger. The saved
  Bird-of-Prey sample is distant, only seven covered pixels, so a larger F-FF
  fixture provides the meaningful texture comparison.
- `-SFCFrame=N` explicitly selects a retained pose sample. Fragment sample
  ordinals are not claimed as native frame/sequence IDs. Their sessions remain
  separate from the intact ships.
- One BMP and receipt are written after 30 captured frames. `-SFCExit` exits
  normally afterward. Without it, the static inspection window remains open.

## Verification

UE 5.8.4, changelist 58902052, bundled .NET 10, MSVC 14.44.35228 and Windows SDK
22621 were used. The missing .NET Framework 4.8 SDK and targeting pack were
added through Visual Studio setup. One compile worker avoids the workstation's
initial memory-pressure failure. Shader workers were limited during cooking.
Editor compilation, content generation (zero errors/warnings), cooking and
packaging succeeded. The first material cook exposed an incompatible default
sampler and was replaced by a matching linear placeholder. The first render
was empty because AInfo hides its owning game-mode actor by default. Explicit
visibility corrected it. Both failed attempts remain local diagnostic evidence.

The **final package** ran serially in four separate processes, all exit 0.
Receipts matched the selected source packet, exact captured frame object and
constructed-array checks. The GPU was RTX 4070 Ti, NVIDIA driver 621.01, DX12
SM6. A separate software rasterizer used the original source arrays, captured
matrices, depth buffering and perspective-correct UVs, rather than UE's adapted
arrays. Comparison excludes triangle edges and nearly black source samples.

| Fixture | Corners / groups | Interior pixels | Within 3 colour levels | Mean maximum-channel error | Actor construction to readback | Process start to normal exit |
| --- | --- | --- | --- | --- | --- | --- |
| K-FF sample 0 | 1356 / 5 | 4 | 100% | 0 | 0.462 s | 3.172 s |
| F-FF sample 0 | 11511 / 35 | 8762 | 98.33% | 0.308 | 0.620 s | 2.906 s |
| F-CA fragment 1 sample 0 | 2667 / 19 | 213 | 99.53% | 0.033 | 0.617 s | 2.890 s |
| Same fragment sample 7 | 2667 / 19 | 209 | 99.04% | 0.086 | 0.592 s | 2.907 s |

The two fragment poses changed 285 output pixels. This establishes changing
captured content, not metadata alone. Small raster/nearest-sampling differences
remain; this is not pixel-identical rendering. Distant K-FF establishes placement
but provides too few samples to qualify texture detail by itself.

Focused Python checks passed: three new asymmetric texture/file comparison
tests and nine existing scene-bundle tests. The negative test detects a vertical
texture flip. OpenSpec strict validation and `git diff --check` passed.

The exact sponsor CMD launcher was also exercised with `-SFCExit`, returned 0,
and produced the expected F-FF receipt with constructed-array checks. No UE
editor, shader worker or packaged-proof processes remained after these checks.

Evidence directories are `artifacts/ue5-proof/first-captured-scene/qualified-0`,
`second-captured-scene/qualified-0`, and
`captured-fragment-poses/qualified-{0,7}`. Each has the BMP, reference, difference,
pixel comparison, actual UE receipt, process receipt and runtime log. The package
receipt is `first-captured-scene/package-receipt.json`. Startup-to-first-displayed
pixel and steady frame performance have **not** been measured. The timed
readback occurs after 30 frames and is not first-frame latency.

## Sponsor checkout and next action

For the larger intact ship, run:

```cmd
cmd.exe /d /c call "C:\Project\SFC-Modernize Engine\artifacts\ue5-proof\first-captured-scene\SFC-UE5-Federation-Proof.cmd"
```

This opens a static UE window using the original captured SFC camera. Close it
normally. `SFC-UE5-Proof.cmd` in the same folder selects the distant K-FF instead.
The package and original images are private local validation inputs, not a
redistributable release. Sponsor visual checkout remains pending.

The sponsor subsequently launched the package and reported no discoverable
normal close action. Alt+F4 was supplied as the current operating-system close
method. This confirms launch, not broad visual acceptance. Exit/Escape support
belongs to the next implementation. The sponsor requested the
[UE integration review](../reconnaissance/2026-11-18-ue-integration-review.md)
before live input. Its findings supersede the immediate next-action ordering
below: first qualify world-space replay and resource ownership.

Next connect the UE consumer to retained live scene updates using the existing
upstream interface. Qualify UE colour/depth/owner GPU return independently
before native suppression. This increment does not provide live SFC attachment,
UE return to SFC, lighting, damage, animated destruction or a stable public DLL
SDK. The two remaining SFC-07 transient/native-pixel gaps remain open.
