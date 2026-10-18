# Textured additive delivery — experimental profile v4

2026-10-18; authority: sponsor requests steady, original-textured delivery at
screen-space resolution. Status: **offline qualified; SFC runtime pending**.
This is NOT original-ship replacement or a milestone exit claim.

**Run31 correction:**full-HD transport originally concealed a256-square hidden
HWND and SDK auto-resize. Hidden client now matches output;actual swapchain size
is checked after every Present,with explicit textured internal resolution scale1.0.
Mismatch fails open for SFC. New textured qualification requires recorded actual
resolution and silhouette IoU>=0.98 in addition to edge limits below. Run30's
0.920925 textured result is historical,not current sharpness qualification.
See [Run31](../runs/2026-10-18-codex-textured-resolution-correction.md).

## Separation from the strict diagnostic baseline

`-TexturedShip` selects an explicit delayed-additive profile: triplet version 4,
diagnostic mode 2. Existing version 3 strict frame/pose/camera matching and
256-square magenta `-VisibleShip` remain available unchanged. Versions and modes
cannot be mixed. Do not use buffered v4 output to suppress native ships.

The newest completed image may be displayed between publications while its
source request is at most **100 ms old at display enqueue**. This is request-age,
not measured photon latency or exact simulation age. Every displayed image keeps
its actual captured frame, pose, camera and sequence; it is never relabelled as
the current pose. A small visible delay during motion is possible. No reprojection
or cached-pixel warp is performed.

Both acquisition and late display validate session, PID, owner epoch, asset and
revision, source/model/LOD identity, resources, viewport and diagnostic offset.
Current frame cannot precede the captured frame. Expiry, retirement, disconnect,
disable or identity change hides output. An already enqueued GPU display may
complete. Native SFC drawing always continues; missing output is simply omitted.

## Resolution, geometry and original images

Actual producer/shared/private GPU targets are **1920 x 1080**. Display spans the
captured native viewport; it is not an upper-corner inset. Unsupported display
dimensions fail closed for the extra image. The legacy compatibility control
prefix still says 256 x 256: v4 GPU descriptors and manifest `output_size`, NOT
that prefix, describe actual output. Four RGBA surfaces total 33,177,600 bytes,
within the existing 128 MiB output reservation. Higher-than-screen rendering and
downsampling (supersampling) are deferred; no arbitrary larger size is enabled.

Fresh semantic packets supply the complete selected rigid mesh and same-packet
resource associations. Worker-side preparation resolves original primary images
from the separate test installation, copies originals, hashes them and derives
PNG/DDS. Materials deduplicate by original image SHA; only index ordering is
regrouped for surfaces. Positions, per-corner normals and UVs are unchanged.
No saved ship or missing-image substitute is used at runtime.

**Run34 current policy:**primary images are reflected surface colour only;
emissiveTexture=null,intensity0,emissive constant0. One white directional inspection
light replaces the tiny world-origin sphere in textured mode because emissionOFF
exposed its ineffective illumination at native ship distances. Direction
(0,-.70710678,-.70710678),angular diameter.53deg,radiance(1,1,1),not native light
recovery. Legacy mode sphere unchanged. Earlier fullbright-primary illumination was
identified as a washout contributor,not native emission evidence. This is still
not recovery of SFC lighting. Secondary images remain
in provenance, not guessed as glow. Missing primary, unqualified primary alpha,
unsupported mesh or safety-limit failure produces a partial result, not a wrong
asset. Texture fidelity does not imply native shading parity.

`textured_asset.py` is a worker adapter; `ship_textured_asset.h` is explicitly
Remix-specific. Adapter packet: 40-byte `<8IQ` header (magic 0x31585453, version 1,
counts, payload bytes, reserved zero, FNV64), 80-byte `<Q72s` material records,
16-byte `<4I` groups, then uint32 indices. Maximum 2 MiB, 256 materials/groups;
indices cover captured corners exactly once. Only SHA-named DDS basenames under
session textures are accepted. This is not yet a renderer-independent contract.
The [future-renderer technical gate](../decisions/2026-10-18-renderer-independent-boundary-gate.md)
remains OPEN.

## Ownership and limits

Existing current-user mappings, single in-flight GPU lease/ack and nonblocking
readiness remain. The 496-byte wire/152-byte key and 4 KiB control mapping retain
their allocation; semantic 16 MiB transport is unchanged. No game-callback image
decoding, disk IO, allocation, waits or readback is added. Busy ACK locks retry
without losing a valid pending GPU lease. Host GPU/publish timeout remains 5 s.

Images: 256 unique resources, 4096-square maximum, 128 MiB original/derived output
with 64 MiB warning. Existing 256 MiB decoded/GPU asset reservation is not a claim
about total SDK VRAM. Non-image logs/evidence: 32 MiB, warning 16 MiB, summaries
after limits; no continuous images or geometry firehose. Profile reserves 384 MiB
of disk/run allowance before launch, including archive coexistence. Overall
sponsor allowance remains 10 GB. Archive useful evidence after review.

## Offline corroboration and remaining uncertainties

Final eight GPU fixtures and exact pins are recorded in
[Run30](../runs/2026-10-18-codex-textured-hd-delivery.md). Normal and slow textured
fixtures displayed on all 59 sampled synthetic-motion callbacks. Renderer death,
expired output, disable/retirement and legacy strict regressions pass. This is
**CONFIRMED offline**, not proof of steady gameplay delivery on every owner.

Textured RGB-derived coverage has raw IoU 0.920925, NOT the old magenta 0.95 gate.
Explicit textured criteria require area ratio 0.90–1.10, centroid within one native
pixel, and at most max(8, 0.1% predicted pixels) outside a three-pixel edge band.
Observed centroid 0.340621 px, area 1.008622, unexpected/missing beyond band 1/5.
Legacy magenta remains IoU >=0.95 (observed 0.994603). Shifted geometry and corrupt
background regressions reject. Pixel-perfect appearance is unproven.

Cold shader output around 0.52 s is rejected by age policy; warmed output around
6 ms was observed. Full offline workflows take about 21–23 s including asset
preparation and fixture phases. Instant asset loading is NOT established.
Single qualified owner/revision only; arbitrary damage/deformation and asset
changes are not qualified. Retained scene depth/effects/UI overlap, synchronized
replacement and native lighting remain separate work. SDK shutdown warning 40
(`common device objects were not disposed of.`) remains unresolved.

## Backend-specific texture-origin policy — 2026-10-18

Run37 measured opposite image origins between the accepted captured OBJ/Blender
path and pinned Remix SDK/DDS. Run38 converts `v_sdk = 1 - v_captured`,U unchanged,
ONLY inside `ship_live_host.cpp` when filling textured Remix SDK vertices,using
`remix_texture_coordinates.h`. It does not change scene transport,raw packets,
live-mesh.bin,exported OBJ or original/derived image rows. No second flip allowed.
Material provenance labels this as a Remix adapter choice,not engine data.

**Do not carry this into a future D3D9/D3D12 or other renderer adapter by default.**
That adapter must qualify its own image/UV convention. DirectX version alone does
not decide it. This is not a claim that Remix is defective;it is missing adapter
normalization. Run39 sponsor accepts the corrected texture orientation for the
qualified ship in actual game output;full native lighting/material parity remains
unqualified. Do not generalize one ship's acceptance to all model conventions.
