# Run146 — documentation-backed stock1.6.1 material trace

## Authority and disposition

User requested tracing with documentation backing, following Run145. Read current
handoff, its operating convention, approved M1 disposition and latest candidate
record. Diagnosis only: no production fix, runtime promotion or gameplay test.
M1's amended component disposition remains unchanged; no aggregate TRL claim.

**PARTIAL: native texture identity is now qualified against the actual candidate
runtime. Replacement selection/application remains unresolved.** Run145's
inactive/unmatched hypothesis is narrowed: a hash mismatch is NOT supported for
the two tested assets. Do not claim materials are applied merely because their
images are loaded, or treat replacement-disabled capture as replacement proof.

## Supported path and source authority

NVIDIA's [material workflow](https://docs.omniverse.nvidia.com/kit/docs/rtx_remix/1.6.1-0/docs/howto/learning-materials.html)
documents hash-associated replacements and separate emission controls. Narrow
inspection of release-linked runtime source at
`0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0` established:

- [USD loader](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_mod_usd.cpp):
  `getMaterialHash` prefers the hexadecimal `mat_` name; direct child `Shader`
  is supported. `/RootNode/Looks` children are processed; opaque data is
  deserialized and stored by that hash. Our generated structure matches these
  rules. Absence of MDL subIdentifier is not established as a failure here.
- [Lookup](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_asset_replacer.cpp):
  `getReplacementMaterial` checks effective replacement policy and searches
  loaded mod material tables.
- [Scene selection](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_scene_manager.cpp):
  the ordinary material's hash is looked up, then a found replacement is copied
  and merged with legacy material data. Matching names alone do not attest this
  runtime branch or its merged values.
- [Vendor capture](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_game_capturer.cpp)
  refuses capture while replacements are enabled.
  [Options](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_options.h)
  support `DXVK_DISABLE_ASSET_REPLACEMENT=1`, disabling all replacement classes
  during initialization. No vendor modification was needed.

Provenance caveat remains important: packaged DLL reports `remix-main+5a7eec84`;
official GitHub commit lookup for that short SHA returned422/no commit found.
Release-linked source describes intended behavior, not independently verified
exact DLL build source. Never silently replace this authority with current main.

## Probe definition and execution

Ignored local diagnostic supervisor `artifacts/trace_candidate_material_capture.py`
injects environment only into the exact verified isolated candidate host child;
no launcher/native source/global environment modification. Existing fixture,
owned-job and storage guards remain intact. One run at a time; no SFC/Toolkit GUI.
Fixed120th-frame NVIDIA scene capture, single-frame, config capture off,
automatic screenshot trigger absent. Existing fixture100s/owned renderer285s,
32MiB non-image evidence/20GB aggregate limits retained. Capture export itself
is diagnostic overhead, NOT a loading performance measurement.

1. `artifacts/remix-runtime/runs/20261024-171212-319819-return-fixture`:
   ordinary replacement policy retained. Log confirms capture env recognized,
   then `Cannot begin capture while replacement assets are enabled.` No USD
   exported; expected restriction, not a failed material hash test.
2. `artifacts/remix-runtime/runs/20261024-171521-679139-return-fixture`:
   same FCA/RCA fixture, documented replacement-disable environment added only
   for this diagnostic. Capture completed with197 filesystem entries,
   24,971,814file bytes,61materials. This does NOT test replacement appearance.

Both fixtures completed normal source/receiver shutdown, native jobexit0,
stop_reason0 and remaining_owned_processes0. First steady delivery594/600;
capture-enabled600/600; these are fixture checks, not comparable speed claims.
State errors0, border/HUD preserved, resize/device recreation completed.
Known vendor common-object teardown warning persists; no leak-free claim.

## Confirmed trace: one known FCA material

Local read-only USD inspection used managed Toolkit libraries
`C:/Program Files/NVIDIA Corporation/RTX Remix/extscache/omni.usd.libs-1.0.3+6312fa25.wx64.r.cp312`,
USD0.25.11. No Toolkit process or installation changes. Diagnostic script
`artifacts/inspect_material_trace.py`; exact receipts in the second run's
`material-trace-analysis.json` and `gpu/material-trace-probe.json`.

- Captured group37 -> ordinary texture0 ->512x128 BGRA upload.
- Worker recomputed `1054E15B0EBB90A7` from actual upload payload.
- NVIDIA exported `materials/mat_1054E15B0EBB90A7.usd` and corresponding texture.
- Decoded NVIDIA texture pixels equal upload pixels byte-for-byte; vertically
  flipped comparison is unequal. No new orientation correction justified.
- Captured mesh `mesh_2CD22029A40FA5F1/mesh` and its instance inherit the known
  material binding. No native pointer used as content identity.
- ALL61 unique hashes from both fresh asset manifests match ALL61 NVIDIA
  captured material hashes; zero missing/unexpected identities.
- Our replacement prim `/RootNode/Looks/mat_1054E15B0EBB90A7/Shader` composes
  successfully. Diffuse/emission/roughness image references resolve to existing
  files with SHA256 matching their content-addressed filenames:
  `69aa5e04d27e8b36df806284b383cbbba5f7fe267fe17f2a7ca3d5b2f20ca2cc`,
  `0bf9278eae8e8c9a9b1dd2eff2b20afac1f989be04bef577ccfa7fd38a2fa07e`,
  `586ec1c7d45136aa4c343d5673552f66473d242f7f5c09223be76f35c0764318`.
- Authored enable_emission=True/intensity5, roughness~0.4 and metallic~0.2
  survive USD composition. This validates authoring/resolution, NOT shader use.
- First run's actual runtime log registers our asset search paths and warns
  about replacement textures lacking mipmaps. Thus some replacement textures
  are reached by the runtime; this is not proof this exact material is selected.

Initial USD inspection emitted NVIDIA-export binding-schema warnings because
its exported prims lack applied MaterialBindingAPI. Inspection was repeated via
direct/inherited binding relationships, with identical known mesh association;
do not repair our geometry/materials based on this vendor-export warning.

## Confidence, remaining boundary and next action

CONFIRMED: capture, upload bytes, texture hashes, generated USD structure and
resolved image paths are coherent for this fixture. CONFIRMED Run145 pixel
tests still show candidate library has no intended observable effect.
STRONG HYPOTHESIS: effective policy, loaded-table publication/selection, or
legacy-material merge/application is bypassing the intended replacement.
SPECULATIVE: a specific vendor bug, parameter regression or cache fault; none
is established by current evidence. Do not rewrite a loader or change hashes.

Exact next action: isolate ONE known hash in the existing standalone fixture
with a deliberately unmistakable material override, then distinguish effective
replacement policy/table selection from merged-material application using the
pinned supported interfaces/source. Preserve accepted maps/settings and the
normal1.5.2 path. No sponsor gameplay or new discovery capture needed.

## Repository and validation

Current turn changes: this record and new HANDOFF checkpoint; ignored diagnostic
scripts/receipts/capture evidence only. Earlier dirty implementation/research
files preserved. HEADfe2eaf7/indexempty; no stage/commit/push/helper/agent.
FuelGuard attach confirmed existing trusted hook; no daemon spawned.
No normal implementation/settings/client/dependency edits or rebuild. Prior
495tests are historical, not rerun here. Seven targeted runtime-candidate tests
PASS (0.029s). Both bounded native fixtures plus USD, hash/pixel/path checks and
`git diff --check` performed. Independent read-only
process inventory found no matching game/renderer/fixture processes afterward.
Governed evidence after probes19,054,172,146bytes<20,000,000,000; no cleanup needed.
No active state must survive restart. Source-level normal qualification remains
valid because no tools/tests/native implementation files changed this turn.
