# Live D3D9 / Remix interface audit — Run159

## Disposition

**Functional, but not yet a clean portable interface.** The ordinary D3D9 scene
submission and pinned NVIDIA output API are real. The surrounding transport still
contains successive proof-era layers. Do not add broad timing infrastructure or
change buffering until these boundaries are adjudicated.

Audit only: no implementation/runtime/tuning/client changes, new game/profiler
run, source relocation, dependency upgrade or architecture pivot. Preserve all
existing dirty work and normal Remix1.5.2. Existing 1.6.1 candidate stays isolated.
This is not an allegation that every custom component is wrong, nor proof any
individual finding causes the observed hiccups.

Authority: newest HANDOFF/Run158, approved D3D9 adapter transition/execution plan,
retained multi-ship contract, neutral scene contract, pipeline modes and Run127
work/safeguards audit. Those project contracts describe implementation intent;
they do not supersede Microsoft/NVIDIA API contracts.

## Documentation checked

Consulted exact normal source pin b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4,
not just latest main or the newer Minecraft example:

- [NVIDIA public header](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/public/include/remix/remix_c.h)
  and [API implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_remix_api.cpp):
  actual Remix-device registration, queued copy into supplied D3D9 surface,
  picking retention, external swapchain limitations and Shutdown ownership.
  Copy success queues work; it is not a cross-process completion fence.
- [Microsoft D3DPOOL](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dpool):
  MANAGED is permitted for D3D9, explicitly invalid for D3D9Ex.
- [Microsoft OpenSharedResource](https://learn.microsoft.com/en-us/windows/win32/api/d3d11/nf-d3d11-id3d11device-opensharedresource):
  shared-resource descriptor/handle rules and restricted generic D3D9/11 formats.
- [Microsoft query completion](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3dquery9-getdata)
  and [Flush](https://learn.microsoft.com/en-us/windows/win32/api/d3d11/nf-d3d11-id3d11devicecontext-flush):
  submission and completion are different; required synchronization cannot be
  deleted merely because Flush/waits cost time.

Normal deps manifest retains release/archive/header hashes and API0.6.4. Candidate
release-linked source versus packaged build caveat from prior runs remains.
Source inspection does not establish instruction-level parity for vendor DLLs.

## Actual boundaries, not an idealized drawing

1. **SFC x86:** semantic/persistent state capture, coherent owner-set publication,
   current game camera and depth; original drawing unchanged.
2. **External preparation coordinator/workers:** fresh packets -> retained neutral
   scene/texture files + Remix-specific material layers. No OBJ/Toolkit dependency
   on active gameplay route. CPU preparation is outside game callbacks.
3. **x64 native host:** owns D3D9Ex device from pinned Remix, ordinary retained
   VB/IB/textures and indexed draws; Remix light/config/output API adjuncts.
4. **Host output:** NVIDIA copies color/depth into host-owned shared D3D9/D3D11
   surfaces; host-generated coverage/image grade; GPU completion before publish.
5. **Separate x86 D3D11 receiver:** opens host surfaces, copies all three planes
   into its own two-slot game output pool, waits for completion, publishes pool,
   then acknowledges producer before producer can reuse its single source set.
6. **SFC-side compositor:** opens pool, pairs output with saved complete N-1
   color/depth/HUD, signals GPU-read lease, never waits in game callback.

The receiver in step5 is NOT NVIDIA's x86 Remix bridge, a required DLL wrapper,
or an API-mandated process. It is our standalone proof receiver promoted into
the live return path. GPU image bytes do not cross CPU IPC or screenshot files.

## Findings

### IF01 — documented D3D9Ex resource-pool mismatch — correction priority 1

CONFIRMED source mismatch. `d3d9_direct_host.cpp:73` creates Device9Ex, while
shared `d3d9_replay.cpp:81,84,93` requests MANAGED VB/IB/textures. That renderer
was originally a plain D3D9 replay consumer, where this pool is appropriate.
Successful Remix fixtures qualify current pinned behavior, NOT generic native
D3D9Ex compliance. Not proven cause of hiccups or loading delay.

Required cleanup: explicit device/resource policy. Keep ordinary scene data;
use supported DEFAULT VB/IB and a documented DEFAULT texture upload path for Ex,
with explicit reset/recreation ownership. Preserve classic D3D9 test policy where
valid. Do not blindly change texture pool and retain an invalid LockRect path.
Offline native Ex + pinned Remix byte/UV/material/output checks before gameplay.

### IF02 — relay serialization is project-owned, not a vendor requirement

CONFIRMED in `output_producer.h::publish`, `output_receiver.cpp`,
`game_output_writer.h` and `d3d9_direct_host.cpp:195`.
The renderer cannot advance past publish until another process copies/fences/
acknowledges its single source output set. Current ACK is ESSENTIAL to safe reuse
of that topology. Removing waits/ACK alone creates a race, not an optimization.

The extra receiver/copy was useful for cross-bitness ownership proof. Do not
freeze it into the clean backend interface. A direct host-owned bounded output
pool opened by SFC is the smallest simplification candidate, NOT demonstrated
yet: preserve resource descriptors, source IDs, producer completion, consumer
GPU read completion, sequence/generation, disconnect/reset and bounded pressure.
Qualify with the existing standalone x86 consumer first; no Vulkan raw-image
identifier shortcut or speculative new renderer. Copy is ~24.9MB/output for
three1080p planes; bandwidth is not established as the bottleneck.

### IF03 — single-owner gate remains ahead of multi-owner scene

`d3d9_direct_host.cpp:143` calls `ownerInput.next(scene,...)`, which qualifies the
selected scheduling anchor against bootstrap Scene vertices before
`cohort.next`/per-instance decode/projection validation in `multi_scene_runtime.h`.
The coherent multi-ship set still depends on the legacy single-owner input route.
Each accepted instance then undergoes another sampled native-composed projection
oracle. Backend consumes native96-word rows, not just neutral Frame matrices.

Session/owner/content/camera coherence and finite values remain essential.
Repeated ~64-point native-vs-converted projection comparisons are integration
oracle checks, not NVIDIA submission requirements. They remain active even in
Performance mode and can reject work. Native36/4 unqualified counts are real,
but combined counter has no timestamp/reason: NOT proof this oracle caused them.

Required cleanup: make coherent scene frame + instances the submission unit;
keep anchor only as source correlation if needed, not implicit whole-scene
ownership. Separate essential validity from test oracle. Preserve oracle in Test
or bounded sampling and prove neutral transform equivalence offline BEFORE any
live policy removal. No guessed matrices or weakened frame/identity matching.

### IF04 — hard-coded bootstrap is proof policy, not readiness interface

`d3d9_direct_host.cpp:155`: frame0 always24Presents with10ms sleeps; ordinary live
updates1Present. No NVIDIA source establishes24 as a material-residency or shader
readiness guarantee. Bootstrap uses first scene before multi-owner main loop.
Source launch-time initialization itself is intentional and should remain.

Prior isolated24→4 control is NOT qualified visual parity and did not remove
first-use pause. Do not promote it blindly. Clean contract needs explicit
initial-assets/renderer/output states with bounded readiness/failure, not a magic
number or a switch that hides incomplete materials. Current behavior stays frozen
until documented supported readiness or matched evidence qualifies replacement.

### IF05 — material publication is a backend lifecycle concern

Coordinator `multi_scene_relay.py:305–319` atomically rebuilds the root USD sublayer
list for unique material arrivals. USD material declarations are a supported
Remix route; using them is not itself a violation or Toolkit dependency. Existing
NVIDIA async mechanisms remain the first investigation, not a homebrew loader.

However packet/geometry admission ACK, material-library publication and material
consumption/readiness are not one documented state. File replacement is NOT proof
the runtime has consumed it. Keep this lifecycle private to Remix adapter, not a
D3D9-neutral readiness assumption. Late-arrival stalls and non-arrival hiccups
remain separate. Changing to SDK geometry is not a cleanup of this D3D9 proof.

### IF06 — evidence and obsolete picking work leak into live host

- Performance mode disables CSV/readback, but `OutputPeer::publish` formats an
  OUTPUT_ACK line EVERY output regardless of mode. Deferred buffer avoids hot
  disk IO but not formatting. Test evidence should not define producer semantics.
- `SFC_D3D9_LIVE_TIMING` also enables real input/lifetime/notification behavior;
  it cannot simply be cleared to disable diagnostics. Preserve function and
  separate policy rather than multiplying experiment switches.
- Host requests vendor object-picking retention once at line97, even though live
  additive branch copies only vendor color/depth and overwrites third plane with
  its own union coverage. NVIDIA source confirms the first picking-copy request
  enables retention. This is a concrete unused live-path vendor request, NOT proof
  of its memory/time cost. Gate it to workflows that actually consume picking;
  keep our required coverage plane and its tests.
- `NormalCoverage` says ONE-owner in its header, but multiship uses union depth
  coverage labeled by scheduling anchor. Existing pool flag documents union,
  not per-ship picking. This is a naming/contract clarity defect; NOT a new finding
  that current code can identify per-owner pixels. Do not use it for replacement.

### IF07 — interoperability is qualified for pinned runtime, not universal

Current shared output uses BGRA8 plus R32_FLOAT. Microsoft's generic D3D9/11
sharing list is narrower. Current Remix implementation/driver fixtures demonstrate
this pair, not universal native D3D9Ex support. Keep format/interop capability
qualification and resource ownership in backend-specific output descriptor.
Future D3D12 must qualify its own formats/synchronization, not inherit legacy
handles, pool choices or Remix-only texture conversion.

### IF08 — essential safeguards are not clutter

Keep version/session/PID/owner epochs/content references, finite schema/count/
index checks, coherent camera/cohort identity, source-frame provenance, GPU
LUID/descriptors, current-user mapping ACLs, producer completion and GPU-read
leases, nonblocking game callbacks, bounded queues/memory/evidence, owned-process
shutdown, restoration/client hashes and exact dependency pins. Legacy GPU handles
are not a malicious-same-user isolation boundary; no stronger claim is made.

Keep whole-frame color/depth/HUD pairing. Old ship pixels on a new camera frame
are not a valid cleanup. Required fencing is not arbitrary delay. Common-device
disposal warnings and profiler-only native teardown uncertainty remain separate
open issues; successful process exit is not leak-free qualification.

## Minimal clean contract / sequence

No new generic engine, serialization framework or renderer architecture needed:

- Immutable retained assets: content identity, geometry/groups/images, revision.
- Coherent scene frames: session/frame/camera/viewport + owner instances/poses.
- Backend-private resource/material readiness and lifecycle.
- Output leases: actual format/extent/color/depth/coverage semantics, matching
  scene provenance and explicit producer/consumer completion ownership.
- Separate diagnostic policy, never an implicit functional transport mode.

Recommended execution order: IF01 supported Ex resource/upload policy and IF06
unused live work first, preserving exact pixels/settings; then qualify IF02
direct bounded return pool using existing standalone receiver as TEST consumer,
not an obligatory relay. Address IF03 scene submission boundary with existing
oracle tests. Investigate IF04/IF05 readiness using pinned vendor mechanisms.
No promise these changes alone remove hiccups or reach2s. No new sponsor run
needed just to establish these source findings.

## Validation / repository state

Existing504Python tests PASS6.798s; Performance read-only preflight PASS. No GPU
fixture or gameplay started. These tests do NOT establish native Ex portability
or completion of any proposed cleanup. Native renderer/source/settings/pins and
existing exact-source qualification unchanged. HEADfe2eaf7/index empty/all prior
work preserved. New audit/run record/HANDOFF only; no stage/commit/push.
