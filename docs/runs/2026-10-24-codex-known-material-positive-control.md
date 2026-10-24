# Run147 — known-material positive control reaches returned pixels

Historical interpretation corrected by [Run148](2026-10-24-codex-full-library-factor-controls.md): the one-normal-material root derivative matches the explicitly disabled control, not a successful restoration; basic full-library submission already works. Raw results below preserved.

## Result and scope

**CONFIRMED: stock1.6.1 can select and apply our known hash replacement through
ordinary D3D9 and the existing returned-image connection.** The standalone
positive control produced a green FCA surface where the baseline had none.
Do not continue describing the entire candidate replacement mechanism as broken.

User authorized the Run146 next diagnostic. Read handoff/Run146 and current
publication implementation. This is diagnosis, not a production runtime upgrade,
appearance change, loading fix, sponsor gameplay or milestone completion. Normal
1.5.2 game dependency, client files and all tuning configurations remain untouched.

## Documentation and code backing

Release-linked NVIDIA source remains pinned at
`0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0`; packaged binary reports5a7eec84,
which remains unavailable in the public commit lookup. Do not claim exact-source
binary attestation or substitute current main.

- [Material inputs/deserialization/merge](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_material_data.h):
  confirms the existing diffuse/emissive/roughness input names. Authored input
  presence marks fields; merge preserves authored fields rather than blindly
  replacing everything with legacy values.
- [Legacy merge](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_materials.h):
  legacy texture and sampler defaults are merged into replacement material data.
  The separate computeIdentityHash is a dynamic-path identity/cache concern;
  do not conflate it with the texture replacement identity verified in Run146.
- [USD loading and texture resolution](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_mod_usd.cpp):
  shader attribute's authoring layer participates in relative texture resolution.
  Thus local USD composition success is not proof of the packaged runtime's
  selected table, resolved resources or application behavior.
- [NVIDIA material workflow](https://docs.omniverse.nvidia.com/kit/docs/rtx_remix/1.6.1-0/docs/howto/learning-materials.html)
  documents material replacement and emission. No custom loader/vendor patch.

## Probe definition

Ignored supervisor `artifacts/trace_material_override.py` temporarily overrides
only `multi_scene_relay.Relay.commit_layers` inside one offline Python process.
Normal implementation files, native host and vendor DLL are not edited/rebuilt.
The existing bounded fixture launches the separately qualified candidate host:
`--multi-ship --prewarm --startup-profile --pipeline-mode performance
--runtime-candidate 1.6.1`. No automatic vendor capture/screenshot environment
or replacement-disable environment is injected in this probe.

Only known material `1054E15B0EBB90A7`, verified by native upload and NVIDIA
capture in Run146, is changed. Root-stage derivative is written before asset
catalog publication/activation; original worker material stages and images stay
unchanged. Diagnostic derivative is not a normal material manifest or gameplay
qualification. Existing runtime100s/job285s/32MiB non-image/20GB bounds apply;
two existing finite early/late fixture BMPs, no continuous images.

### A — positive control

`artifacts/remix-runtime/runs/20261024-172143-140985-return-fixture`.
Strongest-layer `over` for existing shader: diffuse/emissive constant green,
emission20, metallic0, roughness1; diffuse/emissive/roughness texture attributes
blocked. This is deliberately diagnostic, NOT user tuning or accepted appearance.
Managed USD0.25.11 inspection confirms the intended composed values and blocks.

Relative to same-pose basic two-asset candidate baseline171212, late output has
566 new green pixels in fixed FCA region x200..549/y740..919 (baseline0).
Actual returned image visually shows green on the FCA lower saucer/structure,
not another desktop window. Whole ship-region union25,919pixels: mean absolute
RGB difference3.986574/255,6,243pixels differ by>3 in any channel. Incidental
small render noise cannot explain the spatially targeted new green surface.
This proves at least this known replacement is selected and influences output;
it does NOT individually validate every material input or normal map.

### B — exact normal material authored at root

`artifacts/remix-runtime/runs/20261024-172435-519182-return-fixture`.
Uses the existing `material_binding.shader` generator and this known group's
accepted images/values. Authored directly in the strongest root `RootNode/Looks`
definition; only generated image references rebased to the same unchanged files.
Existing sublayers retained. No normal color/roughness/emission values retuned.

Composed fields match baseline values (including emission5, roughness0.4,
metallic0.2); paths point to the same content-addressed DDS files. Late image
changes24.613372/255 over25,919ship pixels;22,458pixels differ>3. No new green
FCA pixels. Large image change is CONFIRMED, not equivalent-material correctness.
Other ship pixels also change, so do not claim only this group's pixels changed
or that geometry identity/lights changed; lighting/material interactions and
publication timing have not been independently isolated.

Baseline is Run146171212 basic FCA/RCA, not Run145's larger three-content layout.
Exact metrics, composed fields and job results are in second run's
`material-override-comparison.json`; per-probe `material-override-probe.json`
records derivative SHA/policy. Reproduce analysis with ignored
`artifacts/analyze_material_override.py`; no image edits/rescaling used.

## Adjudication and limitations

CONFIRMED: a matching known material can affect the final returned pixels.
CONFIRMED: changing publication/authoring of the exact normal material changes
the result substantially. Thus capture identity and blanket inability to apply
replacement materials are no longer the leading explanation.

STRONG HYPOTHESIS: normal library publication/composition/resource-resolution
behavior is implicated. Not a verified root cause: the second probe changes
root prim authoring and path anchoring together; it is one sample, and runtime
load timing differs. Do not assert a particular NVIDIA defect or repair.
Earlier Run145 flat-library experiment showed no intended restoration; retain
that conflicting evidence. A universal "flatten everything" fix is NOT proven.
Earlier full/empty similarity remains factual for those runs, but no longer
supports an unconditional claim that candidate replacements cannot work.

Exact next action: perform an existing-fixture full-library A/B that separates
root prim authoring from texture-path anchoring/publication timing, preserving
all accepted maps/values and verifying final output against the normal1.5.2
control before proposing a candidate material-publication fix or upgrade.
No sponsor gameplay needed. Archive completed generated images before further
fixtures if the existing reservation check requires space; never raise20GB.

## Validation and repository state

Both native fixtures PASS normal exit/jobexit0/stop_reason0/owned0, source state
errors0, original fixture HUD/border checks, resize and device recreation. Both
steady delivery windows595/600, not a new timing/performance claim. Existing
vendor common-device-object teardown warning remains; not leak-free validation.
Seven candidate unit tests PASS0.036s; full495tests are historical, not rerun.
Read-only independent process inventory found no matching owned renderer,
fixture or game afterward. Governed evidence19,309,344,607bytes<20GB before
this small record; no third GPU fixture attempted without storage reservation.

Current-turn versionable edits: this record and HANDOFF; ignored diagnostic
supervisor/analysis scripts, receipts and fixture evidence. Prior dirty files
preserved. HEADfe2eaf7/indexempty; unstaged/uncommitted, no push/helper/agent.
FuelGuard attached through existing trusted hook; no daemon started. No active
GPU/tool state is required to resume. No normal implementation/settings edits,
so existing normal source-qualification receipt was not invalidated.
