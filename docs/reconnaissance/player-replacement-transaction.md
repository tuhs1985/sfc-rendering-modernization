# PLAYER-REPLACEMENT-001 — whole-picture transaction, version 1

Run208, 2026-10-27. Default OFF. This extends the established ordinary-D3D9
adapter and Remix return; it does not introduce a new renderer or Toolkit path.
Sponsor-confirmed depth and previous aligned overlay remain the baseline.
Gameplay acceptance is separate from standalone qualification.

## Native capture and suppression

The existing semantic recorder observes original owner/model/source, geometry,
resource associations and persistent transforms BEFORE altering an invocation.
Only the qualified polygon wrapper at `0x006AC5A0`, primary return `0x0042E55D`
and secondary return `0x0042E626`, may receive a zero count on its stack.
The original wrapper still executes its empty-list path. No stored model/list,
game asset, whole model-function return or shared downstream flush is changed.
Run207's pinned-client instruction checks and isolated zero-count execution
remain necessary evidence; their stubbed state virtuals are not driver tests.

Selection uses the existing configured player-fixture model in
`tools/d3d9_proof/offset_ship.toml` (currently F-CA), not first-observed owner.
**An engine player flag has not been proved.** Two owners matching the same
configured model are ambiguous and refused. Use a different enemy model for
this first checkout. Other ships/effects remain native; only the selected owner
is submitted for replacement. This is not an all-ship replacement mode.

The first qualified list fixes the source-frame decision for both lists.
Expiration between primary/secondary cannot split that decision. Revocation,
identity/revision changes, non-mainline or unknown/nested lists invalidate the
entire picture transaction. Even when one list was already skipped, that partial
native source is never committed. Capture still precedes each decision.

## Shared authorization and output receipts

`replacement_transaction.h` defines a fixed 4,416-byte Store inside the existing
current-user/session mapping: offset `12 MiB - 64 KiB`, below source timing.
Magic `0x31525053`, version 1. No pointers to graphics APIs cross processes.

- Header: session words, game PID, size/version.
- One seqlock Control: mode, generation, owner epoch, asset revision,
  model/source identity, render thread, receiver epoch, exact next source-frame
  permit, reason field and first-list QPC expiry (50 ms).
- 64 fixed source receipts: source frame, generation, owner/revision/model/source,
  thread, Seen/Suppressed/Invalid flags and primary/secondary counters.
- Two output bindings: output sequence, source sequence/checksum, source frame,
  generation, owner/revision and receiver epoch. They are published before the
  existing output slot becomes READY, under its existing GPU/resource lease.
- Eleven bounded lifetime counters; no geometry firehose or callback file IO.

Reads try at most three times; a failed read is refusal. Native hook work uses
preallocated storage and does not wait, allocate, decode images or call a viewer.
The existing worker owns serialization, resource preparation and transfer.
Unknown sessions, pointer reuse, revisions and delayed/stale bindings cannot
authorize a newer ship. Renderer failure revokes future suppression.

## Picture states

1. **Priming:** native drawing continues. Prepare two pending source color/depth
   pairs and one last-complete pre-ReShade color image. Consume a correctly
   paired canary output privately. Native and renderer capability receipts plus
   a usable depth source are required before issuing the next-frame permit.
2. **Active:** capture current native color/depth privately. Match a retained
   source to its exact Remix output and native suppression receipt, including
   generation, owner/revision, source sequence/checksum and receiver epoch.
   Compose only into that pending texture, then copy the completed picture to
   the last-complete image. Only that whole image reaches the backbuffer.
   A source with no selected drawing may commit intact without adding a ship.
3. **Missing output:** repeat the last complete picture, including its own
   background/HUD, for at most two additional presentations. Pending render
   inputs remain limited to 50 ms and the two retained earlier source frames.
   That input-age check does not shorten the separately bounded whole-picture
   hold. No prediction, guessed pose, renewed stale overlay or new refresh cap.
4. **Recovering:** revoke permits, discard pending partial pictures. Hold the
   complete image until a fresh native receipt proves no drawing was suppressed.
   Commit that intact native frame and record its acknowledgement.
5. **LatchedOriginal:** leave native rendering enabled until session restart.
   No repeated automatic hide/reappear/fallback cycle. Device recreation also
   starts latched; unsupported dimensions do not enable replacement.

Nominal presentation remains the existing one-frame buffer. The complete cache
is pre-effects, so every presentation runs the existing ReShade chain once;
repeated cached pictures do not repeatedly grade already graded pixels.
Immediate-context commands stay on the presentation thread. Worker imports use
device resource creation and existing nonblocking lease/fence retirement.

Microsoft documents [CopyResource](https://learn.microsoft.com/en-us/windows/win32/api/d3d11/nf-d3d11-id3d11devicecontext-copyresource)
as an asynchronous GPU copy requiring compatible shape/format/sample counts.
The implementation retains that shape validation and existing GPU leases;
a shared image handle alone is not readiness. Microsoft's
[threading guidance](https://learn.microsoft.com/en-us/windows/win32/direct3d11/overviews-direct3d-11-render-multi-thread-intro)
requires single-threaded immediate-context access, including Present.

## Stop, bounds and failure limits

Stop sets native_stop before teardown. If Active/Recovering, the component's
stop worker waits at most two seconds for a newer intact native-frame receipt.
This is outside rendering callbacks. A missing acknowledgement returns status
12 and retains hooks/storage instead of unloading a potentially live callback.
Original drawing is enabled while awaiting that receipt. The ordinary callback
drain, byte restoration, unload and client-hash checks follow acknowledgement.
Normal process exit reclamation is not controlled-unload evidence.

At 1920x1080 the added last-complete image costs about 7.91 MiB; controlled
color/depth/output textures total about 118.65 MiB within 128 MiB. Existing two
shared output triplets are retained; no new unbounded pool. Native scene transport,
asset/image limits, 32 MiB logs, 90-second tactical / 285-second workflow and
20 GB evidence cap remain. New replacement artifacts are included in accounting.
No continuous screenshots or CPU readbacks in gameplay. Standalone pixel tests
read back after their delivery window, because readback itself can stall the
synthetic source and correctly expire a live permit.

Abrupt device loss cannot recreate a lost GPU image; future native suppression
is revoked and recreation stays latched. A stopped render loop cannot provide
a restoration acknowledgement, so unloading is refused. These are safe-stop
limits, not proof of seamless recovery from every driver failure.

## Qualification and sponsor checkout

`build_player_replacement.ps1`: real 32/64-bit GPU transaction checks and the
actual x86 recorder compiled into a standalone component test. Test both lists,
unchanged captured data, other/nested/revoked calls, identity/generation/revision,
malformed transfers, fixed-size layouts, offscreen commit and exact repeated
pixels. Existing native, buffer, camera/transport and Python regressions remain.

`run_return_fixture.py --multi-ship --prewarm --startup-profile --pipeline-mode
performance --async-material-checkout --player-replacement` uses historical
fresh packets and **synthetic native source receipts**, through the actual
receiver and pinned Remix renderer. It is not SFC gameplay. Add
`--replacement-faults` only here to withhold output leases for one then two
presentations, proving resume versus latched native recovery. That test flag is
removed from the game environment. Check known background/HUD frame markers,
pixel output, graphics state, resize/recreation and normal owned exits.

`player_replacement.py --steady <run> --faults <run>` requires actual final-source
fixtures, native checks, matching binary/dependency/placement locks and bounded
repeats. The receipt says **OFFLINE_PLAYER_REPLACEMENT_PREPARED_NOT_SFC_PASS**.
It permits current valid lighting/rendering settings without altering them.
Never hand-edit source hashes or promote the old additive gate to suppression.

Once offline qualified, use `start_d3d9_player_replacement_session.ps1` from the
usual elevated parent. Enter F-CA versus a different model. Expect one aligned
player ship, no offset duplicate; other ships/effects/HUD remain normal. Start
still, rotate, move/turn, switch away/back, then play briefly with shields/weapons.
Keep SFC open through restoration; exit normally on the two-beep request. No
manual timestamps, on/off cycle, manual RE or routine UAC. Review suppression,
paired-output/recovery receipts, original-depth absence, visible behavior,
unload, hashes and bounds before declaring one-ship replacement demonstrated.
