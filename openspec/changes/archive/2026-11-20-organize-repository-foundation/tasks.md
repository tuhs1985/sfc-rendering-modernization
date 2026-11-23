# Tasks

Implementation is documentation-only. Checkboxes below record progress;
completion does not authorize staging, commits, pushes, file relocation or runtime changes.

## 1. Establish the documented Git baseline

- [x] 1.1 Record dated HEAD, active/upstream branches, divergent local branch status and working-tree categories in `docs/REPOSITORY_MAP.md`; verify against read-only Git commands and distinguish cached remote refs from any live remote check.
- [x] 1.2 Write the Git section of `CONTRIBUTING.md`: one integration lineage, short-lived `codex/` branches, focused commits and release tags; verify it preserves sanitized history and requires no rename, merge, reset or remote mutation in this increment.
- [x] 1.3 Document the separately reviewed production/startup and OpenSpec checkpoints and the intended commit boundary for foundation guidance, including overlapping documentation hunks and excluded local attachments/memory notes; verify the index and branch remain untouched by foundation implementation and each group has supporting evidence.

## 2. Classify the current repository in place

- [x] 2.1 Complete `docs/REPOSITORY_MAP.md` with ordered folder/pattern classifications and exceptions for every tracked root plus intended new project files; verify dated tracked counts against `git ls-files` and explicitly identify mixed/unresolved areas.
- [x] 2.2 Link production classifications to `tools/release/runtime_modules.json`, native manifest/build inputs and the existing payload audits; verify shipped release bootstrap/runtime inputs are not misclassified as removable developer tools.
- [x] 2.3 Document local/generated/proprietary and historical-evidence boundaries using `.gitignore`, `artifacts/README.md` and current evidence-retention rules; verify no classification implies deletion, history rewriting or inclusion of game/capture/private-setting payloads.

## 3. Clarify documentation ownership and entry points

- [x] 3.1 Finish `CONTRIBUTING.md` with a concise contributor starting sequence and documentation-responsibility table; verify it distinguishes requirements, proposed changes, implementation checkpoints, evidence and human-facing context without duplicating their contents.
- [x] 3.2 Add narrow links from README, AGENTS and `docs/OPENSPEC.md` to the contributor/map/roadmap documents; verify standing rules and user authorization are preserved and no historical CDD/run findings are rewritten.
- [x] 3.3 Make the current handoff/status point to the latest implementation result and label superseded guidance as historical where needed for navigation; verify sponsor-confirmed rendering is separate from still-open clean-machine/release qualification.

## 4. Deliver the staged migration roadmap

- [x] 4.1 Write `docs/REPOSITORY_MIGRATION.md` describing foundation, separately authorized checkpointing, development-entry separation and later component relocation; verify every later phase is explicitly a separate change and this phase moves no code.
- [x] 4.2 Include a future-migration checklist for consumers/imports, builds, package allowlists/manifests, qualification paths, relevant actual-process checks and rollback; verify startup-affecting migrations require profiling-off packaged GPU startup while documentation-only edits do not require a gameplay campaign.

## 5. Verify and record the foundation

- [x] 5.1 Check local Markdown links, root-classification coverage and consistency of the three documents with AGENTS/CDD/OpenSpec responsibilities; verify each retained uncertainty and deferred move is explicit rather than claimed complete.
- [x] 5.2 Run strict validation for this OpenSpec change and `git diff --check`; review the focused diff and verify no additional source, build, package, game, settings, Git-index or branch changes were made by this increment. Record documentation checks separately from existing runtime test evidence.
- [x] 5.3 Update the repository checkpoint and existing Obsidian Status Tracker through the documented CLI with delivered guidance, verification and next separately scoped migration action; read back both and confirm no commit/push/release was performed.

## Workflow follow-up

- Review the completed guidance before requesting any source-relocation change.
- Checkpoint, integrate or publish only on a separate explicit request; foundation
  completion does not itself commit existing work or approve a release.
- Archive this change after its documentation tasks are complete and reviewed;
  it has no game-behavior specifications to merge.
