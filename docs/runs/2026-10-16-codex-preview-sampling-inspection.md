# Codex run — PREVIEW-SAMPLING-20261016

Task: sponsor authorized inspection of texture sampling after the direct pixel
audit. Read current HANDOFF/pixel-audit record and existing viewer/renderer config.
HEADfee152f,163 short-status entries/index empty at start; inherited work retained.
Fuel Guard recent-hook receipt verified; direct access denied, no daemon started.
No helper, SFC run, source asset changes, commits or staging.

## Question and inspection

Does an observable low-detail override explain the textured preview's softness?
Originals and PNGs already match exactly; DDS base256²/nine mips/BC7 with small
compression error established. Do not redo capture or assume mip selection.

Read installed Toolkit1.6.0-dev sources: Hydra extern.py exposes a config setter
but no corresponding getter in its documented Python wrapper; settings_bridge.py
reads captured USD configuration, which this offline asset does not contain.
HydraTexture settings-path getter describes its published state, not per-pixel
native sampler telemetry. Existing log `samplerAnisotropy:1` is a capability,
not active filtering. Source USD has five diffuse images/emission OFF, no authored
texture-filter override. Viewer config authors only bloom OFF plus established
child-local Custom4/ImportanceSampled0 NRC-off environment.

Official upstream reference:
[RtxOptions.md](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/main/RtxOptions.md)
describes `rtx.nativeMipBias`, `rtx.maxAnisotropySamples` and sampler-feedback
controls. This moving upstream documentation is NOT evidence of the installed
binary's effective values. No default from it was promoted to runtime fact and
none of these settings was changed.

## Bounded observation

Added pure read-only helper `tools/remix_ingest/preview_sampling_audit.py`, two
unit tests in `test_sampling_audit.py`, runner copying/hash provenance, and a
post-readiness JSON call in `kit_mesh_preview.py`. Definition recorded before run
in MESH-PREVIEW-001 addendum. Reads four published Kit roots; selected scalar
keys only,256 values/8192 visited nodes/depth16/string256/64KiB output limits.
No settings setter, material edit, sampler override or texture conversion.

Bundled Python3.12.14, installed Toolkit/Kit, existing bounded_job guard:

```text
python -m unittest discover -s tools/remix_ingest -p test_*.py
python tools/remix_ingest/run_mesh_preview.py --job C:/Project/RemixJobs/20261016-050350Z-6dffd5be --textures --smoke
git diff --check
```

Process-only PYTHONDONTWRITEBYTECODE=1; tests TEMP/TMP=`artifacts/m1/test-temp`.
One approved out-of-sandbox offline graphics replay, not UAC/security relaxation.
Existing180s job/256MiB scratch/8MiB console/three8MiB PNG limits unchanged;
child-only NRC-off config unchanged. No new runtime game probe.

## Evidence / conclusion

Job `C:\Project\RemixJobs\preview-20261016-051922Z-c8fef267` clean exit0,
16.688s, zero remaining owned processes.452triangles/11mesh prims; source USD
SHA5c08f217b36ef9056c3a1940931ff2fd463286ca67e120d7bd80269b997634b2
unchanged. Peak scratch1236824bytes, console24448bytes, no warning/stop.
`preview-sampling-audit.json`:238 nodes, not truncated, no settings written.
Published Kit roots /rtx,/rtx-transient,/renderer present; persistent Remix settings
extension root absent. Streaming enabled, maxMipCount15; these Kit values do NOT
prove this native Remix renderer's actual resident/sampled mip or filtering.
No native mip bias, active anisotropy or upscaling value obtained. No published
low-detail override found within the qualified observation; not proof none exists.

**PARTIAL diagnosis:** no causal explanation for softness. Per-pixel/native sampled
mip not exposed by this observation. No failed renderer/seam inference, no full
fidelity PASS. Previous texture associations/pixel audit remain valid. Do not
read missing settings as zero, feature support as enablement, or DDS mip count
as the sampled mip. No RenderDoc/extra wrapper/broad graphics instrumentation added.

Validation:23 Remix/preview tests PASS (including missing-vs-zero and bounded
snapshot/nonmutation tests), actual smoke PASS, source hash preserved, diff check
PASS. No native rebuild needed. Versionable edits: helper/tests, runner/Kit script,
probe addendum, this record and HANDOFF. Raw job logs/JSON/PNGs archived separately
without portable caches; no source/raw evidence deletion. Archive details below.
HEAD unchanged; empty index, dirty inherited/new work unstaged, no commit.
Final164 short-status entries. Verified41-file archive:
`artifacts/remix-ingest/evidence/20261016-sampling-inspection.zip`,595829bytes,
SHA256 `d473dd6b190c77bdeb98548be44ef1e14f7a53312803459818af3cc596e788f9`.
No source/raw files deleted; original comparison archives preserved.

Exact next action: propose/obtain approval for one scratch-only A/B preview using
base-mip-only texture derivatives versus the unchanged existing mip chain. Keep
colour/UV/geometry/lights/camera unchanged; do not sharpen/upscale or fix faces.
This is a controlled hypothesis test, not a promised fix. No sponsor gameplay
needed; no A/B rendering change implemented in this run.
