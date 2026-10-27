# Run197 — Remix mapping is part of the first textured submission



Date:2026-10-26 America/New_York. Parent93e8dba; accumulated Run194–197 work remains unstaged/uncommitted. No SFC launch by Codex, normal-runtime promotion, API unpark or milestone claim.



## Direction and implementation



Sponsor separated two contracts: correct mapping on the first base-textured ship, enhanced shading/materials later. The known Remix image-origin conversion now lives in `tools/d3d9_proof/remix_coordinates.py`. The progressive Remix worker derives bottom-row-first BGRA uploads before the first native asset admission. The existing enhanced DDS encoder delegates to the same origin policy. Conversion happens once per constructed backend image, never cumulatively to an original. Raw capture geometry/positions/normals/UV/group/triangle bytes and original image files remain unchanged.



`tools/remix_runtime/parallel_assets.py` uses corrected upload bytes for both base catalogs and native material hashes. Enhanced maps are generated from canonical decoded images, then converted once at DDS encoding; they are not derived from already corrected BGRA. Base asset identity is versioned `sfc.base-asset.v2.remix-image-origin-v1`. The derivative scene manifest records the conversion. Original content hashes remain provenance. Converted uploads count against the existing256MiB working cap; row views avoid a second full row-copy buffer. No callback work, renderer waits, output resizing, material setting changes or new loader were introduced.



The neutral scene exporter/plain D3D9 replay retains original data. This is a Remix backend rule, not a universal D3D9/D3D12 rule. A future adapter applies only its own verified conversions. No model-axis, normal, winding or camera repair.



## Reference checks and checker findings



`qualify_async_material.py` derives expected converted base images from the accepted immutable ZIP and derives renamed material IDs from those exact bytes. All381selected files remain checked: enhanced DDS are byte-exact, stages differ only by deterministic binding-name conversion, geometry/UV/group bytes stay exact. No new output is declared its own golden reference.



One late replay chose the shared-model owner31/revision63 as canonical before owner3/revision3. This is valid sharing, not a changed mesh. The older checker incorrectly required one historical owner's pose. It now accepts only exact model/view/projection/viewport bytes declared in `fixture-rows.bin`, with bounded sequence and unchanged accepted geometry. Tests reject unexplained translations. An isolated-process import-path regression in this check was found and fixed before readiness; a subprocess regression now covers it. These checker rejections preserve useful successful GPU evidence; they are not SFC/render failures.



Exact changed files for mapping/checking: `tools/d3d9_proof/remix_coordinates.py`, `tools/d3d9_proof/material_binding.py`, `tools/remix_runtime/parallel_assets.py`, `tools/remix_runtime/qualify_async_material.py`, `tests/test_remix_coordinates.py`, and the D3D9 README. Prior Run194/195 implementation remains.549main Python tests pass, including asymmetric3-row color/alpha initial-versus-enhanced mapping, unchanged canonical inputs, actual material-hash bytes, bad layouts, shared-owner pose rejection and clean-process import. See final evidence JSON for final build/GPU/qualification paths.



## Resumed enhanced-update investigation — still open



Run196's actual game result remains accepted as fast base-first startup with a missed initial enhancement. Metadata-only notification experiments were withdrawn, not reintroduced here. Correct initial mapping does not establish completed enhanced-material installation.



A process-only probe exercised the existing private triangle warm-up with replacement assets enabled before the already-ready renderer waits for discovery. This is not a production setting or a new warm-up implementation. Its first replay and a purported zero-emission comparison completed without new models. Audit found the first zero-emission probe changed the reported config after Pipeline had already captured its values: generated shaders still had intensity5. Therefore its5.72/255image difference is NOT an emission-positive/negative proof. The diagnostic was corrected to update its own Pipeline values and verify generated material values; original user settings never changed. Do not infer reliability from image difference alone or a returned frame.



Pinned public NVIDIA USD source registers file callbacks after applying initial processing and supports dirty-material async rebuilds. Package/public-source instruction parity remains unverified. No supported USD reload/material-ready ACK was found in the pinned C API. Private warm-up and repeated metadata notifications remain diagnostic-only; no runtime internals patched. See [pinned implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_mod_usd.cpp).



## Bounds, cleanup and state



Existing20GB aggregate and launch reservations retained. Capacity rejections occurred before graphics startup and were resolved by SHA-verified ZIP archival of completed generated asset duplicates; no lower cap, raw packet loss or changed client files. Existing normal qualification is replaced only after a new normal fixture passes. Logs, screenshots, raw geometry packets and archive receipts remain. Capture/transport/90s gameplay/285s workflow bounds unchanged. No active game or manually managed server expected after standalone completion; source-qualified launcher receipts must be renewed for any further implementation edits.



**Next exact action:** finish a deterministic reproduction of the actual long-idle/early-publication missed-enhancement case using the retained live KFF/FCA capture and validated material control; keep initial mapping independent. A sponsor run may verify the first-frame mapping, but is not requested merely to rediscover the delayed enhancement.



## Final-source qualification



Matching candidate x64/O2/WX build and native-light checks PASS. Normal fixture040602renewed through the actual normal adjudicator. Candidate initial040746and late040900both passed the actual optional-checkout adjudicator:381reference files each with only specified conversion/known-frame differences; four owners/three distinct assets; native HUD/scene exact, state errors0, resize/recreate and normal owned exits. Initial600/600checked delivery and zero post-start omissions; late595/600and three isolated post-start omissions(longest1). Counters describe different whole/settled windows and are not contradictory. No rejected/invalid/partial assets. Actual normal and optional read-only game preflights PASS including audit-data serialization. No SFC launched; actual gameplay mapping confirmation pending.



The first valid zero-emission diagnostic was041031: both generated material reports actually contain0, compared with the positive's5. ROI mean RGB difference7.598/255and3421pixels differ by more than10. This supports a material response in that standalone setup, not a runtime installation ACK or a fix for the missed live update. The earlier invalid zero control is preserved and explicitly excluded. Private warm-up remains unpromoted.



Useful generated evidence was SHA-verified ZIP archived before duplicate removal. Final qualified candidate assets are recoverable from their ZIPs; their result files/digests, raw packets, screenshots and logs remain. Current normal040602remains loose; superseded normals were archived only after replacement qualification. See `docs/reconnaissance/evidence/20261026-remix-initial-mapping.json` for archive names/hashes/receipts. No stages/commits/pushes, no user-config edits or accepted-installation changes.


### Final long-idle diagnostic

Replay041129waited30safter existing renderer readiness, with precomputed byte-identical material pieces, and no later model arrival. It produced both ship snapshots and596/600settled returned frames. Generated materials were consumed during this replay, so the live missed update was not reproduced reliably. Native fixture exited1because its bounded duration did not reach device recreation(resized1,recreated0), while native renderer job exit0/stop_reason0/remaining_owned_processes0(the top-level host/fixture exit fields are1). This is a PARTIAL diagnostic with useful material/pixel/timing evidence, not a qualified graphics PASS and not an SFC failure. No timeout/budget was relaxed. Current qualified initial/late launcher receipts remain separate and valid.

The next investigation must distinguish file notification, stage reload, and installed material state under actual activation timing. There is no evidence-backed new production notification fix to ship yet. The mapping correction is ready independently.
