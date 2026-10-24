# Run152 — documented startup boundaries; two negative optimizations; profiler privilege gap

## Outcome

**Delay localized, but no justified production speed fix found.** Correct-material
candidate initial fixtures remain4.32–4.42seconds in this increment. Native steady
ship drawing/return work is usually milliseconds; substantial time precedes it.
The next deeper native trace is blocked by actual Windows profiler permissions.
Normal1.5.2 pin, implementation, assets and visual settings remain unchanged.

Read HANDOFF/Run151 and current code; Fuel Guard attached existing hook/no daemon.
No sponsor gameplay, SFC/Toolkit launch, source patch, helper, agent, staging,
commit or push. Earlier dirty implementation is preserved. All new diagnostic
code is ignored and scoped to standalone worker/supervisor processes.

## Documentation consulted

- NVIDIA release-linked [initializer](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_initializer.cpp):
  asset initialization and shader prewarming are separate mechanisms.
- Pinned [options](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_options.h)
  and [texture manager](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_texture_manager.cpp):
  alwaysWaitForAsyncTextures defaults false; initial preload still schedules
  its first request synchronously in the inspected source. A streaming switch
  alone is not a material-ready latch; Run138 already tested that route.
- Pinned [DXVK supplemental readme](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/dxvk_supplemental_readme.md)
  and [state cache implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/dxvk_state_cache.cpp):
  DXVK_STATE_CACHE_PATH redirects the otherwise current-directory cache. Tested
  this vendor mechanism instead of inventing another shader warm-up/cache.
- NVIDIA [Nsight CLI guide](https://docs.nvidia.com/nsight-systems/UserGuide/index.html)
  states Windows CLI requires administrator. Installed2026.5.1 local help is
  authoritative for CLI arguments: --kill=false, NOT online example --kill=none.

Packaged1.6.1build5a7eec84 vs public0a6cd5b/API0.6.5 source caveat persists.
Documentation does not prove that a particular packaged stall is texture upload,
shader compilation or GPU execution. No vendor internals patched.

## Existing receipts already answer most phase questions

Ignored `artifacts/split_candidate_startup.py` reads existing QPC/perf_counter
records. [Curated evidence](../reconnaissance/evidence/20261024-startup-boundary-controls.json)
contains the nine phase splits, four new successful controls, worker measurements,
cache inventories, helper benchmark and failed-probe disposition.

Representative previous candidate initial192321, seconds:

| Boundary | Seconds |
| --- | ---: |
| First discovery to initial preparation completed | 2.4146 |
| Prepared to supervisor activation | 0.0543 |
| Supervisor to native activation observed | 0.0254 |
| Native activation to renderer asset setup | 0.0359 |
| Asset setup through24bootstrap Presents | 1.6188 |
| Bootstrap output copy/post | 0.0123 |
| Bootstrap output to receiver acknowledgement | 0.1652 |
| Receiver ack to first cohort draw | 0.0970 |
| First real cohort draw | 0.0038 |
| First real cohort copy/post | 0.0072 |

The second bootstrap Present alone took1.2536s; other correct-material candidate
cases repeatedly show~1.17–1.23s at that call. This is a **call-boundary stall**,
not proof1.2s is GPU execution. Old1.5.2 sometimes instead stalls at later Present
or first output fence. Preparation and native device initialization overlap;
do not sum overlapping spans or call all startup CPU work a serial asset cost.

Native code still performs24initial repeated frames, including10ms sleep per
iteration; later live frames are one Present. This legacy bootstrap is NOT an
established material-readiness contract. It adds~0.24s intentional sleep plus
render work but does not explain the whole delay. Not removed blindly: materials
may otherwise appear incomplete and first-use work can simply move later.

## Narrow worker timers fill a real measurement gap

Existing preparation spans grouped everything into identify/prepare. Added
ignored standalone `artifacts/profile_candidate_preparation.py` with per-thread
wall counters around existing functions, no changes to their results. Writes
small timing JSON after each worker completes; no game/render callback work.

First attempt193842-836029 used simultaneous cProfile instances, which fail in
this Python runtime with **“Another profiling tool is already active”**. Two
assets became partial; fixture/host exit1 and resize/recreation not reached.
Owned renderer job exited0/remaining0. Mixed/empty .prof output is INVALID and
excluded, not evidence of SFC/material failure. Replaced profiler with independent
thread-local clocks, not another plugin or global profiler setting.

Successful194000-242400 and194107-556694 both4owners/3contents/ACK/draw, no
partials, HUD/state/resize/recreation/normalexit/owned0; steady595/600 and599/600.
Second FCA worker measured1.830s total: ordinary scene0.311s, material stage1.439s;
within/inclusive are image file writes0.159s, DDS encoding0.137s, roughness0.176s,
path resolution0.077s, and two external-process waits0.720s. FDD1.757s total,
material1.397s and external waits0.767s. RCA0.355s total.

These are **inclusive, scheduling-sensitive wall times**, not disjoint CPU
instruction costs; do not add parent/child durations or infer slow hashing from
subprocess waits. They locate worker-side exposure during concurrent startup.

## Rejected optimization: texture helper build

Inspection found build_material_binding.ps1 lacks explicit /O2, while the native
admission FNV helper already uses /O2. Built an isolated optimized texture hasher
in artifacts/texture-hash-optimized; did NOT change normal build script/binary.
Three alternating repeats on exact same original uploads, all hash stdout bytes
identical. Median normal→optimized56images35.8→28.2ms;5images13.9→14.2ms;
46images29.0→25.1ms. A few milliseconds, NOT the missing seconds.
Separate existing admission helper measured~43–57ms FCA/~14–16ms RCA/~36–37ms FDD.
Thus large concurrent subprocess spans cannot be called pure hash algorithm cost.
Startup CPU contention/scheduling is a hypothesis, not proven root cause. Keep
identity/checksum/bounds safeguards; no unvalidated comparison removal.

## Rejected optimization: NVIDIA persistent state cache

`artifacts/test_candidate_state_cache.py` overrides only the exact candidate
child's DXVK_STATE_CACHE_PATH, using a dedicated candidate1.6.1 directory under
governed d3d9-proof, at most4files/16MiB checked before/after. No driver cache
reset, global environment setting, settings/material edits or custom cache.

Seed194327-484184 and reuse194407-388345 completed4owners/3contents/noassetpartials/
HUD/state/resize/recreation/normalexit/owned0; steady593/600 and599/600.
Initial cohort output4.3192s seed/4.4249s reuse; not a demonstrated gain.
Cache remains a12byte header, no useful pipeline entries. Directory redirect
works but did not populate useful state for this path. Do NOT generalize that
all NVIDIA caches are ineffective; this particular state cache is not the fix.
No persistent cache setting promoted.

All four successful current cases retain same432generated image/native SHA
multisets and all visual config hashes. Settled ship differences0.06–1.00RGB/255
over31,313ship pixels across these controls, consistent with residual temporal
variation, not exact pixel identity. No missing-material speed result accepted.

## Actual blocker: Nsight registry privilege

Installed CLI `C:\Program Files\NVIDIA Corporation\Nsight Systems 2026.5.1\target-windows-x64\nsys.exe`,
version2026.5.1.161-265138896106v0. Actual WindowsPrincipal administrator=false,
even outside the filesystem sandbox. A ONE-second no-op Python child permission
probe used --trace=vulkan --sample=none --cpuctxsw=none --duration=1 --kill=false
--injection-use-detours=true, output within artifacts/d3d9-proof. Exit1:

```
Failed to register Vulkan extension JSON file(s). This operation requires registry writing permissions.
```

Initial online --kill=none syntax was rejected before launch; corrected using
installed help. No production/game process profiled, system-wide injection,
registry edit, UAC request, driver policy or permission changes attempted.
No usable Vulkan trace generated. Actual detailed native attribution requires
legitimate elevated Windows launch; do not confuse sandbox approval with UAC.

## Validation, cleanup and handoff

Current11candidate tests PASS0.197s; normal Performance read-only preflightPASS,
no game/renderer started. Full499passes are Run151 historical, not rerun here.
Independent final CIM check: no owned GPU fixture/renderer/receiver/job/nsys
processes. `git diff --check`, JSON/reference validation recorded at closeout.
No versionable implementation/native/tuning/dependency changes this run.
Only this record, curated evidence and HANDOFF changed/added; earlier dirty work
preserved, HEADfe2eaf7/indexempty/unstaged/uncommitted/nopush.

Existing100sfixture/285sjob/32MiBsupervisor/20GBaggregate unchanged. Three
completed generated sets194000/194327/194407 archived: each432files162,619,600bytes
to10,051,597ZIPbytes, every entry decompressedSHAverified before exact loose
original deletion. Net457,704,009bytes saved before receipts. Recover via
perrun generated-images-archive.json and artifacts/remix-runtime/archives.
Latest detailed timing194107 and invalid profile193842 retained raw; captures,
geometry, logs, BMPs, timing JSON and receipts preserved. Governed evidence
14,780,377,397bytes before small final document overhead, below20GB.

## Exact next action

Obtain legitimate elevated Windows launch for ONE bounded process-tree-only
Nsight Vulkan trace of the existing standalone candidate host/fixture. Use
installed-version help, no CPU/system-wide collection, dedicated output with
reserved storage/timeout and owned cleanup; do not run SFC or silently alter
registry/security to pass. Correlate native bootstrap Present stall with loader,
pipeline compilation/upload and GPU activity BEFORE changing readiness policy
or replacing/removing24bootstrap frames. Normal1.5.2 remains pinned.
