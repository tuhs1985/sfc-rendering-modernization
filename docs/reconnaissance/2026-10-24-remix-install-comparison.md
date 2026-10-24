# RTX Remix installation comparison and cleanup disposition

Date:2026-10-24. Read-only local inspection; no deletions, moves, uninstalls, settings changes or renderer migration authorized/executed. Scope: compare the newly managed Toolkit and the old portable development Toolkit; determine safe cleanup steps.

## Inventory

| Item | Exact path | Version / measured file bytes | Decision |
| --- | --- | --- | --- |
| Managed Toolkit | `C:\Program Files\NVIDIA Corporation\RTX Remix` | `1.6.1-0+1-6-1-0.30549.7d65b007.gl`;9,375,146,294bytes/43,344files (~9.38GB) | Keep as normal Toolkit |
| Portable development Toolkit | `C:\Project\RTXRemix` | `1.6.0-dev+main.30229.3f23f80a.gl`;4,914,104,839bytes/42,472files (~4.91GB) | Candidate to retire after preserving changes and resolving legacy-tool dependencies |
| Original portable download | `C:\Project\RTXRemix-Standalone\download\rtx-remix-1.6.0-dev-main.3f23f80a.zip` |2,118,847,088bytes (~2.12GB) | Keep initially as vendor rollback source |
| Saved SFC offline jobs | `C:\Project\RemixJobs` |130,965,303bytes/2,287files (~131MB) | Preserve; includes accepted source/preview provenance |
| Project-controlled game runtime | `artifacts/d3d9-intercept/deps/remix-1.5.2/.trex/d3d9.dll` and separately used return-test dependency tree | Pinned Remix1.5.2 | Keep; NOT either Toolkit installation |

Decimal GB used above; Toolkit+portable+download total16,408,098,221bytes (~16.41GB), excluding jobs and separate project runtimes. Metrics are compression-adjusted file bytes from Windows GetCompressedFileSize, not exact rounded cluster allocation or a guaranteed reclaim figure. Full stat file IDs were used, skipping reparse points. Both Toolkit scans had zero errors/reparse entries; no cross-install shared file IDs found. These are real separate files, not two names for one junction/hardlinked install.

Raw bounded inventory: `artifacts/d3d9-proof/install-audit-20261024.json`, SHA256 `666D146070AB0D6F316602FF0C92F4DF9A0F9B0B515C54EB0D39EB293DB5B798`.42,309same relative file paths;38,364also have the same byte size. Size equality is NOT proof of equal content.

Managed registration: NVIDIA RTX Remix1.6.1.0, normal NVIDIA Installer2 uninstaller. Desktop/Start Menu Remix shortcuts point to the Program Files launcher. No active `kit.exe` observed during inspection; no application launch performed. Both Kit executables have valid NVIDIA signatures and identical SHA256, but app manifests differ. Matching Kit engine binary does not make the two Toolkit versions identical. Model-ingestion schema SHA256 matches across these installs.

## Why the new copy is larger

Largest top-level differences: old `exts`2.874GB vs new5.590GB; old `deps`3.68MB vs new1.748GB. Extension cache stays~1.83GB in both. The new package contains additional large renderer payloads, including architecture-specific DLLs and multiple runtime locations. Similar-sized DLLs are not automatically duplicates: sampled new `exts/lightspeed.hydra.remix.core/deps/hdremix/d3d9_x64.dll` and `deps/remix_runtime/runtime/.trex/d3d9.dll` have different SHA256 despite equal282,883,696byte size.

Do not manually strip managed extension/runtime DLLs, ARM payloads or NVIDIA Installer2 folders to shrink it; that would modify the vendor install and could break component loading/repair. No manual cross-install deduplication is proposed.

## What still depends on the old Toolkit

Current in-game `tools/remix_runtime/live_owner_timing.py` names the project-controlled1.5.2runtime; current multiship host/bridge does not need either Toolkit. The normal driver, capture, fresh-scene assets, materials and returned-image connection must not be redirected to the new Toolkit's bundled runtime as a cleanup side effect.

Historical dependencies:

1. `tools/remix_ingest/run_mesh_preview.py`: defaults old Toolkit/jobs, rejects whitespace in Toolkit path and pins the exact old VERSION. Program Files path and1.6.1both fail these checks as currently written.
2. `tools/remix_ingest/run_remix_ingest.py`: defaults old Toolkit/jobs, checks old app revision/schema, has the documented whitespace constraint. Schema alone matching does NOT qualify the new app.
3. `tools/d3d9_proof/inspect_intercept.py`: imports USD libraries from the old Toolkit's `extscache/omni.usd.libs-1.0.3+6312fa25.wx64.r.cp312`. Same named library directory exists in managed Toolkit, but no parser-import compatibility test or path migration performed.

One old preview unit test names the old root as a fixture. Historical documentation intentionally retains old locations. Do not bulk replace historical evidence paths.

Removing the old folder without addressing these dependencies would retire those offline preview/inspection entry points. It would NOT silently stop the current in-game renderer. Choose explicit retirement with historical code/evidence preserved, or a separately validated migration; do not bypass version/space checks by simply editing one path or adding a junction.

## Data and recovery safeguards

Both Toolkit `rtx-remix/mods` and capture content scans found no saved USD/image/material work candidates in their respective roots; folders alone are not project backups. Most SFC work is in separate RemixJobs/repository artifacts. Preserve ALL RemixJobs, particularly accepted import `20261015-231057Z-19b131ce` and subsequent captured texture/preview evidence. Shared per-user NVIDIA/Kit preferences/caches were not inventoried and are NOT cleanup targets.

Retained original ZIP matches published SHA256 `83F3E5C2B6094CCF5084EE3AE2652D91D6F43F3F729274519741C130FDAFB781` from the original acquisition record. A read-only full original-file CRC comparison was attempted with180s bound and stopped with `RuntimeError: ZIP audit duration bound` before producing a complete difference manifest. That does NOT certify the current portable folder matches its ZIP; local patches/generated files may exist. No source file changed, no extraction/deletion/backup occurred. Original ZIP alone cannot be assumed to preserve local changes. One-off audit scripts live under ignored artifacts; they are not pipeline additions.

## Recommended cleanup sequence — not yet executed

1. Keep managed Toolkit1.6.1, all saved SFC jobs, current pinned1.5.2runtime and existing research/test evidence.
2. Decide explicitly whether to retire the historical Toolkit launchers or qualify them against managed1.6.1 (including whitespace handling and USD parser use). No game-runner migration needed.
3. Preserve the old folder's local changes. Either complete a checkpointed vendor-ZIP difference audit and verify a small overlay archive, or make/fully verify a complete archive before any removal. Record files/hashes/restore instructions; do not claim the attempted partial comparison is enough.
4. After cleanup authorization, close any Toolkit using the old root, recheck exact resolved target `C:\Project\RTXRemix`, then remove ONLY that retired extracted copy through an approved recoverable/verified-backup workflow. Approximate reclaim4.91GB minus any newly stored overlay/backup. Keep the original2.12GBZIP initially; a full newly verified backup could instead support consolidating redundant backups later, as a separate exact-target decision.
5. Do not delete RemixJobs, pinned runtime dependencies, per-user preferences or managed package components. Do not update the current SFC rendering baseline or loosen its qualification locks for disk cleanup.

No build/game/GPU test needed for this read-only inventory. Before an actual migration/removal, perform its relevant validation and record changes separately. Cleanup authorization is still required; nothing was removed in this run.
