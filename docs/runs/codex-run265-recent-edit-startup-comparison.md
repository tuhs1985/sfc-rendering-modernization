# Run265 — Recent-edit isolation and reproduced dome-file blockage

Sponsor requested investigating recent edits first after the18-carrier test failed to show a replacement ship. Normal rendering source,binaries,appearance,Defender and the accepted game installation were left unchanged. All diagnostic source/builds/helpers are isolated under `artifacts/player-replacement/run265`.

## Recent changes inspected

- With effects.enabled=false,the added native capture sees observation-disabled and skips the full bank copy. The new64-bit effect adapter still does small inactive bookkeeping,but should issue no effect light API calls. Measured current replay summary confirms0active/0changes.
- Native recovery changes act on owner-specific insertion/suppression,after capture. The failed live run had zero committed insertions and no terminal gate reason;the measured host wait is downstream of actual D3D9 draws. No inspected recovery path explains a host command thread blocked inside a file open.
- Cleanup consolidation selected old closed-run generated support,not active dependencies or newly produced runtime light assets. Replay reads the same original captured geometry/image associations successfully. This does not prove every possible effect of recent edits absent;the controlled comparison below tests the most direct new rendering addition.

## Controlled renderer comparison

Created an isolated source copy with only the recent DirectEffectLights include/member/update/attach/draw/close removed. All other current code remains,so this is an **effect-adapter ablation**,not a byte-identical full historical rollback. Use the same executable basename,runtime DLL,build flags and current appearance settings. The normal host remains SHA256 `4FB1C90794FE58D1626A39D125CB947244C65A5374C467AAADE5AC5867D7550C`.

Standalone replay uses all8distinct model families captured in the failed044108game run,original geometry/images and deliberately synthetic identity/camera placement. No .mod parsing or SFC launch. Compared accepted light/material/image/quality files:all four byte-identical between these immediate runs and the failed game run.

| Trial | Renderer/activation | Observed result |
| --- | --- | --- |
|045318|Current,immediate|600frames,2zero-mismatch colour/depth/text checks,8owners. First live output query8.001ms. GPU job exit0. Effects0active/0changes.|
|045458|Effect adapter removed,immediate|600frames,2zero-mismatch colour/depth/text checks,8owners. First live output query8.643ms. GPU job exit0.|
|045940|Current,60sdelayed activation,existing bounded worker sampler|First live cohort timed out at4.993s. Command thread sampled opening the same dome DDS24times spanning4.879s.|
|050309|Effect adapter removed,60sdelayed activation,same sampler|First live cohort timed out at4.991s. Same dome DDS opening path23samples spanning4.443s.|

The first two supervisors report `Independent multi-owner pixels/shared-asset delivery incomplete`:the established fixture's final check expects the normal3owner/shared-asset scene,while this diagnostic supplies8different assets. Their native fixture and GPU renderer exited0 and completed the pixel comparisons. Exception cleanup then terminated the unused legacy observation host. Preserve these as diagnostic results,**not new production qualification passes** or evidence of the gameplay timeout. Neither delayed failure reached that cardinality check;both have the real `offline GPU completion5s limit` failure.

## Directly observed wait

Both delayed cases repeatedly sample `dxvk-cs` in `NtCreateFile → CreateFileW → UCRT fopen` in the pinned runtime,with the OS object name pointing to:

`gpu/textures/f5d105dd91e20553315a24d5ea412d94a0560a58f5fd8d230a6ae04cd7d1e062.dds`

This is the160byte,4×2uniform-white dome image already identified in Run256. The original failed game's copy has Archive attributes,not Compressed. The sampler spans are repeated file-opening observations,not an independently timed uninterrupted single kernel call. Private NVIDIA function names are not established by nearest exported symbol labels. Exact Windows/filter attribution remains unknown;do not claim Defender/NTFScompression/GPU exhaustion proven.

Current delayed slow record:query3.494ms,asset service90.455ms,pause4.897s. No-effects delayed:query3.616ms,service95.653ms,pause4.890s. Sampling suspended threads for398.281ms/221.571ms aggregate across744observations;it perturbs timing and is not performance qualification. The sponsor's unsampled failure and earlier Run256 observations independently establish this is not solely a sampling-created symptom.

## Conclusion and next fix

The new effect-light adapter is **not necessary** for the reproduced failure. Immediate8asset rendering works in both variants;delayed first-live-frame rendering fails in both at the same existing dome-file path. This narrows the failure to first-use environment-resource readiness rather than a demonstrated effect-code or fleet-complexity regression. It does not establish all recent edits incapable of influencing timing.

Code ordering exposes the readiness gap: private triangle render prewarm completes before activation,but accepted scene/dome lights are created/drawn only after the first live input. The160byte dome is generated under the run folder and supplied to Remix by filename at that late stage. Renderer-prewarm readiness therefore does not mean the configured environment is resident.

Next implementation should prepare the actual configured dome/environment through the existing supported light path before live-scene admission,retain/reuse the prepared resource and explicitly qualify readiness/cancellation/ownership. Do not simply move an unverified five-second timeout earlier,add an arbitrary frame warm-up count,disable GI,modify shaders/runtime internals or relax the live completion guard. Test delayed activation with these same8captured assets before another sponsor fleet run. Exact kernel/filter root cause can remain a separate investigation if needed.

The separate physical-hull32submission/fatal-overflow defect remains unfixed and must also be corrected before claiming18carrier+fighter support. Effect integration/emission recorder remain parked/off. No normal renderer/source changes were made in this investigation;isolated ablation/sampler builds remain local. No owned game/renderer/controller processes remain. Evidence/comparison/final-state receipts in run265. Changes unstaged/uncommitted.
