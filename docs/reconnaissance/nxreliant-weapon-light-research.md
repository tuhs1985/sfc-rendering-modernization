# nxreliant contribution — weapon rendering and entity lights

**Review finalized November 7, 2026.** All fourteen source sections have a
recorded disposition below. This completes ingestion and relevance review;
it does not imply independent validation of every contributed finding.

Ingested November 7, 2026, from research supplied by the sponsor and attributed
to **nxreliant**, working on an unrelated SFC project. The document itself says
“Prepared for: Tuhs”; authorship beyond the sponsor's attribution is not inferred.

[Unmodified supplied document](contributions/nxreliant/2026-11-07-Tuhs_SFCOP_Research.txt)
— SHA-256 `3A4E40854EFBAF6BCA95202B15EB724E1E28E2A202FC3913F64EB5CBD1C7E150`.
The source contains research notes, not executable or game-image payloads. Its
recommendations are research input, not authorization to patch the game or add
hooks. No runtime, configuration, materials or original assets changed.

## Compatibility and evidence status

The contribution names **StarFleetOP.exe 2.5.6.5** but supplies no executable hash,
disassembly, byte signatures or raw runtime records. Its “confirmed” labels mean
confirmed by the contributing research, not independently verified here.

**Sponsor clarification:** nxreliant is actively updating the executable and his
client is one revision ahead of ours. Treat it as a separate modified build.
Address differences are cross-build mapping questions, not findings that his
research is incorrect. This clarification is sponsor-provided context; it does
not supply an external binary hash or establish which changes moved each path.

Our existing pinned client/disassembly is labelled **2.5.6.4**, client SHA-256
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Matching addresses are useful corroboration; they do not establish cross-build
compatibility. Keep VAs, file offsets and interface-relative slots distinct.
Do not add these entries to the confirmed community patch/offset tables.

We performed a narrow read-only check of eight relevant disassembly ranges:
**98 instruction encodings match the pinned local PE**. This qualifies those
listed local instructions, not every semantic label or the external build.
[Versionable check record](evidence/20261107-nxreliant-ingestion.json).
The local analysis script is `artifacts/review_nxreliant.py`; raw disassembly and
the executable remain outside Git. No game, renderer or discovery trace ran.

## Where it adds to our corpus

| Topic | Contribution and local relationship | Status / use |
| --- | --- | --- |
| Existing light endpoint | `0x006A9AB0` copies descriptors; `0x006A9C40` enables them | Already qualified locally in the [native light map](2026-10-17-native-light-state-map.md). Corroboration, not new integration. |
| Entity → descriptor | `0x00420447` writes native type 5, copies entity `+0x34/+0x38/+0x3C` to descriptor `+0x10/+0x14/+0x18`, copies entity `+0x220/+0x224/+0x228` to descriptor `+0x1C/+0x20/+0x24`, writes `20.0` at `+0x28` | Locally corroborated instruction flow. A useful upstream relationship beyond our already-working bank consumer. Live weapon owner/slot joining is still unproved. |
| Drifting descriptor | `0x004209DA` has analogous copies with `5.0` at descriptor `+0x28` | Locally corroborated. Does not establish physical emitter radius, duration or brightness. |
| One-light provider | `0x0042167B` returns 1 | Locally corroborated instructions. Reported seeker vtable `0x007978FC`, slots `+0x50/+0x54` still require local class/vtable qualification before use. |
| Gatherer | Reported `0x004BA357`, callsites `0x004BA71F/0x004BA7AB` | Existing disassembly contains the entry and direct calls. Full iteration, entity filtering and owner-to-slot assignment remain external leads; not included in the 98-instruction qualification. |
| Projectile appearance vs illumination | Weapon artwork/particle RGB and entity-light RGB are separate sources | Consistent with our separate effects/material/light paths. Preserve this distinction in future weapon-specific enhancements; do not sample light colour from a bitmap. |
| RGB setter | `0x006AD340` stores renderer RGB at `+0x1F08/+0x1F0C/+0x1F10` | Stores locally byte-checked. Reported slot `+0x130`, texture slot `+0x134`/setter `0x006AD3E0` and full vertex-consumption chain are additional qualification leads. |
| Phaser colour storage | Constructor `0x004FFE06` copies incoming values to effect `+0x40/+0x44/+0x48` | Locally corroborated. Exact colour argument semantics and runtime ownership still require their caller chain. |
| Photon dispatch | Calls at `0x0041C6A9 → 0x00500F26`, `0x0041C6B3 → 0x004F66D9` | Locally byte-checked calls. The external visual IDs 15/16/17 and normal/fighter sharing are leads pending the full local dispatch mapping. |
| Effect draw paths | Photon `0x00500C30`, HeavyPhoton `0x004F63E3`, Fusion `0x004F4719`, Hellbore `0x004F6F1D`, Plasma `0x00501FED` | Already present in our RTTI-backed [executable inventory](rendering-executable-inventory.md). Particle helpers and RGB callsites add search leads, not new live coverage. |
| Photon resources | `photons-2.bmp` cache `0x00857FC4`; heavy-photon image/cache | Normal literal/cache and heavy literal already documented locally. External 4×4, 512×512 indexed-atlas description has no supplied asset hash; do not assume it matches every installed image. |
| Source identity | Entity `+0x1C4` reported as `fFromID`; lookup around `0x004249C0`; source race/class-prefix `+0x86C` | High-value external lead for joining light/projectile to firing unit. Not a qualified owner epoch, carrier relationship, model identity or safe dereference contract. |
| Impact classification | `0x004204B2 → 0x0042135F` reported as `tEntity_HellboreBlast`, not ordinary photon impact | Retain as an explicit caution. Disassembly contains the call; class attribution and other impact chains remain unverified in this ingestion. |

## Cross-build address differences to retain

Two supplied addresses are **not instruction starts in our pinned client**:

- Reported phaser drawing routine `0x004FFE40` falls inside the instruction at
  `0x004FFE3C`; local implementation starts `0x004FFE39`. Our existing inventory
  correctly distinguishes virtual entry `0x00500312`, thunk `0x00500306` and
  implementation `0x004FFE39`. Do not replace those with the contributed address.
- Reported conversion routine `0x0041C788` falls inside the instruction at
  `0x0041C787`. It is not an approved local function/hook boundary. The claimed
  byte-to-float conversion needs its actual enclosing path established.

These observations do not prove nxreliant's different build is wrong. They do
show why external addresses must not be copied directly into our integration.
We have not examined his executable, so do not attribute either difference to
a specific edit or assume a uniform address delta between revisions.

The reported legacy editor offset `0x437600` and normalization-table explanation
remain external/version-specific. Our hash-qualified editor landmarks retain
their own provenance; no older table is reclassified from this note alone.

## How to use this research next

1. **Weapon-specific lighting attribution:** locally qualify the seeker provider
   vtable and gatherer path, then join entity/source identity to the descriptor
   and actual bank slot/frame. Reuse existing light observations first. Only if
   they lack that upstream identity should a bounded opt-in correlation capture
   be proposed. The functional bank bridge already works and needs no redesign.
2. **Weapon rendering support:** follow our existing effect inventory and enrich
   it with separate core/particle texture, RGB and animation state. Keep native
   impact/shield/explosion families separate until creation paths identify them.
   Shared atlas names do not prove UV ownership or a universal weapon renderer.
3. **Keep unresolved fields unresolved:** entity type/reference fields,
   source-owner/carrier relationships, exact RGB defaults, `0x1C0` allocations,
   sixteen `0x18` particle records and atlas metadata are useful retained leads,
   not approved structure definitions or patch sites.

The source also preserves preliminary disruptor helpers, weapon audio mappings
and safe binary-inspection guidance. They remain available in the original;
audio is outside our current renderer scope. No assets, weapon mechanics or
per-weapon enhancements are implemented by this ingestion.

## Complete source disposition

| Source section | Corpus disposition |
| --- | --- |
| 1 — Overview | Retained as contributor context. Separating artwork, renderer colour and entity lights agrees with the existing family/lighting split. |
| 2 — Photon rendering | Main draw addresses cross-reference the qualified inventory. Dispatch calls locally checked; category IDs, factory allocation and particle layout remain explicit external leads. |
| 3 — Weapon entity | Position/RGB copy flow locally checked. Type, visual-reference and source-ID meanings remain externally reported until their local callers/lifetime are qualified. |
| 4 — Renderer RGB | RGB stores checked locally; retain graphics slot, texture-selection and vertex-colour-consumer leads. Do not infer emitted light RGB from this state. |
| 5 — Textures/animation | Existing photon literal/cache evidence cross-linked. Preserve external atlas/file-offset details without assuming installed-asset equality or changing original images. |
| 6 — Dynamic illumination | Descriptor copy paths and one-light return checked. Gatherer/provider-vtable/weapon-to-slot correlation retained for future work. Reported RGB defaults and range values do not establish physical Remix power or shape. |
| 7 — Phaser/source identity | Constructor stores checked; local implementation entry retained. Source owner/race lookup and legacy editor-table interpretation remain build-specific leads. |
| 8 — Other weapons | Fusion/Hellbore/Plasma draw entries already in inventory; disruptor helper and family-specific RGB paths retained. No new universal effect support claim. |
| 9 — Impacts/explosions | Retain separate impact-family warning and reported HellboreBlast identity. Call existence alone does not establish class, runtime effect or atlas-region ownership. |
| 10 — Audio | Preserved in original for reference; no audio work or rendering inference derived from it. |
| 11 — Executable compatibility | Applies as research guidance, consistent with existing hash/byte/PE-mapping discipline. Does not authorize patches, structure expansion or additional hooks. |
| 12 — Recommended investigations | Reconciled with the three follow-ups above; current live light consumer stays intact. No extra gameplay capture requested by ingestion. |
| 13 — Confidence/limitations | Contributor confidence retained verbatim; local corroboration is labelled separately. Unverified claims are not promoted into qualified hook/patch tables. |
| 14 — Conclusion | Added as corroboration and upstream investigation leads, without changing release scope or current engineering priority. |

## Finalization checks

- Archived source is byte-identical to the supplied attachment; its hash is
  retained in the review and machine-readable evidence.
- Curated evidence accounts for 98 checked instruction records across eight
  ranges, with the existing pinned client and disassembly hashes.
- Review links resolve to the preserved source, native light map, executable
  inventory and evidence record. Related family/light/inventory documents link
  back here; repository handoff/status and Obsidian tracker record incorporation.
- Existing implementation work is preserved. No runtime changes, live capture,
  staging, commit or push is part of this finalization.

## Current priority

This enriches the research corpus without changing the engineering queue.
The prepared live FCA debris checkout remains next. The new light-ownership
leads should be consulted when refining weapon integration or exposing a more
complete backend-neutral effect/light interface. Universal weapon coverage,
exact physical light conversion and cross-build compatibility remain open.
