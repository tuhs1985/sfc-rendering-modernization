# Run88 — current frame path efficiency and scaling audit

Local2026-10-20 America/New_York. Sponsor requests checking avoidable time losses,
especially before all-model capture. Read-only source/evidence audit,not authority
to change architecture or remove synchronization checks. Fuel Guard attached via
trusted-hook receipt,no daemon started. HEADd29111f7,index empty,existing dirty work
preserved. No SFC/renderer/helper/agents/build/stage/commit/push.

## Confirmed current path / overlooked overhead

1. tools/d3d9_proof/d3d9_direct_host.cpp::wait9 issues D3D9 EVENT,then polls
   GetData(D3DGETDATA_FLUSH) with Sleep(1) until complete. This is on EVERY rendered
   output before D3D11 grade/coverage. Run82/83event fences replaced later native
   D3D11postprocess/receiver waits,NOT this D3D9/Remix boundary. Do not claim all
   millisecond GPU polling was removed. Run87render-ready timing includes this
   polling/scheduler behavior AND actual GPU completion;not pure renderer time.
   Exact removable delay unmeasured:no poll-count/last-not-ready/first-ready stamps.
2. live_owner_input.h::next samples latest bounded inbox,then Sleep(1) if empty.
   CONFIRMED potential scheduler wakeup margin loss;no assumption exactly1ms on
   this machine. Existing taken_qpc includes take/checksum/decode/projection checks
   before capture,so offered->taken is NOT isolated sleep cost.
3. d3d9_direct_host.cpp and output_receiver.cpp set cout unitbuf. RETURNED is
   printed before peer.publish;OUTPUT_ACK is printed before publish returns;
   RECEIVED follows receiver ACK. Multiple stream insertions flush individually.
   This is actual synchronous diagnostic I/O in renderer/receiver workers,not SFC
   callbacks. Other timing CSV writes are buffered but still critical-worker work.
   Peer timing includes host RETURNED/ACK overhead;not isolated GPU copy cost.
   No measured proof log I/O is the dominant delay. Move to fixed bounded telemetry
   records and off-path formatting/writing rather than losing evidence.
4. build_direct64.ps1/build_receiver.ps1 request /std:c++20 /EHsc /W4 /WX but
   no explicit optimized release flag. Reproducible performance build must specify
   optimization explicitly and record inherited CL/_CL_ options;do not claim
   verified machine-code performance from absent flags alone. Preserve precise
   floating-point/ABI behavior;no blanket fast-math or unreviewed SFC hook build change.
5. live_owner_input validates projected geometry at~64sampled vertices for every
   update. projection_matches reparses native composed matrix and multiplies four
   matrices/vectors per sample. Useful correctness evidence,not proved bottleneck.
   Precompute invariants once per packet;retain finite/identity checks and offline
   oracle coverage. Do not delete safeguards merely because speed matters.
6. OutputPeer::publish waits for receiver GPU copy/ACK before next host input.
   This serializes reuse of a single producer output generation. Necessary with
   CURRENT resource ownership;cannot remove ACK/fences and safely overwrite an
   acquired texture. Receiver copies three full-resolution surfaces into two-slot
   game pool. At1920x1080*12bytes this is24,883,200B/frame(~1.493GB/s at60Hz)
   payload for this extra GPUcopy alone,not total bandwidth or PCIe traffic.
   Removing copy/serialization requires reviewed pooled-output ownership,matching
   API compatibility and GPU tests;not a casual wait deletion or CPU screenshot path.

## Costs already NOT repeated per frame

Renderer constructor creates/uploads VB,IB,textures once. Runtime shared handles,
SRVs,queries,pool resources and shaders are prepared once,not per ship per frame.
Live mode sets TIMING_ONLY=1 and noReadback;CPU pixel dumps/staging readbacks are
disabled. One bootstrap frame performs24warm-up Presents;normal live frames one
Present,not24. No renderer pacing Sleep(10) on steady single-Present path.
Light file reader runs separately;per-frame light stage~.0042ms in Run87.
Game import worker Sleep(1) checks initialization/lifetime,NOT repeated import of
every completed frame. Distinguish this from critical input and D3D9wait polling.
Game compositor uses nonblocking query retirement and restores immediate-context
state through deferred command execution. Keep restoration/lease safety intact.
Run86DDS fix retains identical images and reduces offline prep~16.67->1.23..1.35s.

## Multi-model implications (constraints,not implementation)

Current renderer is intentionally one selected asset/owner. Renderer::draw clears
target/depth and BeginScene/EndScene each call;host Presents after it. Calling this
whole path for each owner would erase prior ships AND multiply render/return cost.
Future shared scene must clear/begin once,draw instances from resident content-
keyed geometry/material caches,then end/present/render/export/grade/copy once per
scene frame. Camera/global lights/image policy once per frame;owner pose once per
instance;mesh/images only on qualified new asset revision. No per-owner renderer
process,full-screen output triplet,Present,global light update or image conversion.
Do not estimate30ships as30times single-ship13ms:shared cost amortizes,but actual
draw/geometry/ray-tracing/acceleration-structure cost still grows and needs stress
measurement. Current isolated-owner depth-sentinel coverage is NOT multiship IDs;
preserve explicit limitation,do not assign one owner's identity to the whole scene.
Current transport remains one-owner;no accidental universal/all-model claim.

## Prioritized next bounded work

First add low-cost bounded timing counters to isolate input wait/checks,D3D9query
poll count/wake intervals,and output-ready versus host ACK. Keep telemetry in fixed
memory;format off critical path. This measurement replaces rather than piles on
per-frame flushed diagnostics. Compare explicit optimized build and buffered/off-
path logging using deterministic changing-camera input while preserving output.
Then evaluate notified input wakeup and qualified D3D9completion strategy. A D3D11
event from a DIFFERENT device does not by itself prove translated D3D9/Vulkan GPU
work finished;never substitute an unrelated fence. No unbounded busy spin or global
timer/security changes. Preserve exact frame/owner identity,current effects,logs
bounds,disconnect cleanup. Quantify median,p95,worst and late streaks,not just FPS.

Necessary GPU work cannot be optimized away. If measured unavoidable tails exceed
the source window,seek explicit coordinated whole-frame synchronization decision;
do not solve by stale ship pixels,fallback claims,lowered quality or loosened IDs.
No fixes implemented by this audit. No new sponsor gameplay request/launcher.

Validation:source call paths inspected,Run87per-frame joins reused,byte arithmetic
checked,referenced paths verified,git diff --check/index status checked. No native
or Python source changed here;370previous tests historical,not rerun as new proof.
Files:this record,HANDOFF. Runtime source/client artifacts unchanged,index empty,
all prior/current changes unstaged/uncommitted. M1 CONTINUES,delivery OPEN.
