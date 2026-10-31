# Run224 — native insertion observation complete; earlier timing blocker measured

Source: `artifacts/remix-runtime/runs/20261031-042154-201204-in-game`. Sponsor paused near the beginning, performed full camera rotations and allowed shield damage; confirms normal rendering/HUD/targeting/controls. Exact action timestamps were not supplied and are not inferred from individual draw states.

## Run validity and cleanup

No runner error. Normal game exit, controller0, renderer0, controlled hook-byte restoration and component unload all confirmed. Test proxy/config restored; accepted critical files unchanged. Native replacement suppression/commit counts both zero, as required for observation. The startup and recovery repairs from Run223 worked in this run.

Native metadata: 93,464 events, no ring drops or wrong-thread records, 5,301 qualified output-discard observations, clean stopped header. The 8MiB detailed-event cap retained the first 65,536 records (80.622 seconds, source frames114–4952); 27,928 later records omitted from detailed storage while aggregate counters continued. Full native callbacks continue after the 90-second presentation observation stops and before the 120-second semantic watchdog removes hooks. Those tail callbacks explain large stale-frame lags in the aggregate summary and must not be classified as renderer stalls during gameplay.

Analysis scripts/review: `artifacts/player-replacement/run224/analyze.py`, `review.json`. All retained event ordinals validate and QPC values are monotonic; owner2/revision2 remains the observed identity. Raw input preserved unchanged, checksummed in review.

## Findings

Native target observed: 1920×1080, RGBA8 TYPELESS resource (27), linear RGBA8 UNORM view (28), 8×MSAA and D32_FLOAT depth view (40). Selected-model samples are depth-tested/depth-writing with comparison4 (LESS_EQUAL). Later sampled draws include the same native target/depth with depth testing ON, writes OFF and comparison4. Other later work has depth disabled or different targets. These are real candidate scene states; they do not identify every sampled draw exclusively as a shield or pause text.

Joined earliest observed upstream output-publication stamps by source-frame number, using the retained raw prefix. Using the earliest publication is conservative: if even it is late, later copies cannot have been ready earlier.

| Boundary | Joined frames | Publication after boundary, median | Already published at boundary |
| --- | ---: | ---: | ---: |
| Source offer | 4,836 | 10.147ms | 0 |
| Selected visual/model exit marker | 4,701 | 9.300ms | 0 |
| First sampled native read-only-depth draw after selected exit | 4,380 | 9.272ms | 0 |
| Before-Present observation | 4,836 | −5.244ms | 4,814 |

Visual-exit minimum lateness8.082ms, p95 10.553ms, maximum22.710ms. Full-summary visual exit→Present median14.613ms (5,168 pairs). This gap is not independently identified as idle GPU budget, a pacing wait, or guaranteed time available to relocate.

Crucial clock distinction: event `output_qpc` copies `Packet.published_qpc`, stamped in `output_producer.h` **before** the D3D11 output receiver copies/fences and publishes the game pool. `game_output_writer.h` preserves the upstream stamp. These deltas are therefore lower bounds on game-usable output lateness, not exact game-pool arrival latency. Actual READY observations independently show zero same-frame output in 7,046 sampled native read-only-depth draws; 213 same-frame observations occurred at depth-disabled native draws later in the frame. Neither readiness nor matching frame number alone proves full asset/camera/pose/GPU ownership matching.

## Decision and next action

This is useful evidence; another broad discovery run is unnecessary. The earlier target/depth path exists, but merely moving Present composition to visual exit cannot work with this schedule. The matching image is produced later. Existing whole-finished-picture buffering cannot by itself reconstruct the native commands/effects that would need to draw afterward.

**Next engineering step:** qualify an explicit same-source-frame scheduling/synchronization path at the earlier native scene boundary, using the measured delays as test inputs, then qualify the existing depth compositor for the observed RGBA8 resource/view/device combination. Establish whether native drawing can resume after insertion within the measured frame budget; do not assume the observed gap is free capacity. Preserve original scene ordering, owner-qualified suppression and capture, and reject mismatched poses/epochs. Any bounded wait or retained-command mechanism is a new contract to qualify, not silently insert into the existing nonblocking capture callback.

Native shared flush completion/ownership remains to be established; visual exit is a CPU marker, not a GPU-completion proof. No shield replay expansion, N−1 image over frame N, unbounded wait, continuous native fallback policy change, or replacement-success claim. No rendering implementation/settings/binaries/qualification receipts changed in this review. Existing 20,000,000,000-byte evidence allowance remains; observed total about19.292GB. Source evidence retained, no staging/commit/push.
