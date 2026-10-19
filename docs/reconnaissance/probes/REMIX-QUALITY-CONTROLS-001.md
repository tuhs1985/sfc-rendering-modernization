# REMIX-QUALITY-CONTROLS-001 — bounded quality control proof

2026-10-19. Question: verify native filtering,mip,temporal AA and denoiser options
on the pinned Remix1.5.2/SDK0.6.4 direct SDK path. Supersampling>1is deliberately
not implemented: pinned SDK CopyRenderingOutput uses NEAREST,not a quality resolve.
Do not advertise a scale knob which merely enlarges/picks pixels.

Build with existing build_live_return.ps1 plus build_image_probe.ps1 (VS2026,
x86/x64 C++20). Offline pixel experiment:
`python tools/remix_runtime/run_image_probe.py --execute --quality`.
No SFC launch/injection. Uses owned hidden128square SDK scene,synthetic slanted
checker texture with8mips and a controlled lamp for denoiser comparisons.10cases,
64frames each,16final16x16 samples;record spatial/temporal luminance statistics,
not screenshots. Compare option effects,not just API return codes.

Exact tool/runtime/compiler/driver pins: existing dependency manifest. Same bounds
as image probe:60s internal/75s runner wall,250ms cap polling,16MiB warning/32MiB
hard log limit. Expected output<128KiB including synthetic DDS. Current-user worker
files only. Start/stop immediate/finite;kill/wait only owned child on timeout.
Use existing elevated parent if GPU access requires it;do not prompt for routine
UAC or change security policy. No global vendor tracing/multi-GB output.

Live quality.toml relay:500ms poll,16KiB config,48byte packet,256edits,16snapshots
plus latest/100console messages. Packet8uint32 (magic0x31544C51,version1,enabled,
anisotropic,samples,AAenum,denoise,reserved0),2floats (mip bias,scale1),FNV1a64.
Native application after output completion/lease idle. Initial disabled does
nothing;false after edits restores pre-quality runtime defaults. Invalid file or
unsupported supersampling preserves last valid profile. Native option failure
attempts rollback then stops optional host;original SFC still renders normally.

Cleanup uses established GPU/window shutdown. SDK40warning is separately open.
Output and proof receipts stay under ignored runs;curated summaries/versioned
run record remain in docs. Existing texture-output cap128MiB/session and overall
10GB evidence cap still apply to full return fixtures. Archive/consolidate verified
duplicate fixture textures before a repeat matrix if required;never remove originals.

## Explicit SDK sampler relationship

Associated pinned [C++ SDK defaults](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/public/include/remix/remix.h)
set MaterialInfo.filterMode=1 (Linear),while zero-initialized C records leave0.
CreateMaterial passes that byte into native material data. Enabled quality now
sets1 explicitly and recreates scoped host material/mesh bindings on quality
revision,using the existing completed-output retirement boundary. Disabled
quality restores0;texture UVs,images,wrapping and captured geometry stay untouched.
Do not conflate this field with global anisotropy or material highlight anisotropy.
The tenth pixel case uses the previous field0 as an explicit point reference.

Only native option acceptance is established for global AF/mip options when
differences remain below1%of measured spatial variance;do not promote tiny noisy
differences. Native temporal AA and denoiser effects plus explicit linear/point
sampler difference must be measured before qualification can pass. Mip bias is
not an image sharpening filter and cannot add missing texture resolution.

Current return matrix14cases includes quality reload,invalidSS and restoration.
Disk reservation tightened from384to192MiB:128MiB image cap+32MiB other output+
32MiB margin. Actual capture caps NOT raised;overall10GB guard remains active.
