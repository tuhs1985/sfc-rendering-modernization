# Run148 — full-library controls correct the material diagnosis

## Outcome

**The existing full material library WORKS in the basic two-asset stock1.6.1
fixture. Emission affects returned pixels. No library-layout repair or runtime
upgrade is justified by this increment.**

This corrects the overly broad interpretation in Runs145–147, not their raw
measurements. Their larger three-content/four-owner cases and earlier full/empty
similarity remain historical evidence. Do not generalize that finding to every
candidate material submission, or use it to justify rewriting a working loader.

User authorized full-library factor isolation and comparison against working
1.5.2. Current handoff/instructions, Run147 and approved M1 disposition read.
No sponsor gameplay, game installation changes, production fixes, tuning changes,
architecture change or milestone claim. Source/SDK/runtime pins unchanged.

## Documentation backing

NVIDIA's [material workflow](https://docs.omniverse.nvidia.com/kit/docs/rtx_remix/1.6.1-0/docs/howto/learning-materials.html)
and release-linked [USD material loader](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_mod_usd.cpp)
support the existing material/hash submission path. Narrow source check confirms
texture lookup first uses USD-resolved paths, then its layer-relative fallback,
followed by asset lookup/preloading. The path-only test does NOT prove this
packaged DLL executes every branch identically to release-linked source.
Packaged build5a7eec84 vs public source0a6cd5b caveat remains.

## Probe and factors

Ignored `artifacts/trace_library_factor.py` changes only standalone supervisor
behavior, never normal source/native/runtime binaries or user configuration.
Same existing FCA/RCA captured packets, ordinary D3D9 adapter, camera, light/image/
quality baseline, process ownership,100s fixture/285s job,32MiB non-image evidence
and20GB total bounds. No automatic scene capture; only existing two finite BMPs.
No concurrent GPU fixtures. All normal pipeline qualifications explicitly remain
separate from these diagnostic derivatives.

Cases under `artifacts/remix-runtime/runs/`:

| Suffix | Factor | Adjudication |
| --- | --- | --- |
|171212-319819|Prior ordinary candidate layered library|Basic full-library reference|
|171521-679139|Prior NVIDIA environment explicitly disables replacements|Actual negative control, not merely an empty generated stage|
|172435-519182|Prior one-normal-material root derivative|Matches disabled; NOT a successful restoration|
|175809-323667|Initial empty root-declaration derivative|Invalid USD syntax; EXCLUDED from layout conclusions|
|175854-436164|Original layers, image references made absolute|Matches disabled; no improvement; not promoted|
|175950-136276|Existing full flat-library generator|Matches ordinary layered result closely; no needed flattening fix|
|180049-258706|Working1.5.2, same basic fixture and settings|Direct version control; recognizable materials, residual differences remain|
|180207-758927|Corrected empty root declarations, no material/path edits|Full61materials; close to layered result, not a repair|
|180335-481323|Flat control with only authored emission intensity set0|Clear returned-image change with same image bytes|
|180537-490349|Flat control with roughness texture blocked/constant0.02|No reliable isolated positive effect distinguished from control variation|

Initial175809 native output/HUD/exit succeeded but material USD failed parsing.
Managed USD parser independently detected invalid inline child syntax. Error is
our ignored diagnostic, not NVIDIA or game regression. Original evidence kept;
corrected script now parses each derivative before publication, then reran.
Do not count native fixture transport success as successful material validation.

One roughness attempt was refused BEFORE fixture/process creation by existing
768MiB reservation inside20GB. Completed images were recoverably archived before
retry; no cap increase and no failed-run performance claim.

## Measured image results and confidence

Curated [comparison evidence](../reconnaissance/evidence/20261024-library-factor-controls.json).
Full raw analysis: `artifacts/library-factor-analysis.json`, reproduced by
`artifacts/analyze_library_factors.py`. USD0.25.11 from existing managed libraries;
no Toolkit GUI/install change. Relative image paths may resolve missing AFTER
compaction; restore via generated-images-archive.json before decoding images.

Late comparisons use the25,919pixel non-background ship union, no scaling:

- Ordinary candidate vs explicitly disabled: mean absolute RGB24.6145/255,
 22,467pixels change>3/channel. Therefore blanket "library has no effect" is false
 for this fixture. All61identities already verified against NVIDIA capture.
- Ordinary candidate vs complete flat library:0.0882mean,54pixels>3. Identical
 generated image SHA multiset and material values. Both are on the material-
 applied side of the negative control. Flattening is not a demonstrated fix.
- Valid root-declaration-only vs layered:0.4581mean,559pixels>3; also clearly
 distinct from disabled. Root declarations alone do not explain a universal
 material failure; no reason to add them to normal pipeline from this test.
- Working1.5.2 vs ordinary candidate:2.4944mean,7,665pixels>3. Same layout/assets/
 generated image hashes/settings. This is much closer than disabled25.0105,
 but NOT pixel equality or complete version/appearance qualification.
- Emission0 vs full flat:4.4935mean,4,316pixels>3 with unchanged images. Confirms
 actual texture-based material library's emission control affects returned image;
 no need to infer it from the earlier green constant alone.
- Roughness smooth vs full flat:0.4654mean,576pixels>3; versus neutral root-only
 control0.0733mean/39pixels. This is comparable to control variation, not a
 trustworthy isolated roughness-response proof. Preserve limitation, no claim
 all material controls are validated.
- Absolute paths vs disabled0.0674mean/19pixels; Run147 one-root material vs
 disabled0.0623mean/15pixels. Those changed outputs were regressions toward the
 negative control, not successful normal-material restoration. Their final
 files compose61materials, but runtime logs have only root search-path registration
 and no replacement-texture warnings; exact startup/table/resource cause remains
 unproven. Never promote either diagnostic as a path repair.

All basic cases retain272generated image/native-upload files102,477,040bytes,
same SHA multiset, even where diagnostic shader constants/input presence differ.
This verifies images unchanged, NOT that every case uses them successfully.

CONFIRMED: full static two-asset submission and emission work. CONFIRMED: normal
flattening is unnecessary for this case. STRONG HYPOTHESIS: remaining problem is
specific to larger/incrementally published libraries or startup/loading state,
not blanket incompatible material submission. No exact root cause demonstrated.
Do not extrapolate this test to the larger432-file/three-content cases, claim
all controls work, select a new architecture or assert a vendor bug.

## Validation, compaction and repo state

Seven executed native fixtures this turn completed jobexit0/stop_reason0/owned0,
source state/HUD/border/resize/recreation/normal exit checks. One is the excluded
invalid-USD diagnostic above. Valid steady windows: path594/600, flat600/600,
working control596/600, corrected root595/600, emission594/600, roughness593/600.
These are bounded transport checks, NOT equivalent-material startup speedups.
Vendor common-device-object teardown warnings remain, not leak-free validation.

24targeted Python tests PASS0.218s (candidate, material-library, normal-material
binding). Prior full495suite historical; no source implementation/build changed
this turn. Independent read-only inventory no owned game/renderer/fixture left.
`git diff --check` checked. No client files, normal binaries, managed Toolkit,
dependency pins or tuning files changed. No stage/commit/push/helper/agent.
FuelGuard attached through existing trusted hook; no daemon started.

Eleven completed generated image sets were archived272files each, every entry
decompressed/SHA256checked BEFORE exact originals removed. Each102,477,040bytes
becomes6,572,793byteZIP; net1,054,946,717bytes before receipt overhead. Scoped
script `artifacts/archive-material-trace-images.ps1`, per-run restore manifests,
ZIPs under `artifacts/remix-runtime/archives`. Source packets, geometry/UVs,
logs/receipts/comparison BMPs and Run146 NVIDIA capture retained. Final evidence
19,148,476,109bytes<20GB before this small documentation, dependency exclusion
unchanged. Compaction is reversible; no evidence history erased.

Current turn versionable additions: this record and curated comparison JSON;
HANDOFF updated. Other prior dirty files preserved; HEADfe2eaf7/indexempty/
unstaged/uncommitted. Ignored diagnostic scripts/results only. No active state
required for resume; normal1.5.2 qualification unchanged.

## Exact next action

Use the EXISTING larger three-content/four-owner late-arrival fixture with an
explicit replacement-disable control and matched initial/late material-response
checks, separating initial success from material-table behavior after library
publication. Preserve normal maps/values and1.5.2; archive completed outputs
before reserving as necessary. Do not repeat broad discovery, flatten normal
code, promote candidate or claim sub2s until this larger-path discrepancy and
appearance/material response are adjudicated. No sponsor gameplay needed.
