# Proposal

## Why

The working renderer is now ahead of the repository's organization: production
components share `tools/` with experiments, current guidance competes with
historical records, and the active Git branch still carries a privacy-cleanup
name. Establish a navigable, documented foundation before relocating code or
preparing a public alpha.

## What Changes

- Document one integration-lineage policy, short-lived `codex/` change branches,
  focused commit boundaries and release-tag expectations. Retain the existing
  remote `master` name for this increment; no branch rename, merge or history
  rewrite is included.
- Classify the current repository into production, mixed runtime/development,
  developer tooling, tests, release tooling, current guidance, historical evidence
  and local/generated inputs. Reuse existing audits and the production allowlist;
  do not treat all files under `tools/` as disposable utilities.
- Establish documentation ownership and a small contributor entry point linking
  the CDD, current checkpoint, evidence, diagnostics, OpenSpec and Obsidian.
- Write a staged migration plan with component boundaries, dependencies,
  verification and rollback expectations for later code-relocation changes.
- Describe how pending work should be reviewed and separated for future requested
  commits. Do not stage or commit that work as part of this authorization.

### Scope and non-goals

This change delivers contributor/Git conventions, a repository map, documentation
ownership and a migration roadmap. It does not relocate source files, delete
evidence, change imports or build paths, rewrite the CDD, introduce CI workflows,
alter runtime behavior, modify the private alpha or publish a release. Existing
uncommitted work and unrelated local files remain intact.

## Capabilities

### New Capabilities

None. This is repository documentation and development-process organization;
`.openspec.yaml` sets `skip_specs: true` rather than inventing a game capability.

### Modified Capabilities

None. Rendering behavior, interfaces, packaging behavior and acceptance thresholds
remain unchanged. Later migrations need their own scoped changes.

## Impact

Planned documentation: `CONTRIBUTING.md`, `docs/REPOSITORY_MAP.md` and
`docs/REPOSITORY_MIGRATION.md`, with narrow navigation/ownership links in README,
AGENTS and current continuity records where needed. No application dependency or
alpha payload is added.

The November 9 inventory found 1,602 tracked files: 819 documentation files,
568 under `tools/`, 208 tests and one `src/README.md`. These are dated tracked-tree
counts, not package sizes or proof that files are obsolete. At exploration time,
production separation, startup correction and OpenSpec setup were uncommitted.
The runtime/package changes were subsequently checkpointed as `35fda1b` at the
sponsor's request, separately from OpenSpec setup and this plan. Sponsor confirmed
enhancements returned after the startup correction;
that does not establish clean-machine release readiness.

At exploration, `codex/github-sanitized` was at `49373fd`, one commit ahead of the
locally cached `origin/master`; local `master` had divergent history. The runtime
checkpoint is now `35fda1b` on the same active branch.
Remote freshness/default-branch settings must be checked before any later Git
integration action. No remote mutation is needed for this documentation change.
