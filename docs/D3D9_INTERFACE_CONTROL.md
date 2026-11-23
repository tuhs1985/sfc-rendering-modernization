# SFC renderer interface control document

**Baseline:** merged alpha `e450c30`, reviewed November 14, 2026. This document is the entry point for renderer integration. The linked code defines the exact layouts and accepted behavior of the pinned build. The current interfaces are experimental and versioned in the repository. A third-party renderer currently needs a source-level adapter.

## Connection points

The project will deliver this interface as a reusable DLL and its necessary
supporting components, with documentation and a consumer example. The second
deliverable is a UE5 wrapper built on that interface. The current experimental
contracts and existing source-level adapters are the implementation baseline.
[Sponsor-confirmed deliverables](decisions/2026-11-17-project-deliverables.md).

```text
SFC 2.5.6.4 (x86)
  semantic capture → session IPC → scene receipt and asset preparation
      → retained scene/frame input → D3D9Ex submission host (x64) → RTX Remix
      → completed GPU output → x86 receiver → game-side D3D11 insertion
  SFC continues drawing the remaining scene and tactical UI
```

| Contributor goal | Connect here | What to expect |
| --- | --- | --- |
| Read captured SFC data independently | Decoded geometry, image associations and scene state upstream of backend preparation | Best starting point for UE5, D3D12 or an inspection tool. See the [scene view](reconnaissance/scene-contract-v1.md) and [offline reader](../tools/asset_diagnostics/inspect_scene.py). |
| Consume ordinary D3D9 draws | The host's fixed-function draw stream | Geometry, primary texture and transform state are visible here. Enhanced materials, source damage and light semantics use other paths. See [D3D9 submission](#d3d9-submission). |
| Return a new renderer's pixels to SFC | A backend-specific GPU producer feeding the current receiver and insertion contract | Requires matching colour, depth, owner coverage and frame membership, plus a qualified GPU handoff. See [GPU return and native insertion](#gpu-return-and-native-insertion). |

## Scene input upstream of D3D9

### UE output adapter — standalone qualification, November 22

The packaged Development/Shipping checks transferred actual UE colour and
linear depth into a D3D11 consumer. Explicit Windows shared resources wrapped
through public RHI passed. Development and Shipping checks use shared producer
and consumer GPU fences. Native-depth conversion and exact single-owner bits
passed source-geometry comparisons, including opaque black markings.
See the [experiment and limits](runs/2026-11-22-codex-ue-actual-gpu-output.md).

The [candidate output contract](contracts/UE_OUTPUT.md) defines full source
identity, 64-bit NT handle ownership, peer/LUID identity and a two-slot lease.
Its 280-byte descriptor, explicit target/viewport and state-machine tests pass
x86/x64. A Windows two-slot GPU test passes repeated reuse; persistent UE
publication remains pending. The native-format normalizer writes directly into
caller-owned targets, with separate GPU qualification. The UE source reader consumes the existing source
channel upstream of D3D9 with original geometry, UVs and image bytes.
The reader's decoded-buffer ownership is explicit. Normal existing receiver
callers retain their previous default ownership.
Ninety-one retained frames and four original assets pass actual source IPC;
its generated F-CA input also passes packaged UE/GPU export. This is replay
through the current transport, not a new live SFC checkout.

### UE adapter foundation — offline qualification only

`src/ue_wrapper/Plugins/SFCBridge` is an independent consumer of the existing
checked offline source scene facade. It preserves original local positions,
corner normals/UVs, group/image associations, content/revision and available
fragment relationships. Session-owned assets are separate from world-owned
instances and camera state. UE basis/row-matrix conversion belongs in this
adapter; neither neutral packets nor Remix's UV/material rules are changed.

This is not a new live ABI, trusted submission ticket or native suppression
authorization. The upstream inspector establishes packet/image provenance;
the offline loader checks structural admission and frame owner/revision.
No UE GPU resource or type enters the source DLL wire. GPU sharing and live
receipt remain separately gated. Normal mode omits readback/array comparisons;
the `SFCDiagnostics` fixture explicitly enables them. See the
[foundation implementation record](runs/2026-11-18-codex-ue-worldspace-foundation.md)
for demonstrated capabilities and pending qualifications.

The x86 component captures the supported mesh and game state. Workers receive and acknowledge asset transfers, prepare resources and maintain the catalog. The x64 host consumes one frame snapshot for a set of retained owners. Each owner has its own pose and lifetime even when several owners share geometry. Asset readiness can change independently of frame availability.

| Input | What the consumer receives | Control reference |
| --- | --- | --- |
| Geometry and source images | Native-unit positions, triangle indices, corner normals and UVs, rendering groups, and original image associations. Reuse by content and revision. Native pointers and IDs are meaningful within the qualified capture session. | [Mesh capture](../tools/m1_component/m1_mesh_export.h), [receiver](../src/transport/scene_receiver.py), [scene preparation](../src/assets/scene_bundle.py) |
| Instance and camera | Session, owner epoch, asset revision, source frame and sequence, owner pose, view, projection and tactical viewport. Decode SFC transforms through the existing arithmetic, where the effective column-vector operation is `p_out = R × p_in + t`. Preserve native units and viewport offsets. | [Persistent owners](../tools/scene_bridge/persistent_scene.h), [pose decoder](../tools/d3d9_proof/live_owner_decode.h) |
| Retained frame and catalog | Version 3 `multi_scene::Frame` and `Asset`. The frame carries qualified owner rows with a coherent camera and optional damage. The reader checks the expected frame and sequence, publication guard, and checksum. The catalog binds owner/revision to model/source identity and content. Current capacity is 256 owner rows, 1,024 catalog slots and eight frame slots. | [Native wire](../tools/d3d9_proof/multi_scene_wire.h), [Python wire](../src/transport/multi_scene.py), [capacity](../src/transport/scene_capacity.py), [consumer](../tools/d3d9_proof/multi_scene_runtime.h) |
| Damage and debris | Optional reversible per-owner damage scalar and family. Supported destruction fragments have their own pose and lifecycle and reuse qualified geometry. Preserve the distinction between an intact instance and fragment instances. | [Damage state](../tools/scene_bridge/damage_state.h), [fragment preparation](../src/assets/break_scene.py) |
| Lighting | Source observations of scene and effect lights, including activation and known position/direction, colour and range fields. Consume the frame-keyed native effect-light bank in addition to the retained mesh stream. Backend light shape, intensity conversion and appearance controls are adapter decisions. | [Native light bank](../tools/scene_bridge/effect_lights.h), [light transport](../src/transport/light_transport.py) |

Read the qualified data at receipt and decoding when building a new backend. The existing live relay and prepared assets include Remix-specific UV handling, generated materials and resource scheduling. Treat that processing as a reference implementation for Remix. Keep original coordinates and image associations available to other adapters.

## Transient draw frame evidence

The opt-in [batch observer](../tools/effect_probe/effect_native.h) tags the selected indexed batch and engine Present with the same observer-local scene ordinal. The ordinal comes from the engine scene-begin boundary used by M1 to advance its own frame counter. A failed begin, intervening begin, or different manager/thread cannot establish a match. The [offline reader](../tools/effect_probe/capture.py) reports this as `native_scene_ordinal`. Older captures return null for that field.

Treat the standalone batch observer's scene ordinal, Present ordinal and D3D9 adapter source frame as separate identifiers. Live publication needs an explicit association to the retained frame's same-session frame, sequence and checksum. The standalone `-Batch` mode omits the retained-frame key. The retained cohort is published before some native effects draw, so eventual transient consumers need a separately qualified delivery phase. [Frame publication](../tools/m1_component/m1_live_scene.h) · [Offline companion contract](../src/transport/transient_draw.h)

Copied-game evidence confirms one main drone quad joined through native scene 2269 to successful engine Present 2270. These are separate run-local counters. [Live scene-marker checkout](runs/2026-11-13-codex-sfc07-scene-consumer.md#live-scene-marker-checkout)

The diagnostic [retained-frame verifier](../tools/effect_probe/retained_frame_join.h) defines the same-run join. The publisher, native flush and engine Present each supply a stamp with session, process, render thread, manager, source frame, sequence, checksum and scene-start tick. The verifier also checks timestamp order and reads the retained packet through the production reader. A different frame, failed Present or unavailable retained slot leaves the association unqualified.

The opt-in `-Join` launcher connects the diagnostic producer and observer in one process. M1 owns scene begin. Its diagnostic worker selects an anchor after a validated asset acknowledgement. M1 publishes a stamp only after the retained frame and its notification are committed. The observer stays passive until the first frame is readable, then checks the current source-frame identity at submission, flush and Present. A worker verifies and saves one matching retained packet and receipt. The single stamp slot uses spare space after the existing multi-scene store in the private scene mapping. The payload and offsets of the existing production frame protocol are unchanged. The synthetic process passed. The first copied-game attempt failed before capture and reported a game freeze. [Join checkout and failure](runs/2026-11-13-codex-sfc07-scene-consumer.md#first-live-join-failure)

`-JoinProducerOnly` isolates the retained-frame publication and shutdown path for diagnosis. The copied-game check passed with the transient observer passive. The revised combined `-Join` run then verified one exact retained-frame association and clean teardown. The captured surface lacks a verified same-run filename. [Combined checkout](runs/2026-11-13-codex-sfc07-scene-consumer.md#live-join-checkout--frame-verified-texture-name-missing)

The diagnostic worker resolves queued resource snapshots after detachment and before trace closure. The frame receipt is checked independently of texture completeness. A missing or ambiguous texture binding still leaves the full draw partial. The final copied-game run verified the named binding, indexed draw and exact retained frame together. [Live checkout](runs/2026-11-13-codex-sfc07-scene-consumer.md#final-live-drone-checkout)

November 17 x86 and x64 fixtures verified the optional companion with a saved
live draw carrying Present ordinal 782. The diagnostic test accepts the
expected ordinal as an argument and rejected the wrong one. The fixture
still attaches the saved draw to a synthetic frame to exercise the same
retained reader. The live join has its separate retained frame receipt.
Verified offline payload and live producer evidence are available. Live
transient publication to a renderer and matched native pixels remain open.
[Verification](runs/2026-11-13-codex-sfc07-scene-consumer.md#november-17-interface-verification-and-ue5-reference).

The [UE5 consumer investigation](reconnaissance/2026-11-17-ue5-consumer-investigation.md)
uses the renderer-independent geometry and camera inputs. It records screen
landmarks and a topology constraint for captured break models. It adds no
wire format or renderer connection.

### Packaged offline UE consumer — verified November 18

`src/ue5_proof` consumes a checked local scene view produced by
`tools/ue5_proof/prepare.py` from the independent reader. This adds no live wire
format or DLL export. The view carries original source positions, per-corner
normals/UVs, triangle groups, image identities, instance/session and captured
model/view/projection/viewport. Prepared BGRA files retain original top-row
orientation and hashes. The UE adapter applies its own camera-space axis and
reversed-depth conversion. It never imports Remix's texture correction.

The Win64 package builds procedural mesh sections and original-colour unlit
materials. `-SFCScene`, `-SFCOutput` and optional `-SFCFrame` explicitly select
checked input, bounded output and captured sample. It does not accept live
updates, join sessions or return shared GPU surfaces. Inputs must be prepared
by the checked development reader; this proof is not an untrusted public
scene-file parser or stable SDK. Source arrays, texture sampling and camera
projection were checked through the actual packaged renderer.
[Contract, evidence and limitations](runs/2026-11-18-codex-ue5-packaged-proof.md).

The subsequent [UE integration review](reconnaissance/2026-11-18-ue-integration-review.md)
defines recommended pre-live qualification. It proposes a UE-owned runtime
adapter with session/world lifetimes and local-space asset reuse. No new live
connection, wire layout or exported ABI is implemented by that review. The
current proof's camera-baked mesh must not become the live transform path.
Separately, Remix-prepared images must not replace original image semantics
in the neutral live interface.

The proposed [UE insertion plan](../openspec/changes/ue-native-insertion/design.md)
adds a separately qualified UE GPU producer/import front end while retaining
the current native game-pool, leases and insertion gate. Original scene input
stays upstream of D3D9. The plan evaluates Epic Texture Share before new
transfer code and explicitly checks cross-API/bitness/handle compatibility.
These are proposed connection points only. No UE live input or GPU-return ABI
is implemented or qualified yet.

## D3D9 submission

The separate x64 host creates a D3D9Ex device through the pinned Remix 1.6.1 runtime with API headers at version 0.6.5. It submits fixed-function `XYZ | NORMAL | TEX1` vertex buffers, indexed triangle lists per rendering group and primary texture bindings. It applies the D3D9 row-vector matrix convention to the decoded world/view/projection transforms and uses the captured viewport. The baseline draw sets fixed-function lighting off. Remix intercepts these ordinary draws. Its material library, light API and runtime controls supply the enhanced appearance separately. An observer of `DrawIndexedPrimitive` alone will therefore receive only part of the rendering input.

The plain system-D3D9 replay is the starting example for consuming a captured scene without Remix. The combined production host also owns private startup, material readiness, output extraction and adapter-specific configuration. Reuse its behavior as needed when implementing a source-level backend adapter. [D3D9 geometry and replay](../tools/d3d9_proof/d3d9_replay.cpp) · [Production host](../tools/d3d9_proof/d3d9_direct_host.cpp) · [Runtime pin and startup](../src/rendering/renderer_backend.py)

## GPU return and native insertion

1. **Prepare and activate.** The host and output receiver can start passively before the first ship is ready. Bind the live session and late asset identity through the startup ticket before accepting output. Use the session lifetime, target extent and resource generation when opening or retiring shared resources. [Startup ticket](../tools/d3d9_proof/startup_ticket.h) · [Passive receiver](reconnaissance/early-output-receiver-contract.md)
2. **Publish one coherent result.** Carry the session, source frame/sequence, cohort hash, output sequence, resource generation and exact member identities. The current two-slot D3D11 game pool uses `B8G8R8A8_UNORM` colour and two `R32_FLOAT` surfaces for depth and coverage. The physical hull pass supplies first-hit depth and owner coverage for supported geometry. Keep all surfaces spatially and temporally aligned. The current Remix backend keeps the rendered image accessible at backbuffer 0 for its post-`PresentEx` colour copy. [Game output wire](../tools/d3d9_proof/game_output_wire.h) · [Receiver](../tools/d3d9_proof/game_output_writer.h) · [Hull pass](../tools/d3d9_proof/physical_hull_depth.h) · [Membership contract](../tools/native_insertion/cohort_contract.h) · [Colour provenance](runs/2026-11-12-codex-frame-provenance-audit.md)
3. **Hand ownership over explicitly.** Match the Windows graphics adapter, resource descriptors and generation. Publish game-side readiness after the GPU copy completes. Hold the lease through every queued game GPU read. Retire the old generation on a target change and drain before releasing or reusing resources. A backend on another graphics API needs a qualified transfer implementation. [Game-side import](../tools/remix_runtime/d3d9_game_receiver.h) · [GPU read lease](../tools/remix_runtime/game_gpu_read_lease.h)
4. **Insert before suppression.** The game-side, same-process `native_gate::Dispatch` uses Acquire, Commit and Cancel. Capture occurs first. A matching output lease and successful insertion authorize suppression for the qualified owner's original draw lists. Missing, stale or ineligible output keeps original drawing active. ReShade provides game-side target access. Native shields, effects and text continue at their original points relative to insertion. The normal coordinator uses ExtraFrame with an absolute deadline and a 60 Hz reference period. Same-process ticket fields such as manager and list addresses stay within the game process. [Gate ABI](../tools/native_insertion/gate_contract.h) · [Return add-on](../tools/remix_runtime/return_addon.cpp) · [Normal coordinator](../src/session/coordinator.py)

On shutdown or failure, stop new work, wake pending coordination, then drain callback and GPU ownership before releasing resources. Keep the renderer worker off the game capture callback and preserve original rendering whenever admission fails before commit.

## Capability and compatibility status

- Supported rigid ship and fighter assets, damage, qualified break fragments, and scene/weapon lighting have gameplay evidence on the current backend. Coverage depends on the captured model and path. Cloak/transparency, fighter formation counts, and remaining background, projectile, grid and UI families have open ownership or rendering questions. [Coverage map](reconnaissance/rendering-family-map.md)
- SFC-07's sampled main drone quad is verified at native indexed-batch capture with same-run texture binding, draw state, presentation order and an exact retained-frame match. The offline companion can encode the captured draw. Standalone D3D9 replay verified sampling, placement, blend and depth under controlled conditions, using `1−V` only in the diagnostic adapter. Native pixel parity, production transient publication and Remix submission remain open. [Standalone replay](runs/2026-11-13-codex-sfc07-scene-consumer.md#standalone-d3d9-drone-replay)
- Version numbers describe the repository's wire layouts. Maintain the paired producer/consumer build and use the pinned dependency set. A stable public ABI, backend discovery and D3D12/UE5 GPU return are future work. [Dependency closure](releases/DEPENDENCY_CLOSURE.md)

## Contributor bring-up

1. Start from a matching checkout and inspect a qualified `scene.bin` and `scene.json` pair with the [offline scene reader](../tools/asset_diagnostics/inspect_scene.py). Check indices, UVs, original image associations, transforms and viewport before allocating backend resources.
2. Bring up one scene offline. Compare decoded bytes and projected positions, then exercise asset sharing, retirement and a new asset revision. Treat unqualified families as native fallback. The [D3D9 proof instructions](../tools/d3d9_proof/README.md) describe existing replay and fixture entry points.
3. For live input, exercise the actual versioned reader with explicit source identity. Verify rejection of stale or wrong-session data and behavior with delayed consumption, missing assets and source shutdown. Keep the source callback bounded.
4. Add GPU return only when needed. First qualify a standalone producer/receiver pair with changing frame content and exact colour/depth/coverage provenance. Include device/target generation changes, slot lifetime and disconnect. Verify native insertion and fallback in the copied game before enabling suppression for additional families.

When changing an interface, update the owning producer and consumer together, document field and lifecycle changes here or in the linked wire contract, and record supported versions and fallback behavior. Use focused malformed-input, frame-matching and teardown fixtures before gameplay checkout.
