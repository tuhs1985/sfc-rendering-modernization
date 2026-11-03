# Run275 — 72-owner carrier/fighter stress review

## Result

Reviewed completed gameplay `20261102-235349-273253-in-game` using its existing results, full gate records and renderer log. Sponsor reports the stress scenario runs, with stability issues. No production code/configuration/process changes or new capture. Structural capacity, publication and teardown passed this scenario; smooth replacement under stress remains partial.

## Delivery and coverage

-72 qualified owner/revision records, all72 have successful replacement insertions at some point. This does not establish72 simultaneously visible or every object in the mission being supported.
-17 distinct model assets loaded,55 shared-asset bindings. Renderer191,373owner draws; native receipts85,901owner insertions and179,601list suppressions. Different units: these are not displayed-frame counts.
-0 rejected assets,0 partial asset results,0 physical-hull omissions with capacity256. Renderer omitted476owner draw attempts while an asset was not yet resident; that is not476missing ships or a hull-cap recurrence. Every retained owner eventually received insertion.
-0 material publication retries, warnings or unresolved stages/library. The new ReplaceFileW path is active; this run did not exercise the nonfatal retry branch because no denial occurred. Run274's fault injection establishes that branch separately.
- Prepared project dome adopted once without recreation. No evidence of the old first-use dome/file denial in this run.
- First successful insertion at frame54,0.955419s after first gate record,0.921582s after earliest retained preparation span. The selected report's63.11s includes pre-tactical waiting; do not present that as model conversion time.
- Initial unique asset admissions run0.477–4.607s relative to first gate record. Later unique admissions43.039–50.695s. Thus first appearance is fast, but the entire initial set is not proved ready in under two seconds. Do not equate late admission with late engine visibility without checking discovery timestamps.
- Retained renderer scene backing66,013,044B(about63MiB); recorded image output131,655,360B(about125.6MiB). Neither is a VRAM-use measurement. No allocation/capacity error observed.

## Instability quantified

The90.228s gate recording contains4,004frames.52native-only frames precede the first successful insertion. After that,3,856frames insert and96frames time out:2.43% of3,952post-startup frames. No invalid gate transactions, terminal recovery reason, partial gate or lost gate records.

There are46post-startup fallback episodes:31single-frame,5two-frame,2three-frame,3four-frame,1five-frame,2seven-frame,1eight-frame and1ten-frame. The ten-frame episode begins52.029s and spans286ms through its last presentation. This is large enough to explain visible changes back to native appearance. The earlier modest Run272 had only five isolated post-startup misses; workloads are different, so this is a load comparison, not a controlled code regression.

Most misses cluster during later asset activity:17fallbacks in45–50s,56in50–55s. There are also11in30–40s, before the later unique admissions, so new geometry/material arrival is not the sole established cause. After60s there are no fallback frames in the remaining recording.

The selected Strict policy has a16.667ms source-frame deadline. Of96post-startup timeout records,94show game-pool readiness after that deadline; median readiness lateness0.494ms,p952.983ms,max4.339ms. Two ready timestamps are on time but admission still times out. Their exact scheduling/validation costs are not isolated by this evidence. Most misses are therefore output arriving late for this policy, not simply all-ready pixels being rejected by identity checks.

Typical pool readiness14.379ms,p9515.990ms,p9917.388ms. Typical source-to-presentation age19.026ms. Typical presentation interval22.298ms(about44.8FPS at that median);p9525.748ms,p9929.404ms. These are observed combined-path timings, not pure GPU cost or actual scanout latency. Outstanding output queue stays1; no growing queue/epoch errors. Reference60Hz schedule drift does not mean latency accumulated by23seconds.

Two larger gaps require separate treatment:

- Frame1484 near32.584s:104.821ms between presentations, comprising68.267ms between the previous presentation and next recorded source start, then36.554ms within that source frame.
- Frame1616 near35.618s:65.843ms interval,41.191ms between frames and24.653ms inside the next frame; replacement actually inserts successfully on this frame.

Thus those gaps cannot be attributed wholly to the synchronous insertion wait. The saved evidence does not identify what occupied the between-frame intervals. Do not label them Defender, asset loading, camera switching or GPU saturation without stronger evidence.

## Likely bottleneck and next smallest step

Confirmed immediate cause of replacement flicker: short bursts of output missing the Strict deadline, leading to original drawing. Under this scene load, available timing headroom is small. Late asset/material work correlates with the largest sustained burst; it is not proved the exclusive underlying cost.

Existing implementation still finalizes D3D9 resources/hull preparation on the render-worker path after background CPU preparation. Measured single-asset GPU admission has outliers16.117ms(id2) and6.356ms(id10); most later admissions are0.197–0.909ms. These are concrete potential interruptions, not proof of the full50–55s burst. CPU preparation/outside runtime shader/texture work and admission scheduling remain distinguishable questions.

Recommend compare the same stress fixture using the ALREADY SUPPORTED ExtraFrame timing policy before changing architecture or checks. It tests whether modestly more admission time removes visual switches while preserving identity and depth. It does not promise higher FPS or fix the two between-frame hitches. Retain current Strict evidence; choose policy from smoothness plus measured latency. If broader waiting is unacceptable or misses persist, investigate remaining resource-finalization/presentation scheduling using existing timestamps before requesting a new trace.

## Cleanup and limitations

Normal game exit, controlled hook unload, controller/renderer exit0, owned renderer children remaining0. Original client hashes and launcher settings unchanged. All final reports complete; observation window completed.

Source-timing diagnostic ring saturates32,768records with31,254drops and its historical diagnostic owner-limit counter175,806. This is limited diagnostic coverage, not the functioning scene registry's capacity being exceeded. The full gate stream has0drops. Completion diagnostics record first outputs, not every expensive RTX internal operation; no all-frame GPU execution attribution is available.

Compact derived evidence: `artifacts/player-replacement/run275/analysis.json`. Analyzer `artifacts/player-replacement/review_stress_run275.py` uses the established gate decoder and preserves original packets/logs. No staging or commit.
