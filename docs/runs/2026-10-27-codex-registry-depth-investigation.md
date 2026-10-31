# Run214 — registry lettering holes traced to reflected depth

2026-10-27 America/New_York; parent e4d1e33. Prior unstaged work preserved.
Sponsor reports replacement worked apart from see-through black lettering.
Investigation only: no production code, settings, dependencies or assets changed.
No SFC launched by Codex.

## Latest gameplay

UTC-named `20261028-020234-504365-in-game` completed with error=null, normal exit,
controlled hook unload/controller0, renderer0, unchanged accepted critical files
and launcher settings. Protocol2:5301suppressed submissions,5291matching commits,
6cumulative repeats/peak2,2reactivations,3recoveries including shutdown,
1native rejection at final stop, generation6. Last ordinary cause OutputMiss.
NativeFallback presentations2 counts that state only, not total fallback duration.
This supports revised recovery operating in gameplay; seamless/alpha readiness
is not established. Sponsor reports replacement worked minus the lettering.

## Reproduction

[Machine-readable evidence](../reconnaissance/evidence/20261027-registry-depth-holes.json).
Standalone ordinary-D3D9 replay uses that run's captured first frame, prepared
textures/materials and pinned Remix1.6.1.1920x1080,24startup Presents,current
image/quality packets. Native lights were not replayed: this is not an exact
live-colour reproduction. Required diagnostic offset -0.0001 is identical in
each case, not a production setting change.

| Child-only setting | Valid depth/coverage pixels | Restored | Lost |
| --- | ---: | ---: | ---: |
| Existing reflection/transmission PSR | 15202 | 0 | 0 |
| Both PSR paths disabled | 15267 | 65 | 0 |
| Reflection PSR off; transmission ON | 15267 | 65 | 0 |

Every restored pixel had exactly background-depth sentinel -1234 in baseline.
The holes trace registry lettering and small related surface regions. Baseline
also has10068covered near-black pixels: no blanket black-colour transparency.
All56uploaded texture planes have alpha255 throughout. Successful children
exit0,stop_reason0,no remaining owned processes,normal API shutdown; peak scratch
approximately102.4MB. Vendor device-objects-not-disposed warning is retained;
process exit alone does not prove every GPU resource was explicitly released.

Initial setup attempts retained: dispatcher DLL could not load implementation;
next replay omitted referenced DDS paths/required offset. Corrected complete
replay passed. These are fixture setup errors, not production-path failures.
Scripts, hashes, images and recoverable bulk archive receipts are under
`artifacts/player-replacement/run214`; restore archived inputs before reuse.

## Findings

**CONFIRMED:** additive/replacement compositors and combined image/coverage pass
use depth/coverage, not RGB keying; accepted output is opaque. Generated material
opacity_constant=1 and uploaded source alpha is opaque.

**CONFIRMED:** pinned CopyRenderingOutput DEPTH exports m_primaryDepth. Reflection
PSR (Primary Surface Replacement) substitutes reflected surfaces in the G-buffer.
The resolver writes virtual-hit depth, or clearColorDepth on a primary miss.
Our adapter wrongly assumes that depth always describes the physical hull.
Reflection-only A/B restores all65holes without editing geometry,UVs,images or
material definitions. This is a reflected-depth/physical-coverage contract defect,
not proof that temporal AA or the black clear colour causes transparency.

Pinned NVIDIA sources, commit0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0:

- [Output API](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_remix_api.cpp): DEPTH=m_primaryDepth; FINAL_COLOR uses backbuffer in this pin, unlike older local1.5.2source.
- [Geometry resolver](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/shaders/rtx/algorithm/geometry_resolver.slangh): geometryResolverOutputMiss, virtual-hit projection and PSR.
- [Options](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_options.h): enablePSRR/enablePSTR describe special mirror/refraction paths, not all ray-traced reflections.

**STRONG HYPOTHESIS:** saved roughness generation (strength1,black0,gamma0.5)
makes dark markings very smooth, contributing to PSR eligibility. Exact
per-texel hit/eligibility not instrumented; do not change sponsor appearance to
hide this contract defect.

**HYPOTHESIS:** an aligned original hull previously filled the holes, masking
them before suppression. No historical same-view paired image/depth proof of
exact onset. Existing coverage predates suppression; do not blame buffering as
a confirmed cause.

## Disposition

Cause reproduced; production fix NOT applied. Prefer physical first-hull depth
and coverage independent of reflection shading, with exact source-frame pairing.
No RGB cutout, guessed hole filling or material changes. Child-only
enablePSRR=False is a demonstrated compatibility option with a special-mirror
quality tradeoff, not a silent baseline change.

Next inspect supported pinned outputs for physical first-hit depth. Current
CopyRenderingOutput enum exposes colour/depth/normals/picking/GUI, no separately
named first-hit depth. Picking alone cannot provide physical depth or presumed
semantic ownership. If none qualifies, define the smallest geometric-depth
adapter extension before implementation. Do not patch vendor code by default.

Only run record,evidence,STATUS and authoritative handoff changed in repository.
No rebuild required for documentation. JSON/path/diff/settings checks recorded;
all changes unstaged/uncommitted. No new sponsor gameplay needed for this cause.
