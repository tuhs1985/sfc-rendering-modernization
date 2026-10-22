# Ordinary-D3D9 additive output v2

Latest2026-10-21:[Run90](../runs/2026-10-21-codex-texture-origin-and-viewport-scale.md)
corrects full-frustum output placement to captured native tactical viewport and
native depth coordinates. No model rescale. Remix replacement DDS rows invert
vertically once;color/emission/roughness share origin. Raw UV/ordinary D3D9uploads
unchanged. Actual quadrant control,projection oracle and599/600offline PASS;real
ship visual confirmation pending. Last game improved stability but controller8
means process-exit reclamation,not controlled live unload. No gate closure.

Latest2026-10-20 Run89:private250us worker query/input timer with original GPU
completion authority;fixed6MiB deferred worker diagnostics;/O2 precise builds.
Offline599/600,pixels/state/cleanup PASS;actual fast-camera stability still OPEN.
Same wire/pool identity and current appearance. Aggregate budget now20GB by explicit
sponsor authorization;per-run resource/log/image limits below remain unchanged.
See [Run89](../runs/2026-10-20-codex-worker-efficiency-preparation.md).

Status: offline qualified, actual SFC test pending; M1 CONTINUES.
Run83 current:camera-relative left displacement/background light-file cache,
599/600offline frames. Old v1 static-world-offset pool rejected. Actual225915still
flickered;new correction is not yet gameplay demonstrated.
Run82 supersedes initial readiness:first game delivery FAILED (mostly stale).
Current worker correction is offline-qualified,not gameplay validated. Explicit
offset_ship.toml selects known player-fixture FCA;not generic player ownership.
Missing/ambiguous matches reject. New fixed600-frame offline readiness guard.
Authority:[approved additive plan](d3d9-to-sfc-additive-execution-plan.md).

Fresh semantic rigid mesh/resources -> ordinary D3D9 draws -> pinned Remix1.5.2
64bit host -> shared GPU color/depth/isolated-owner coverage -> x86 receiver ->
two-slot GPU pool -> current native-depth-qualified D3D11 game compositor.
SDK interfaces are used for output/light controls only, never geometry registration.
Native Remix USDA contains material policy only. No OBJ/USD geometry/Toolkit.

Pool is576B at16MiB semantic mapping offset11MiB+128KiB, between raw source store
and12MiB timing store. Current-user ACL/session mapping unchanged. Header64B:
magic0x314f4753,version2,bytes576,gamePID,full source-session words,receiverPID,
hostPID,stopped/ready/publication/replacement/busy/error counters. Asset SHA32B,
camera offset3float(negative X distance,zero Y/Z),diagnosticMode1,padding to128.
Producer/game derive actual displacement from exact view row0 of SAME frame.
Two192B slots then64B
stats at512. Slot includes existing128B packet with GPU LUID, dimensions, handles,
owner/revision/frame/state hash and resource epoch;32B padding metadata holds
source sequence,full source nonce,FNV checksum. Never use ordinary picking ID0 as
background: output depth finite[0,1] against negative-1234 sentinel qualifies the
isolated owner's coverage. This does not separate multiple overlapping owners.

Producer GPU work completes before output offer. Receiver copies to an Idle slot
or replaces only unclaimed Ready;it never overwrites Acquired. Completion uses
native D3D11.4 event completion on isolated workers instead of millisecond
query polling. Grade/coverage commands share one completion batch.5s worker wait
limit;unsupported/removed devices fail safely. SFC callbacks remain nonblocking.
GPU completion must precede Ready publication/producer ACK. Game worker imports and verifies
handles/LUID/descriptors outside callbacks. Render callback nonblockingly acquires
only exact current source session/sequence/hash/frame/owner/revision, qualified
native viewport/depth and ready resources. Deferred composition preserves complete
immediate graphics state. It releases a displayed slot only after DONOTFLUSH GPU
query completion. No waiting, disk IO, allocation or stale-image hold in callback.
Source shutdown, retirement or invalidity hides output. Saturation omits extra ship,
not original. Resize/device recreation requires a fresh generation/session; original
renderer remains operational. Same-GPU non-SINGLETHREADED game device required.

One selected fresh asset,camera-left distance=1.0*maximum captured bounds span
(Run91,sponsor2026-10-21reduces former1.5gap by one third;scale/depth unchanged).
delta_world=-distance*view_row0;view rotation maps it to[-distance,0,0],not camera
forward/back or up. Separate diagnostic parent only;
original transforms/geometry/UVs untouched. Materials resolve original images by
fresh association/hash, primary image native XXH3 identity; existing generated
roughness and provisional weighted-secondary emission policy are explicit. Native
texture hashes checked against independent captures. SDK-era V inversion is NOT
carried into ordinary D3D9. Same-primary/conflicting pairs and negative native-USD
anisotropy reject rather than guess. Four existing TOMLs frozen for this90s proof.
Fresh native light packets must match current session/owner/model/source and bounded
age. Newer-light/older-owner frames skip; no historical fallback in gameplay.
Run83:fixed-size light/shape cache (~1008B) read by owned background thread every
10ms,outside critical renderer path. Brief try-lock only copies snapshots;no IO/API
under lock,API remains host-worker-only. Cached observed time NEVER refreshed;
same identity/checksum/future-frame/500ms expiry and shape revision validation.
Transient IO failures retain data only within existing freshness bound. Thread
joined before API shutdown. Legacy SDK default file-read path unchanged. Additive
mode skips unused vendor picking copy;depth-derived owner coverage still generated.
Current textures/emission/roughness,lights/image/quality policy unchanged.

1920x1080 output only for first game test, two pooled triplets plus producer/grade
~83MB, <=128MiB. Mapping16MiB; logs32MiB/warn16MiB; original/derived images128MiB/
warn64MiB. Current20GB aggregate cap/reservation applies(sponsor raised2026-10-20). Internal120/130s watchdogs
allow<=30s preparation plus90s formal test; outer workflow<=285s. No image dumps.

Offline receipts:[Run81](../runs/2026-10-20-codex-normal-d3d9-material-binding.md).
Full-event proxy required for public depth/draw events; only copied game's proxy
is temporarily replaced and verified rollback restored after normal exit. Existing
normal proxy forwarding, accepted install and client binaries unchanged.

Not qualified: steady live-game delivery, automatic resize recovery, all assets,
multiship replacement, original suppression, effects/grid/UI occlusion universally,
future D3D12, vendor warning40 disposal. Rejected stale images are omissions, not
successful delivery. No requirement waiver or milestone completion.
