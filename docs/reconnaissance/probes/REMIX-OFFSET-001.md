# REMIX-OFFSET-001 — world-offset ship and masked return preparation

2026-10-17; sponsor-approved offset experiment. **Offline only, not ready for
gameplay.** Original ships remain enabled. No Toolkit, wrapper changes, game
launch, suppression, appearance tuning or milestone claim.

Question: can the runtime draw the selected ship at a deliberately different
world position, return coherent color/picking/native-Z, and use its mask in a
native x86 compositor without changing background or pipeline state?

## Mechanism / tools

Reuse Run19 source capture `20261018-025737-262069-in-game`, FCA owner2/revision2,
snapshots0/2. Source geometry, native pose and SDK camera stay unchanged. Runner
derives camera-right **world translation**, towards the roomier side, nominally
20% viewport width at owner center depth. Refuse clipping; no fit, scale/rotation
repair or finished-image displacement. Future live runs need their own fresh state.

Pinned Remix1.5.2 x64/SDK0.6.4 and NRC/DLSS/RR-off environment unchanged from
REMIX-TRIPLET-001. VS2026 18.7.3 C++20 /W4 /WX; x64 producer, x86 receiver,
explicit D3D11 feature10_1. Python3.12. New `ship_triplet_compositor.h` constructs
shaders/deferred context before drawing. Pixel shader admits only exact picking
ID29 with finite nativeZ in[0,1]; opaque output only. Background is discarded,
not a black rectangle. No retained-scene depth, HUD-order or transparency claim.
`ExecuteCommandList(...,TRUE)` restores immediate-context state.

Wirev3=496B; Key152B. Native source-pose hash stays unchanged; explicit mode1
and3float world offset distinguish diagnostic state. Mode0 requires zero offset;
malformed/nonfinite/excessive offset rejected. Both architectures assert layouts;
previous v2 packets rejected. Existing session/GPU EVENT/ACK/identity guards stay.

## Build / launch / limits

From repository root, existing prepared parent; no routine UAC/security changes:

```text
PS7 -NoProfile -File tools/remix_runtime/build_triplet_probe.ps1
artifacts/remix-runtime/triplet-bin/ship_compositor_gpu_tests.exe
python tools/remix_runtime/run_coverage_probe.py --execute --triplet --native-depth --calibration-run artifacts/remix-runtime/runs/20261018-025737-262069-in-game --snapshot 0
python tools/remix_runtime/run_coverage_probe.py --execute --triplet --native-depth --diagnostic-offset --calibration-run artifacts/remix-runtime/runs/20261018-025737-262069-in-game --snapshot 0
```

Repeat offset snapshot2. Negative controls append `--triplet-fault slow` or
`--triplet-fault exit`. Nonzero negative exit expected ONLY when result records
EXPECTED_TRIPLET_RECEIVER_FAULT and published1/ACK0/accepted0/READY.
Scoped external GPU execution may be required by sandbox; not a privilege change
to SFC. Default original probe binary and game modes stay untouched.

96 render frames,120s process cap,32MiB hard/16MiB warning evidence per run;
fixture5s ACK timeout,slow control6s,owned receiver110s cap/job cleanup.
Three256square shared outputs=786432B; fourth producer output is existing ID
decoder. Fixture-only compositor destination/state-sentinel272square targets
and private staging are additional bounded test resources, not added transport
pool members. Synthetic test uses8square inputs and16/24square targets.
No production readback or waits.

Outputs: unique `artifacts/remix-runtime/runs/*-coverage` (~5.42MB positive,
~5.36MB negative), fixed planes/logs/result/manifest,152B request. Child log is
outside any game process, overwritten only within its fresh run. No per-frame
image dumps. Current controls cannot create multi-GB output; broad API tracing
elsewhere can, and must not be substituted.

Receiver compares every composite pixel with returned color under exact owner/
depth mask and checks unchanged background/border. Synthetic tests cover foreign
ID,NaN/infinity,sentinel,out-of-range depth,invalid viewport/key and state restore.
Source hashes and independently shifted native projection corroborate GPU output.

```text
python tools/remix_runtime/analyze_ship_offset.py BASELINE_RUN OFFSET_RUN
```

Writes bounded `offset.analysis.json` and512x284 comparison figure in offset run.
Checkerboard is an analysis figure, not a game insertion mechanism.

## Cleanup / limitations

Nominal child drains GPU use before ACK/release. Faults do not authorize reuse;
only owned fixture child may be stopped by its job. Archive exact folders with
existing `run_coverage_probe.py --archive ...`, CRC check, retain small raw data
under sponsor10GB allowance. Known SDK common-object teardown warning stays open.

No actual addon adoption,live output timing,HUD/effect occlusion or suppression
proven. Exact-frame fixture keys represent recorded poses,not live requests. Do
not pass replay off as current game rendering. Next: fresh-request/receiver
adoption and UI-safe copied-game insertion,originals ON,with offline tests first.
