# REMIX-ROUGHNESS-MAP-001 — optional artistic material derivative

## Current amendment — acknowledged cache retirement (Run61)

This supersedes the original retain-every-revision policy below. Same128MiB
combined image cap,64MiB warning,4096dimensions and256edit ceiling;none increased.
The cap measures generated/source image files,NOT machine RAM exhaustion.

Host writes a40byte atomic material-receipt.bin in its unique session directory:
little-endian magic0x314b414d,version1,processed revision uint64,active revision
uint64,status uint32(1applied/2rejected),reserved0,FNV64 of preceding32bytes.
Success follows original GPU-completion/receiver-idle boundary AND successful
old mesh/material destruction. Initial receipt follows initial asset creation.
Rejection follows candidate cleanup and retains previous active revision. Receipt
publishing retries on the existing500ms host worker poll;no SFC callback changes.

Worker permits ONE outstanding material revision. Missing/malformed/stale receipt
postpones further publication and protects current/in-flight maps;never guesses
that CONFIG_ACCEPTED means GPU application. Matching receipt permits deletion
only of session textures named roughness-<64hex source>-<16hex revision>.dds or
.pending outside active revision. Source/emission DDS and all nonmatching files
are untouched. Reject symlink/redirected cache directory or managed entry;locked
files remain and are retried. Unpublished partial generation is also reclaimed.
Unexpected receipt/IO failure cannot authorize deletion of active files.

New cache diagnostic explicitly names needed bytes/limit and says NOT system RAM.
Current+pending sets must genuinely fit128MiB;large assets or locked files may still
hit a legitimate budget limit. Last-good remains,not arbitrary cap increase.
Original generated maps are reproducible artistic derivatives:their hashes,
source and settings remain evidence,not every retired on-disk copy.

Validation expands existing --material-controls fixture to4consecutive enabled
map revisions,invalid edit,then disabled restoration:6accepted material profiles.
Private consumer holds the valid stationary state20additional seconds under
SFC_PRIVATE_MATERIAL_CACHE;the overall60s cap is unchanged. Private factory
material is published before asset preparation,not sponsor's mutable settings.
Require host acknowledgement,positive reclaimed byte count,no pending revision,
unchanged normal output/exit. Unit tests exercise30edits under1300byte synthetic
budget,delayed/corrupt/stale receipts and host rejection. All existing60s/32MiB
fixture,128MiB image and10GB session evidence controls still apply.

Question: can our pinned opaque Remix material consume a worker-generated
roughness image, reload it safely and restore uniform roughness?

Tooling: pinned Remix1.5.2 / SDK0.6.4, existing VS2026 C++20 host,
bundled Python/Pillow12.3.0/NumPy2.3.5. No wrapper/runtime change.

Static CONFIRMED: `remixapi_MaterialInfoOpaqueEXT` exposes roughnessTexture,
roughnessConstant, metallic, anisotropy and thin film, but no independent opaque
specular strength/reflectivity field. Do not relabel metallic, translucent IoR,
thin film or ray-sampling probabilities as that missing control. SDK header
artifacts/remix-runtime/deps/include/remix/remix_c.h remains unchanged.

## Implementation / contract

Existing material packet remains56bytes; version2 reuses six formerly reserved
floats for enabled,strength,black,white,invert,gamma. First four fields unchanged.
FNV64 covers first48bytes. Native reader accepts validated v1 as map-disabled,
or v2 with finite/range/boolean checks and white>black. No game ABI change.

Worker derives encoded Rec709 luminance from the already-qualified primary image,
levels/clamps it, applies exponent1/gamma, optionally inverts, then blends with
uniform roughness by strength. Quantize to8bit replicated RGB DDS. This is an
ARTISTIC APPROXIMATION, not a captured material/specular map. White=rough.
Source diffuse/emission files, geometry, UVs and existing lights remain unchanged.

Files are named with source-image digest and immutable material revision. Worker
finishes them before atomic packet publication. API roughnessTexture is bound
only when enabled; SDK constant remains the fallback. Regeneration/rebinding uses
existing GPU-complete/receiver-idle boundary and material retirement paths.
No SFC render callback IO, allocation, image generation or waits are added.

Output: session textures/roughness-<source>-<revision>.dds plus latest
roughness-manifest.json with source/derived hashes, dimensions, formula and byte
warning. Existing16 material config snapshots preserve settings history.
128-row processing strips limit intermediate floating-point storage. Maximum
4096x4096; combined session texture output128MiB, warning64MiB. No per-frame
generation;256 accepted material edits/session. Immutable old derivatives count
against the budget; saturation rejects edits and retains last good. Files can
grow by about4*width*height bytes per distinct image/revision, not per frame.

## Offline use before gameplay

Build: `pwsh -NoProfile -File tools/remix_runtime/build_live_return.ps1`.
Tests: bundled Python `-m unittest discover -s tests` (project-local TEMP/TMP).
Actual SDK fixture: bundled Python
`tools/remix_runtime/qualify_live_return.py --execute --material-controls`.
It uses recorded geometry + synthetic state, NEVER launches SFC; toggles map
on, rejects invalid roughness, restores uniform material. Existing private
consumer validates output/synchronization/cleanup. Source-matched full return,
image and quality qualification must be refreshed before sponsor gameplay.

Inherited fixture limits:60seconds/32MiB logs (16MiB warning),128MiB images,
192MiB reserved before each case, total retained evidence10GB. Existing pixel
probes75seconds/32MiB. No screenshots continuously. Any generated fixture
compaction must zip/decompress/hash-verify exact generated directories first.

## Gameplay after offline qualification only

Use existing elevated-parent start_light_tuning_session.ps1; process-scoped
execution-policy bypass, no global security/UAC changes. Same two-ship skirmish,
30minute tuning ceiling, normal exit. Initially map OFF: no appearance change.
Save materials.toml with enabled=true; observe markings/reflections, change only
one parameter at a time. Disable to return to uniform roughness. Original SFC
ship/HUD remain untouched; no suppression or milestone-completion claim.
Cleanup: existing runner restores copied installation, checks client hashes;
archive useful generated evidence after exit, never originals. No manual RE or
timestamps required from sponsor.

SDK binding acceptance is not proof that this artistic map improves fidelity.
Only a controlled visual comparison can establish usefulness; it does not prove
the cause of previous washout. Independent specular control remains unavailable
through this opaque-material API; no dummy slider is provided.
