# Run286 — reversible live damage textures

Status: IMPLEMENTED / standalone GPU insertion qualified; SFC gameplay checkout pending.
Local work began November3; fixture folder names use November4 UTC. Changes remain unstaged and uncommitted.

## Source and behavior

Build on Run284, not a new discovery campaign. The pinned client selects an absolute damage tier from its current scalar: below0.125 none, below0.375 light, below0.625 medium, otherwise heavy. Sponsor confirms this state can reverse. Every frame uses current state; heavy→medium→light→none works without retaining a maximum. Initialization/reentry is not a hit event. Future effect triggers must distinguish damage increases from repairs; no per-hit location or weapon attribution is proven.

`tools/scene_bridge/damage_state.h` carries renderer-independent owner/revision/scalar/family/qualification. The existing ship render path derives its scalar from the simulation structure returned by virtual+0x88:1−float((current−base)/(maximum−base)). This implementation reads only qualified simple accessor code; it never executes an unknown virtual method. Its result must agree with the real model argument before that owner's persistent damage state is accepted. Complex accessors remain unsupported; the first gameplay checkout must qualify this real relationship. Unsupported owners remain native in this opt-in checkout. This is a specific compatibility limit, not universal damage support.

Capture retains original positions/normals/UVs. Optional header words27..29 carry native model bounds and damage-projection version. An asset worker constructs a SEPARATE damage UV channel using0042EB52..0042EE28. All19,110 F-CA captured damage UV pairs match bit-for-bit; source packet cf04df68c6656ef8399bb8785881500abcfbf65dac75eaad708c3df3bbb7296f and Run284 damage mapping9c0a6c9de9303e2c1c2ab23af036512b9830d282b95aa48f9be31eea7e589f4e. The large-model branch is statically supported but not separately gameplay qualified.

Coherent scene wire version3 appends per-owner damage state inside the existing checksummed snapshot: owner/revision mismatch is rejected and the decoder/both endpoints must be rebuilt together. FrameSlot103488B, Store959040B, existing mapping region unchanged. Ordinary damage-off captures keep their previous bytes and replay version1; damage-enabled local replay version2 adds8B UV per corner. Shared-memory reservation includes those bytes.

## Remix adapter

Default-off `-DamageTextures` on the existing native multi-ship launcher. Nine shared original primary/SI pairs cover standard/starbase/organic and three severities. Prepare/cache before host activation; no image work in SFC callbacks. Each256×256 pair retains source hashes/dimensions and group-family assignment in `gpu/damage-provenance.json`. All original files remain unchanged.

Exact RGB black receives derived alpha0; all other RGB values remain unchanged with alpha255. The ordinary hull's black lettering stays opaque. Adapter-specific row conversion remains in the Remix layer. Cached separate UV vertex buffers submit an ordinary D3D9 decal draw; a repaired undamaged state submits no decal. Per-owner state stays independent even with shared geometry/textures. Alpha testing uses reference8; no custom geometry offset or CPU screenshot compositor.

Use NVIDIA's existing `rtx.decalTextures` category and `rtx.enableDecalMaterialBlending`, rather than a new decal renderer. Pinned source:[rtx_options.h](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_options.h). [Official category reference](https://docs.omniverse.nvidia.com/kit/docs/rtx_remix/latest/docs/toolkitinterface/remix-toolkitinterface-categories.html). Legacy alpha state is supplied by D3D9 and honored by AperturePBR_Opacity. The SI contribution reuses our existing provisional primary×SI material policy; the exact native companion lighting equation is NOT newly proven. No appearance settings changed.

## Validation and limitations

- 673 Python tests PASS;26 damage-source checks on both32/64bit;101 scene wire checks on both architectures. Existing native gate1216/cohort193 per architecture, hook recorder82, native flush12300 and corner-copy checks passed during integration builds.
- Two stale Python assertions were corrected to exercise today's ReplaceFileW abstraction and existing native fixture reservation, without changing publication behavior or budgets.
- Actual ExtraFrame damage fixture `20261104-041128-562113-return-fixture`:600frames,584commits,1752draw receipts; all3owners observed, two different captured assets/shared third owner; native depth/text pixel mismatches0, state errors0, both processes exit0. Bounded offline-only BGRA snapshots show undamaged→heavy→repaired at the same pose. Local comparison:`artifacts/player-replacement/run286/damage-reversal.png`.
- Damage-off regressions:Strict `20261104-041211-409869-return-fixture`, ExtraFrame `20261104-041303-502143-return-fixture`;600frames each, native pixel/state errors0, all3owners, exits0. The versioned receiver was rebuilt; an earlier attempt with an old receiver correctly failed to authorize insertion and was retained as partial evidence.
- Median frame period damage ExtraFrame16.8834ms versus damage-off ExtraFrame16.9255ms; p9522.2352/22.4335ms. These include deliberate deadline overruns. Damage fixture uses static poses and three bounded readbacks, baseline uses moving poses; these are regression observations, NOT a causal claim that damage costs nothing or speeds rendering up.
- No SFC gameplay launched for these tests. Actual live source/accessor qualification, damage appearance across gameplay/repair, other families, destruction/break models and alpha readiness remain pending. No alpha-release completion claim.
- Normal path has no damage readbacks or continuous dumps. Nine textures2,359,296B GPU plus one cached32B-per-corner damage VB/8B UV channel per asset; accounted against existing256MiB residency. Library original/derived output128MiB; warnings64MiB. Existing90second tactical/five-minute workflow/output/evidence limits remain.

## Cleanup and next action

Old completed generated inputs compacted recoverably to Run286 `historical-performance-inputs.zip` and `closed-game-generated-inputs.zip`. Each member was decompressed and SHA256-compared BEFORE removing its loose generated copy. Receipts preserve exact relative paths, lengths and hashes. Native captures, result/log metadata, game installations and existing archives retained. About1.07GB logical space recovered;20GB evidence allowance unchanged.

Next: use the existing F-CA fixture, allow hull damage, switch cameras, and continue normal play. If repairs occur, the layer must retreat. No need to wait for first-hit lazy mapping; mapping/materials are prepared beforehand. Review persistent damage source agreement and per-owner insertion evidence before enabling by default. Launcher qualification/preflight must pass before requesting gameplay. No commits requested.

Final preparation: existing native-light observer offline qualification refreshed after header changes; native cohort qualification refreshed from the three passing fixtures. Read-only `run_return_game.py --native-insertion-policy ExtraFrame --native-all-ships --pipeline-mode performance --damage-textures` preflight PASS. Both pinned client hashes unchanged; no owned renderer/receiver/fixture/game remains. `git diff --check` PASS.
