# Actual UE GPU output exchange

November 22, 2026. OpenSpec change `ue-native-insertion` remains in progress.
Implementation is unstaged on `codex/expand-rendering-interface`.

## Verified boundary

The packaged UE 5.8.4 Development executable renders the captured ship through
its existing source camera. An explicit committed DX12 shared texture is wrapped
with public `RHICreateTexture2DFromResource`. RHI commands copy the actual scene
capture into it, then a queued RHI command calls `RHISignalManualFence`.
The producer queues its GPU signal after the RHI copy. The D3D11 child imports
that shared fence and queues its GPU wait before reading, then signals a separate
GPU acknowledgement. Resources remain held until the child exits and both
completion values are checked.
The child duplicates the shared NT handle from the explicit parent PID and
selects that adapter by LUID. CPU readback exists only for diagnostic comparisons
after the GPU transfer. The reference UE readback occurs after export so it cannot
supply export readiness.

UE's generic Shared texture allocation exported a handle but D3D11 rejected
its import with E_INVALIDARG. Explicit committed resources with SHARED heap,
ALLOW_SIMULTANEOUS_ACCESS and ALLOW_RENDER_TARGET passed. The initial fence
signal was incorrectly called during recording and caused an assertion because
there was no active RHI context. Enqueueing the call on the RHI execution path
corrected that error. Depth target initialization also required a diagnostic
render-command drain before fetching its new resource.

## Results

- F-FF output at 1720×1020 matches every received colour pixel against UE.
  Independent source-colour comparison remains 99.50% within three levels.
- F-CA fragment poses 0 and 7 each produce distinct matching received images.
- Real UE R32_FLOAT scene depth matches independent source geometry. F-FF's
  8,784 interior pixels have maximum relative error 0.00006478.
- The D3D11 compute shader converts linear depth using the original source
  projection, `z_native = -P22 + P23 / depth`, and writes native depth and
  exact owner bits into R32_FLOAT outputs. It preserves the -1234 empty depth
  convention from the current physical-hull output path.
- F-FF native depth maximum error is 0.000003334. All 12,188 owner-covered
  pixels match source coverage, including black pixels. No background false
  owners occur. Fragment coverage counts are 286 and 292, with zero false owners.
- The close-camera fixture compares 267,558 stable depth pixels, maximum native
  error 0.00009713. Five hardware/reference edge differences are explicitly
  checked against adjacent reference surfaces. The coverage comparison finds
  13 edge pixels outside software coverage. This is recorded rather than
  claiming pixel-identical coverage against the software rasterizer.
- Missing consumer executable produces an explicit recoverable rejection.
  Exit-before-import, wrong acknowledgement and a fifteen-second bounded stalled
  child also reject. The last case terminates only the diagnostic child.
- Updated Development and Shipping packages pass the real F-CA input emitted by
  the neutral source reader. Every received colour pixel matches UE. Independent
  comparison is 99.71% within three levels; 11,398 stable depth pixels have maximum
  native error 0.000002590. All 15,685 owner pixels are attributed; one lies at a
  software/hardware coverage boundary. This is standalone evidence, not gameplay.
- Source-to-renderer preparation and readiness in this one Shipping fixture are
  0.211 and 0.470 seconds. These are internal offline timings, not live SFC startup
  or presentation latency, and the diagnostic process takes 4.54 seconds overall.

## Neutral source receipt

`src/rendering/ue/source_reader.py` receives original captured packets through
the existing Windows shared-memory transfers. Decoder ownership moves once to
the reader; existing callers retain their prior default. It preserves positions,
corner normals/UVs, polygon groups, original image hashes and primary/secondary
associations without Remix conversion. It emits coherent source frame/sequence,
camera, owner epoch/revision and explicit retirement records.

`tools/ue_wrapper/qualify_source_reader.py` replays 91 retained native frames
from `20261023-205121-223108-in-game`, verifies their original checksums and
explicitly adapts the historical layout into a fresh current-protocol session.
Four assets and owners are read. A second synthetic F-CA owner shares its cached
asset and images; retirement propagates and cross-session reuse rejects. Original
positions/corners match decoded packet arrays. Images occupy 91,772,928 bytes;
the receiver retains no duplicate decoded meshes. No new live SFC run occurred.

The resulting F-CA input is generated from the reader's admitted data and
captured matrices, not an old scene template. Development and Shipping then
render that input and export colour/depth to the independent D3D11 child. This
qualifies the source-reader boundary; continuous UE live binding is still open.

## Slot reuse and native-format normalization

The Windows fixture's `--check-pool` retains two physical sets of resources for
twelve changing frames. Both slots are deliberately occupied before a slow
consumer acknowledges the first. Pixel/depth/owner values match on every reuse.
`--check-pool-disconnect` exits with no acknowledgement and no slot reuse.
This is Windows-only qualification, not persistent UE publication.

`ue_output_normalizer.h` writes colour, native depth and owner bits together into
caller-owned targets using a single D3D11 draw. Its dedicated GPU test passes
17,974,164 pixel-value checks: an odd 11×7 source in a 19×13 target, 1280×360
at 0,180 in 1280×720, and 1720×1020 at 200,30 in 1920×1080. Target resources
are recreated while the same normalizer/shaders are retained. Checks include
changing frames, margins, valid opaque black and owner bits including 0xffffffff.
The first enlarged fixture failed because its CPU oracle treated all positive
linear depths as covered, including points beyond the native far plane. Applying
the original projection's clip interval to the oracle corrected the fixture;
the normalization implementation did not change.
No image is allocated, mapped or read back by the runtime helper. Diagnostic
upload/readback lives in the test. Publication fences and leases remain the caller's
responsibility. The normalizer is not yet wired to the UE export or game pool.

Evidence is in `artifacts/ue-foundation/gpu-exchange/`, including
`ue-final-summary.json`, `ue-depth-owners`, `depth-fragment-{0,7}` and
`depth-near-camera-edges`. These are local diagnostic inputs/outputs.

## Reproduction

Build the diagnostic consumer from a VS x64 developer prompt using the command
in the preceding Windows probe record, also linking `d3dcompiler.lib`.
Build UE with `tools/ue_wrapper/build.ps1 -Configuration Development`.

Run `tools/ue_wrapper/qualify.py` with the packaged executable, qualified scene
and a new output directory. Add `--gpu-exchange --gpu-depth --gpu-consumer
<absolute gpu_exchange_probe.exe>`. The consumed source owner is explicitly
the single qualified owner. Multi-owner depth-to-owner attribution is unqualified.

## Remaining production work

This diagnostic spawns a child per texture and blocks at explicit deadlines.
It does not implement the production two-slot pool or immutable complete-image
publication for continuous UE rendering. Real UE shared ready/acknowledgement
fences pass one-shot checks. The next implementation must combine these verified
boundaries with persistent resources and exact session/frame/camera/revision
identity. Resize, device generation, cancellation while GPU reads are in flight,
allocation failure and stalled consumers still require qualification.

Current diagnostic output is not native insertion authorization. Source capture,
native suppression and gameplay are not exercised by these runs.

## Sponsor-requested pause checkpoint

Stopped after the prepared viewport checks, with no owned UE/GPU helpers left.
Task 2.3 and 3.1 are now checked from the evidence above; plan status is 8/30.
Everything remains unstaged/uncommitted. Alpha and existing Remix operation are
unchanged. The next implementation step is persistent paired UE colour/depth
publication, integrating ready/acknowledgement leases and native normalization.
Keep actual resize/device generation and cancellation checks open. Do not start
a live SFC run before those lower-level boundaries are connected and qualified.
