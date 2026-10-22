# Synchronized presentation buffer — version 1

Status: Run107 SFC test exposed alternating-frame regression; Run108 fixes
ownership and adds early/late offline qualification. Buffered SFC retest pending.
This is bounded delivery work, not prediction, replacement,
an appearance change, or an aggregate TRL claim.

## Contract

The default-off `SFC_D3D9_SYNC_BUFFER=1` child-process option saves the complete
pre-ReShade-effects native backbuffer and its matching native depth. At the next
adjacent game frame, it presents that saved scene with only the returned Remix
image bearing the saved scene's owner/revision, input sequence and camera hash.
The current original scene is captured before the saved scene is restored.
Native HUD pixels in the backbuffer travel with the scene; later ReShade UI and
the OS hardware cursor are not deliberately delayed.

Two preallocated local GPU history slots hold color and resolved R32 depth.
The qualified input is 1920×1080 single-sample BGRA/RGBA8 color and eight-sample
R32 native depth. Depth resolves to the closest sample; any non-finite or
out-of-range sample invalidates that pixel rather than inventing visibility.
Deferred execution restores the immediate graphics state. Existing GPU shared
output ownership/fences remain in force; history uses same-context GPU ordering.
No CPU GPU-completion wait or image readback is added to the game callback.

### Run108 output ownership correction

Buffered mode explicitly propagates to the separate output worker. Its writer
reserves ONLY idle slots; READY images are immutable until consumed/rejected.
The unbuffered latest-wins policy remains unchanged. If both slots are occupied,
skip a publication nonblockingly and count busy; never overwrite a queued image.

For buffered mode only, each imported slot has an `ID3D11Fence`. The game thread
signals its monotonically increasing value after the compositor draw. The
existing worker polls `GetCompletedValue` and returns the slot to idle as soon
as the GPU read completes, including between Presents. The worker never calls
the game immediate context; it polls at the existing bounded worker cadence.
No extra image buffers, context locks, CPU waits or explicit callback flushes.
Unsupported fence/context interfaces park buffered insertion safely. Signal
failure or device-removed sentinel sets the existing error path; do not release
an uncertain GPU lease. Unbuffered EVENT-query retirement is unchanged.

Microsoft documents that [Signal](https://learn.microsoft.com/en-us/windows/win32/api/d3d11_3/nf-d3d11_3-id3d11devicecontext4-signal)
updates only after preceding GPU work completes, and
[GetCompletedValue](https://learn.microsoft.com/en-us/windows/win32/api/d3d11_3/nf-d3d11_3-id3d11fence-getcompletedvalue)
reads fence completion. This backend-specific synchronization is not a new
renderer-neutral scene requirement. No D3D9/D3D12 portability claim is added.

Admission requires consecutive, nonwrapped game-frame IDs, unchanged active
owner/revision/model/source identity, valid sequences, monotonic time, and age
no greater than 50 ms. The intended delay is ONE frame; 50 ms is an expiry
ceiling, not an intentional three-frame buffer. Camera changes are allowed only
because the entire saved scene and its matching camera/output move together.
An output already ready for the current frame remains available for its next
presentation; older-than-saved output is rejected.

If the matching ship is late, the saved native scene still advances without the
extra ship. Never retain an old overlay on a new camera scene or freeze the game
to hide a deadline miss. Disable, disconnect, invalid identity, retirement,
unsupported resources, or caught resource/command failure flushes history and
leaves original drawing. Resize/device recreation safely omits the effect;
recovery can require a fresh supported session, not automatic pool recreation.
Shutdown stops the worker before releasing storage. Original ships remain ON.

## Bounds and evidence

- Additional history: 33,177,600 GPU bytes; conservative fourteen full-resolution
  32-bit surfaces including existing resources: 116,121,600 bytes, below 128 MiB.
- Existing bridge/capture limits stay unchanged. Audit: 8,192 × 72-byte records
  plus a 64-byte header (589,888 bytes), fixed reserved mapping region below
  12 MiB. After saturation increment dropped counters; do not grow storage.
- Audit version1 magic `0x31424653`, offset `11 MiB + 128 KiB + 4096`.
  Session/PID bind records. Status1=paired; 2=scene without returned ship;
  3=warmup; 4=reset. Decoder rejects false frame/sequence/hash provenance,
  malformed layout and inconsistent maximum age. Native current-Present audit
  remains separate: its intentional N versus N−1 mismatch is NOT buffer failure.
- 90-second tactical window, five-minute prepared workflow, existing output/log
  limits, no continuous screenshots or diagnostic geometry hook.

## Qualification and use

Build `tools/d3d9_proof/build_synchronized_buffer.ps1` and
`tools/remix_runtime/build_return_probe.ps1`; run Python tests. Validate an
unbuffered persistent fixture first, then a separate fixture with
`--synchronized-buffer` and another with `--synchronized-buffer --buffer-early-ready`.
Both phases must demonstrate worker fence releases, retained READY policy and
zero overwritten outputs. GPU unit tests now33 per architecture; native slot
tests649checks include full/pending/queued safety and600step early-ready replay.
Refresh light, persistent and synchronized qualifiers (the latter requires
`--fixture <late-run> --early-fixture <early-run>`);
the buffered fixture must NOT overwrite the unbuffered display qualification.
The new launcher rejects stale source/binary/config receipts before launching.

Use `tools/d3d9_proof/start_d3d9_buffered_scene_session.ps1`; `-CheckOnly` starts
no game. It uses the existing elevated-parent workflow, copied test client,
current lighting/material/image/quality settings and existing player fixture.
No new UAC policy, semantic hook, native API translator, or Toolkit dependency.

See [probe](probes/D3D9-SYNC-BUFFER-001.md),
[run](../runs/2026-10-21-codex-synchronized-buffer-implementation.md) and
[curated evidence](evidence/20261021-synchronized-buffer-prepared.json).
CONFIRMED: offline whole-scene/HUD/depth correspondence and bounded operation.
STRONG HYPOTHESIS: one extra frame can reduce actual SFC late-output blips.
Run107 disproved the original implementation's runtime continuity: the old
latest-wins writer conflicted with its delayed consumer. Do not reuse Run106
offline PASS as proof this corrected build works in actual SFC.
Unresolved: SFC responsiveness, actual camera-transition continuity, and misses
beyond the additional frame. No physical input-to-photon latency measurement.
