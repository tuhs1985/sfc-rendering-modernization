# Ship triplet return — offline-qualified experimental contract

## Current extension — diagnostic offset, 2026-10-17

[REMIX-OFFSET-001](probes/REMIX-OFFSET-001.md) supersedes the wire layout below:
version3,Wire496B/Key152B; explicit diagnostic mode/world translation preserve
native source-pose identity. Mode0=zero,mode1=finite nonzero bounded translation.
Wrong offset cannot claim another lease. Version2 evidence below is historical.
New opaque masked compositor is qualified offline with actual Remix output and
synthetic wrong-owner/invalid-depth cases. A deferred command list restores
immediate-context state. NOT installed in SFC; scene depth/HUD/live timing remain.

## Historical version2 qualification

2026-10-17;[Run21](../runs/2026-10-17-codex-ship-triplet-return.md),
[probe](probes/REMIX-TRIPLET-001.md). Authority:approved return-path investigation.
This is NOT final renderer design,live ship replacement or a milestone PASS.

## Qualified boundary

Actual pinned64bit Remix produces colorBGRA8,depthR32F and pickingR32F. A native
D3D11 device owns THREE shared textures;Remix imports via publicD3D9Ex API.
After all3copies and producerGPU EVENT complete,ONE packet publishes them together.
A separate32bit native10_1 consumer opens the actual GPU handles,creates shader
resource views,validates metadata and verifies byte-identical outputs. No Toolkit,
CPUimage upload,Vulkan image-as-handle or window overlay involved.

Current actual tests:256×256,one reusable triplet,two sequences per session,two
fresh captured FCAposes,12/12plane deliveries to32bit process exact. PickingID29
is an explicit renderer label associated with semanticowner2,not a ship pointer.
Object-picking values are UINTBITS inR32F;not float-valued IDs. Source geometry
and corrected nativeZcamera from Run19/20,opaque diagnostic material. Actual
texture/light fidelity is not part of this transport qualification.

## Explicit versioned wire

ship_triplet_wire.h:magic33544653,version2,Wire464bytes,Key136bytes;bothx86/x64
native tests assert identical sizes. Version1(416/112bytes) was development-only
and superseded before integration;old packets rejected by version/size.
Extension at byte512 in a fresh4096B current-user-SID-DACL GUID mapping. Existing
diagnosticv2 mapping/security prefix is reused ONLY as an independent envelope;
the old one-color protocol does not become a ship contract implicitly. No existing
game return channel is overwritten,opened by guess or shared between test runs.

Key includes:

- Fresh RETURN session GUID4words,plus original SEMANTIC source-session4words
  and verified captured sourcePID. Fixture receiverPID is separate from sourcePID.
- Semantic owner epoch,asset revision,engine frame,renderer pickingID.
- Pose and camera FNV1a64 hashes of exact native words (M17words;V/P/viewport40).
  These are accidental-mismatch identifiers,not cryptographic authentication.
- Full captured packetSHA25632bytes. This identifies a same-session revision,
  not a universal cross-session normalized geometry/material cache key.
- Output dimensions,original tactical viewport,resource epoch and nativeZ enum1.
- Reserved0. No native game pointer is dereferenced by the consumer.

Wire contains immutable textureformats/handles/dimensions/adapterLUID/resource
epoch,requested and published keys,monotonic sequence/ACK,publishQPC/frequency,
three expected/consumed hashes and counters. Current resource descriptors are
pinned by Consumer;changed handles/size/format/LUID/epoch are NOT silently opened
or used through old views. Caller must disable and reconstruct outside callbacks.
Legacy KMT handles canonically32bit;unsupported width rejected. Do NOT CloseHandle
KMT GPU handles;native COM texture leases own lifetime. Mapping/process/job handles
are ordinary owned handles and closed normally.

## Ownership / nonblocking receiver

`IDLE → RENDERING → READY → READING → IDLE`.

Reserve BEFORE GPU output writes. No new reservation while output is outstanding
or sequence!=ACK. Publish ONLY after producer completion;requested key must still
match. Caller changes during rendering discard that output after completion.
Consumer claim requires exact CURRENT key,session/descriptors andfreshQPC<=1s.
The1sceiling does NOT authorize old game frames;frame/pose/camera must match too.
Wrong/stale READY packet is discarded without exposing textures. Invalid/stopped
channel never yields usable output. No cached previous-owner image fallback.

Consumer::submitted queues a native EVENT after caller GPU use. Consumer::poll
uses DONOTFLUSH and cannot ACK before submitted or GPU completion. Sequence
overflow is refused. Try-lock only,no waits or queues in request/claim/poll.
Original renderer remains fallback. Device loss sets error/no ACK;resources must
not be recycled on an unproven timeout. Session stop/device-reset/hot-unload
lifecycle in a real addon remains integration work,not qualified by this fixture.

Consumer constructor creates views/resources BEFORE runtime use. It binds no
graphics state or shaders. The offline test pilot ONLY copies to private staging,
maps completed data and checks every byte,picking IDs and finite depth. That
readback/fixture Sleep/producer wait MUST NOT be copied into SFC callbacks.
An actual compositor must preserve state/UI ordering and fence its GPU use.

## Bounds / failures / unqualified areas

One triplet=3shared textures,786432B at256square. Existing producer shaderID
decode target is fourthoutput;readback/staging allocations are not pool members.
Descriptors capped1920×1080/four allocations<=128MiB;ONLY256square exercised.
No claim full-size,resize/device recreation or final composition validated.
32MiB log/output run cap(warn16),120s owned host,5s fixture fence/child waits,
110s childcap. Owned child in KILL_ON_JOB_CLOSE job;never includes SFC.
No continuous images,unbounded geometry or on-disk game changes.

Deliberately slow6s receiver and exited receiver both terminate fixture with
expected failure:published1,ACK0,accepted0,READY lease,no second overwrite or
false success. These are controlled negative results,not provider/tool failures.
Separate SDK40-object teardown warning remains in positive and negative runs;
normal process0 is NOT warning-free resource shutdown. SFC54/67warnings open.

This prototype has not measured live engine→SDK→game latency. A30Hz stream and
offline captured frame labels are NOT a synchronized replacement mechanism.
Future game caller must build CURRENT keys from fresh semantic state and omit
late output while original drawing stays enabled. Coverage/scene depth/UI/effects,
owner-specific suppression and failback still need actual integration evidence.
No black-background cutout or rectangle can substitute for that work.
