# Run261 — Transient game lights prepared

Sponsor requested adding lights driven by SFC position, colour, shape where supported, intensity and on/off state while away. Implemented the existing light-bank connection rather than creating another effects renderer. [Contract](../reconnaissance/effect-light-bridge.md).

## Delivered

- Frame-keyed native type1/type5 positional sources from slots2..63, captured before the existing persistent-scene wake-up. Four bounded raw memory cells plus a checked Remix policy cell reuse18560bytes within the existing16MiB mapping. No new hook or per-frame disk/SDK operation in SFC.
- Exact world position/RGB/native activation, with full-rate observation instead of the old5Hz discovery sampling. One bank per scene avoids multiplying the same light for every ship. Native gate/first-disabled-prefix and configuration OFF retire the lights; stale source-frame data never becomes persistent GI.
- Existing public Remix sphere-light adapter support, explicit configurable sphere approximation, effect/global intensity and colour multipliers, radius and per-slot overrides in the same lighting file. Native range retained, not guessed to mean power or emitter shape. Type5's original shading/falloff is not reproduced.
- Existing scene slots0/1, project_fill, main light angles, materials/images, camera, native insertion and early-exit cleanup retained. Original three scene-control dictionaries and global conversion/master values compare exactly to the sponsor baseline; only the transient section was added.

## Evidence and checks

- Nine actual retained active type5 world/local-position comparisons: maximum error4.16522461e-7native units. Read original archived capture without altering it.
-30native tests per architecture: capture/stable-read/used-field validation, unused NaN direction, exact frame/session, motion/colour, prefix/off/on, native global disable, missing frame, bad input, configuration disable and balanced API handle teardown.91focused Python lighting/gate/startup/lifecycle tests pass. Existing native hook82/core1216/membership193/flush12300/corner tests and actual light-observer/worker tests pass.
- Initial development fixture222120 passed; after final conversion-bound adjustment, **Strict222413** and **ExtraFrame222607** are the authoritative actual runtime checks. Both completed600measurementframes/3owners/2unique+sharedassets; two independent colour/depth/text comparisons each had zero mismatches, state errors0, terminalpartial0 and normal fixture/renderer exits. Synthetic moving/pulsing type1/type5 bank, explicitly fixture-only.
- Strict effect summary:584updates,292active slot observations,302changes,invalid0/unavailable0/remaining0. ExtraFrame:601updates,300active,310changes,invalid0/unavailable0/remaining0. On/off is not inferred only from frame delivery: native lifecycle tests check removal, and GPU qualification requires inactive periods as well as active output.
- Measured native commits537/600Strict and583/600ExtraFrame include deliberate deadline overruns. Median presentation intervals16.862ms for both. These do not establish stress performance under many simultaneous weapon sources or100%admission.
- Final host SHA256 `4FB1C90794FE58D1626A39D125CB947244C65A5374C467AAADE5AC5867D7550C`; source receipt rebuilt after Python-only qualification changes with unchanged final binary. Updated cohort qualification requires actual effect runtime summary and native test receipts for effect fixtures. Current launcher preflight passes; no SFC launched and no owned processes remain.
- Appearance baseline scene values remain unchanged. New lighting file SHA256 `A85F4217903FFD544EBCCDC55EF58E25AD1C9F2D9B4E29365A034AC4E0C59939`. Material/image configuration untouched. Closed converted DDS/texture copies archived losslessly with per-file hashes/recovery manifests to preserve the20GB allowance; original captures/client assets/logs remain.

## Next exact action

Sponsor follow-up: prepare targeted light-emission recording for this integration test before requesting gameplay. Current aggregate summaries cannot establish emission/falloff behaviour. Scope and required evidence are recorded in the contract checkout section; recorder implementation remains pending, not silently enabled.

Same `tools/native_insertion/start_native_multiship_session.ps1` launcher. Familiar skirmish, fire weapons and take impacts; observe returned ships' illumination during camera changes. Normal early exit is allowed. No timestamps or new manual setup. Gameplay correctness/brightness/emitter-size checkout is pending; do not call alpha weapon-lighting complete yet. Damage textures and break-model support remain separate alpha items. Changes unstaged/uncommitted.
