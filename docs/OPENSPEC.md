# OpenSpec development workflow

Initialized November 9, 2026 with the official standalone Windows CLI **1.16.1**
and its core Codex profile. This is development tooling, not an alpha dependency.
Set `OPENSPEC_TELEMETRY=0` for repository commands in environments that do not inherit the local telemetry preference.

## Installed locations

- Local CLI: `%LOCALAPPDATA%\Programs\openspec\openspec.exe`; the official
  installer adds its directory to the user PATH. New terminals pick it up.
- Project context and artifact rules: [config](../openspec/config.yaml).
- Standing behavior specifications: `openspec/specs/`.
- Proposed changes and completed-change history: `openspec/changes/`.
- Six generated Codex workflows: `.agents/skills/openspec-*/SKILL.md`.

The first change, [organize-repository-foundation](../openspec/changes/archive/2026-11-20-organize-repository-foundation/proposal.md),
tracked 14 documentation and process tasks. Completed changes live in
`openspec/changes/archive/`. The [UE5 offline consumer spec](../openspec/specs/ue5-offline-consumer/spec.md)
covers the packaged captured-scene proof.

The installation preserved AGENTS.md. Generated workflows should be refreshed
through OpenSpec rather than manually customized; project rules belong in config.

## Using it

The workflows are `openspec-explore`, `openspec-propose`,
`openspec-apply-change`, `openspec-update-change`, `openspec-sync-specs` and
`openspec-archive-change`. Codex receives skills, not a duplicate command set.
Use the skills picker; the proposal skill can also be invoked by name:

```text
$openspec-propose "Describe the change"
```

1. **Plan in OpenSpec.** Start with the capability requirements and the applicable
   change. Keep the approved scope, behavior, design and task list there.
   Brainstorming and plan-writing techniques can refine those artifacts. Use the
   existing OpenSpec files as their destination instead of creating separate
   specs or plans under `docs/superpowers/`. Existing approval covers the same scope.
2. **Implement and verify with Superpowers.** For an OpenSpec change, use
   apply-change to resolve the change, read the controlling artifacts and identify
   pending tasks. Use the applicable Superpowers implementation, debugging, review
   and verification practices to execute that task list. Follow SFC's focused
   verification rules. Use engineering judgment for choices within approved scope.
   If a decision changes approved behavior or acceptance criteria, surface it and
   update the OpenSpec artifacts after approval. Investigate routine failures
   within scope and keep blocked or unverified tasks open. Stage, commit and push
   only when requested.
3. **Record evidence and close in OpenSpec.** Link the actual checks and results
   in a run record or handoff before checking off the corresponding task. A local
   execution ledger may track working details. OpenSpec owns durable task status.
   Include the final documentation and continuity task and apply the
   [documentation completion checks](../AGENTS.md#documentation-completion-checks).
   Review completed behavior deltas against the evidence, sync accepted
   requirements into standing specs, then archive the completed change.
   Archive verified process-only changes without creating behavior requirements.
   Keep links to moved artifacts current. Leave unfinished changes active.

Useful terminal commands, from the repository root:

```text
openspec --version
openspec list --json
openspec doctor --json
openspec validate --all --strict --no-interactive
openspec update --dry-run --json
```

Validation checks planning structure; it does not execute our renderer, prove
packaged startup or replace gameplay confirmation. An initially empty spec/change
inventory has nothing to validate and is not a software qualification result.

## Documentation responsibilities

The CDD/capability requirements govern overall objectives and milestones. OpenSpec
holds detailed behavior contracts and scoped changes. AGENTS.md holds standing
contributor instructions. The handoff holds the current engineering checkpoint;
run records hold evidence, and Obsidian remains the sponsor-facing dashboard and
parking lot. Link these records rather than maintaining competing requirements.

The [contributor guide](../CONTRIBUTING.md#documentation-responsibilities) assigns
each record's responsibility; the [repository map](REPOSITORY_MAP.md) classifies
current files, and the [migration roadmap](REPOSITORY_MIGRATION.md) orders later
changes. Use those guides without treating the foundation plan as authorization
to move runtime code.

Initialize future capability specs from verified current behavior and approved
requirements; retain unknowns explicitly. Do not convert every historical run to
a specification. Neither archival nor completed checkboxes establish milestone
completion or release approval.

The alpha's explicit production-file allowlist excludes `openspec/` and
`.agents/`. Installing this tooling does not change the working alpha or require
testers to install it.

Upstream: [installation](https://github.com/Fission-AI/OpenSpec/blob/main/docs/installation.md),
[workflow](https://github.com/Fission-AI/OpenSpec/blob/main/docs/workflows.md),
[customization](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md).
