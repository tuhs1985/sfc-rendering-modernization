# Run180 — parallel asset preparation and progressive materials

2026-10-25, America/New_York. Sponsor approved the parallel preparation plan,
including applying individual materials as they become available. No staging,
commit or push authorized. Preserve existing Run178/179 working changes.

Implementation files added: `tools/remix_runtime/parallel_assets.py`,
`tools/remix_runtime/progressive_scene_relay.py`,
`tools/remix_runtime/check_parallel_assets.py`, `tests/test_parallel_assets.py`.
Changed: `tools/scene_bridge/scene_bundle.py`,
`tools/remix_runtime/multi_scene_relay.py` (selectable bootstrap job),
`tools/remix_runtime/multi_scene_resources.py` (reservation follows final path),
`tools/remix_runtime/run_return_fixture.py` (isolated flags/scheduling).
Documentation: this run/curated JSON, HANDOFF/STATUS and D3D9 README. Reviewed
Obsidian tracker refreshed byte-exact after checking no unrelated sponsor edits.

## Implemented

`parallel_assets.py` provides a dependency graph with four bounded execution
workers, at most four active decoded assets and64 queued asset descriptors.
Workers do not await other workers. Decode each captured packet once, then build
geometry independently of image reads/decodes. Source image reads and decodes are
single-flight across active assets; completed enhanced derivatives share tasks
using original content, image role and frozen settings. Coordinator owns all
catalog/material publication and reservations; no SFC callback changes.

`scene_bundle.prepare` accepts immutable prepared capture, images, geometry and
output dimensions. The new path writes1920x1080 initially; no follow-up resize,
full replay validation, file rewrite or rehash. Original helpers retain diagnostic
behavior. No geometry/image origin, source assets, texture interpretation or
material settings changed.

`progressive_scene_relay.py` admits each diffuse-ready asset independently, chooses
the first ready supported ship as bootstrap, and assigns separate ready-order
resource paths. It does not require discovery job1 or the initial quiet-window/
all-assets-settled barrier. The existing immutable catalog/native submission and
owner-epoch/camera contracts remain unchanged. Shared geometry content binds
independent owners through the same existing native residency mechanism.

Each material group becomes its own completion. Only complete required maps are
published, through immutable image files and atomic per-asset USD stage updates.
Completions in the same coordinator cycle share a master-library commit without
a new intentional batching delay. Other groups retain ordinary diffuse appearance.
Material conflicts are rejected, leaving the prior stage intact. CPU-ready and
stage-publication timestamps explicitly do not claim GPU consumption.

The new route is available **only in the standalone fixture** using
`--multi-ship --prewarm --startup-profile --pipeline-mode performance --parallel-assets`.
`--parallel-material-delay-ms 5000` delays one group per asset in the coordinator,
not by sleeping a worker. No candidate runtime/API/loading-policy experiments may
be combined. Gameplay selection is guarded off until the publication gate passes.

## Bounds and shutdown

- Four execution workers, four decoded contexts,64 asset descriptors,8192 live
  task descriptors. Completed per-asset tasks and image/derivative values release
  when their last active user finishes; historical spans retain no pixel data.
- Per-context decoded working-image accounting256MiB covers original+RGBA+BGRA;
  this is distinct from unchanged128MiB primary-output and material-output bounds,
  and native256MiB retained backing. Four active contexts bound that accounted
  input working set to1GiB; in-flight conversion buffers are additional temporary
  memory, not a claimed global process-memory cap. Existing4096/image count/disk
  limits remain. No unbounded image or decoded-mesh queue/cache.
- Disk reservations span preparation and coordinator writes, including failures
  and final renamed paths. Slow/malformed/unsupported assets cannot block worker
  threads waiting for another future. Shutdown cancels queued tasks, drains
  running work before releasing inputs/reservations, and preserves partial results.
- Existing20GB aggregate,32MiB evidence policy and owned renderer limits retained.
  No native hook, wire, runtime/SDK pin, original-client or sponsor-settings edits.

## Validation and results

600 Python tests PASS:518 main plus36recon/13survey/6effects/5API/22early-observer,
including10 new focused tests: same-asset overlap,
independent ready materials/ships, shared tasks, dependency failure, shutdown,
single-worker scheduling, image/path/dimension errors, exact derivative origin,
geometry preservation and progressive stages/conflicting associations. Existing
native qualification and separate observer regressions are recorded at closeout.

Captured FCA CPU replay uses live-captured binary geometry, not a MOD conversion.
Final geometry/original hashes, every derived-image metadata/hash and complete
material-stage hash exactly equal the accepted reference. Early replay caught
stage declaration ordering; fixed to preserve captured scene order and reran.

Serial unprofiled CPU controls, same captured FCA/settings, no GPU/regressions
running concurrently:

| Control | Preparation elapsed | Evidence under artifacts/initial-readiness |
| --- | ---: | --- |
| Existing path | 2.5793763s | parallel-cpu-20261025-185742-112115 |
| Parallel path | 1.4719835s | parallel-cpu-20261025-185748-297302 |

One pair, with cache/process-startup variation; not a universal speedup or visible
loading result. Earlier isolated replay184537 had diffuse readiness778.40ms and
enhanced readiness1208.74ms. Final-source185350 repeated exact parity. Normal
complete-scene<2s remains unresolved, particularly for multiple assets.

Standalone four-owner/three-content controls, all exited normally with all four
catalog acknowledgements, no partial/rejected owners, unchanged native HUD/scene,
resize/recreation and original drawing preserved. All three final asset material
stages and every derived-image metadata/hash equal accepted FCA/RCA/FDD references:

| Run under artifacts/remix-runtime/runs | Condition | Delivery window |
| --- | --- | ---: |
| 20261025-184629-703184-return-fixture | Delayed group, initial implementation | 431/600 |
| 20261025-184840-854857-return-fixture | Corrected scheduler, no deliberate delay | 596/600 |
| 20261025-185029-286186-return-fixture | Corrected scheduler, delayed group | **538/600** |
| 20261025-185405-546280-return-fixture | Existing gameplay path/shared refactor control | 600/600 |
| 20261025-185841-390784-return-fixture | Final-source existing gameplay path control | 595/600 |

First fixture exposed50ms outer polling amplifying a fine-grained task graph.
The standalone progressive runner now polls at2ms, and dependency-ready geometry/
assembly gets scheduling priority. Native source capture frequency is unchanged.
This was a harness bottleneck, not the GPU rendering cost.

No-delay first anchor output2.718694s and first cohort output2.971100s after first
discovery; those are output readiness, not physical display or complete enhanced
material readiness. That run's FDD diffuse prep still3.417s: do not present the
single-asset CPU result as the complete multi-ship loading target being achieved.

## Adjudication — PARTIAL, progressive publication not promoted

Parallel construction, independent diffuse admission and per-group publication
are implemented and exercised. **The delayed-material run fails the existing
90% delivery gate:538<540 of600.** It also loses materially more outputs than the
stable control. No original-game problem is claimed; these are standalone tests.

Existing pinned USD reload uses a1000ms watcher and unload/load at processing time
(qualified upstream source `artifacts/remix-runtime/deps/rtx_mod_usd.cpp`, Run163).
Delayed publication correlates with interrupted delivery, but these receipts do
not attribute each missing frame to a particular internal reload operation.
Prepared-file parity is proved; exact per-group first GPU-consumption time and
final visual equivalence under progressive updates remain unqualified. No public
reload-completion barrier was established in the pinned SDK. No runtime patch,
undocumented function, architecture switch or stale-frame concealment introduced.

Gameplay continues to use the qualified existing route. Do not hand the sponsor
an experimental gameplay launcher or overwrite the stable qualification with the
progressive fixture. Current native/offline baseline qualification refreshed from
the final-source185841 fixture through its normal adjudicator and native source
checks; normal read-only performance gameplay preflight PASS. No lock bypass.
New implementation stays unstaged/uncommitted; HEAD9ff2d3d/not pushed.

After analysis, compressed only seven generated CPU-control `gpu`/`asset` subtrees
to `artifacts/initial-readiness/run180-cpu-generated.zip`:542,678,747B→40,237,508B,
1404files individually SHA-verified before removing generated originals. Archive
SHA25681a666eb1bde0772f853764c2bfb090f4d24cc0a5c7023989401bb3ad34e5021.
Receipt `run180-cpu-generated-archive.json` lists exact recoverable paths; captured
gate packets, analyses and profiles remain loose. Accepted reference assets and
all actual rendering-run evidence remain unchanged. No active owned host/channel
or helper/server/session remains. `git diff --check` PASS.

**Exact next action:** isolate the pinned runtime's supported material-consumption
step during delayed publication, using this fixture's CPU publication and output
timing. Establish a non-disruptive update method before promoting progressive
gameplay. No additional gameplay discovery run or appearance tuning needed.
