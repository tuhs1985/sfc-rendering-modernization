# Repository map

Start with [contributing](../CONTRIBUTING.md). This map describes current
locations; the [migration roadmap](REPOSITORY_MIGRATION.md) proposes later work.
Classification is not permission to move or delete files.

## Git baseline — November 9, 2026

The foundation branch is `codex/organize-repository-foundation`, created on the
sponsor's instruction from `fe17b8dc49c9682ede22e2f3b25b36a010f4502e`. At creation,
a live `git ls-remote --symref origin HEAD refs/heads/master` check confirmed
GitHub's default branch was `master` at that same commit. This is a dated remote
observation, not a promise about future remote state.

| Reference | Observed state / treatment |
| --- | --- |
| `origin/master` | Existing integration line; live remote verified at `fe17b8d` |
| `codex/organize-repository-foundation` | Current short-lived work branch at that baseline; no upstream configured yet |
| `codex/github-sanitized` | Previous local work branch at the same checkpoint, tracking `origin/master` |
| Local `master` | Older divergent history at `f0751b5`; do not merge, reset, delete or publish automatically |
| Index at branch creation | Empty; no staged changes |
| Other working files | Untracked `.codex-attachments/` and `windows-memory-audit.md`; unrelated and excluded from the reviewed commits |

The source history was already sanitized for publication. Preserve that lineage;
an old branch or folder is not automatically a valid merge source. Remote changes,
commits and release publication require their own authorization.

## Project workspace outside this repository

The sponsor clarified that organization must account for the SFC-related folders
our work also created under `C:\Project`, not just tracked files in this repository.
The Git checkout is only one part of the development workspace. These are separate
directories; switching Git branches does not switch or roll them back.

Observed November 9, 2026; purposes are corroborated by current context, directory
markers and historical records. This is a role inventory, not a full content,
size, redundancy or deletion audit.

| Location under `C:\Project` | Role / current evidence | Organization treatment |
| --- | --- | --- |
| `SFC-Modernize Engine` | Active source Git repository and ignored local artifacts; `git worktree list` reports this sole worktree | Authoritative development checkout; current branch is documented above |
| `SFC-Alpha-Checkout` | Private portable-alpha game copy containing `SFCRemix`; no `.git` marker | Current package/gameplay checkout. Preserve editable settings, recovery journal, game assets and saves; not a source clone or public-release input |
| `SFC-Remix-Return-Test` | Separate development game copy selected by `runtime_context.development`; no `.git` marker | Keep distinct from both accepted installation and alpha checkout; paths and transactional graphics recovery depend on its role |
| `SFC-Modernize-Publish` | Independent old publishing clone with its own `.git`, local `master` at `74dece9` on inspection | Historical sanitization/publication workspace, not a linked worktree or current source. Review unique content and its purpose before any later consolidation; do not sync or publish automatically |
| `SFC-Modernize Engine Backups` | Offline bundles/ZIPs, including pre-sanitization history and the independent `20261026-appearance-r3.zip` settings backup | Local recovery/privacy boundary. Preserve known useful rollback/settings evidence; never publish or merge the old history merely because it is a backup |
| `RemixJobs` | Historical captured-geometry/texture ingestion and preview jobs referenced by old run records and Toolkit tools | Preserve provenance and accepted comparison inputs. Contains local asset-derived material, not alpha or Git payload; older jobs are not automatically obsolete |
| `RTXRemix-Standalone` | Legacy Toolkit vendor download and `rollback-20261024-115425` records | Separate vendor/archive area, not the pinned game-renderer dependency directory. Old full portable rollback ZIP was explicitly deleted in the recorded cleanup; remaining manifests alone are not a restorable installation |

The retired `C:\Project\RTXRemix` extracted Toolkit root is absent on this check.
The managed Toolkit and per-user NVIDIA preferences are separate from this
parent-folder inventory; they are not cleanup targets here. Other unrelated
projects under `C:\Project` are outside SFC scope.

Before consolidating these directories, identify active consumers/hardcoded paths,
unique source or settings, pending recovery and retained provenance. Classify each
as active source, test deployment, archive, vendor input or verified redundant
output. A separate clone needs its own Git/content review. A game copy needs
normal-exit/recovery verification. A backup needs a proven replacement before
removal. Do not treat the parent folder as a single repository, copy it into a
release ZIP, or delete outside directories as part of ordinary branch cleanup.

Sources: [runtime context](../tools/remix_runtime/runtime_context.py),
[private alpha contract](releases/PORTABLE_ALPHA.md),
[publication decision](decisions/2026-10-18-private-github-publication.md),
[Toolkit installation comparison](reconnaissance/2026-10-24-remix-install-comparison.md)
and the dated cleanup entries retained in [the handoff](HANDOFF.md).

Reviewed checkpoints already pushed before this phase:

- `49373fd`: portable-alpha baseline and production-cleanup audit.
- `35fda1b`: explicit production dependencies and profiling-independent startup;
  [CPU/GPU evidence and sponsor confirmation](runs/2026-11-09-codex-production-module-separation.md).
- `fe17b8d`: OpenSpec setup and the scoped foundation proposal/design/tasks.

This foundation's documentation is the next separate commit boundary when
requested. Shared handoff/status edits need focused review; unrelated local
notes and attachments must not be swept in by a blanket staging command.

## Tracked-tree inventory

At `fe17b8d`, `git ls-files` reports **1,623 tracked files**, including hidden
workflow files. Counts exclude ignored artifacts, installed packages and
untracked working files; they are not the alpha's dependency counts or disk size.

| Tracked root | Files | Responsibility |
| --- | ---: | --- |
| `.agents/` | 7 | Six generated OpenSpec skills and tool-selection metadata; development only |
| `.gitattributes` | 1 | Git file/line-ending policy |
| `.gitignore` | 1 | Local/generated/proprietary exclusion rules |
| `AGENTS.md` | 1 | Standing agent/contributor instructions |
| `LICENSE` | 1 | MIT for project-authored material; separate third-party terms remain |
| `README.md` | 1 | Public project introduction and navigation |
| `artifacts/` | 1 | Only its policy README is tracked; generated contents are ignored |
| `docs/` | 821 | Current guidance, requirements, decisions and dated evidence |
| `openspec/` | 8 | Project workflow configuration, initial change and placeholders |
| `src/` | 1 at foundation | Now owns the first migrated component: portable launcher; see the relocation note below |
| `tests/` | 209 | Python/native tests, test documentation and legally trackable fixtures |
| `tools/` | 571 | Mixed production sources, shared interfaces, diagnostics and build tools |

Intentional new files in this phase are `CONTRIBUTING.md`, this map and
`REPOSITORY_MIGRATION.md`. They are current guidance, not product inputs. Updated
guidance/task files remain in their existing categories. New files outside these
rules need explicit classification; do not silently classify them as disposable.

## Classification rules — apply in order

1. **Shipping status comes from manifests.** The
   [production Python allowlist](../tools/release/runtime_modules.json) selects
   59 modules, not every import branch. Native role mappings and required default
   profiles come from [release staging](../tools/release/stage_preflight_fixture.py)
   and the installed immutable manifest. Staging is a private fixture, not an
   approved release builder. Vendor closure remains separately qualified.
2. **Build inputs are not all shipped files.** Runtime `.cpp`, `.h` and `.def`
   files remain production/shared source even when only their compiled output
   ships. Classify them through their component's build and include graph.
3. **Tests and diagnostic entry points are development work.** `tests/`,
   standalone fixtures, probe/analysis/qualification runners and build scripts
   are not runtime dependencies merely because they sit beside runtime modules.
   A listed allowlist member overrides a filename such as `analyze_*`.
4. **Mixed helpers remain mixed.** A retained module with inactive diagnostic
   methods is not fully production-minimal. Follow its consumers before proposing
   removal or relocation; folder-level classifications do not settle this.
5. **Guidance/planning and evidence have different jobs.** Use the contributor
   [ownership table](../CONTRIBUTING.md#documentation-responsibilities).
   `docs/runs/`, `docs/reconnaissance/`, milestone records and decisions preserve
   dated evidence. A decision can still govern a current interface; its age does
   not revoke it. Check its scoped authority and the latest handoff.
6. **Generated or proprietary inputs stay local.** The
   [ignore policy](../.gitignore) and [artifact policy](../artifacts/README.md)
   cover game assets, runtime downloads, compiled products, captures and caches.
   Curated versioned text/JSON evidence already under `docs/` is an intentional
   exception to bulk-capture exclusion. Audit its content before publication;
   extension or location alone does not establish redistribution rights.

## Production islands inside `tools/`

The first physical migration on November 9 moved the five portable-launcher
inputs to `src/launcher`. Build tools stay in `tools/release`. New packages use
`code/src/launcher`; existing packages retain their paired old launcher/layout.
Historical run records still name their original paths. The root counts above
are the foundation inventory, not a fresh count after this move. See the
[separation record](runs/2026-11-09-codex-release-tooling-separation.md).

These Python counts come directly from the current allowlist, not a new manifest:

| Area | Listed Python modules | Production responsibility / important exception |
| --- | ---: | --- |
| `tools/remix_runtime/` | 41 | Coordinator, preparation, appearance controls, recovery, IPC and runtime selection; also contains many development-only paths |
| `tools/d3d9_proof/` | 9 | D3D9-side material/light helpers, identity/recovery, coordinate conversion and checksums; not all proof fixtures ship |
| `tools/remix_ingest/` | 4 | Active break/live capture decoding and camera conversion coexist with historical Toolkit/OBJ utilities |
| `tools/scene_bridge/` | 2 | Scene bundle preparation and damage mapping; other neutral protocols/tests support development |
| `src/launcher/` | 2 | `bootstrap.py` and `session_recording.py`; native entry source and CMD wrappers share this application boundary |
| `tools/release/` | 0 | Build/packaging tools, allowlist, qualification and release-document inputs only |
| `tools/m1_component/` | 1 | `analyze_live_camera.py` is retained despite its analysis name; this area also owns native observation sources |

Native components have distinct lifetimes. Current source/build anchors:

| Component / role | Source and build anchor |
| --- | --- |
| Player-facing Windows launcher | [launcher.cpp](../src/launcher/launcher.cpp), [build_launcher.py](../tools/release/build_launcher.py) |
| Verified game launch, legacy observation host, return add-on | [return_launcher.cpp](../tools/remix_runtime/return_launcher.cpp), [return_host.cpp](../tools/remix_runtime/return_host.cpp), [return_addon.cpp](../tools/remix_runtime/return_addon.cpp); [build_return_probe.ps1](../tools/remix_runtime/build_return_probe.ps1) also builds fixtures/tests |
| Native startup gate and semantic observer | [m1_component.cpp](../tools/m1_component/m1_component.cpp); [build_m1_component.ps1](../tools/m1_component/build_m1_component.ps1) and [build_light_discovery.ps1](../tools/m1_component/build_light_discovery.ps1) use different defines/exports |
| Observation controller | [m1_controller.cpp](../tools/m1_component/m1_controller.cpp), [build_m1_controller.ps1](../tools/m1_component/build_m1_controller.ps1) |
| D3D9/Remix renderer | [d3d9_direct_host.cpp](../tools/d3d9_proof/d3d9_direct_host.cpp), [build_candidate_runtime.ps1](../tools/d3d9_proof/build_candidate_runtime.ps1) |
| GPU output receiver | [output_receiver.cpp](../tools/d3d9_proof/output_receiver.cpp), [build_receiver.ps1](../tools/d3d9_proof/build_receiver.ps1) |
| Owned-process lifetime guard | [bounded_job.cpp](../tools/remix_ingest/bounded_job.cpp), [build_remix_job.ps1](../tools/remix_ingest/build_remix_job.ps1) |
| Native geometry checksum helper | [mesh_checksum.cpp](../tools/d3d9_proof/mesh_checksum.cpp), [build_mesh_checksum.ps1](../tools/d3d9_proof/build_mesh_checksum.ps1) |

`tools/native_insertion/` owns shared gate/cohort contracts and tests used by
native components; it is not an extra interchangeable renderer. Header ownership
and conditional compilation remain mixed and need a component-specific review
before moves. Qualified artifacts and their hashes, not a similarly named build
script, determine which binary is accepted. Some scripts still use workstation
paths or legacy runtime locations; this map is not a clean-machine build recipe.

## Development areas and historical context

- `tools/break_probe`, `damage_probe`, `early_model_probe`, `effect_probe`,
  `m0_probe` and `render_survey`: isolated discovery/capture and their fixtures.
- `tools/recon`: inspection/publication-audit helpers, some reused by build-time
  inventory; retain dependencies before classifying individual helpers as unused.
- `tools/remix_api_proof`: separate API experiment; not the current ordinary-D3D9
  geometry path.
- `tools/native_foreground`: parked shield/effect replay investigations. Current
  native insertion lets later native effects draw normally; do not restart replay
  just because its code remains.
- Mixed runtime areas above also contain builds, fixtures, former exporters and
  investigations. Consult [diagnostics](DIAGNOSTICS.md),
  [packaged-tools audit](releases/PACKAGED_TOOLS_AUDIT.md) and
  [payload audit](releases/PROJECT_PAYLOAD_AUDIT.md) for their dated findings.

The eight release documents, ten decisions, 48 M1 records, seven M0 records,
340 reconnaissance files and 401 run files are dated inventories at this
checkpoint. The governing requirements have two tracked files. Current top-level
docs are HANDOFF, STATUS, DIAGNOSTICS, OBSIDIAN and OPENSPEC; this phase adds the
map and roadmap. Counts do not establish obsolete content or deletion scope.

## Local-only material and open classification limits

`Game Assets/`, `References/`, bulk `artifacts/`, SDK/runtime downloads, compiled
binaries, captures, game-saved preferences and private settings are not source
publication inputs. The public ZIP uses its reviewed recipe and notices, not a
recursive copy of this workspace. Repository ignore rules and package inclusion
rules are separate controls; neither replaces a content/licensing review.

The existing untracked attachments and memory audit remain untouched. Their
presence does not authorize adding them, deleting them or silently changing
ignore rules. Classification of every inactive method/shared native include,
full clean-machine vendor closure and each future destination directory remains
open. They are follow-up work, not claims made by this map.
