# OpenSpec development workflow

Initialized November 9, 2026 with the official standalone Windows CLI **1.16.1**
and its core Codex profile. This is development tooling, not an alpha dependency.
Anonymous CLI telemetry is disabled in the local OpenSpec configuration.

## Installed locations

- Local CLI: `%LOCALAPPDATA%\Programs\openspec\openspec.exe`; the official
  installer adds its directory to the user PATH. New terminals pick it up.
- Project context and artifact rules: [config](../openspec/config.yaml).
- Standing behavior specifications: `openspec/specs/`.
- Proposed changes and completed-change history: `openspec/changes/`.
- Six generated Codex workflows: `.agents/skills/openspec-*/SKILL.md`.

The first change, [organize-repository-foundation](../openspec/changes/organize-repository-foundation/proposal.md),
has a proposal, design and 14 tracked implementation tasks; see its task list for
current completion. It deliberately skips
behavior specs because its scope is documentation/process only. No standing
specifications have been generated. Existing research, requirements, plans and
evidence have not been migrated or rewritten.
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

Proposal and exploration workflows do planning; implementation uses apply-change.
Existing user instructions and authorization retain precedence. We do not add a
new approval gate for routine work merely because the framework is installed.
The optional verify workflow is not installed by the core profile; our existing
tests and evidence requirements continue to apply regardless.

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
