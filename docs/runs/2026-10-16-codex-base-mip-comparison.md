# Codex run — BASE-MIP-AB-20261016

Sponsor approved the proposed scratch-only A/B. Current HANDOFF/sampling-inspection
record reviewed. HEADfee152f137a55a3efeb47a5c236ebf9e3e1951cb,164 short-status entries,
index empty at start. Inherited work retained. Fuel Guard recent exact-thread
hook verified/direct access denied; no daemon started. Quota guidance: finish this
bounded experiment and checkpoint; do not expand into further rendering work.

Question: does removing lower mip levels, without changing base pixels, improve
visible detail? No SFC run, installed game/client edits, renderer architecture,
original/import asset modification, helper invocation or commit.

## Mechanism / validation

New `tools/remix_ingest/base_mip_diagnostic.py` with two unit tests in
`test_base_mip.py`. Explicit `run_mesh_preview.py --base-mip-only` requires both
`--textures --smoke`. Qualifies observed DX10/BC7 format98,256²,array-size1 only.
In newly owned scratch DDS copies, preserves exact compressed65536-byte base
payload; removes lower levels, changes mip count/related flags/caps only. DDS
length87556 ->65684bytes each; Pillow before/after decoded RGBA must match exactly.
Updates only new scratch dependency hashes/config and records per-file before/
after hashes, sizes and helper SHA. Five resources required; original/import hashes
rechecked independently against prior baseline metadata. No recompression, resize,
UV/image flip, normals/geometry/light/camera/material change. Default viewer unchanged.
Probe addendum in MESH-PREVIEW-001 recorded before execution.

Bundled Python3.12.14/Pillow12.3.0, existing Toolkit1.6.0-dev/Kit110.1.1:

```text
python -m unittest discover -s tools/remix_ingest -p test_*.py
python tools/remix_ingest/run_mesh_preview.py --job C:/Project/RemixJobs/20261016-050350Z-6dffd5be --textures --smoke --base-mip-only
git diff --check
```

PYTHONDONTWRITEBYTECODE=1; tests TEMP/TMP=`artifacts/m1/test-temp`.
25 relevant tests PASS. Actual full-detail DDS decoded-pixel and compressed-payload
checks PASS for all five. Approved graphics replay outside sandbox, same child-only
Custom4/ImportanceSampled0 NRC-off/bloom-off and180s/256MiB/8MiB/three8MiB PNG guards.
No UAC/security/global settings changes. No unbounded trace or native rebuild.

## Result

Baseline `C:/Project/RemixJobs/preview-20261016-051922Z-c8fef267` versus test
`C:/Project/RemixJobs/preview-20261016-052216Z-f60dc2ed`. Test clean exit0,
16.313s, peak scratch1173317bytes, console24448bytes, no warning or remaining
owned process. Same452triangles/11mesh prims/source USD SHA
`5c08f217b36ef9056c3a1940931ff2fd463286ca67e120d7bd80269b997634b2` unchanged.
Original imported DDS/dependencies hashes still match baseline. All source BMPs/
PNGs and previous previews untouched; only newly generated scratch copies changed.

Analyst inspected test `above.png` against baseline: wing panel lines/details
visibly sharper, whereas brightness and existing dark/open surfaces remain.
**CONFIRMED:** removing lower mip availability while preserving base pixels changed
the preview and restored visible panel detail. **STRONG HYPOTHESIS:** mip selection/
lower-resolution sampling contributes materially to prior softness. Actual GPU
selected mip number/filter algorithm remains unknown. Do not claim sole cause or
that globally disabling mips is a production-quality fix; aliasing/distance behavior
not tested. No sharpen/upscale operation, game improvement or full texture PASS.

Generated `base-mip-diagnostic.json` and `base-mip-comparison.json` preserve exact
experiment and whole-frame RGB differences; means above≈1.155/1.006/1.058,
angled≈0.831/0.651/0.796, front≈0.074/0.066/0.077 (0–255). Whole-image black
background and stochastic rendering mean these are NOT sharpness scores or
pixel-level causal proof. No matched repeated control runs, no broader image
quality/performance qualification. Existing partial placement/glow findings stand.

Versionable edits: helper/tests, opt-in runner flag, probe addendum, this record,
result addendum and HANDOFF.25 tests/diff check PASS. Verified44-file archive
`artifacts/remix-ingest/evidence/20261016-base-mip-comparison.zip`,549225bytes,
SHA256 `c7a101be37c561ae91fb6865dd53bf8279bbaff8ec9e6706148438093c5916e6`.
Includes logs/config/texture derivatives/three PNGs, excludes portable caches;
prior baseline archives retained. No raw/source deletion or multi-GB output.
Final HEAD unchanged, index empty;165 short-status entries after this record,
inherited/new work unstaged, nothing committed. No active game/viewer process.

## Exact next action / safe restart

Present the sharper `above.png` to sponsor for comparison. Do NOT run another
capture, redo pixel extraction or change the default sampler blindly. If approved
later, plan one bounded preview-only choice of filtering/mip policy; maintain the
scratch diagnostic as diagnostic, not the default. Address brightness/surface/glow
separately. Current run stops here with durable checkpoint; no further work started.

### Sponsor visual confirmation

Sponsor answered **“Yes”** when asked whether the full-detail-only diagnostic
looks closer to the supplied ModelBrowser reference. This confirms perceived
improvement, not exact pixel/placement parity or a production sampler policy.
No additional execution, rendering changes, staging or commit. Next smallest
engineering action, when resumed: review one bounded preview-only mip/filtering
policy test; retain the current base-only result as diagnostic evidence.
