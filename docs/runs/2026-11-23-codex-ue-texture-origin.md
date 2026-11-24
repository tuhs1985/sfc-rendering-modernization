# November 23 — reuse the known vertical texture conversion in UE

Sponsor confirms the UE flip is exactly the appearance corrected earlier in
Remix. Reuse the established conversion rather than another discovery pass:
U unchanged, vertical origin reversed, once per UE texture upload.

`ue_texture_origin.h` reverses rows into the transient UE texture's working
buffer. `USFCSessionSubsystem` calls it while filling the first mip. The original
decoded images, content identities, source UV/corner arrays, geometry and files
remain unchanged. There is no UV flip in addition to this row conversion, no
new material/shader pass, and no change to the existing Remix adapter.

## Verification

- The asymmetric 2×2 native fixture first fails `Bottom row not at UE V=0`
  with the previous straight copy. The corrected helper passes x86 and x64,
  checking preserved columns/channel values, original source bytes, padded rows
  and rejected truncated/zero-extent inputs.
- Shipping and Development build. Both packaged fixtures keep constructed
  positions, normals and UVs equal to the source and retain one mesh build.
- `texture-origin-{shipping,development}-01` compare 11,336 source interior
  pixels against the independent bottom-origin raster reference: **99.7089%**
  within three levels in each configuration. Direct comparison against the old
  top-origin interpretation matches only about **33.05%**, demonstrating that
  the conversion actually reaches rendered pixels.
- The reference rasterizer adds an explicit optional image-origin choice;
  its historical top-origin default remains unchanged for the old proof.
  Current UE qualification selects bottom origin, without rewriting its inputs.
  Three old-proof tests and five original-definition tests pass.
- `texture-origin-window-01` verifies the converted output still displays
  opaquely and aspect-fitted in the actual 1280×800 Slate window (IoU 0.947255).
- Read-only live-launch preflight and Git whitespace checks pass. No SFC
  gameplay is launched for these standalone checks.

The same launcher is ready for sponsor appearance confirmation. Task 3.5 stays
open until that result; no native game-pool insertion is connected. The reported
3–4 second live appearance delay remains recorded, not remeasured or claimed
fixed by this mapping correction. All changes remain uncommitted.

## Sponsor checkout passed — November 23

UTC-named run `20261124-011346-171859-in-game` completes with error=null,
3042 source snapshots, two asset definitions and 94 original images. Sponsor
confirms both textures are aligned and ships centered in the viewer. Game and
UE exit normally; graphics restoration, unchanged protected client/launcher
settings and no remaining owned controller are recorded. Hook cleanup is
process-exit reclamation, not a controlled live-unload claim.

Together with the documented passive cancellation, supervisor-death, relaunch
and standalone checks, this closes task 3.5. OpenSpec is now 16/30. The next
boundary is 4.1: connect UE's completed GPU output to the existing native game
pool/readiness path, with suppression disabled for the additive proof. Current
native_output/original_suppressed remain false. No appearance parity, game
insertion or resolution of the observed startup delay is claimed.
