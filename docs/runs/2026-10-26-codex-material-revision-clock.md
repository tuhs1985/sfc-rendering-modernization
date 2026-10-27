# Run200 — Windows OpenUSD material revision collision

M1 integration/performance continues. Fast, correctly mapped base display remains accepted; fully enhanced readiness in gameplay remains open. No formal milestone claim, API unpark, appearance tuning or SFC launch by Codex. Parent`93e8dba`; accumulated work unstaged/uncommitted, no push.

## Live finding and supported mechanism

Sponsor confirms Run199 priming did **not** fix roughness waiting for a shuttle. Actual`20261026-052012-553947-in-game`used priming once; private readiness preceded first enhancement publication by approximately10.244s. Recorded normal exit/component cleanup/client-hash checks passed. Private GPU readiness is not an installed-material acknowledgement.

Initial61material definitions remain unchanged in final63; the shuttle adds two definitions. FCA has roughness assigned in58/58groups. It does not correct existing material rules.

**CONFIRMED:** exact packaged`usd_arch.dll`,namespaceOpenUSD25.11,returns the same file timestamp for NTFS times`.1`and`.8`within a second; the next second differs. SHA256:`52dab8f4b87ce09d86ed6f048a7071a55c29071aa7a13981f259d789997f51b5`. Called its public path-based`ArchGetModificationTime`,not a private address. [OpenUSD25.11 Windows implementation](https://github.com/PixarAnimationStudios/OpenUSD/blob/v25.11/pxr/base/arch/fileSystem.cpp#L154) uses`_wstat64`and integral`st_mtime`; [resolver contract](https://openusd.org/release/api/class_ar_resolver.html) explains why unchanged timestamps can skip reloads. The pinned [Remix path](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_mod_usd.cpp#L1360) invokes`UsdStage::Reload`. OS notification is not proof of parsing. Package5a7eec84/public0a6cd5b instruction parity remains unverified; timestamp evidence uses the actual DLL.

## Standalone causal controls

Versioned probes:`20261026_material_refresh_isolation.py`and`20261026_material_refresh_analysis.py`in`docs/reconnaissance/probes`. Saved latest-live KFF/FCA geometry, synthetic fixed poses, actual ordinary-D3D9/GPU return fixture, never SFC. NVIDIA primary-perceptual-roughness view89 removes lighting from the judgement; final grading still applies. Two existing snapshots only. Fixed FCA ROI815,740–1050,915contains clear pixels plus surface:2colors means flat;197is patterned. Patterned output was visually inspected.

| Control | Fixture UTC suffix | FCA first→late colors |
|---|---|---|
| Natural publication, previous implementation |104508-124830|2→2|
| Add unused material;existing images,no new geometry |104559-209587|2→197|
| Publish only after first snapshot |104652-057412|2→2|
| Distinct timestamps,diagnostic override |104940-800962|2→197|
| Constant timestamp after first snapshot |105119-089917|2→2|
| Integrated fix,no timestamp override |105556-985784|2→197|
| Integrated fix,force natural write times to collide |105854-127363|2→197|

All seven fixture/host0,state0,resize/recreation and normal owned exits. First snapshots can precede enhancement installation: no first-base-frame/full-enhancement or subsecond readiness claim. No installed-material ACK. File-only refresh and exact-DLL negative/positive controls discriminate this failure without a new-resource test or manual UI reload. No internal reload interface invented. Other independent failures are not ruled out universally.

## Contained fix and exact implementation files

- `tools/remix_runtime/material_library.py`:new`publish_remix_revision`gives the pending master a timestamp distinguishable at whole-second precision **before** atomic exchange. Keep natural time when already distinct;otherwise previous logical second+1. No sleep,grace window,repeated touch,image copying/decoding or render-callback work. Logical file time can lead wallclock by the rapid-publication count;it is revision metadata,not performance timing. Existing64revision/session bound remains;QPC clocks unchanged.
- `tools/remix_runtime/async_material_checkout.py`:only this opt-in Remix/flat publisher uses the compatibility policy and records receipts. Normal1.5.2/layered/plain/future adapters unchanged. Existing sharing-busy retry retains last good stage and derives its next timestamp from the unchanged target.
- `tools/remix_runtime/qualify_async_material.py`:reject missing,colliding or discontinuous revision receipts.
- `tests/test_material_revision.py`:64rapid revisions,clock ahead,unchanged content/platform newline convention,no waits,busy exchange preservation/retry,bounds,checkout-only routing and negative receipt checks.

Documentation:the two probes,curated`docs/reconnaissance/evidence/20261026-material-revision-clock.json`,this record,HANDOFF,STATUS,D3D9 README and probe definition. Prior dirty work preserved.

## Final validation and limits

557Python PASS;candidate x64/O2/WX build/dependencies and native-light checks PASS. Normal105940graphics/source qualification PASS including native collector tests. Integrated initial110250and late110353:4acknowledged owners/3distinct assets,381selected files match accepted content with the established Remix mapping conversion,no invalid/rejected/partial assets,exact native HUD/scene,state0,resize/recreation,normal owned exits. Both596/600settled,one isolated whole-interval post-start omitted return each(max1). These are not observed SFC frame drops. Both actual read-only launcher preflights PASS.

First restricted standalone attempt failed WinError5 before usable graphics and was retried with normal graphics access. A test initially expected LF bytes on Windows;corrected to the existing platform newline convention,no production newline change. A capacity refusal occurred before startup. Completed generated images were fully decompressed/SHA-verified into ZIPs before duplicate files were removed. An archival batch stopped on a nonzero historical host result;completed earlier archives have individual receipts and were inventoried,the last target stayed intact. No failure relabeled PASS. Curated evidence records full archive inventory/byte ledger. Restore archived generated images before content reinspection. Raw packets,results,logs,BMPs remain loose. Current normal105940and golden222711retained. Existing20GBaggregate/reservations,90s tactical,285s workflow and image/transport bounds unchanged.

No SFC drawing suppression,original client/assets/configuration change,vendor patch,Toolkit startup or new GPU resources. Existing priming idleCPU/earlier memory reservation remain separately tracked asSFC-16. No active owned renderer/receiver remains.

**Exact next action:** sponsor runs the existing multiship launcher with`-AsyncMaterialCheckout`;inspect roughness/illumination before launching a shuttle,play normally and exit on the runner cue. Expect the same correctly mapped textured camera-left copies;enhancements should apply without another-model trigger. Review actual result/cleanup/hashes before declaring the live update issue resolved. No manual timestamps,new appearance settings or additional discovery.
