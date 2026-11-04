# Run287 — damage checkout blocked enhanced hulls

Sponsor: damage-enabled launcher failed to show enhanced ships twice; normal launcher worked. No new discovery capture requested or needed.

## Evidence

- `20261104-042003-396133-in-game`:damage enabled;393render frames,1loaded asset,0hull draws;393unqualified damage observations.
- `20261104-042118-917115-in-game`:damage enabled;218frames,2loaded assets,0hull draws;435unqualified damage observations.
- `20261104-042205-888177-in-game`:damage off;4037hull draws,2owners.
- `20261104-042332-182115-in-game`:damage off;6263hull draws,2owners.
- All four report normal game exit, no supervisor error and unchanged original client. All used process-exit reclamation rather than clean in-process hook unload (`gate_clean_unloaded=false`, controller8); this also occurs in both successful damage-off controls. Do not misreport that as successful hook restoration or blame it on this damage regression. No owned process remains after the runs.

The renderer loaded the textures/geometry; damage-source admission blocked drawing. This was not a model loading/Remix mesh decoder failure. The standalone fixture used supplied synthetic damage state, so its previous success did not qualify the actual SFC statistics getter.

## Root cause and correction

Default simulation creation00448E4B→00448235 installs vtable0079D530. Its slot+88 points to00448B6E, not a bare LEA accessor. That getter performs lazy diagnostic-string registration, then unconditionally returns `this+0x8AC` at00448B9B..00448BA2. Run286's reader rejected the registration prologue as unsupported. The alternate simulation vtable0079CC78 has the already-supported simple getter004443CC→this+0x7C0.

The bounded read-only accessor now recognizes the exact pinned default vtable/function/prefix/return tail and reads `this+0x8AC`. It never calls the getter, registers strings, writes game state or loosens native client identity.29native checks per architecture include this actual default getter form, repaired/undamaged state and rejection of a modified tail. Native model-argument agreement remains required for damage-state qualification.

Decoupled optional damage readiness from base-hull readiness: if damage state is unavailable, retain the qualified enhanced hull and skip ONLY the unqualified decal, counting the missing observation as partial damage support. Do not guess an undamaged source state or latch stale damage. Valid state still follows current light/medium/heavy/none, including repair. Unrelated owner/asset/frame/depth/output matching remains unchanged.

## Regression

Actual ExtraFrame damage fixture `20261104-042929-398884-return-fixture`:600frames,1741insertiondraws,0native pixel/state errors,all3owners,processes exit0. Deliberately made the first owner's damage observation unavailable for100frames: that owner still drew601times; damage unqualified counter100,1189valid decal draws overall. Thus the exact prior condition no longer removes an enhanced hull. Two distinct assets and a shared third owner exercised. Synthetic fixture state remains distinct from live SFC qualification.

Strict damage-off regression and final launcher qualification recorded below after completion. No game assets, appearance settings or normal mode defaults changed. No staging/commit/push. Next sponsor run uses the SAME `-DamageTextures` command, followed by analysis of native source agreement and actual damage appearance.

Storage: three completed Run286 fixture generated-input sets compacted into Run287 `closed-fixture-inputs.zip`;all886entries decompressed/SHA256-compared before removing loose generated copies.325496296B→21887143B. Raw captures, snapshots, logs, results and metadata retained;restoration manifest gives exact relative paths/hashes.20GB allowance unchanged.

Final validation:Strict damage-off fixture `20261104-043107-313560-return-fixture` PASS600frames/all3owners/0native pixel-state errors/exits0;673Python tests PASS;29damage-state checks per32/64bit PASS. Candidate host and native component rebuilt;both timing-policy qualification refreshed from current fixtures. Damage-enabled read-only launcher preflight and git diff --check PASS. Gameplay retry remains pending;no default/settings/assets changed.
