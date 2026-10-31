# Run230 — camera-transition rejection research

Scope: research the retained-scene trigger and the sponsor's Lyran camera-switch observation. No live pipeline/configuration changes or SFC launch. Used the Run229 evidence and small standalone CPU experiments calling the actual current projection checker.

## Confirmed findings

**SFC state was early on all 90 recorded steady deadline misses.** In `20261031-170825-272571-in-game`, publication was at most 0.1798 ms after native frame start; gate entry at most 0.2887 ms. Median publication was 0.1016 ms, essentially the same as successful frames' 0.1011 ms. Thus these recorded misses are not explained by waiting most of the frame to obtain SFC state. Of those 90 frames, 29 have same-frame GPU-pool readiness observed by Present: median17.311 ms,maximum19.4622 ms,after Strict's16.667 ms admission deadline. The other61 have no recorded same-frame readiness at Present. These are observations,not a complete per-stage GPU timing breakdown.

**Geometry and textures are retained.** Existing per-owner content bindings and preparation records show no repeated preparation during late camera bursts. The native persistent registry continues reading living objects and includes offscreen objects whenever its update runs. It is triggered by the first qualified primary wrapper; a scene with no such calls can lack publication. That trigger dependency is real, but does not explain late state on the 90 misses above: those packets were published promptly.

**Our screen-position checker can falsely reject valid offscreen geometry.** `live_owner::projection_matches` compares two floating-point routes to screen pixels, with a fixed quarter-pixel tolerance. It divides by the perspective denominator before considering whether the point is outside the visible volume or behind the camera. Near the camera plane, rounding between a stored single-precision composed matrix and separately evaluated matrices can become a large apparent screen error. `MultiSceneRuntime::draw` drops the whole owner if any sampled vertex fails. That removes it from actual rendered membership; insertion therefore retains native drawing.

Microsoft documents the normal ordering: clipping is defined in homogeneous coordinates, with conversion to screen pixels afterward. This supports treating offscreen/singular perspective positions separately rather than using their pixel error as a scene-identity verdict. References: [transformation pipeline](https://learn.microsoft.com/en-us/windows/win32/dxtecharts/the-direct3d-transformation-pipeline), [D3D9 viewports and clipping](https://learn.microsoft.com/en-us/windows/win32/direct3d9/viewports-and-clipping). Any correction must respect the project's neutral source projection convention; do not copy D3D9 depth inequalities blindly into source-camera math.

**A second copy of that check can block the entire scene.** `LiveOwnerInput::next` runs the same per-vertex projection test against the scheduling anchor's bootstrap geometry before the host can consume/draw the multi-owner scene. In this run the anchor stays KFF owner1/revision2,generation1,with no rebindings. Camera focus on the Lyran does not change that anchor. Therefore a false failure on an offscreen Klingon can discard the scene input for the visible Lyran and every other ship. A scheduling anchor is incorrectly acting as a view-dependent whole-scene eligibility condition.

## Reproduction using captured geometry

The offline experiment reads the final recorded cohort rows and actual fresh-capture corner positions. It keeps geometry and world poses unchanged, rotates only the camera through3,600 controlled yaw angles and rebuilds the composed reference with the actual producer's float-matrix multiplication. It calls the actual `live_owner::decode` and `projection_matches` functions; it does not imitate the checker in Python.

| Input | Baseline failures | Valid camera cases rejected | Failed point comparisons | Failed points inside visible volume |
|---|---:|---:|---:|---:|
| LFF,68 sampled corners | 0 | 14 /3,600 | 126 | 0 |
| Scheduling KFF,65 sampled corners | 0 | 10 /3,600 | 74 | 0 |

All camera cases pass matrix decoding. Every failed sampled point is offscreen; the first LFF failure is behind the camera and differs by3.485 pixels,with larger apparent errors at other angles. The first KFF failure differs by899.896 pixels with a perspective denominator close to zero. These are constructed camera replays using captured models,not literal replays of the historical missing transition matrices.

Evidence: `artifacts/player-replacement/run230/projection_replay.cpp`, `projection-replay.txt`, `anchor-projection-replay.txt`, captured row/sample inputs, `analyze.py` and `research.json`. The latter records source/raw-input hashes and timing distributions. Proprietary geometry snippets remain ignored local artifacts,not versioned sources.

## Attribution and limits

Run229 records six per-owner projection rejections and six limited LFF membership-unavailable events. The shared checker provides a reproduced mechanism consistent with that Lyran-specific fallback, but bounded logs do not prove each historical pair is the same event.

The renderer additionally records29 rejected anchor inputs,while the gate has a29-frame no-ready burst. That is consistent with the whole-scene failure mechanism. However the anchor counter combines identity,decode,thread and projection failures; no per-rejection reason/frame is retained. Do not claim all29 are proven projection failures or that this alone explains all90 timeouts. Some output demonstrably completes after the deadline; the current performance logs cannot separate every CPU scheduling,ray-tracing,post-processing and GPU-copy interval.

This establishes a real defect in our qualification policy and its ability to block whole-scene rendering. It rules out late source-state arrival on the recorded timeouts and repeated texture/model loading during the bursts. It does not establish a Remix internal culling/shader defect. Cloak admission remains a separate Run229 gap.

## Next implementation priority

Correct the view-dependent rejection before adding latency or another visibility warm-up mechanism. Keep session/owner/revision/frame/content checks and finite matrix validation. Validate matrix/projection consistency without treating undefined or offscreen pixel positions as proof the object is invalid. A scheduling anchor must not discard an otherwise valid retained scene solely because its geometry is offscreen. Do not solve it by swapping anchors whenever the user changes cameras,using stale poses,or silently dropping living offscreen shadow casters.

Retain a focused regression based on both actual geometries: front/behind-camera,near-plane crossing,ordinary visible points and genuinely mismatched transforms. Then remeasure existing Strict gameplay. ExtraFrame remains a useful diagnostic afterward,but cannot repair an input rejected before rendering. No implementation fix is claimed in this research checkpoint.
