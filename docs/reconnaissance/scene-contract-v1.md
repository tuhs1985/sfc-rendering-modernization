# Neutral scene view v1 — offline D3D9 proof

2026-10-19. Experimental,rigid mainline scope only. This is NOT a replacement
for the established live capture protocol,and NOT closure of the
[renderer-independent boundary gate](../decisions/2026-10-18-renderer-independent-boundary-gate.md).

## Meaning / provenance

`tools/scene_bridge/scene_bundle.py` adapts already captured mesh packets and
same-owner/revision state rows. It reuses existing game-format validation and
qualified native17word arithmetic without importing a Remix SDK or USD API.
Directories named`remix_ingest` currently house some reusable validators;their
filesystem name is not evidence of a renderer dependency. Do not relocate them
and stale all earlier qualification receipts merely for naming consistency.

`scene.json` records capture session,packet/reference/update/metadata SHA256,
source row numbers,model filename,geometry content hash,asset image/group hash,
coherent frame records and explicit unavailable capabilities. The model filename
is an identity label:geometry is decoded from the runtime packet,NEVER the MOD.
Image files alone are resolved from same-capture resource filenames. Native
resource IDs/pointers are not reusable image or renderer handles.

Identity:(source session,owner epoch,asset revision). Reusable asset identity:
captured geometry/group content and original primary-image hashes. Each frame
contains model/view/projection from ONE96word source row;source-composed matrix
is preserved separately for an independent projection oracle. This is a coherent
OWNER snapshot,not a claim of a sealed complete multi-object engine frame.

Position/native units,corner normal and UV preserved. Native transform decoding
honors affine dispatch flag rather than casting17words to a graphics matrix.
Effective column-vector convention:p_out=R*p_in+t. No geometry fit,centering,
normal repair,face reversal,world offset or texture-coordinate flip.

## Local replay files — NOT live transport

`scene.bin`:little-endian header8uint32:magic0x31534653,version1,nvertices,
nindices,ngroups,nframes,width,height;then32byte XYZ/normal/UV vertices,32bit
indices,16byte group records(id,material-index,first-index,index-count),224byte
frame records. Frame:owner/revision/source-frame/active fouruint32,then three
16float model/view/projection matrices plus fourfloat native viewport(x,y,w,h).
Per-folder manifest binds session/content. Native consumer accepts only this
single replay namespace;this is not an authenticated cross-process interchange.

Limits:32768corner vertices,triangular count,one complete permutation of corner
indices,256groups,16frames,2MiB geometry/frame file. Preserve distinct corners for
normal/UV seams,regroup triangle indices by captured rendering group. This copy
is an explicit offline adapter representation,not a second source of truth.

`texture-N.bin`:fouruint32 magic0x31544653,width,height,bytecount,then top-row-first
BGRA8. Original encoded colors decoded by Pillow,no exposure/gamma/levels bake.
<=4096eachdimension,256resources,128MiB combined original/decoded image preparation.
Original-file and decoded-pixel hashes remain distinct. First proof rejects alpha
images/untextured or missing primary associations rather than substituting.

No backend material handle belongs in these files. Secondary images remain in
the preserved source association but are NOT applied by this consumer. Native
light joining,secondary contribution,alpha/blend semantics and material parity
are explicitly unqualified;first proof is unlit original PRIMARY color.

## D3D9 adapter-specific choices

`tools/d3d9_proof/d3d9_replay.cpp` imports no Remix/scene capture headers. It loads
the absolute Windows system D3D9 library,verifies loaded x86 PE32 identity and
audits its owned process for Remix/ReShade/DXVK modules. No game proxy chain.

Transpose the effective column matrices for D3D9 row-vector SetTransform ONLY.
Use captured native perspective/depth directly;no generic OpenGL Z remap. Windows
D3D9 raster pixel centers are integer;oracle accounts for that explicitly without
changing captured geometry. Native1920x1080 viewport maps to960x540 proof output,
with explicit integer viewport rounding;not an automatically fit camera.

Ordinary XYZ/NORMAL/TEX1 managed VB plus32bit IB;group texture bindings and
DrawIndexedPrimitive. No UP calls,pretransformed vertices or shaders. Point
sampling,wrap,one mip,opaque,two-sided,unlit,encoded color/no sRGB conversion are
DIAGNOSTIC choices,not newly adopted production image/material settings. Standard
D24S8 depth on this standalone D3D9 device is NOT shared SFC scene depth.

The Remix adapter's V=1-v correction is NOT used. Actual primary texture sampling
is independently checked against raw captured UVs and original decoded pixels.
D3D12 must qualify its own adapter choices;none is inherited merely by API name.

## Validation / limits of conclusions

- Original captured geometry and both VB/IB uploads read back byte-identical;
  texture upload rows read back byte-identical,group indices/material mapping
  checked through independent software raster+perspective UV/color sampling.
- Native-composed projection oracle requires mask IoU>=0.95 and no mismatch
  beyond1pixel. Actual measured capture masks>=0.998. Raster top-left/texel-boundary
  precision excluded explicitly,not fixed by altering input.
- Texture claim requires>=64interior pixels and>=98%exact encoded BGR agreement.
  Tiny frames remain placement-only evidence;at least one qualified frame per
  asset mandatory. A39pixel sample with one mismatch is NOT called qualified.
- Known synthetic translation,rotation,camera and asymmetric UV/group controls
  are mechanical tests,not invented SFC observations. Captured scenes remain
  separate evidence. Readback is OFFLINE ONLY,not a proposed real-time CPU path.
- Device Reset/resize verified;retired-instance visibility flag and another owner
  using the same asset exercised. These simple controls do NOT qualify live
  pointer reuse,simultaneous scene transactions,asset revisions or dynamic loss.

Run73 extends this view to ordinary64bit D3D9/Remix output without SDK mesh calls;
actual static image/depth/projection proven within one process. Missing:SDK adapter
consuming this exact view,separate32bit consumer/ownership,live frame sealing,
cadence/timing,live depth/coverage exchange and in-game composition.
No complete renderer portability,playability,universal asset or milestone claim.

References:[transition plan](d3d9-adapter-transition-plan.md),
[Microsoft transform pipeline](https://learn.microsoft.com/en-us/windows/win32/dxtecharts/the-direct3d-transformation-pipeline),
[D3D9 SetTransform](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-settransform).
