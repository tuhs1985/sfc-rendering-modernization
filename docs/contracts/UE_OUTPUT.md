# UE output contract v1

Experimental backend contract. This record covers the descriptor and lease
state machine in `src/rendering/ue/ue_output_contract.h` and
`ue_output_leases.h`. The current diagnostic GPU exporter still uses explicit
process arguments. Wiring these types into persistent GPU publication is pending.

The descriptor is 280 bytes under x86 and x64. It carries 128-bit session
identity, asset content, owner epoch, revision, source frame and sequence,
camera/pose and cohort hashes, activation, device and target generations,
output sequence, resource/slot epochs, peer PIDs, adapter LUID, dimensions,
64-bit producer-owned NT texture/fence handles, completion values and formats.
Export width/height are distinct from the full native target width/height.
Explicit viewport x/y place the image without changing its captured projection.
Admission rejects overflow, clipping and a changed viewport on an existing lease.

Live admission requires explicit source frame and sequence. Replay descriptors
require explicit diagnostic admission and cannot enter the default live path.
Do not fill absent native fields with guessed values.

The producer owns its NT handles. A named, current-user-only session mapping
will carry descriptors. The receiver duplicates them from the exact expected
producer process. Opening a numeric handle in another process directly is invalid.
Compare actual LUID and opened descriptors. Native game-pool handles retain their
existing 32-bit constraints. Normalize into that pool instead of truncating the
64-bit producer handles.

Colour uses B8G8R8A8_UNORM. Native depth and owner coverage use R32_FLOAT, with
owner bits copied by `asfloat(owner)`. Source linear depth requires conversion
through the original projection. The native empty-depth sentinel is -1234.

## Lease behavior

There are two slots. Publish only an idle slot, with a new slot epoch. Validate
the full source identity against the expected transaction, then compare the
resource descriptor against the admitted lease. Keep GPU objects until release.

Publication does not imply GPU completion. Acquire requires the producer fence
to have reached the ticket's value. Release requires both a matching receipt
and the consumer fence to have reached its value. A later GPU timeline value
completes earlier work. UINT64_MAX indicates device removal and cannot qualify
completion. Shared fence values increase across both slots.

Stop prevents new publications/acquisitions and retires outstanding slots.
An unacquired slot can cancel only after its producer write completes.
An acquired slot still needs its matching completed read. A lost acknowledgement
keeps that generation retired. A new epoch cannot reuse those resources early.

Budget calculations cover two UE source planes, four export planes, four
normalization planes and six native game-pool planes, at four bytes each.
The conservative total is 64 bytes per full-target pixel against the existing 128 MiB cap.
Diagnostic readback staging is additional and requires separate reservation.

`ue_output_normalizer.h` can draw directly into caller-owned native-format
targets. It creates shader/views once on resource admission and updates only
constants per frame. Colour, physical depth and packed owner coverage are written
in one draw. Margins are cleared, and opaque black retains valid coverage.
It owns no image allocations, waits, readback or file access. The caller must
hold input leases and qualify GPU completion before publishing the destination.
This helper is not yet connected to the actual UE exporter or game pool.

## Verification

The x86/x64 fixture sends 27 valid/invalid descriptors to actual child processes,
preserving handles above UINT32_MAX. It exercises wrong sessions, owners, assets,
revisions, frames, camera/cohort identity, peer processes, LUIDs, generations,
formats/bounds, and diagnostic versus live admission.

In-process lease tests cover matching/stale acknowledgements, stopped pools,
two slots, shared-fence monotonicity, resource reuse and generation rejection.
These are state-machine checks. The [actual GPU experiment](../runs/2026-11-22-codex-ue-actual-gpu-output.md)
separately establishes UE-to-D3D11 resource sharing and GPU fences.
Persistent publication, real GPU pool reuse, resize and cancellation in flight
remain required before native insertion.

The separate Windows GPU fixture now reuses two real slots over twelve changing
frames, forcing both occupied before a delayed consumer acknowledges either.
Its early-disconnect case retains unacknowledged output. This does not establish
persistent UE publication. The normalization fixture separately checks 17,974,164
GPU pixel values across odd dimensions, the historical 1280×360 case and a
1720×1020 tactical image at 200,30 in a 1920×1080 target. It recreates targets
while retaining the normalizer, with changing frames, margins and exact bits.
