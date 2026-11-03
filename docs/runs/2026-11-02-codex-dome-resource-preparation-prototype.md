# Run269 — Supported dome-resource reuse prototype and material-publication blocker

## Outcome

An isolated prototype demonstrates preparing the configured project dome through the existing Remix API, retaining its actual light handle, and transferring that handle into live lighting without recreating it. First-live completion-query waits were **6.075–7.869 ms** in five prepared-resource trials. This is the measured completion stage, not total model appearance time.

Three of six total trials completed the standard 600-frame native fixture, colour/depth/text checks and normal teardown: stable-file-only delayed startup, prepared-resource immediate startup, and one prepared-resource delayed startup. Three other prepared-resource delayed trials delivered their first live images quickly but later failed material-library publication. Do not hide those failures or claim reliable production startup is fixed.

No normal source, renderer binary, configuration, game file or protection setting was changed. The normal host remains SHA256 `4fb1c90794fe58d1626a39d125cb947244c65a5374c467aaade5ac5867d7550c`. Effect lights remain off. The separate physical-hull32 defect remains unfixed; no sponsor fleet launcher is newly qualified.

## NVIDIA-supported behavior and why handle reuse matters

- [Pinned CreateLight implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_remix_api.cpp#L1066) queues dome texture resolution/preloading and residency tracking on the command stream.
- [Asset lookup](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_asset_data_manager.cpp#L571) constructs a new loader on lookup; keeping some other light alive does not prove that recreating the live light avoids another file open.
- [Light manager](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_light_manager.cpp#L765) retains handles separately from submitting their instances. Preparation can therefore precede live participation.

Public source is corroboration; exact packaged private-function/source parity remains unverified. No runtime internals were patched, new decoder invented, or alternative graphics architecture introduced.

## Isolated implementation

Files are under `artifacts/player-replacement/run269`, outside frozen production-source globs. Source starts from the byte-identical pre-effect host used in the controlled comparison.

1. Keep one immutable, content-named copy of the exact existing 160-byte white DDS in a diagnostic environment cache. Python checks exact source bytes/hash. The prototype requires its filename to match the light shape's content filename. Neither pixels nor light settings change.
2. A stable-path-only variant redirects that dome image to the cache, retaining normal live light creation. It provides a separate control from API preparation.
3. The prepared variant supplies the existing checked 808-byte shape packet before host startup. It supports only the currently enabled **project_fill dome**, whose complete settings are known independently of ship capture. It does not invent early native scene-light values or bind a ship identity before activation.
4. The host creates that actual configured dome using the existing `createShapedLight`/public `CreateLight` path before private renderer warm-up and before declaring startup ready. Existing GPU-query completion, five-second guard, startup cancellation and hidden/private output boundaries remain.
5. Transfer the prepared handle and exact previous row/shape into the existing live light cache. Live packets still pass their ordinary validation. Their byte-identical dome row/shape does not trigger destruction/recreation; native scene slots0/1 continue normally.
6. Existing live-light cleanup owns the transferred handle. If not transferred, the diagnostic preparation object destroys it during unwind. No second live dome is submitted.

This tests actual runtime resource preparation, not just an early CPU file read or another arbitrary frame count. The five measured API-preparation intervals were **14.541–70.511 ms**, all before activation. No timeout was extended to force success. Cold security stalls longer than the existing preparation guard are not qualified by these trials.

All five prepared trials have byte-identical early and live shape packets and no later `LIGHT_TYPE_APPLIED slot=2` recreation. Accepted lighting, material, image/quality settings and `rtx.conf` match the stable-path control exactly. Canonical captured geometry, UVs and original image files remain unchanged.

## Trial ledger

| Run | Variant | First-live query | Result |
| --- | --- | ---: | --- |
| `20261102-062238-816284-return-fixture` | Stable file only; 60-second startup idle | 10.351 ms | Standard 600-frame fixture pass |
| `20261102-062525-655556-return-fixture` | Prepared/transferred dome; 60-second idle | 6.075 ms | Later material-publication failure |
| `20261102-062721-687505-return-fixture` | Prepared/transferred dome; immediate activation | 7.592 ms | Standard 600-frame fixture pass |
| `20261102-062924-792301-return-fixture` | Prepared/transferred dome; 60-second idle | 7.456 ms | Later material-publication failure |
| `20261102-063328-190389-return-fixture` | Same; bounded mapping observation on first publication error | 7.869 ms | Later material-publication failure |
| `20261102-063837-330068-return-fixture` | Same; bounded Windows ownership observation on first publication error | 6.391 ms | One publication denial recovered; standard 600-frame fixture pass |

These use the standard three-owner/two-asset/shared-instance fixture, so the old eight-family final-check mismatch does not apply. In failed cases the GPU job still exited zero during cleanup, but that does not make the failed overall fixture a pass. The mapping/ownership probes perturb service timing; do not use those trials as clean comparative performance benchmarks. No new SFC run was requested.

## Separate publication failure: precise new evidence

The supervisor catches every `PermissionError` as “sharing-busy” and raises after five seconds. Narrow exception observation shows the new failures are specifically **WinError5 / access denied**, while atomically renaming `mod.usda.pending` over the active aggregate `mod.usda` in `publish_remix_revision`. They are not independently established WinError32 sharing violations, five-second GPU waits, or bad dome inputs.

The repeat trial retained 32 of 93 errors; the mapping-observation trial recorded 39 errors. The final successful trial had one denial that recovered. A control using the exact unchanged publisher on a directory never loaded by Remix completed 100 publications with zero errors in 63.318 ms. That narrows the conditions; it does not prove which process/filter denied the live rename.

At the first denial, a metadata-only probe verified the exact prototype renderer path, then inspected at most8192 memory regions/250ms for a mapping of the exact target file. No matching mapping was found. The last query also asked Windows Restart Manager for resource owners and received an empty list. No shutdown/restart operation was requested. These negative snapshots do not rule out ordinary file handles, a short mapping elsewhere, filter activity or races. Do not claim USD memory mapping, Defender or a particular lock owner is proved for this rename error.

The probes are local diagnostic helpers, not runtime features. Their timings and bounded result packets are retained. No additional kernel trace or security exception was introduced.

## Limits and next exact action

This is a tested **prototype**, not a production fix. It handles the current configured white project dome, not every custom HDR environment, a native light switched to dome, live configuration mutation, device loss or the full cancellation/failure campaign. Before promotion, implement explicit configuration/session identity and prepared-resource ownership in the normal startup contract, with focused readiness/cancellation/mismatch tests. Do not introduce a bootstrap dependency on ship asset SHA or game-side attachment.

The material publisher's five-second fatal policy is a separate operational blocker: an unavailable enhancement update should preserve the last valid material/geometry and retry under the existing bounded work/storage policy rather than terminate the whole renderer. Any change must retain explicit pending/failed publication evidence; do not claim enhancements applied without acceptance. Investigate the denied rename before choosing a different publication mechanism. Do not silently change USD layout, material content, appearance or renderer architecture.

Correct physical-hull capacity before the next large fleet checkout. Keep the normal host unchanged until the promoted path and relevant qualification receipts are complete. The full standalone/fixture passes here establish a workable supported direction, not universal low-latency/security behavior or sponsor gameplay acceptance.

`summary.json` records all trials, matching settings, resource preparation, handle reuse and the unchanged production host. Source variants, binaries, bounded publication observations, CPU control and metadata probe remain in run269. No owned renderer/game processes remain. Documentation/status/tools reference updated; changes unstaged and uncommitted.
