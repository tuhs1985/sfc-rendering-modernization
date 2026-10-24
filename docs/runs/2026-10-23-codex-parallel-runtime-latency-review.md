# Run126 — parallel runtime loading review

Date: 2026-10-23 (America/New_York). Read-only runtime analysis; no implementation or game launch.

Authority: current HANDOFF Run125 and retained multi-ship contract/probe. Sponsor reports successful loading, approximately 17 seconds to all models, unacceptable latency. Do not infer additional visible-behavior acceptance.

Starting/final HEAD: d40f8f230fc7504023e4a052c99a81b5a08ce6b4. Existing Run113–125 working changes preserved; index empty. No staging, commit or push. Fuel Guard attached through verified trusted-hook receipt; no daemon started.

## Evidence

Actual completed run: artifacts/remix-runtime/runs/20261023-205121-223108-in-game/result.json and gpu/job-result.json. Reviewed worker implementation in tools/remix_runtime/{asset_preparation,multi_scene_relay}.py. Timing clock: recorded QueryPerformanceCounter/perf_counter_ns.

- CONFIRMED: four actual concurrent preparations; six jobs, five unique prepared contents, sixth aliases fifth. All jobs ready/alias, workers closed, no unfinished jobs.
- CONFIRMED: initial four identification spans 0.278, 0.418, 0.381, 0.443 seconds. These include decoding/content identification, not only geometry parsing.
- CONFIRMED: initial four full preparation spans 9.531, 9.412, 9.959, 12.269 seconds, overlapping. Initial library publication/renderer launch 12.866 seconds after first job discovery. These spans include conversion/material generation/proof hashing/capacity checks; no existing substage profile attributes the cost individually.
- CONFIRMED: fifth job first discovered 14.307 seconds after first; prepared in 4.476 seconds. Sixth alias discovered at 25.133 seconds. Sponsor's approximate 17 seconds is not an exact measured all-owner appearance time; discovery/publish/display are distinct.
- CONFIRMED: initial material publication followed by one late material update. Known late-reload risk remains; no new exact GPU stall adjudication in this review.
- CONFIRMED: persistent registry admitted six, rejected zero, 40,751 pose publications including 33,556 offscreen updates, zero failed updates.
- CONFIRMED: runner reports no error, normal game exit, clean hook unload, renderer exit 0, accepted critical files and launcher settings unchanged. Owned job reports zero remaining processes.

## Decision

Parallelism works, but does not remove the expensive per-asset preparation path. Current measurements do NOT establish rendering effects as the cause of those preparation seconds. More threads alone is not an evidence-backed fix. Smallest next engineering action: substage-profile the existing captured initial assets through scene preparation, material binding, proof construction and capacity checking, including CPU versus wall time. No new sponsor gameplay required for that investigation. Use results to remove redundant work or address CPU serialization; do not guess the culprit, weaken identity validation, alter renderer architecture or add new test caps.

No implementation change or compression was performed. Validation: parsed completed JSON, checked recorded worker spans and cleanup flags; git diff --check. Files created: this record. Files modified: docs/HANDOFF.md newest checkpoint only; historical evidence retained.
