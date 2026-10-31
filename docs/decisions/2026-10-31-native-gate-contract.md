# Native insertion contract v1 — player F-CA comparison

Default off. This increment uses the existing captured geometry, retained D3D9 assets, Remix runtime, original textures, appearance controls and GPU transfer. It does not return through the Toolkit, replay shields, add prediction or change the game's refresh cap. The copied installation is the only gameplay target.

## Transaction and ownership

The native component calls the same-process `SFCNativeInsertionV1` interface: Acquire → Commit, or Cancel before commit. Renderer resources stay inside the return adapter. The interface uses fixed-size versioned records; it is not an external pointer/handle protocol.

A ticket contains session, source PID/thread, owner epoch, asset revision, original model/source/list identity, source frame, source sequence, full cohort hash, activation generation, native-frame start and absolute deadline. The immutable lease additionally binds the imported handles, packet checksum, slot resource epoch and tagged graphics-device identity. A fresh device/session is required after recreation; recycled resources cannot revive an old ticket.

Capture observes the original arguments first. The separate coordinator runs after `RecordHook` releases its critical section. A short snapshot lock is released before acquisition or flushing. Both known primary/secondary lists must qualify. The first selected primary decides the whole owner/frame; failed admission retains both original lists. Unknown/nested or ambiguous calls remain native.

Actual READY means the game-pool worker has copied colour/physical depth/coverage and its GPU fence has completed. It stamps and signals only then. The upstream renderer publication timestamp is insufficient. Notifications and current-user-only security descriptors are created before hooks; imports and per-slot GPU-read fences are prepared by the existing worker before a lease can be acquired.

The wait is on READY, stop and receiver-process exit. Every wake revalidates the ticket, with one absolute deadline. Strict is source-frame start + ceil(QPC frequency / 60); ExtraFrame is start + ceil(2 × frequency / 60). There is no deadline renewal, callback sleep, stale-pose substitution or refresh-rate setting change.

## Native insertion

The pinned batch flush is `0x006AB380`, with `ECX = manager + 0x1F4C`. It closes preceding queued work; it does not select or suppress an owner. Empty batches are skipped. Counts, mode and device are checked before calling. The offline extracted-function fixture checks actual client instructions, fake COM arguments, preserved registers and untouched manager fields. Client instruction bytes are not stored in the repository.

Commit validates the active native 1920×1080 RGBA8 typeless resource/linear UNORM view, 8×MSAA and R32 typeless/D32 depth view. The existing depth compositor writes the returned colour and physical depth, preserving graphics state. Coverage is the existing physical hull identity mask, never a black-colour key. This keeps black registry markings solid.

Only after insertion is queued does the coordinator pass count zero to the original selected wrapper at `0x006AC5A0`, for returns `0x0042E55D` / `0x0042E626`. Original wrapper/state maintenance continues. Capture data, mesh storage, simulation, effects and UI are unchanged. SFC draws later effects and text normally against the updated native targets. The old late compositor and old authorization are bypassed in this mode; their launchers remain separate diagnostics.

The slot stays acquired until SFC's GPU-read fence completes; the worker alone retires it. Before-commit failure cancels the lease and leaves native drawing. Unexpected after-commit failure retains resources, marks partial and disables later commits. It does not undo GPU writes or rewrite unknown native calls.

## Lifetime, bounds and measurement

Stop signals waiting coordinators first. The last committed primary/secondary frame may finish consistently; a subsequent native frame acknowledges the boundary. Capture/coordinator/hook-span activity must drain. Thread suspension checks PCs against complete hook stubs and trampolines before restoring hooks or unloading. The adapter reference and mapping outlive active dispatch.

The sidecar occupies 8,576 bytes in the existing reserved mapping, with a 64-record ring. An external evidence worker drains it; no callback file access is added. At most one gate request is active. There are two fixed output slots; the established conservative 116,121,600-byte output envelope remains below 128 MiB. The native game's existing MSAA targets are not additional shared output copies. Logs remain 32 MiB combined, evidence 20 GB, tactical observation 90 seconds and prepared workflow 285 seconds.

Records retain frame start, offer, gate entry/exit, actual pool readiness where observed, insertion and Present callback, source sequence/hash, owner/revision, generation/resource epoch, primary/secondary receipts, output occupancy and pending source slots. Analysis includes frame-period median/p95/p99/max, timeouts, longest fallback sequence, source age and rolling five-second queue/latency/reference-schedule drift. Present callbacks do not measure physical monitor scanout. Bounded queue occupancy alone does not prove that frame scheduling has not slipped against the 60 Hz reference.

The standalone comparison uses the same endpoints and 600 measured frames per run. It changes synthetic rigid poses, checks exact returned pixels twice against normally drawn near/far effects and depth-disabled text, and injects worker-only 12 ms / 32 ms completion delays on deterministic source frames. These injected fallbacks are intentional test stress, not sponsor gameplay acceptance. Diagnostic readback frames remain in raw evidence and are excluded from clean timing distributions. Gameplay explicitly removes fixture-only delays.

## Operating sequence

Build using `tools/native_insertion/build_gate.ps1` and the existing receiver/candidate-host builds. Freeze passing baseline/Strict/ExtraFrame receipts using `tools/native_insertion/qualify_gate.py`. The prepared gameplay launcher requires `-TimingPolicy Strict` or `-TimingPolicy ExtraFrame`; preflight rejects stale qualifications. It never elevates itself or silently replaces a failed test receipt.

Sponsor uses the unique F-CA fixture, begins still, rotates/moves/turns, changes camera, exposes shields, briefly pauses/unpauses and exits at the normal two-beep request. Strict goes first. Compare those observations separately from deterministic replay: manual runs are not identical. Neither a standalone fixture nor a functioning launcher proves seamless gameplay.

GPU-side shared-fence scheduling remains the next candidate if CPU coordination is too costly. It requires its own advance-reservation and renderer-loss contract; it is not introduced by this increment.
