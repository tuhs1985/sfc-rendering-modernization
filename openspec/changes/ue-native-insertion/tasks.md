# UE-to-SFC insertion implementation plan

> For implementation, use the executing-plans workflow inline. This planning
> turn does not authorize code edits, staging, commits or publication.

**Goal:** return packaged UE output to SFC, then replace one qualified player
ship through the current native insertion boundary.

**Architecture:** retain the neutral x86 capture/session input. A separate x64
UE runtime plugin owns retained assets/world state and publishes completed
output through a qualified GPU adapter into the existing native game pool.
The current game-side x86 add-on, capture-first gate and ExtraFrame policy remain.

**Tech stack:** pinned UE 5.8.4 CL 58902052, C++, existing Windows IPC,
DX12 UE rendering and the established D3D11/native insertion consumer.

**Spec:** [scene consumer](specs/ue-scene-consumer/spec.md),
[game output](specs/ue-game-output/spec.md), [design](design.md).

## Global constraints

- Preserve `src/ue5_proof`, its packaged comparator, the accepted Remix alpha,
  original game assets, appearance profiles and user preferences.
- Current test installation only, serial game/GPU runs, existing preparation
  and transactional cleanup. No new full game copies.
- ExtraFrame stays standard. No new source-rate cap, stacked deadline or
  arbitrary owner-count clamp. Reuse declared source and memory budgets.
- No engine patch, CPU screenshot transfer, late detached overlay, native
  effect replay, full-scene rollout or removal of dgVoodoo/ReShade.
- Keep detailed logs within 32 MiB, warn at 16 MiB, active evidence within
  20 GB, and output resources within 128 MiB with the existing two-slot pool.
  Diagnostic limits stop recording, not untimed normal play.
- All tasks below are pending. Update owning contracts and handoff after each
  verified stage. A failed essential gate reports the exact blocker.

## Review focus

- New owner/session identity must not inherit a recycled pointer's asset.
- Object and camera motion must not rewrite geometry or revive retired output.
- UE completion, D3D11 copy completion and game GPU lease completion are distinct.
- Device/target generation and viewport offsets must match every accepted image.
- Missing resources and early exit must work with diagnostics/assertions disabled.

## 1. Packaged world-space foundation

**Proposed files:**
`src/ue_wrapper/SFCUEWrapper.uproject`, `Config/`,
`Plugins/SFCBridge/SFCBridge.uplugin`, and
`Plugins/SFCBridge/Source/SFCBridgeRuntime/{Public,Private}/` for session/world
subsystems, source types/reader, asset cache, source camera and Exit controls.
Keep editor asset generation in `SFCBridgeEditor`. Tests belong in the runtime
module's development test directory and `tools/ue5_proof` qualification tools.
Do not move the working proof or neutral interface into the plugin.

**Boundary:** original asset definitions + identified immutable source frames
enter the adapter. Separate retained asset handles, owner instances and one
source camera leave it. Runtime code has no dependency on `UnrealEd`.

- [ ] 1.1 Add failing replay checks for independent model/camera translation and rotation, shared owners, viewport mapping and constant local geometry; verify they expose the proof's camera-baking/duplication behavior.
- [ ] 1.2 Implement the session/world lifetime split and separate local-space asset, owner and camera state; verify exact projection against the retained source-space reference and unchanged UV/group data.
- [ ] 1.3 Qualify runtime StaticMesh fast building against the compact procedural baseline, using the intact ships and recorded fragment topology; verify packaged source pixels/attributes, geometry sharing and required shadow/ray-tracing capability before selecting a path.
- [ ] 1.4 Make required I/O and structural admission independent of assertions, with recoverable missing/bad input; verify intended Development and Shipping packages and truthful diagnostic receipt flags.
- [ ] 1.5 Separate editor generation, pin full engine/build dependencies, allowlist plugins/config and add Exit/Escape/cleanup; verify relocation, early exit, immediate relaunch and no injected private generated configuration in the candidate package.
- [ ] 1.6 Publish the foundation qualification record, measured asset/transform costs and selected mesh rationale; update the interface/handoff/Obsidian and read them back before proceeding.

## 2. Standalone GPU output feasibility and contract

**Proposed files:** runtime plugin `SFCOutputProducer`/`SFCOutputTicket` files,
`tools/ue5_proof/run_gpu_exchange.py`, a standalone D3D11 consumer/fixture, and
backend-specific source under `src/rendering/ue/` if needed. Reuse the neutral
parts of `game_output_writer.h`, `output_channel.h` and existing lease tests.
Document any required protocol extension instead of relaxing the existing one.

**Boundary:** one UE-completed render ticket with colour/depth/owner resources
enters the export adapter. A D3D11 consumer receives immutable, same-identity
resources and owns their lease until completion. No SFC process is intercepted.

- [ ] 2.1 Evaluate the installed Texture Share public plugin/SDK route with changing colour/depth/owner fixtures; verify actual UE DX12-to-D3D11 exchange, CPU-copy absence, same-LUID selection, stop/disconnect and bounded/non-stacked synchronization.
- [ ] 2.2 If that route fails, record its exact unsupported capability and qualify the smallest public-RHI/Windows shared-resource/fence alternative; verify without engine patches or silently switching rendering APIs, otherwise stop at the foundation checkpoint.
- [ ] 2.3 Define the backend output/import contract from the successful experiment, including session/frame/camera/asset identity, handle kind/ownership and completion; verify stale/wrong tickets and 64-bit versus existing 32-bit handle restrictions with process-boundary tests.
- [ ] 2.4 Produce native-compatible colour, physical depth and packed owner coverage from the same snapshot; verify near/far ordering, opaque black markings, exact owner bits, viewport offset and visibly different consecutive poses/markers.
- [ ] 2.5 Exercise target resize/device generation, occupied pool, slow/crashed consumer, failed allocation and stop during GPU use; verify leases drain before reuse and old pixels cannot reappear under new metadata.
- [ ] 2.6 Record the GPU mechanism, limits, timing, descriptor/ownership contract and failures; update the interface/handoff/Obsidian and read back the demonstrated standalone gate.

## 3. Retained live scene input

**Files:** runtime plugin `SFCSourceReader`, session/world subsystems and asset
cache, existing `src/transport/`/scene contracts as necessary, and opt-in UE
backend selection in `src/rendering/renderer_backend.py` and the session entry
point. Keep the existing Remix selector/default behavior intact.

**Boundary:** reuse the established session-owned source transfers through a
neutral reader facade. Original CPU geometry/images plus coherent source
frames enter UE. No UObject is accessed by source receipt workers.

- [ ] 3.1 Qualify the exact reader boundary for original source geometry/images and live frame identities, using actual existing transfers; verify no Remix UV/material processing or saved-template requirement leaks into UE.
- [ ] 3.2 Implement passive startup/late activation and base-model admission as assets arrive; verify renderer startup does not wait for all ships/enhancements and original image identity is retained without expensive repeated comparisons.
- [ ] 3.3 Replay multiple/shared owners, offscreen motion, revision changes, delayed material arrival, retirement, pointer reuse and new sessions through the real reader; verify zero geometry rebuilds for transform-only updates and no cross-associated ship.
- [ ] 3.4 Measure 1/6/100+ representative-owner replay within declared budgets, including GPU/CPU timing and resource growth; verify diagnostics-off operation creates no image/trace recordings and introduces no new count/rate cap.
- [ ] 3.5 Prepare an explicit UE read-only launcher from the existing parent/recovery workflow; verify preflight, cancellation, parent death and relaunch, then record source/camera continuity and any remaining live-only question before additive checkout.

## 4. Additive in-game insertion

**Files:** proposed `src/rendering/ue/ue_output_receiver.cpp`, a UE-specific
checkout launcher, shared native output writer/target contracts where needed,
and backend import glue in `tools/remix_runtime/return_addon.cpp` only if the
existing game-pool interface is insufficient. Keep game-side code x86.

**Boundary:** the x64 UE-selected receiver normalizes output into the current
D3D11 game pool. The existing x86 return adapter consumes the completed pool
through native target/lease rules. Original SFC drawing remains enabled.

- [ ] 4.1 Wire the successful GPU return mechanism into the existing pool and readiness path; verify readiness follows actual game-side GPU copy completion, target generation and coherent output identity, with no new deadline.
- [ ] 4.2 Reuse the native insertion point before later effects/text with suppression disabled and a documented world-space diagnostic offset on the identified player; verify the offset, scene/depth mapping and all graphics-state restoration in the standalone native fixture.
- [ ] 4.3 Run relevant scene, transport, native-insertion and cleanup regressions plus read-only launcher preflight; prepare one copy-paste CMD command only when lower-level gates pass.
- [ ] 4.4 Sponsor checkout: textured offset player, camera turns/zooms, motion, shield exposure, pause text and normal exit; record real insertion provenance and sponsor gameplay observations, then confirm restoration/unchanged protected client files.
- [ ] 4.5 Record additive insertion as its own result, including timing tails and any repeated camera misses; update contracts, run record, status, Obsidian and restart instructions before enabling suppression.

## 5. One-player native replacement

**Files:** UE backend eligibility/output membership, existing player selection,
`tools/native_insertion/{gate_contract,cohort_contract}.h`, current capture-first
suppression dispatch and UE checkout launcher. Extend existing interfaces only
for a demonstrated missing relationship and keep changes paired/versioned.

**Boundary:** after capture, matching output is acquired, inserted and committed
before qualified original primary/secondary lists are suppressed. Existing
ExtraFrame timing and native recovery remain authoritative.

- [ ] 5.1 Add failing transaction checks for wrong owner/revision/session, stale camera, unavailable output and inconsistent primary/secondary decisions; verify no pre-commit suppression or relaxed identity matching.
- [ ] 5.2 Enable zero diagnostic offset and reuse commit-qualified suppression for the identified player only; verify continuing source capture/poses and native behavior for unknown/transparent or unsupported submissions.
- [ ] 5.3 Qualify stationary then moving deterministic native insertion, camera changes, disconnect, missing output, retirement and shutdown; verify no suppressed scene lacks its matching committed replacement and no GPU resources are prematurely reused.
- [ ] 5.4 Prepare sponsor replacement checkout with shields, pause/unpause, camera-away/return and normal movement; require one aligned solid ship, correct native occlusion and normal HUD/controls, then verify cleanup and unchanged client files.
- [ ] 5.5 Record ONE-PLAYER UE REPLACEMENT separately from ADDITIVE UE INSERTION, or report the smallest exact unresolved timing/visibility condition; keep all-owner coverage and feature parity unclaimed.

## 6. Integrated qualification and handoff

- [ ] 6.1 Run the packaged normal entry point and integrated scene/output/recovery regressions, including early exit and repeated mission/world sessions; verify diagnostics and storage limits do not stop normal play.
- [ ] 6.2 Compare source-to-display age, admission misses/streaks, resource occupancy and median/p95/p99/max timing with the retained baseline; distinguish asset startup from completed-image/native-presentation timing and report any accumulating delay.
- [ ] 6.3 Update the neutral-interface and UE output contracts, exact build/dependency receipts, test/run records, handoff, repository status and dated Obsidian entry; refresh the restart brief and read all changed checkpoints back.

## Workflow follow-up

- Leave changes uncommitted unless the sponsor asks for a reviewed checkpoint.
- Broader ship replacement and UE lighting/damage/destruction are later coverage
  changes after this insertion gate. Keep the two SFC-07 gaps separately tracked.
- Archive or publish nothing as a side effect of finishing a test.
