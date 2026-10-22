# D3D9 adapter transition — bounded proof before replacement

Newest2026-10-19:[Run73](../runs/2026-10-19-codex-direct64-d3d9-output.md).
Sponsor approved direct64bit ordinary-D3D9 host;offline GPU output/projection/depth
subproof CONFIRMED within one process. Gate2 CONTINUES pending standalone32bit
consumer/ownership,then timing architecture. SFC capture32bit unchanged,no SDK
geometry registration. This supersedes the pending-approval next action below.

Latest2026-10-19:[Run72](../runs/2026-10-19-codex-d3d9-awake-and-output-capabilities.md)
clears native startup/reference after awake desktop. Normal32bit Remix bridge
initializes API but lacks public output-copy/external-image/picking functions.
Planned return route BLOCKED;live integration not started. Proposed separate64bit
ordinary-D3D9 host/output qualification needs sponsor approval. This supersedes
the inactive-desktop next action below;architecture gate remains OPEN.

2026-10-19 execution authority:sponsor approved the detailed
[startup-to-additive-SFC plan](d3d9-to-sfc-additive-execution-plan.md),originals ON.
[Run71](../runs/2026-10-19-codex-d3d9-startup-and-return-gates.md) found active
Screen-saver desktop while consumer uses Default. Gate1 pauses for normal user
wake/unlock and paired native retest;cause strong hypothesis,not confirmed yet.
This supersedes the generic next-action wording below,not the architecture gates.

Date:2026-10-19. Status:historical plain-D3D9 proof CONFIRMED;normal Remix
geometry/primary-image delivery CONFIRMED,overall qualification PARTIAL.
Final native regression,camera-export omission and disposal warning remain open;
live integration NOT started. [Run70](../runs/2026-10-19-codex-normal-d3d9-remix-proof.md)
supersedes old next-action wording,not the reviewed architecture gates.
See [Run69](../runs/2026-10-19-codex-plain-d3d9-proof.md) and
[neutral view contract](scene-contract-v1.md). Full portability gate remains OPEN.
Authority:sponsor requests updated pathway to D3D9,then D3D12. This is not a CDD
amendment,gate PASS,authorization to replace the accepted installation or commit.
Governing [renderer boundary gate](../decisions/2026-10-18-renderer-independent-boundary-gate.md)
remains OPEN;[CDD](../requirements/Starfleet%20Command%20Rendering%20Modernization%20Capability%20Requirements.md)
and approved milestone allocation remain authoritative.

## Recommendation / disposition of existing work

Preserve current SDK renderer as a reference backend,not the permanent design.
Park further SDK-specific replacement,depth-display cadence fixes,appearance
tuning and extra gameplay requests. Run67 established native depth availability
but not usable occlusion. Its30Hz fresh-output-only path is not a replacement
baseline. Do not discard its evidence or treat fallback as steady-state success.

No additional SFC runtime test is a prerequisite to the FIRST offline D3D9 proof.
Reuse existing capture,assets,mathematical camera tests and timing logs. A specific
missing relationship may justify one narrowly scoped later observation.

## First increment — same captured ship,ordinary D3D9,no Remix

Input:one provenance-qualified fresh runtime mesh packet and original resolved
images from an accepted capture,plus a coherent owner/camera snapshot. Use captured
geometry,not a conversion of the installed MOD file. Add a second different asset
and shared-asset/distinct-owner fixture offline;no universal coverage claim.

1. Inventory current payload meanings and isolate a minimal neutral view of
   positions,indices,corner normals/UVs,groups,image hashes,owner epoch/revision,
   transforms,camera/viewport,qualified lights and frame/session identity.
   Preserve raw source evidence separately;do not force native17word transforms
   into a guessed matrix or include Remix handles/material structs in the contract.
   Reuse existing layouts where sound;no new engine/framework or redundant network
   format merely to create an abstraction.
2. Build a small Windows x86 D3D9 reference consumer,matching the existing game
   architecture for this initial experiment. Use standard reusable vertex/index
   buffers,original textures,explicit world/view/projection and fixed-function
   state. Qualify DLL dependency loading so plain D3D9 really runs without Remix.
   UV/orientation/color conversion must be backend-qualified,not inherited from
   the Remix-only V correction. Start with a documented simple material/light;
   appearance parity is not this gate.
3. Replay deterministic camera/object motion and lifetime/revision changes through
   the SAME neutral scene input used by the reference SDK adapter. Render complete
   snapshots,not independently sampled camera and pose. Test missing resources,
   invalid payloads,resize/device reset,resource ownership and clean shutdown.

Acceptance:matching packet/image hashes and group assignments;read-back geometry
and UVs match;projection matches independent native-composed-transform oracle
using existing tolerances where applicable;both distinct assets render without
saved USD/template or Remix SDK dependency;owner retirement/revision not confused;
bounded resources and clean reset/exit. Record actual results,not visual plausibility
alone. Native/transport/Python regressions and unchanged source/client checks pass.
No sponsor gameplay needed. Stop for review with this small proof.

## Second gate — normal Remix interception of that D3D9 scene

After reference proof review,pin and verify compatible x86 runtime/dependencies,
then run the identical D3D9 consumer through normal Remix interception. No public
SDK mesh registration in this adapter. Verify recognized meshes/instances,textures,
camera/transform changes and stable resource identity using runtime capture/logs.
An overlay appearing or a fullscreen texture is NOT success. Compare against
plain D3D9 output and the existing SDK reference;do not tune appearance yet.

If capture fails,investigate the exact draw/transform/render-target classification
or dependency issue. Do not automatically reconstruct the lost custom shim,
install a new translator,patch Remix internals or promise compatibility.

## Presentation architecture gate — before live in-game implementation

D3D9 rendering proof is not SFC display integration. Make this decision explicit:
where is a complete source frame sealed,and how are its scene depth,effects/UI
and rendered replacement made part of ONE corresponding displayed frame?

Preferred hypothesis to qualify:a frame-boundary-driven x86 D3D9 adapter,
initially evaluated alongside the existing game-facing component,with no Python
polling scheduler or arbitrary30Hz publication cap on the critical frame path.
This does not mandate moving Remix internals in-process or assume same-process
code alone solves GPU timing. Keep disk/image preparation and resource creation
off original render callbacks;cache assets by content outside the critical path.

Before choosing integration topology,measure source frame/camera/pose seal,
submission,GPU completion,transfer and present with sequence IDs/common timestamps,
CPU/GPU timings and queue occupancy. Distinguish game cadence,bridge throttle,
renderer capacity and transfer delay;do not equate a draw-counter rate with FPS.
First use offline replay/existing logs;request a bounded live timing run ONLY
where evidence cannot answer a specific question.

Compare an in-process submission adapter and a bounded out-of-process producer
only against actual ownership,API interop,device lifetime and timing evidence.
Select ONE implementation after the gate;do not develop both speculative paths.
If cross-process remains,show that complete matching native scene and returned
output can be presented coherently;old ship pixels over a current camera/depth
are not synchronization. If whole-frame buffering is necessary,qualify all
retained scene/UI/input timing and latency implications before adopting it.

Required gate result:document exact insertion point,shared/copy mechanism and
formats,ownership/fences,present scheduling,maximum queue/latency/resource bounds,
behavior under slow renderer/device reset/disconnect,and whether measured
performance supports CDD KPP-3. ExistingReShade return can remain a development
compositor only if it meets that contract;its removal is not a prerequisite by
itself. No guaranteed portable depth/coverage export from normal interception is
assumed:qualify it before promising partial-scene replacement.

Reject indefinite waits,normal-frame original fallback,unbounded queues and
indefinitely cached pixels. CDD Threshold p95<=33.3ms,zero control-blocking stalls
and resource-exhaustion failures remain;also measure end-to-end latency because
good frame-time alone does not establish responsive synchronized output.
Original rendering is emergency rollback,not a substitute for demonstrated
playable replacement. If neither topology meets the contract,report the precise
blocker before more gameplay or suppression work.

## Later gates — coarse only

- Live D3D9 scene delivery at measured source cadence,then coherent in-game
  composition preserving native depth/effects/tactical UI;originals still ON.
- Owner-specific batch-safe suppression only after matching-frame delivery and
  coverage/visibility qualify. No SDK-path completion prerequisite.
- D3D12 adapter against the SAME scene contract after D3D9 proof/integration
  review. Separate API-specific resources,materials,synchronization and capability
  support. D3D12 is not a normal input to Remix,nor a guarantee of future-tech
  compatibility. No detailed D3D12 implementation plan now.

## Records / limits / exact next action

Retain existing capture/output/security/current-user isolation/client-hash rules;
offline outputs bounded and recoverably compacted after analysis. Test only copied
install when live integration is authorized;no helper,unrelated RE or staging/commit.
Each increment records sources/dependencies,tests,confidence and unresolved fields.

Exact next action:resolve native windowed-D3D9 compatibility regression without
bypassing checks,then independently qualify actual Remix camera/viewport output.
Normal interception now captures both complete ships;the missing exported camera
field must not silently become assumed runtime correctness. Do not begin live
implementation before the presentation architecture gate.

References: [Microsoft fixed-function transforms](https://learn.microsoft.com/en-us/windows/win32/direct3d9/transforms),
[NVIDIA compatibility guidance](https://github.com/NVIDIAGameWorks/rtx-remix/wiki/Compatibility),
[Run67](../runs/2026-10-19-codex-scene-depth-runtime-review.md).
