# Codex run — TEXTURE-PIXELS-20261016

Task: sponsor requested direct comparison with original image files after noting
softness in the preview. Read-only diagnosis; no renderer/sampler/material changes.
HEADfee152f,160 short-status entries/index empty at start; inherited work retained.
Fuel Guard recent exact-thread hook verified; direct sandbox daemon access denied,
no new daemon or quota assumption. No helper, game, Kit or preview process launched.

Source evidence: TEXTURE-EXPORT-001 actual association/manifest and runtime result;
original installed KFF images; import `20261016-050350Z-6dffd5be`; preview
`preview-20261016-050403Z-9003afa9`. Sponsor recognized the preview. New sponsor
screenshots are **ModelBrowser1.0.7.2**, selected `kff.mod`, LOD1, Fix issues OFF,
diffuse ON, emissive first ON then OFF. These are not in-game screenshots. Both
retain sharper panel detail than our preview; emissive toggle changes bright wing
markings/lights, not the basic panel sharpness. It supports utility emissive use,
not proof of SFC's secondary-image implementation or exact scene fidelity.

## Method / reproducibility

New read-only `tools/m1_component/compare_recovered_textures.py`; tests
`tests/test_compare_recovered_textures.py`. Python3.12.14/Pillow12.3.0, process-only
PYTHONDONTWRITEBYTECODE=1; tests TEMP/TMP=`artifacts/m1/test-temp`.

```text
python tools/m1_component/compare_recovered_textures.py artifacts/m1/runs/20261016-010112-enabled C:/Project/RemixJobs/20261016-050350Z-6dffd5be C:/Project/RemixJobs/preview-20261016-050403Z-9003afa9 --output artifacts/m1/runs/20261016-010112-enabled/TEXTURE-EXPORT-001-pixel-comparison.json
python -m unittest discover -s tests -p test_compare_recovered_textures.py
```

Original manifest hashes required; compare original BMP vs copied BMP, derivative
PNG, staged input PNG, then primary output DDS and staged preview DDS. Decode at
base resolution to RGBA; no resizing, colour adjustment or repair. Record RGB MAE,
max error, changed pixels, RMSE, PSNR and alpha comparison; orientation alternatives
are diagnostic scores, never applied. Limits: ten images,4096²,128MiB/file,
64KiB report, exclusive report creation. Actual images256²; no high-volume output.
Existing runtime90s/image128MiB/log32MiB caps unchanged; no new runtime probe.

## CONFIRMED result

- All ten copied BMPs byte-identical to originals; all ten derived and staged
  PNGs pixel-identical to decoded original RGB/alpha. No capture/export blur.
- Five displayed DDS files remain256², with nine mip levels. Header DXGI98 is
  BC7_UNORM (Windows SDK `10.0.26100.0/shared/dxgiformat.h:111`). No base-image
  down-resolution. Preview DDS hashes identical to import DDS hashes.
- DDS compression is lossy. Average absolute channel error ranges0.819–1.386
  levels out of255; individual maximum errors reach38. Do not claim pixel-perfect
  DDS or that local compression artifacts are impossible.

| ID / primary | RGB RMSE | PSNR dB | unchanged / vertical-flip / horizontal-flip RMSE |
|---|---:|---:|---|
|170 / KFF_1_2|1.6722|43.665|1.67 /41.00 /49.06|
|172 / KFF_1_1|1.4532|44.884|1.45 /56.07 /57.80|
|174 / KFF_1_4|2.4876|40.215|2.49 /69.36 /72.45|
|176 / KFF_1_3|2.0366|41.953|2.04 /61.12 /65.51|
|178 / KFF_1_5|2.1865|41.336|2.19 /58.25 /55.33|

No evidence of a global file-image flip; this **does not qualify UV placement on
geometry**. Lower mip selection/filtering, lighting, existing surface issues or
other preview differences remain hypotheses. No causal blur diagnosis yet. Same
source dimensions alone do not explain why ModelBrowser looks sharper.

Validation: three focused tests PASS (exact palette decoding, known pixel error/
alpha separation, resolution mismatch rejection); actual audit PASS; full project
Python suite/diff check recorded below. Raw per-image metrics/hashes are in the
new JSON. Preserve previous texture archive unchanged; additional evidence archived
separately with the two supplied screenshots, not edited/resized reference images.

Final validation:81 project Python tests PASS; `git diff --check` PASS;163
short-status entries, empty index, HEAD unchanged. No staging or commit.
Generated pixel report39295bytes, SHA256
`2834caeff3c8fa56c1b19e7d707374526edc992a18577d3cec3884aa7be427d6`.
Both supplied reference PNGs copied without editing to `<run>/reference/`.
Separate verified3-file archive (prior archive untouched):
`artifacts/remix-ingest/evidence/20261016-texture-pixel-comparison.zip`,282995bytes,
SHA256 `79daf1b0a9d175b5d20df85429be79a67b33b4131742b2d05d4539ab5c6c2260`.
No raw/image files deleted. ModelBrowser ON PNG146180bytes SHA256
`3d0cce7610c74129774fbe6556e753c20bdce78ccc15be5d8f7065d9773f2b86`;
OFF PNG144113bytes SHA256
`c95f64fbdc1847b0c9fa0fd05605b3db6b323788630a3333071381c00b677e5c`.

Versionable changes: diagnostic script/tests, this run record, result addendum and
new HANDOFF checkpoint. No source images, capture, DDS, USD or game artifacts
modified. No staging/commit. Overall remains PARTIAL: recognizable primary textures,
unqualified exact placement and secondary/glow role. Exact next action: inspect
the preview's effective mip/filtering state read-only before choosing a change.
