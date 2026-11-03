# Early passive receiver — output bootstrap v1

## Placement and bootstrap

The existing external x64 D3D9 host creates its current-user-only output mapping/events and launches the x86 receiver **before** entering warm_start.wait. Private renderer warm-up and existing output-resource allocation remain in their established order. Shared startup readiness is announced only after the receiver reports passive readiness. No M1 changes:its LiveChannel disk-configuration bootstrap still precedes shared-memory attachment. The receiver uses the explicit inherited session name/game PID to attach independently;no dependency on M1 attachment or the not-yet-known asset hash.

The mapping stays192bytes and the output Packet stays128bytes. Before the first output,that packet area temporarily holds output_startup::Control(128bytes,magic0x3152534f,version1,checksum at104). The current-user ACL and original ready/done auto-reset events are reused;no new mappings/events/files or per-frame transport work. Updated paired producer/receiver binaries are required;old consumers fail closed rather than interpreting bootstrap as GPU output.

States:Boot6 -> Passive7 -> Activate8 -> idle0. Thereafter original ready1/acquired2/acknowledged3/idle0 and stopped4/rejected5 remain unchanged. Bootstrap cannot be mistaken for a valid frame because its state is never ready1. Packet metadata padding retains its original32-byte layout.

Control binds parent PID,unique output nonce,flags and receiver PID/ready QPC. Passive readiness means protocol/session attachment only,not a GPU frame. Existing accepted supervisor ticket provides late source PID/session,asset SHA256 and exact float offset. The receiver independently validates the ticket layout/checksum,accepted state,host PID and source session/game/supervisor liveness. The parent checks its already-accepted asset identity before activation and validates the receiver's returned identity against a held snapshot afterward. One-shot receipt includes accepted asset bytes/session/offset and activation QPC;no inference from stale inherited asset/offset environment values.

GameOutputWriter binds those validated bytes explicitly for early mode. The legacy late-start/default OutputPeer caller autoactivates with existing inherited configuration and retains its original environment-based asset parsing. Bootstrap flags distinguish the paths;simply inheriting PREWARM does not silently switch a legacy late caller. No fallback to an unqualified/null asset. The source supervisor remains the single immutable ticket writer;this is correctness validation within existing current-user trust,not a new cryptographic security boundary.

## Lifetime, failure and ownership

Passive receiver lifetime is bounded by its285-second limit,the original host's180-second activation deadline and the enclosing prepared-workflow watchdog,whichever ends the session first. It waits on existing events/process handles and does not create a D3D device,open GPU images or publish a game pool. Parent death is an error;game/supervisor exit or explicit stop cancels preparation. The host's existing warm-up pump checks receiver liveness so a dead receiver cannot leave the host waiting indefinitely for assets.

Active-work deadline starts exactly at validated activation,once. Existing60s offline/110s live/130s game/tuning duration values are preserved;passive menu time is not deducted and output activity never renews the deadline. Controlled cancellation before first output exits0 with explicit RECEIVER_CANCELLED frames0 evidence;outer workflows still require actual output/pixel receipts before claiming rendering success.

No GPU resource is opened until a valid output packet arrives. The original descriptor,adapter,session,sequence,checksum,resource-epoch and ACK checks remain. GPU copy/fence and two-slot game-pool ownership are unchanged. Pool asset/session bytes are populated from the validated late binding,not inherited startup guesses. The host waits for receiver retirement before freeing output textures on normal/error teardown. Existing native matching/fallback/suppression policy is unchanged;receiver failure never independently authorizes suppression.

## Measurements and qualification

Startup profile separates peer_process_begin/created,peer_passive_ready,receiver_started,activated,receiver_activated and first valid cohort output/ACK. Creation time is preparation,not a post-activation stage. Existing historical profile parser remains compatible;new parsing avoids subtracting early receiver timestamps from later material readiness. Profiles are opt-in worker evidence,not SFC callback work.

Reproduce:

1. Build receiver via tools/d3d9_proof/build_receiver.ps1.
2. Build no-GPU probes/wire tests via tools/d3d9_proof/build_receiver_startup.ps1.
3. Run tools/remix_runtime/qualify_receiver_startup.py(real receiver lifecycle/identity;no SFC/GPU,includes61second passive case).
4. Build pinned host via tools/d3d9_proof/build_candidate_runtime.ps1.
5. Existing standalone native-all-ships fixture,Strict immediate and ExtraFrame60second menu delay,performance/startup-profile/graceful. Gameplay remains separate sponsor checkout.

See Run252 for measured first valid rendered/inserted output,limits and remaining later setup cost. This removes late process creation as an asset-readiness dependency;it does not disable Defender or guarantee cold preparation/whole startup is sub-two-seconds.
