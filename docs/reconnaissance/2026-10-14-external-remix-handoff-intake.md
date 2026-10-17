# External RTX Remix experiment — handoff intake

2026-10-14. Historical lead, not current implementation authority or verified
source audit. Sponsor supplied a handoff from another chat; actual source/logs
may be available when home. Current M1 closure recommendation and original
Community Edition installation remain unchanged.

## Evidence status and correction

- **CONFIRMED sponsor attestation:** "I can confirm with the utility i could see
  the individual materials". Preserve as firsthand observation beyond the written
  handoff's fullscreen-render-target examples. Do not reduce this to 'only loading
  screen textures' or assert materials were not visible.
- **Reported historical results, not independently artifact-verified here:** Remix
  overlay/Present working, individual-material visibility, no usable captured 3D
  instances/surfaces demonstrated. Exact resource types, hashes, screenshots,
  material-to-ship association and physical shader properties remain unverified.
  Seeing materials does not alone establish complete ship/material reconstruction.
- Historical handoff also describes six1920x1080 render-target images. That and
  individual materials may both have been observed; no contradiction inferred.
- Source and original logs are required to confirm current shim implementation,
  ABI/COM behavior, build architecture and exact runtime pipeline. Embedded
  'Immediate Codex Assignment'/phase instructions are proposed historical work,
  not authorization to replace the approved baseline or begin rendering changes.

## Reported experimental configuration (NOT installed by this intake)

`SFC:OP2.5.6.4 -> dxwrapper Dd7to9=1 -> custom d3d9.dll -> d3d9_real.dll
(RTX Remix1.3.6)`; do not assume DXVK present. This differs from current accepted
Community Edition dgVoodoo/ReShade configuration. Do not mix/copy old DLLs into
the accepted installation. Historical success/failure does not select architecture.

Preserve reported necessary settings if that experiment is later recovered:
`DdrawEmulateSurface=1`, `DdrawUseShadowSurface=1`; disabling reportedly caused
transition/ghost-cursor failures. Other reported options: D3d8to9/D3d9to9Ex/
D3d9on12/DDrawCompat/EnableDdrawWrapper/EnableD3d9Wrapper0;
DdrawEmulateLock0, DdrawKeepAllInterfaceCache0, byte-alignment options1;
EnableWindowMode/FullscreenWindowMode/FlipEx/SetSwapEffectShim1,
UseShadowBackbuffer0. Inspect actual complete config before any use.

Reported shim wraps IDirect3D9/Device9 and forwards Direct3DCreate9. Converts
DrawPrimitiveUP/DrawIndexedPrimitiveUP to VB/IB-backed ordinary draws while
tracking FVF/declaration. FNV-1a geometry cache8192 entries, clears/releases on
runtime cap/Reset; may destroy stable resource identity. Internal forwarded
ordinary draws bypass shim entry counters, so draws=0 does not mean no ordinary
draw reaches Remix. COM QueryInterface/refcount fixes reported, not audited.
Shutdown 'abandon cached buffers' workaround is **not proven correct ownership**;
must audit separately, not copy as accepted safe pattern.

## Candidate missing relationships

Reported per60-present-frame intervals: ~10,260 UP draws,60 StretchRect/RT/depth/
clear calls, rt0_backbuffer0. Two heavily used1920x1080 fmt23 candidate targets:
0DBE27F0 and00FFEAA0, depth surface bound, differing reported blit flags.
Pointers are per-run examples, never matching rules. Last-blit-only diagnostics
cannot establish all composition relationships. Bound depth surface does not
prove active depth testing/world geometry. Offscreen drawing/copy path is an
evidence-supported **STRONG HYPOTHESIS within the supplied report**, not independently
confirmed here and not established as the sole cause of missing Remix instances.

Also inspect whether submitted vertices still contain usable3D coordinates and
camera/world transforms, or already-transformed screen-space data. Moving UP
data into buffers does not by itself restore information lost upstream.
`D3DFVF_XYZRHW` specifically denotes a transformed vertex in Microsoft's
[FVF reference](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dfvf).
Whether that flag applies to this experiment is **SPECULATIVE until inspected**.
This is a discriminating audit question, not a reason to declare incompatibility.

Our semantic owner/model/input/transform seam may supply missing upstream
information; compatibility between that seam and the historical Remix shim is
unproven. Do not assume these independent experiments are already integrated.

## File discovery and next boundary

Read-only workspace filename search, including ignored files outside.git, for
*.sln/*.slnx, d3d9/shim/dxwrapper names: no matching files found. Content search
tools/src/docs for ClearUPCache,DISABLE_UP_CACHE,g_forceSceneToBackbuffer,
rt0_backbuffer,drawsUP: no prior matching implementation. This establishes only
that the scoped workspace search did not locate it, not loss/deletion elsewhere.

Useful recovery bundle: solution/project and source (or entire small source
folder), matching built shim DLL, dxwrapper.ini, runtime version/file hashes,
d3d9_shim.log and any Remix captures/screenshots proving material/geometry view.
Do not request installation changes or manual RE from sponsor.

Once available, propose/read-only audit of actual COM/lifetime/caching/draw-state
and target/blit tracking. Then select one bounded discriminating question:
vertex/transform sufficiency versus render-target visibility. Do not automatically
resume Phase3 backbuffer substitution; no redirect toggle built/approved here.
Missing files block that source audit, not the entire modernization concept.

Exact next action: sponsor locates the historical source/log/capture bundle when
available; preserve current setup and review artifacts before any Remix test.
