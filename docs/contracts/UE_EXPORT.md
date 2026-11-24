# UE raw paired-output transport v1

Experimental, private to the UE backend. This does not change the neutral source
DLL wire, ordinary D3D9 submission or Remix output. It precedes the native-format
[output contract](UE_OUTPUT.md); a raw export is never insertion authorization.

## Payload and ownership

`src/rendering/ue/ue_export_channel.h` defines a 280-byte packet with full source
identity, producer/consumer PIDs, actual adapter LUID, tactical extent/offset,
full native target extent, resource and slot epochs, two 64-bit NT texture
handles, shared ready/acknowledgement fence handles/values, and original P22/P23.
The textures are B8G8R8A8_UNORM colour and R32_FLOAT linear scene depth. The
single qualified owner is explicit; multi-owner coverage is not established.

The producer owns two persistent sets of raw resources and both GPU fences.
The receiver duplicates handles from the held producer process, matches its
actual LUID, verifies opened descriptors and retains imported references. It
normalizes into two retained sets of three full native-target surfaces.
It does not stretch the tactical crop. Output colour, native physical depth and
packed owner bits are written together by the existing normalizer.

The mapping and notifications use a fresh Local namespace GUID and the same
current-user-only DACL pattern as existing IPC. Its header binds the session and
producer PID. A single child binds its PID once; the producer checks it against
the actual process it created. Process handles are retained through teardown.
This is shared metadata and GPU resources, never CPU image transport.

Explicit standalone replay packets require replay admission at both ends.
Saved/synthetic frames do not gain live provenance by being submitted again.
The diagnostic session is separate from its recorded source-session label.

## Slot and GPU ordering

Two slots progress Idle → Writing → Published → Reading → Complete → Idle.
The producer reserves only Idle storage. It copies both UE targets through
public RHI, restores shader-resource access, then queues a shared-fence signal
on the RHI execution path. Only afterward does it publish the immutable packet.
Publication means the descriptor is available, not that the GPU has finished.

The D3D11 worker queues a GPU wait on that ready value, normalizes the pair,
then signals its acknowledgement after the read. Completion receipts follow
observed GPU completion. The producer requires both exact receipt identity and
GPU fence completion before reusing the slot. Epochs/fence values increase.
UINT64_MAX never qualifies completion. The receiver consumes the oldest
published timeline value first; processing slots by numeric index could rewind
the shared acknowledgement timeline.

The UE submit path does not wait or flush RHI per frame. A busy pair skips
publication; it does not pause SFC. Source capture and native insertion are not
connected to this path yet. No additional source refresh-rate limit is added.
Target resizing uses an explicit retirement exchange. All slots drain, the
receiver drops old imports and normalized outputs, and only then acknowledges
retirement. UE releases the old exports before creating the next generation.
Fence timelines persist and old-generation publication is rejected. Device
change retires the renderer rather than silently reopening incompatible imports.
Injected device loss and failed generation allocation are tested; an actual
driver reset remains unqualified.

## Diagnostics and bounds

`SFCGpuStream` is explicit standalone orchestration and requires SFCDiagnostics.
Its frame count is a bounded test length, not normal-play lifetime. It alternates
fixture poses without rebuilding geometry. The receiver may capture at most four
triplets for comparison (outputs 1, 2, N-1 and N). One staging triplet is shared by the serial worker;
duplicating staging per slot would exceed the 1080p budget.

Without readback, the explicit surfaces cost eight bytes per tactical pixel for
two UE source targets, sixteen per tactical pixel for four exports and twenty-four
per native-target pixel for six normalized outputs. Diagnostic staging adds
twelve per native-target pixel. These fit the existing conservative 64-byte/full
pixel reservation and 128 MiB output cap at 1080p. Engine-internal scene rendering
resources are separate from this output-transport budget.

Optional QPC counters distinguish capture submission, descriptor publication,
receiver acquisition and observed GPU acknowledgement. Publication is a CPU
submission timestamp, not a GPU timestamp. Complete-output timing excludes the
later native drawing/presentation. Game-pool publication is now separately
qualified by the optional native-pool adapter; historical timings exclude it.
The native ExtraFrame deadline is not changed or renewed by this receiver.

## Current evidence

An actual Development package completed twelve alternating F-CA outputs through
one receiver process and two reused slots. Independent pixels distinguish 25,866
changed pixels; outputs 1/3 and 2/4 match their corresponding poses. Colour is
99.71%/99.73% within three levels of the source rasterizer. Native depth p99.5
error is below 1.2e-7 on stable surfaces. Coverage, margins and low owner IDs pass.
See [paired-output record](../runs/2026-11-22-codex-ue-persistent-output.md).
Development and Shipping both pass 600-output reuse with actual first/last
pixel comparisons. A Shipping no-readback run measures median 4.594 ms,
p95 5.510 ms, p99 6.305 ms and maximum 15.547 ms from capture submission to
observed normalized GPU completion. A separate Development run handles 49
target-generation changes in 100 outputs. This is not live SFC or an ExtraFrame
performance qualification. The native-pool boundary is separately qualified;
native SFC presentation remains unwired.

## Optional native-pool destination

An explicit producer option starts the same receiver with --game-pool.
The receiver qualifies original native source/target data independently, reserves
an existing pool slot, normalizes directly into it and publishes only after its
GPU fence completes. It does not allocate standalone normalized triplets in
this mode. Busy native slots skip output while completing the raw UE lease;
they never hold up SFC or get overwritten. Native-consumer read completion is
separate from UE raw-export completion. Retire both domains before recreation.

The option is not enabled by normal inspection. The explicit SFCGamePoolFixture
diagnostic mode additionally needs a precreated native-read event and paces test
frames until that consumer releases each GPU read lease. This event is not part
of live scheduling. See [qualification](../runs/2026-11-23-codex-ue-native-game-pool.md).
