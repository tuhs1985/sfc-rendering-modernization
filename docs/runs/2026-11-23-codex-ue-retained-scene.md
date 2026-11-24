# November 23 — retained UE scene input

Continued uncommitted work on `codex/ue-native-insertion`, parent `1834379`,
using the approved OpenSpec change. Fuel Guard attached at 100% of the five-hour
allowance; sponsor requests a clean stop at 5% or a real input/blocker boundary.
No new game copy, native source-hook edit, alpha change or publication.

## Implemented boundary

The session subsystem now caches geometry, original textures and material sets
separately from owner/revision bindings. The world subsystem owns independent
actors and camera state. Both consume the existing source mapping, immutable
catalog and owner-state slots read-only. Assets remain alive when an owner
leaves view or another owner retires; source epochs prevent pointer reuse from
reviving prior instances. World recreation reuses session assets and the reader.
See the [source contract](../contracts/UE_SOURCE.md).

The first packaged shared-owner test failed before implementation, as expected.
The first implemented attempt then exposed a bootstrap error: header
`asset_ready` is the consuming host's receipt, not a publication counter. The
reader now scans unseen immutable slot guards and validates each descriptor
once. No source wire or acknowledgement policy was changed.

A second readiness failure came from waiting for the intentionally hidden owner
whose next resource revision was not ready. The world now checks eligibility
before scene-proxy readiness, allowing the other ship to render throughout.
Installed public `CaptureScene()` already dispatches end-of-frame component
updates before capture; no extra flush was introduced.

## Pixel-backed lifecycle evidence

`registry-lifecycle-02` verifies eight Development stages through actual source
IPC: two owners sharing one mesh, offscreen motion, unavailable next revision,
late material application, retirement plus late completion, recycled model/source
labels under a new epoch, foreign-session rejection and a stale retired row.
World recreation occurs after the first owner retires. All stages retain one
geometry build, two material sets after the update, and one actual mesh pointer
shared by living owners. Pixel agreement is 99.68–99.99% within three levels.

`registry-slot-reuse-red-01` then demonstrates a missed intermediate tombstone:
the state slot changes epoch but the old actor remains, producing three owners
instead of two. The pinned producer explicitly recycles only retired slots.
The reader now retains the last epoch per slot and retires it on reassignment.
`registry-slot-reuse-green-01` passes all nine stages with independent pixels.

Resource tests found two additional errors and verified their fixes:

- Equal BGRA bytes with different 2D extents reused the wrong texture. Stage 10
  failed at 81.70% pixel agreement. The cache key now includes dimensions/format;
  the new view creates its own texture while geometry remains shared.
- Reordering group enumeration misbound materials to retained mesh slots.
  Stage 11 failed at 54.75%. Materials now map by original group ID into the
  original sections, without rebuilding geometry. `registry-resource-keys-green-01`
  passes all eleven stages.

These are explicit derived fixtures. Original geometry/image bytes are unchanged;
material association/view metadata is synthetic and is not claimed as natural
SFC damage or cloak behavior. The first pixel oracle attempt placed both ships
outside view. Its apparent NaN result was invalidated in `invalid-oracle.json`;
the oracle now requires at least 100 visible source pixels and finite accuracy.

## Current work and remaining gates

The shared-asset publisher now emits a small binding-only definition after the
first complete asset. Its fifth unit test first failed and now passes. The UE
reader has a metadata-only cached-content path and resolves a one-level sibling
definition on cold admission. The first packaged binding-only check reached the
correct two-owner state, then exposed a real Windows diagnostic file race.
Stage receipts are now written closed and atomically published, after the image.
This affects explicit diagnostics, not normal source receipt.

`registry-complete-development-02` and `registry-complete-shipping-01` pass all
14 stages. These include binding-only replay, unsupported-pose hide/return
without retirement, and a recorded F-CA fragment as a new geometry revision.
The fragment retains its actual arrays/images; its synthetic current-session
binding deliberately omits a cross-capture parent join. Final counts are two
geometry builds, five material sets, two actual mesh resources and two living
owners. Every accepted stage has independently compared pixels; accuracy is
99.60–99.98% within three colour levels. Both exit normally. Five publisher tests
and three preserved UE proof tests also pass. Task 3.3 is qualified.

## Representative owner timing and resources

`qualify_registry_timing.py` publishes actual source packets full-rate to the
packaged reader. Its optional sampler uses two public RHI GPU fences, queried
nonblocking on later ticks. Busy measurement slots skip a sample without
delaying source or capture. No image readback or rendered-image CPU transfer
occurs. These are completion-observation timings, including queue/poll latency,
not GPU timestamp execution durations. They exclude native game-pool transfer,
normalization, SFC contention and final presentation. The fixture uses original
F-CA geometry/images with explicitly synthetic independent instance placement;
it does not establish 128 unique-asset or fully lit UE performance.

All rows use 600 completed samples at the captured 1720×1020 tactical extent.
CPU is source receipt plus scene updates; completion begins at capture submission.

| Configuration / owners | CPU median / p99 ms | Completion median / p99 / max ms | Process physical MiB |
| --- | --- | --- | --- |
| Development / 1 | 0.124 / 0.311 | 5.512 / 20.740 / 236.096 | 1061.6 |
| Development / 6 | 0.138 / 0.308 | 5.724 / 23.344 / 214.446 | 1027.5 |
| Development / 100 | 0.312 / 0.680 | 6.379 / 12.615 / 42.332 | 1060.4 |
| Development / 128 | 0.342 / 0.782 | 6.811 / 10.270 / 47.897 | 1075.7 |
| Shipping / 128 | 0.334 / 0.512 | 4.324 / 6.895 / 44.479 | 1362.3 |

Evidence directories: `registry-resources-{one,six,hundred,128}-01` and
`registry-shipping-128-01`. Raw bounded numeric samples preserve initialization
tails. Development's 128-owner first admission produced a 1041 ms source/scene
tick and 1122 ms source-to-observed completion, although cached resource
construction itself totalled 26 ms. An earlier 100-owner run similarly reached
928 ms. These remain startup limitations, not silently excluded steady-state
results or attributed to Defender without evidence. Shipping's observed maximum
source age was 56.461 ms; a gameplay timing guarantee is not established.

Every count retains one actual mesh, 56 textures and 21,970,920 accounted source
bytes. RHI texture counters remain 34,832,384 streaming plus 96,215,040
nonstreaming bytes; these include engine resources and are not total VRAM.
The colour target is 7,017,600 bytes. Process physical/virtual counters are whole
UE process totals, not per-owner allocations. Bounds remain unchanged: 256 MiB
retained source, 128 MiB output allowance, existing source capacity and no new
count/rate cap. Capture skips unchanged snapshots after initial readiness;
it does not wait for the diagnostic sampler or limit source publication.

`registry-normal-hundred-01` and `registry-normal-shipping-128-01` run without
`SFCDiagnostics`, stay alive until the source stops, then exit normally with no
images, traces or renderer receipts. Only the parent writes its final test result.
Task 3.4 is qualified for this declared representative replay scope. Task 3.5's
normal-parent launcher remains next. No live UE/SFC insertion or suppression is
connected.

## Live-parent preparation and stopping point

`run_source_session.py` selects an explicit read-only SourceService behind the
existing session parent. Native startup, copied-process verification, controller,
proxy rollback and interrupted recovery are reused. Its clean environment
disables game output, suppression and native gate; all original SFC drawing stays
on. The existing source scheduling anchor is initialized from a qualified live
binding, not treated as the player identity. A definition is published before
the corresponding immutable catalogue guard. Passive source PID=0 is now
properly treated as waiting rather than a wrong-process error.

`source-service-01` passes a real retained packet/reference transfer and ACK,
original image preparation, neutral definition/catalogue publication and 20
completed Shipping GPU samples with one geometry build. Separate process
`source-lifetime-shipping-01` passes cancellation before assets, independent
parent death and immediate relaunch in three unique sessions. The parent uses
the optional public UE process handle; no source-wire/engine patch is involved.

Three source-service policy tests, five publisher tests, eight protected
preference tests, three production dependency tests and seven desktop break
transport tests pass. Restricted worker handshake fails while the same desktop
test passes. x86/x64 read-only native mapping/process tests pass. The final
14-stage scheduling regression also passes. Read-only launcher preflight passes;
no SFC gameplay was started in this session. Task 3.5 stays open for that check.

The combined evidence inventory briefly exceeded the 20 GB allowance because
intermediate replays retained duplicate BGRA copies. Exact SHA-256 comparison
verified 1233 obsolete intermediate copies against retained final inputs/images.
Only those copies were removed, 947,536,256 logical bytes. Some were hardlinks;
this is not equal physical-space savings. All receipts, actual final pixels,
original assets and aliases remain; see local `evidence-deduplication.json`.
The live-parent reservation now includes UE evidence, excluding build packages.
