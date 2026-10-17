# Codex run — PROVISIONAL-LIGHTING-20261016

Active task: offline texture recovery; milestone/gates unchanged. Sponsor:
"Don't have access to computer. Do what the code suggests. We can verify later."
This authorizes a labelled hypothesis preview before runtime validation, **not**
promotion of a role/fidelity claim or requirements waiver. Starting HEAD
fee152f137a55a3efeb47a5c236ebf9e3e1951cb,170 short-status paths/index empty;
inherited work preserved. Fuel Guard exact-thread recent hook verified/direct
sandbox access denied/quota health unknown; no daemon spawned.

## Inputs / implementation decisions

Read HANDOFF, secondary-role adjudication/preparation/probe, current preview and
ingestion tools/tests, accepted capture20261016-010112-enabled association manifest,
accepted textured import20261016-050350Z-6dffd5be and installed AperturePBR MDL.
Static intended legacy operation primary*clamp(secondary+vertex_lighting) remains
supported; actual branch predicates were not captured. Do not invent them now.

Default-off `--provisional-lighting` requires `--textures --resident-textures`;
incompatible with other sampling diagnostics. New helper verifies import/capture
packet and manifest/reference/ten PNG hashes, exactly five captured group pairs,
matching opaque256² images. Computes per-channel floor((primary_encoded *
secondary_encoded+127)/255), producing five separate uncompressed RGBA DDS plus
PNG products with exact decoder round trips. No original/import overwrite,
UV flip, geometry/normal/winding/rotation repair or source alpha invention.

This product is the unsaturated algebraic term, **not** exact reproduction of
legacy intermediate clamping. Encoded-space multiplication, emission intensity1
and sRGB emissive interpretation are explicit preview assumptions; legacy color
space/physical strength unproven. Installed AperturePBR_Opacity.mdl145–153/493–495
documents sRGB emissive_mask_texture and emission intensity; use mask, not an
unsupported parameter. No RTX feature/final architecture selection implied.

Kit authors only matching source_000..004 shader emission asset/bool/intensity in
anonymous session, verifies each original primary-image filename, records five
read-back authored assignments. Reuses existing UVs/cameras/lights/residency. UI
and manifest state PROVISIONAL / RUNTIME UNVERIFIED. Normal textured/grey launchers
remain unchanged; new separate `start_provisional_lighting_preview.cmd` reproduces
this hypothesis only. No SFC runtime code changes or new capture this run.

## Validation / evidence

Python3.12.14/Pillow12.3.0; Toolkit1.6.0-dev+main.30229.3f23f80a.gl/Kit110.1.1,
existing bounded_job.exe. Probe MESH-PREVIEW-001 updated before renderer use.
Reproduction, with configured bundled Python executable:

```
tools/remix_ingest/run_mesh_preview.py --job C:/Project/RemixJobs/20261016-050350Z-6dffd5be --textures --resident-textures --provisional-lighting --smoke
tools/remix_ingest/run_mesh_preview.py --job C:/Project/RemixJobs/20261016-050350Z-6dffd5be --textures --resident-textures --smoke
```

Scoped execution exception only for sandbox GPU startup; no admin dialog/security
change or sponsor gameplay required. Same child NRC off/bloom off,180s wall,
120s interactive viewing,128MiB scratch warning/256MiB stop,8MiB console,
three fixed1024x640 smoke PNGs <=8MiB each,64KiB reports. Product output cap8MiB,
below original128MiB total-image envelope; only ten logical image slots in preview
(five diffuse/five product emission), no continuous dumps/multi-GB mechanism.

Under C:/Project/RemixJobs:

| Job | Setting | Time | Console / peak scratch bytes |
| --- | --- | --- | --- |
|preview-20261016-184026Z-5d2bfcb9|provisional product emission|16.390s|24594 /2729067|
|preview-20261016-184126Z-4af65ccc|unchanged emission-OFF control|16.297s|24594 /1285038|

Both exit0/stop0/READY452triangles/11prims, no warning, zero remaining owned
processes, source USD unchanged. New product PNG+DDS total1422112bytes. Existing
five diffuse DDS in both jobs hash-identical to import; all ten original installed
BMP and lossless PNG hashes still match prior manifest. Original USD SHA256
5c08f217b36ef9056c3a1940931ff2fd463286ca67e120d7bd80269b997634b2 unchanged.

Analyst inspected both above.png: reconstructed mode visibly brightens localized
wing markings/neck-rim/lights; original panel detail remains sharp. Emission also
illuminates nearby surfaces through the preview renderer; this is NOT evidence
of SFC's original indirect-light behavior or a repair of existing dark/open faces.
Above-image RGB RMS difference7.736/7.094/5.317; difference includes sampling
variation and is not a fidelity score. Five source/image/shader assignments
confirmed in preview-provisional-lighting.json. **CONFIRMED offline preparation,
decoding, assignment and visible effect; runtime role/fidelity UNVERIFIED.**

34 preview/ingestion unittest cases PASS;83 project Python cases PASS. New tests
cover exact product, no input mutation, size refusal, full five-group derivative/
round trips, provenance changes rejected before output, repeat refusal, session-only
shader changes, labels and explicit option gating. git diff --check/link checks
PASS. No C++ rebuild needed; prior prepared0.16 runtime collector untouched.

Both installed/reference client SHA256 unchanged:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
No game/controller/Kit process remains; no game-directory files created/removed.

Archive useful evidence, portable caches excluded, no originals/raw deletion:
`artifacts/remix-ingest/evidence/20261016-provisional-lighting-preview.zip`,
1531564bytes,97 entries each SHA256-verified against source after ZIP reopen;
ZIP SHA256 fca90e38bc7acb462edfe3fc9228a5924a45f896f863a09896956033ae01b707.
Contains both job configs/scripts/logs/screenshots and product manifest/images.
Older archives/shared caches unchanged. No helper/server/live session used.

## Files / handoff

- New tools/remix_ingest/provisional_lighting.py, test_provisional_lighting.py,
  start_provisional_lighting_preview.cmd.
- Updated tools/remix_ingest/run_mesh_preview.py, kit_mesh_preview.py,
  test_mesh_preview.py.
- Updated docs/reconnaissance/probes/MESH-PREVIEW-001.md,
  docs/reconnaissance/2026-10-16-secondary-texture-role.md,
  docs/HANDOFF.md; this new run record.

Rejected scope: game changes, guessed confirmed glow, final physical calibration,
brightness/face repair, new wrapper, broad RE, extra runtime requests while sponsor
away, modifying defaults. Overall texture recovery still PARTIAL. No current input
blocker for the authorized provisional preparation; completed and safely stopped.
Final HEAD unchanged/171 short-status paths/index empty; inherited changes preserved, nothing staged or
committed. Generated outputs ignored. No process/tool state needs to survive restart.
Exact next action when sponsor returns: run prepared texture export to observe both
branch predicates, then compare this labelled saved-ship lighting preview with SFC.
Do not redo capture/pixel recovery/mip investigation or infer old missing fields.
