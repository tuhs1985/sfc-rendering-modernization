# UE output contract v1

Experimental backend contract. This record covers the descriptor and lease
state machine in `src/rendering/ue/ue_output_contract.h` and
`ue_output_leases.h`. The one-shot comparator uses explicit process arguments.
The [raw paired-export protocol](UE_EXPORT.md) now qualifies persistent UE-to-
D3D11 exchange before normalization. The explicit UE game-pool adapter now
publishes independently qualified normalized output into the existing pool;
this is not current suppression authorization.

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
The receiver now uses this helper directly against existing native game-pool
targets when explicitly enabled; the default standalone path is unchanged.

## Verification

The x86/x64 fixture sends 27 valid/invalid descriptors to actual child processes,
preserving handles above UINT32_MAX. It exercises wrong sessions, owners, assets,
revisions, frames, camera/cohort identity, peer processes, LUIDs, generations,
formats/bounds, and diagnostic versus live admission.

In-process lease tests cover matching/stale acknowledgements, stopped pools,
two slots, shared-fence monotonicity, resource reuse and generation rejection.
These are state-machine checks. The [actual GPU experiment](../runs/2026-11-22-codex-ue-actual-gpu-output.md)
separately establishes UE-to-D3D11 resource sharing and GPU fences.
The later [persistent adapter](UE_EXPORT.md) qualifies actual UE publication,
two-slot GPU reuse, target-generation retirement, receiver failures and
cancellation during a read in both packaged configurations. Its normalized
outputs remain private by default. The later explicit native-pool adapter is
qualified below; native presentation still remains required for insertion.

The separate Windows GPU fixture now reuses two real slots over twelve changing
frames, forcing both occupied before a delayed consumer acknowledges either.
Its early-disconnect case retains unacknowledged output. This earlier fixture
is distinct from the later persistent UE test. The normalization fixture separately checks 17,974,164
GPU pixel values across odd dimensions, the historical 1280×360 case and a
1720×1020 tactical image at 200,30 in a 1920×1080 target. It recreates targets
while retaining the normalizer, with changing frames, margins and exact bits.

## Native pool adapter — November 23

The native-pool contract defines independent source/target admission and legacy
metadata mapping. The writer owns one late source binding and delegates
resources, reservation, publication and retirement to existing GameOutputWriter.
The receiver's --game-pool is default-off and rejects original-mesh replacement
authorization for this additive increment. GPU completion precedes READY;
native read leases remain independently owned. No additional output queue,
image surfaces or deadline are introduced.

Actual packaged UE/x64 receiver/x86 consumer tests and exact native resize,
held-slot and GPU-fence checks pass. See [boundary evidence](../runs/2026-11-23-codex-ue-native-game-pool.md).
Standalone read-completion event pacing and diagnostic readbacks are test-only.
Live native insertion and suppression are not established by these checks.

The final adapter cohort identity is the complete sealed native-frame checksum,
matching the existing native gate ticket; original camera/pose is checked
independently. A same-pose/different-seal fixture is rejected. The optional
additive native hook policy can commit output without zeroing either original
list. Actual hook checks pass; live insertion is still unqualified.

## Native-target pixel layout and additive gate — November 23

The existing native Pool now admits version 3 (legacy camera-surface pixels) or
version 4 (full native-target pixels). Version 4 requires NativePixelsFlag=2 in
reserved[2]; CohortFlag=1 remains independent. Version 3 forbids the new flag;
unknown flags and inconsistent versions are rejected before resource import.
Pool size stays 576 bytes, with the same two slots and metadata. Old receivers
reject version 4. Rebuild both endpoints when adopting this extension.

UE's writer alone opts into version 4. Its normalizer already clears native
margins and places the tactical crop at the original viewport offset. The native
compositor samples these images one-to-one, clipped to the qualified viewport.
Legacy version 3 and the default compositor argument keep their current Remix
mapping. No second crop/scale, allocation, queue or synchronization is added.

The explicit additive UE component now joins the retained registry to this
output path. A unique configured F-CA selects the player fixture; original
source identity is unchanged by a fixed UE-only native-world offset. The existing
Acquire/Commit boundary inserts colour/depth before later native effects/text,
while the additive hook leaves both original mesh lists unchanged. This mode
forbids replacement and all-ship authorization. Readiness follows normalization
and GPU completion; native read leases remain distinct from UE export leases.

Both packages pass 60 consecutive standalone native coordinator commits with
zero post-start misses and correct native occlusion. This does not establish live
SFC insertion; the prepared default-off gameplay checkout remains required.
See [qualification and command](../runs/2026-11-23-codex-ue-additive-insertion.md).

### Live additive result

The sponsor checkout now confirms correct native depth. The gate commits all
2,270 requested transactions with no timeout/invalid/partial result; native
cleanup restores protected files/settings. There are 433 no-request frames,
which require separate eligibility analysis before claiming seamless replacement.
This is a live additive result only; suppression remains disabled.
