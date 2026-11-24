# Persistent UE paired GPU output

November 22, 2026. Work resumed from committed/pushed `1834379` on renamed
`codex/ue-native-insertion`. Sponsor requested Fuel Guard and stopping at 5% of
the five-hour allowance. Initial refreshed allowance was 99%. New work remains
uncommitted. Alpha, source DLL, native insertion and appearance are unchanged.

## Implemented boundary

`FSFCOutputProducer` creates one persistent x64 D3D11 receiver, two pairs of
explicit shared DX12 textures and two shared GPU fences. It wraps those resources
through the pinned engine's public RHI. Each submission queues paired colour/depth
copies and its signal without a per-frame render-command flush or CPU wait.
The receiver uses the [raw export contract](../contracts/UE_EXPORT.md), selects
the same GPU by LUID, reuses imports/views/shaders/output targets and writes the
native triplet in one normalization draw. Exact acknowledged GPU reads govern
slot reuse. The original one-shot diagnostic remains available as a comparator.

`FSFCStreamCheck` is explicitly selected diagnostic orchestration. The normal
inspection path remains unchanged. Build receipts now include the external UE
adapter headers, so those dependencies cannot silently change during a build.

## Verification so far

- Raw packet/channel fixture passes actual child-process handshake, 64-bit NT
  handle values, repeated slot reuse, incomplete-GPU rejection, passive stop and
  cross-session rejection. Run this fixture in the desktop environment; restricted
  child execution could not complete its handshake, while the desktop run passed.
- The first UE build exposed the engine's hidden Windows atomic macros. Using
  explicit MSVC interlocked intrinsics and a standard publication fence resolved
  the compile issue without changing the engine.
- Actual Development F-CA test completed twelve outputs and reclaimed twelve
  leases. The independent source fixture alternates its original pose and a
  clearly labeled synthetic +24 native-unit translation. It retains all original
  geometry/images; no native frame identity is fabricated.
- Outputs 1/3 and 2/4 are exactly identical within each pose, while the poses
  differ at 25,866 pixels. Colour agrees at 99.71%/99.73% within three levels.
  Stable native-depth p99.5 errors are about 1.12e-7 and 1.16e-7, with owner
  coverage and cleared native viewport margins passing.
- Added low owner IDs 3 and 7 to the normalizer fixture, alongside normal and
  0xffffffff bit patterns. All 17,974,164 checks still pass, including the odd
  extent and historical 1280×360 layout case.

Initial diagnostic evidence is local at
`artifacts/ue-foundation/gpu-exchange/persistent-fca-01`. The twelve-output interval
is 0.692 seconds and includes four readback/file-writing triplets, with 31 busy
publication skips. It is not a normal-mode latency measurement. A timing-only
mode is being qualified separately; no SFC timing claim follows from this run.

The first receiver duplicated diagnostic staging per slot. It was reduced to one
worker-shared triplet before further qualification, keeping the explicit 1080p
surface allocations below the existing output budget. No output budget was raised.

## Failure, generation and Shipping qualification

The updated desktop fault campaign rejects passive receiver exit, crash after
acquisition, an acknowledgement beyond submitted work, a mismatched receipt and
an injected E_OUTOFMEMORY after partial export allocation. Those runs exit in
2.58–2.66 seconds overall. Wrong acknowledgement also added a producer timeline
bound; a future fence value cannot legitimize work never submitted.

Cancellation before first output submits zero frames and drains. Cancellation
during a deliberately held read submits two frames, completes one read and
cancels the unread second frame; both slots drain. No owned UE/receiver processes
remain afterward. A crashed read causes the standalone UE process to retire;
in-process restart after a lost read acknowledgement is not claimed.

A deliberately 50 ms slow receiver also completes twelve frames with correct
pixels/packet identity and no overwritten slot. Its 125 ms median output age
and busy skips are expected test-induced delays, not production timings.

The 600-frame no-readback run completes in 2.892 seconds of fixture operation.
Capture submission to observed normalized GPU completion is median 6.278 ms,
p95 7.672 ms, p99 8.577 ms and maximum 17.226 ms. None exceeds 33.333 ms.
There are 105 busy publication skips at the fixture's unrestricted rate, with
two outstanding slots maximum and no growing queue. The receiver creates no
recording directory. These measurements exclude SFC source receipt, contention
with its graphics work, the final game-pool transfer and native presentation.
They do not establish the live ExtraFrame acceptance gate.

Evidence: `persistent-no-readback-01/qualified.json`, `persistent-slow-01`,
`persistent-fault-summary.json`, and `persistent-cancel-*` beneath the same
local GPU evidence directory. Task 2.4 is now verified; plan status is 9/30.

Target retirement now drains all slots, drops receiver imports and normalized
outputs, acknowledges retirement, and releases UE exports before recreation.
Shared fence values continue across generations. A 100-output Development run
completes 49 target changes without readback: median 6.794 ms, p95 8.836 ms,
p99 15.547 ms, maximum 17.117 ms. The resize pixel fixture verifies both
1920x1080 and 1600x900 native targets, their tactical offsets, and depth.
Simulated device loss, stale device identity and allocation failure after old
generation retirement all reject. These are injected device-failure cases,
not an actual Windows driver-reset qualification.

Shipping passes pixels, resizing, and 600 no-readback outputs: median 4.594 ms,
p95 5.510 ms, p99 6.305 ms, maximum 15.547 ms; zero samples over 33.333 ms.
Both configurations also compare outputs 1, 2, 599 and 600 against independent
source rasterization and exact corresponding-pose pixels. All pass. Diagnostic
readback/file-writing intervals include large stalls and are not performance
baselines. Local evidence: `shipping-persistent-summary.json`,
`persistent-generation-summary.json`, `persistent-late-samples-01` and
`shipping-late-samples-01` under the GPU evidence directory.

The native source-reader fixture exposed a camera-before-assets coupling.
The neutral facade now returns coherent camera state before a ship revision is
admitted; original asset identity validation remains. Its recorded-data
qualification covers 91 frames and four fragments with camera-before-assets.
A new read-only C++ view also matches the existing native scene writer's exact
layout and bytes. Neither introduces a source wire or changes native capture.

Persistent live scene binding and existing native game-pool publication remain
unwired. No live insertion, suppression or complete production lifetime claim
follows from these standalone results.

## Direct source-reader increment

The C++ reader opens the existing protocol4 mapping with FILE_MAP_READ and a
held SYNCHRONIZE-only source-process handle. It does not write acknowledgements,
dereference game pointers or introduce a new frame format. Native layout checks
compare against the actual version3 scene writer, including damage padding and
slot stride. Actual separate-process tests check read-only mapping protection,
passive startup, PID/session mismatch, duplicates, producer exit and close.

One failing test demonstrated a legitimate publication race: the writer closes
a reused slot before advancing the header's current frame. A reader can briefly
see the new sealed slot under the old header number. This returns Retry rather
than an invalid-frame failure. Checksum and identity checks for admitted frames
remain. Existing native capture/writer code is unchanged.

`FSFCLiveSource` is a CPU-only adapter over that reader. The parent must supply
the selected owner epoch, revision and opaque model/source identities; it never
selects the first ship. Original model/view/projection and viewport are decoded
without basis conversion, then the existing UE world boundary applies its
adapter conversion. Missing rows leave retained geometry alone. Parent/source
exit closes the standalone renderer. No per-frame asset files or asset rebuilds.

The opt-in packaged source path accepts a late immutable source definition and
checks its session/owner/revision before world activation. Immediate Development
activation completes twelve accepted updates with one mesh build (0.173 seconds
preparation); delayed activation also passes (0.124 seconds preparation).
Independent source-space pixels agree at 99.73% within three levels for the
accepted sequence. Evidence: `source-reader/packaged-immediate-01` and
`packaged-passive-02`. The latter initially checked matrices/one mesh build;
the pixel comparison was added afterward and is covered by the immediate run.

These are explicitly synthetic changing-pose replays using original retained
arrays/images, not native gameplay. Subsequent qualification below completes
the base-admission boundary without claiming normal parent selection or
multi-owner lifetime.

`scene_definition.py` replaces fixture-specific assembly with a reusable
one-time publisher. Actual source IPC qualification compares its original
positions, corners, indices, images and frame against the independent exporter.
Four focused tests verify exact data, duplicate publication without writes,
wrong session/owner/revision/asset rejection, immutable revision identity and
cross-session publisher reuse rejection. A red/green test caught the latter:
the publisher now belongs to one session and cannot overwrite an old definition
under a new session label. The local schema optionally carries
PID/model/source binding labels; no source mapping or DLL protocol changes.

The packaged source mode now validates those binding labels as well as
session/owner/revision. A red/green Shipping fixture demonstrates the formerly
missing model binding rejection. Wrong session, owner, revision, opaque binding
and source stop before any asset are qualified. UE's existing graceful exit can
return zero even on rejection, so fixtures require an explicit rejection receipt
and absent success receipt, rather than treating zero as successful admission.
Normal parents must treat unexpected renderer exit as unavailable, irrespective
of that exit code.

Shipping accepts the fresh publisher's actual output, with one asset build and
unchanged image identity. Independently varying model and camera translations
match the exact accepted source sequence and rendered pixels (99.69% within
three levels); preparation is 0.163 seconds in that run. Delayed fresh-definition
admission also passes, 0.297 seconds preparation. Source updates skip obsolete
frames without queuing or rebuilding. Local evidence:
`source-reader/shipping-fresh-definition-01`, `shipping-moving-camera-01`,
`wrong-binding-red-01`, `wrong-binding-green-01`, and `shipping-wrong-*`.
The prior GPU output path still passes after the source/world refactor at
`gpu-exchange/shipping-source-refactor-01`.

Task 3.2 is now complete, plan 13/30. Multi-owner UE lifetimes/revisions/material
arrival, the normal parent/backend selector and native game-pool return remain
open. Seven existing break-transport tests pass in the desktop session (the
restricted sandbox cannot start that fixture); three UE-proof regressions and
strict OpenSpec validation also pass. Development and Shipping packages are
current. The refreshed Development package accepts a fresh definition and
independently changing camera/model data with one build (0.161 seconds) and
99.65% stable source-pixel agreement. Both meet the existing 97% tolerance.

The x64 scene-view fixture also measures 1/6/100/256 representative owner rows,
1,000 snapshots per case. Median copy/checksum/identity validation costs are
79.4/79.5/81.9/92.1 microseconds; p99 costs are 183.9/165.8/102.1/112.0
microseconds. Every snapshot copies the existing 103,464-byte frame. The largest
observed scheduling tail is 515.6 microseconds. This is an in-memory native
receipt benchmark, excluding matrix decoding, UE transforms/rendering and
cross-process scheduling. It does not complete task 3.4's representative UE owner
replay. Evidence: `source-reader/frame-view-timing.txt`; rerun the x64 native
scene-view test with `--benchmark`.
