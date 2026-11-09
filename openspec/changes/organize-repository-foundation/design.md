# Design

## Context

See [proposal.md](proposal.md) for motivation and scope. The current renderer's
source is mostly under `tools/`; `src/` contains a placeholder README. The alpha
now has an explicit 59-Python-module production allowlist and manifest roles for
native components. Those records are better evidence of runtime responsibility
than folder names. Historical qualification also hashes source paths, so moving
files can invalidate tests and build receipts even when behavior is unchanged.

The active branch contains the sanitized lineage and working-alpha fixes,
checkpointed separately as `35fda1b` after exploration. OpenSpec setup and this
plan are recorded separately. The local `master` branch diverges from the active
lineage. This increment can document the
desired Git workflow without changing any branch, index, remote or package.

## Goals / Non-Goals

**Goals:**

- Give a new contributor an entry point and an authoritative answer for each
  documentation topic.
- Identify which parts run in the product, which support development, and which
  require separation before a later move.
- Provide an executable sequence for later scoped migrations, with evidence and
  rollback appropriate to the boundary each move changes.
- Define commit/branch conventions without consuming unreviewed pending work.

**Non-Goals:**

- No target source tree is imposed on existing modules in this increment.
- No source move, historical-evidence purge, branch cleanup, CI implementation,
  renderer refactor, dependency upgrade or package rebuild.
- No runtime guards, logging, configuration defaults or performance changes.
- No rewriting the CDD or converting old observations into accepted capabilities.

## Decisions

### 1. Preserve lineage; document a simple branch model

Document the currently observed remote integration line (`origin/master`) and
short-lived `codex/<change-name>` branches. Verify the remote default and current
refs before a future integration operation; local tracking refs are not a live
GitHub query. Keep the remote primary name unchanged in this change.

Record local `master` as divergent, not a branch to merge automatically. Neither
reset nor rename the active dirty branch. Later requested commits should group
production separation/startup correction, OpenSpec setup and repository guidance
into reviewable units; overlapping documentation edits need hunk-level review.
Do not promise an exact number of commits before reviewing their dependencies.
Version tags refer to reviewed commits and approved release artifacts, never to
the mere existence of a working directory or alpha test copy.

Alternative: rename everything to `main` now. Rejected because it solves naming
before lineage and introduces unnecessary remote and working-tree changes.

### 2. Classify in place before relocating

Create `docs/REPOSITORY_MAP.md` with folder/pattern ownership plus explicit
exceptions, linked to the existing payload audits and allowlist. Cover all
tracked roots and intentional new project files; list mixed/uncertain areas
explicitly rather than pretending the classification proves safe removal.

| Class | Current anchors | Treatment |
| --- | --- | --- |
| Production Python | `tools/release/runtime_modules.json` | Retain paths; link actual listed modules |
| Native runtime/shared interfaces | Native manifest roles and associated build inputs in `m1_component`, `native_insertion`, `d3d9_proof`, `remix_runtime`, `remix_ingest` | Identify built component and shared headers; mark mixed folders |
| Development probes/experiments | `*_probe`, `recon`, `render_survey`, API/preview qualification paths | Retain as tools/evidence support; not alpha payload by location alone |
| Tests | `tests/` and documented qualification fixtures beside tools | Distinguish test sources from essential runtime support |
| Release tooling | `tools/release/` | Separate build-time tools from shipped bootstrap/context inputs |
| Current guidance/planning | Root guidance, requirements, current docs, `openspec/`, `.agents/` | Link ownership; development instructions stay outside product |
| Historical evidence | `docs/runs`, `docs/reconnaissance`, milestone records and decisions | Preserve dated conclusions and provenance; index instead of mass-moving |
| Local/generated/proprietary | Ignored artifacts, game assets, dependencies, captures, settings and local attachments | Keep outside commits and public ZIPs; record review needs |

The map is a navigation/classification document, not a second package manifest.
Use ordered classification rules and exceptions so no tracked root is silently
omitted. Fresh Git counts must be dated and distinguish tracked files from
untracked proposals and ignored work products. No duplicate 1,600-row inventory
or new inventory program is needed for this increment.

Alternative: move all `tools/` Python into `src/`. Rejected because that merges
production, bootstrap, retired experiments and diagnostic paths indiscriminately.

### 3. Assign documentation responsibility, not competing authority

`CONTRIBUTING.md` becomes the contributor entry point, with narrow links from
README and AGENTS. It describes the Git workflow, focused verification and
commit review. `docs/REPOSITORY_MAP.md` owns the present layout;
`docs/REPOSITORY_MIGRATION.md` owns the staged future layout work.

Document these responsibilities:

- Approved capability requirements and amendments: project scope and milestones.
- OpenSpec: detailed accepted behavior contracts and proposed changes, once
  authored; this process-only change deliberately has no behavior delta.
- AGENTS: standing contributor/agent instructions, not run chronology.
- HANDOFF: one clearly identified current engineering checkpoint.
- STATUS: short current/open/parked summary linking to evidence.
- DIAGNOSTICS: reusable procedures and when each diagnostic is appropriate.
- Run/reconnaissance records: dated evidence and limitations, not today's defaults.
- Release documents: the delivery contract and current release-readiness limits.
- Obsidian: human-facing context and deferred ideas; implementation authority
  remains in the repository.

Current guidance should point to the latest result and label historical records.
Do not rewrite old run results to make them look current. No new automatic
Obsidian synchronization service is introduced. Existing CLI workflow remains.

### 4. Stage later migrations by exercised boundary

Create a roadmap, not an automatic migration script:

1. **Foundation (this change):** contributor conventions, classification,
   documentation links and the staged roadmap; no physical source changes.
2. **Record a reviewed baseline (separate Git authorization):** checkpoint the
   working alpha and setup in focused commits before code relocation. Preserve
   unrelated local work and publish only when requested.
3. **Separate development entry points:** later changes select one component,
   map its runtime versus diagnostic imports, and choose a destination from that
   evidence. Preserve launch compatibility where qualified.
4. **Relocate production components:** later changes move one cohesive component
   with its imports/build inputs/allowlist and source-qualification references
   updated together. Do not redesign the renderer at the same time.
5. **Reorganize historical navigation if justified:** update indexes first;
   physical evidence moves need explicit provenance/link review and their own
   change. Deletion is never implied by age or classification.

Every later migration needs a source/destination map, affected consumers,
relevant tests, package-startup check and rollback. At any point the source
manifest, generated package manifest and actual loaded files must agree. Because
the profiling-off regression escaped CPU-only checks, moves affecting startup
must exercise the real packaged host/receiver with diagnostics off. GPU/gameplay
checks are reserved for migrations that touch those paths; documentation changes
do not trigger a full rendering campaign.

## Risks / Trade-offs

- **Classification becomes stale:** link authoritative manifests/build inputs
  instead of maintaining duplicate lists; update maps with affected changes.
- **Mixed folders are misread as removable:** label exceptions and preserve
  unknowns; classification grants no removal authorization.
- **Documentation creates more bureaucracy:** three concise entry documents,
  links to existing records and proportionate checks; no rewriting old history.
- **Dirty-tree changes are lost or swept into commits:** review explicit paths
  and overlapping hunks; no staging, resets or blanket cleanup in this change.
- **A future rename breaks paths or readiness:** use independent scoped changes
  and actual boundary checks; keep the working baseline available for rollback.
- **Old privacy material returns through Git cleanup:** preserve sanitized
  lineage; any divergent-branch integration requires explicit history review.

## Migration Plan

For this documentation-only increment, first inventory the current refs and
tracked roots read-only, then author the three entry documents and narrow links.
Validate local links, coverage of root categories, current-vs-historical labels
and consistency with existing instructions. Confirm no application/source path,
package allowlist, game copy or settings changed. Record outcomes in the current
handoff/status and existing Obsidian tracker.

Rollback consists of reverting only these documentation/navigation changes,
preserving all pre-existing edits and this change's planning history. No game-file
restoration or runtime process cleanup is required because none are touched.

## Open Questions

- Exact destination directories for each production component are deferred to
  the corresponding relocation change. This roadmap does not authorize moves.
- Whether to rename the remote integration branch later is independent of these
  conventions; keep its current name until a separate decision.
