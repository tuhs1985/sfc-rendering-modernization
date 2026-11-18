# UE-to-SFC insertion design

## Context

This plan starts from the uncommitted packaged UE proof on
`codex/expand-rendering-interface`, parent `e07a025`. Preserve that proof and
the accepted Remix alpha. The [UE review](../../../docs/reconnaissance/2026-11-18-ue-integration-review.md)
is the prerequisite assessment. No stage below is implemented by this plan.

The existing game-side route is not a detached overlay. An x86 return add-on
inserts colour/depth into SFC's active native targets before later shields,
effects and text. The native gate acquires a matching output lease, commits
insertion and only then authorizes original-mesh suppression. Reuse that route.
ReShade supplies the target access and dgVoodoo supplies the current D3D11 game
device. Removing either is outside this change.

Relevant boundaries:

- Neutral receipt: `src/transport/scene_receiver.py`, `live_scene.py`,
  `multi_scene.py`, `tools/d3d9_proof/multi_scene_wire.h`.
- Output: `tools/d3d9_proof/output_channel.h`, `game_output_wire.h`,
  `game_output_writer.h`, `output_target.h`.
- Insertion: `tools/native_insertion/gate_contract.h`, `cohort_contract.h`,
  `tools/remix_runtime/return_addon.cpp`, `d3d9_game_receiver.h`.
- Startup/selection: `src/session/coordinator.py`,
  `src/rendering/renderer_backend.py`, existing startup ticket and recovery.

## Goals / Non-Goals

**End state:** one identified player ship is rendered by packaged UE using
fresh qualified source assets, camera and pose, then inserted at the original
location with its original draw suppressed only after matching insertion.
Native shields/text occlude it correctly, source tracking continues, and normal
gameplay/cleanup remain intact. Additive in-game insertion is a separate earlier
checkpoint that does not suppress anything.

This is not full-scene UE coverage, the final public SDK, a new alpha release,
or parity with all Remix appearance settings. The source DLL/interface remains
renderer-independent and the UE wrapper is a separate deliverable. No UE types
or RHI resources enter the neutral shared ABI. Native unsupported objects and
effects remain SFC's responsibility.

## Decisions

### 1. Use a UE runtime adapter, retaining the proof as a comparator

Create `src/ue_wrapper/SFCUEWrapper.uproject` and a project plugin
`Plugins/SFCBridge`, with runtime and editor/development responsibilities
separate. A session subsystem owns IPC/worker/asset lifetimes. A world subsystem
owns visible instances and the source camera. The small application owns window
controls. UE does not simulate SFC gameplay, collisions or ship movement.

Keep original local positions, corner attributes and material groups. Convert
the world basis/units once in the UE adapter and apply separate instance and
camera transforms. Qualify the shared runtime `UStaticMesh` fast-build path for
rigid assets against the procedural reference, including recorded break-piece
topology. If it fails a required capability, record the failure and evaluate
the compact procedural alternative. Do not silently repair geometry or begin
writing a custom mesh renderer. Pose and material updates never rebuild meshes.

Move required loads out of assertions, use recoverable admission errors, and
keep diagnostic comparisons genuinely optional. Avoid full-array copies per
material group. Provide visible Exit, Escape and correct widget cleanup.

### 2. Qualify GPU output before spending a game run on it

The engine contains Epic's Texture Share plugin with DX11/DX12 resource paths.
Its installed descriptor marks it Beta. The documented ThirdParty samples are
not present at their documented location in this installed binary engine.
Check the installed public interfaces first rather than assuming a sample is
available or downloading a full engine tree.

**Preferred qualification:** Epic Texture Share sends UE's completed output to
a standalone D3D11 consumer, using explicit source identity and bounded owned
resources. Its default blocking/frame-sync policies are not automatically
compatible with SFC. Test cancellation, missing receivers and deadline behavior.
SDK support for both APIs does not prove our cross-API combination works.

If Texture Share cannot meet the contract, use the smallest backend-specific
adapter through public UE RHI and documented Windows shared-resource/fence
facilities. The installed `ID3D12DynamicRHI.h` exposes resource wrapping, but
that alone proves neither sharing nor safe transitions. Document the specific
gap before adding code. Do not patch the engine, use private backbuffer offsets,
switch UE to DX11 silently, or substitute CPU screenshots.

The preferred practical bridge is a UE-selected **x64 D3D11 receiver front end**
that imports UE GPU output and feeds the existing game-pool writer. It replaces
the existing renderer-output receiver role for this backend, rather than adding
another serial receiver. SFC and its game-side return add-on stay x86. The
current standalone output receiver is x86 and Texture Share is Win64, so it
must not be assumed directly reusable as a Texture Share client.

Reuse backend-neutral pool/lease logic where it actually compiles and matches
the contract. Existing `output_channel.h` v2 constrains handles to 32-bit values.
Never put a new NT/native handle into that field by truncating it or removing
validation. Normalize into the established game pool, or add a documented,
versioned UE-front-end handoff with correct process ownership. Keep the Remix
consumer's protocol unchanged.

Sources: [Epic Texture Share](https://dev.epicgames.com/documentation/unreal-engine/texture-share-in-unreal-engine),
[Quick Start](https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-share-quick-start-for-unreal-engine),
[Microsoft shared fences](https://learn.microsoft.com/en-us/windows/win32/api/d3d11_4/nf-d3d11_4-id3d11device5-opensharedfence).
Windows distinguishes shared fences from shared textures; qualify both.

### 3. Preserve an exact, completed output transaction

One immutable ticket binds session, owner epoch, asset revision/content,
source frame/sequence, camera/pose/cohort identity, target extent, target/device
generation and output generation/sequence. Reuse the existing field definitions
where supported. A renderer counter or matching frame number alone is not an
adequate join. Copy a known completed render target, not a guessed backbuffer
after Present. Include changing visible content in provenance tests.

The native consumer currently uses `B8G8R8A8_UNORM` colour and two `R32_FLOAT`
surfaces for physical first-hit depth and owner coverage. `physical_hull_depth.h`
packs the owner with `asfloat(owner)`. Preserve those integer bits and decode
with the existing convention. Do not replace owner identity with UE's 8-bit
custom stencil, a blurred mask or a black-background cutout. Black markings
remain opaque where hull coverage is present.

Convert UE reversed depth into the native consumer's proven projection/depth
convention. Do not submit linear world-distance SceneDepth as device depth.
Derive and test the conversion for the captured projection, including near/far,
occlusion and cleared background. Colour, hull coverage and depth must describe
the same geometry, pose, viewport and completed output. A supplemental hull
pass is acceptable if necessary, but must be bound to that same snapshot and
its cost measured. No native effect replay is needed.

Use the native target notice, not desktop dimensions or a forced user INI.
The first live fixture uses an already-qualified game extent. Preserve its
tactical view rectangle and offsets within full-sized return surfaces. Never
stretch the proof's 1720×1020 crop to 1920×1080. Qualify other supported game
sizes through the same path. The historical 1280×360 case is a negative/layout
regression, not a newly supported SFC resolution.

Same-GPU LUID, descriptors, ownership and completion are checked at import.
Actual GPU completion must precede readiness. A render-thread command fence
alone is insufficient. The existing game-pool copy must complete before the
native gate is notified, and its read lease stays held until SFC's GPU finishes.
Target changes retire/drain an old generation before resource reuse.

### 4. Keep timing and source receipt coherent without another scheduler

Workers prepare CPU arrays and original images. Game-thread code owns UObject
and scene changes. UE queues render work through supported engine facilities.
Source frame state for camera and owners is applied coherently. Readback,
hash comparisons, screenshots and traces are not normal-frame work.

Reuse current session-owned IPC and persistent owner tracking. The raw source
assets and the prepared Remix submission are different boundaries. Qualify a
small neutral reader facade that supplies original arrays/images and frame
identities. Do not make UE undo hidden Remix material processing. If an original
field cannot be recovered from an existing transfer, document the smallest
source-interface extension before implementing it. No fresh EXE discovery or
source-hook redesign is assumed necessary.

Keep renderer/receiver passive prewarming at launch. Bind late session/asset
activation through the existing startup ticket. Present a ready base model
without waiting for unrelated assets or enhanced materials. Share qualified
content and update instances independently. Camera visibility does not retire
living ships. No new 30 Hz or owner-count cap is introduced.

Retain the current **ExtraFrame** admission policy as standard. Reuse its
single absolute native deadline; do not add a second Texture Share wait or a
second extra frame inside UE. No Strict-versus-ExtraFrame campaign is needed.
Do not globally disable UE threading or invent prediction to hide late work.
Discard obsolete work. Missing output before commit retains native rendering.
Repeated ordinary camera-switch fallback fails the stability goal and requires
diagnosis, not looser pose matching. No GPU-waiting in SFC capture callbacks.

### 5. Insert first without suppression, then replace the player

The first copied-game checkout returns a full textured player ship with a
documented diagnostic offset through the existing native insertion point.
Keep all original drawing. This exposes scale, mapping, stale frames and depth
without z-fighting. The offset is an adapter diagnostic transform, not edited
source geometry. Use a controlled world-space offset and test camera rotation
so the diagnostic does not accidentally orbit the original.

After that gate passes, use zero offset and the existing player identity,
capture-first suppression and Acquire/Commit/Cancel sequence. Suppress the
player's supported primary/secondary lists only after matching insertion has
committed for that native source frame. Unknown callers, transparent/cloaked
geometry and unsupported revisions remain native. Do not replace the first
owner encountered or suppress at a shared draw flush.

Validate native shields, grid intersections, weapons and pause text through
their normal rendering, without capture/replay. On destruction, retire the
qualified intact instance and leave unsupported debris native. Supporting UE
destruction, damage and all-owner replacement are subsequent coverage increments,
not conditions hidden inside this first player-ship proof.

## Migration Plan — six measured checkpoints

| Stage | Deliverable | Exit gate |
| --- | --- | --- |
| 1. Packaged foundation | World-space assets/camera, runtime/editor separation, Exit controls, explicit diagnostics | Packaged replay preserves source pixels/arrays with independent camera/object motion, asset sharing and normal teardown. Development/Shipping checks agree. |
| 2. Standalone GPU return | UE-produced colour/depth/owner transaction in a D3D11 consumer | Real cross-process GPU transfer, changing-content identity, correct formats/depth/owner bits and resource lifetime pass. No game interception yet. |
| 3. Live read-only UE scene | Fresh assets and retained SFC camera/poses in UE | Player identity, repeated camera changes, late assets and source shutdown work without changing SFC rendering. No saved-ship dependency. |
| 4. Additive in-game insertion | Full textured offset player inside the native frame | Sponsor sees it in the correct scene order with normal controls/HUD and no recurring flicker. No original suppression. |
| 5. One-player replacement | Zero offset and commit-qualified suppression | One aligned ship, solid markings, correct shield/text occlusion, no stale/doubled ship and normal fallback/recovery. |
| 6. Qualification/handoff | Bounded stress/relaunch evidence and interface documentation | Exact tested capability and remaining coverage gaps recorded separately from future full-scene work. |

Stages are separately reviewable. Stage 2 is deliberately before live scene
wiring so an unavailable return mechanism is discovered early. Only stages
with a demonstrated lower-level gate may proceed to native suppression.

Most work uses captured/replayed input and standalone GPU tests. Prepare sponsor
checks only after that evidence passes. Live read-only viewing can be combined
with the additive checkout when already qualified offline. Normally two focused
gameplay checkouts suffice: additive, then replacement. Failures may require a
specific further run; do not promise an arbitrary number of successful attempts.

Preserve the current prepared/elevated-parent workflow and one copy-paste CMD
launcher per requested checkout. Use the existing short tactical test mode for
focused evidence. Normal play remains untimed, diagnostics off by default and
cleanup follows early exit. Do not modify appearance profiles or user INIs.
Reusing the test installation requires serial sessions and transactional recovery.
Do not create another full game copy or replace the tester ZIP.

Rollback is backend selection plus ordinary transactional restoration. Stop
wakes pending work, rejects new commits and drains owned CPU/GPU leases before
release. The current native recovery policy remains authoritative. Do not add
arbitrary whole-run aborts for ordinary missed output.

## Risks / Trade-offs

- **Texture Share may add blocking or incompatible ownership.** Qualify its
  pinned implementation first. If unsuitable, name the gap and qualify the
  small public-RHI/Windows route. No assumed cross-API support or engine patch.
- **Runtime StaticMesh may not supply a desired lighting feature.** Test actual
  packaged capabilities. Do not equate ray tracing, Lumen, Nanite and runtime
  asset building. No appearance tuning is required for initial insertion.
- **UE render latency may exceed the existing native deadline.** Measure the
  producer, GPU copy and native readiness separately. Stable insertion is a
  gate, not a promise. Do not relax frame identity or mask accumulating queues.
- **Native return helpers contain D3D9-era assumptions.** Inspect their real
  format, handle-width, startup and session requirements. Isolate backend
  import behavior and add paired tests for any required versioned extension.
- **Large fleet loading can amplify duplicate resources.** Qualify shared assets
  and measured 1/6/100+ owner replay within existing declared capacities. Do not
  add a new magic hull cap or turn diagnostic limits into gameplay stops.

## Operating limits and qualification records

Preserve the existing source/asset budgets. Keep the two-slot game-output pool
unless a separately justified contract change is necessary. Check total output
allocation against the existing 128 MiB budget, including intermediate/export
surfaces, rather than checking one texture alone. Reject unsupported extents
for insertion while native rendering continues. Do not expand queue depth.

Detailed diagnostic logs stay within 32 MiB per test session, with a warning
at 16 MiB and counters thereafter. Active evidence stays within the authorized
20 GB allowance. Reuse builds and fixtures, avoid duplicate game/package trees,
and account for existing proof storage before new runs. Exhausting optional
diagnostic recording stops recording, not untimed normal gameplay. Required
working-resource allocation failure prevents new commits and follows existing
native recovery.

Record cold/warm decode, asset creation, base-texture readiness, optional
enhancement readiness, first completed image, transfer, native readiness and
final presentation separately. Report median/p95/p99/max, source-to-display
age, missed-admission streaks and resource occupancy. Use optional bounded UE
Insights traces and existing native timing tools. First priority is to eliminate
unnecessary waits; do not reintroduce full-asset comparisons on normal frames.

## Capability questions resolved by gates

The built-in sharing path, packaged runtime-mesh feature set and measured
ExtraFrame readiness are deliberately experimental acceptance gates. A failed
gate reports its exact missing capability and keeps the preceding successful
checkpoint. It does not authorize changing the architecture, the user's game
settings or the timing policy. No additional sponsor decision is required to
write this plan; implementation is not part of the planning turn.
