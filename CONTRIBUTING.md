# Contributing

Start with the [current checkpoint](docs/HANDOFF.md), then the
[repository map](docs/REPOSITORY_MAP.md). This is an existing Windows rendering
integration with a working private alpha, not a clean-sheet engine project.

## Working sequence

1. Read [AGENTS.md](AGENTS.md), current status and the relevant requirements or
   interface contract. Separate current guidance from dated experiments.
2. Check `git status --short`, the current branch and its base. Preserve unrelated
   local work. A folder name such as `tools/` does not make its contents disposable.
3. Choose one scoped change. [OpenSpec](docs/OPENSPEC.md) records its purpose,
   approach and tasks; existing user authorization governs what may proceed.
4. Implement and verify the affected boundary. Preserve compatibility and user
   settings, and record what the checks actually establish.
5. Update the current checkpoint and links. Stage, commit, push, integrate or
   publish only when requested; starting implementation does not authorize them.

For current build/test prerequisites and commands, use the
[development setup](README.md#start-here). Some developer scripts still
contain workstation-specific paths and require local dependency preparation.
Do not assume a fresh clone can launch the accepted integration immediately.

## Git conventions

- **Integration line:** GitHub `master` is the verified primary line as of
  November 9, 2026. `origin/master` is a local tracking ref, which may become
  stale. Check the live remote before integrating or publishing.
- **Work branches:** use short-lived `codex/<change-name>` branches from an
  explicitly reviewed integration checkpoint. The current foundation branch
  starts at `fe17b8d`; it does not change the primary branch's name.
- **Historical local branches:** local `master` and recovery branches may have
  divergent or pre-publication history. Do not merge them just to reconcile names.
  Follow the [publication safeguards](docs/decisions/2026-10-18-private-github-publication.md)
  and preserve the sanitized lineage. No automatic force push or history rewrite.
- **Commit units:** keep working-runtime fixes, development-tool setup and
  documentation organization independently reviewable. Tests and evidence for a
  fix belong with it. Review overlapping documentation hunks when splitting work.
- **Review scope:** use explicit paths and inspect the staged diff. Exclude game
  assets, captured models/textures, vendor binaries, private settings and unrelated
  attachments/notes. A clean working tree is not a reason to delete unrelated work.
- **Integration:** review the focused diff and relevant evidence before merging
  back. A pull request is the usual review record for contributions; this guide
  does not change the maintainer's existing authorization rules or GitHub settings.
- **Releases:** tags identify reviewed commits and approved, checksummed packages.
  A successful local checkout or archived plan is not release approval. Preserve
  the [portable-alpha contract](docs/releases/PORTABLE_ALPHA.md).

The prerequisite checkpoints are already recorded: `35fda1b` contains the
production separation/startup correction and `fe17b8d` contains OpenSpec setup
and the foundation plan. Both reached GitHub before foundation implementation.
The next requested checkpoint should contain only the foundation documents,
navigation/continuity edits and task completion. Local `.codex-attachments/` and
`windows-memory-audit.md` were deliberately excluded from the earlier commits.

Useful read-only review commands:

```text
git status --short
git branch -vv
git log --oneline --decorate -5
git diff --stat
git diff --check
git diff --cached --name-only
git diff --cached
```

## Documentation responsibilities

| Question | Authoritative record / responsibility |
| --- | --- |
| What are the project objectives and milestone thresholds? | [Capability requirements](docs/requirements/README.md) and their approved scoped amendments; do not rewrite historical assessments |
| What behavior is accepted, or proposed to change? | OpenSpec specifications and individual changes; an unfinished proposal is not implemented behavior |
| What standing rules apply to contributors/agents? | [AGENTS.md](AGENTS.md) |
| Where does the code live now? | [Repository map](docs/REPOSITORY_MAP.md); manifests/build inputs determine actual dependencies |
| What will move later, and under what checks? | [Migration roadmap](docs/REPOSITORY_MIGRATION.md); separate changes authorize each move |
| What is the latest implementation checkpoint? | The top current section of [HANDOFF](docs/HANDOFF.md); older checkpoints are historical |
| What is open, parked or recently completed? | [STATUS](docs/STATUS.md), linking to evidence rather than duplicating it |
| Which diagnostic should be used, and when? | [DIAGNOSTICS](docs/DIAGNOSTICS.md) and its probe definitions |
| What happened during a specific experiment? | Dated run/reconnaissance records; report their limits and later superseding results |
| What is distributable and how is it packaged? | [Release contract](docs/releases/PORTABLE_ALPHA.md), reviewed build recipe, immutable manifest and third-party notices |
| What does the sponsor need to resume or defer? | Existing Obsidian tracker/parking lot through the [CLI workflow](docs/OBSIDIAN.md); repository evidence governs implementation |

Keep rules in their owning record and link them elsewhere. Do not copy a whole
handoff into a new specification, convert a hypothesis into a requirement, or use
task checkboxes as proof of universal compatibility. Current status belongs at
the top; retain historical findings as dated evidence with clear labels.

## Verification proportional to the change

- **Documentation only:** check local links, ownership/classification consistency,
  OpenSpec structure, the focused diff and unchanged runtime inputs. No GPU or
  gameplay campaign is required simply for editing Markdown.
- **Code or build changes:** use focused tests first. Exercise the actual file,
  process, transport or GPU boundary the change affects; a mock-only result is
  insufficient when the fault lived at that boundary.
- **Package/startup changes:** verify the extracted package's normal entry point,
  real host/receiver startup with diagnostics off, and relevant cleanup/relaunch
  behavior. Preserve early passive startup and actual readiness independently of
  optional profiling. An integrity preflight is not a rendering test.
- **Gameplay changes:** use only the verified test copy and prepared workflow.
  Sponsor observations, automated checks and standalone GPU results are separate
  evidence categories; state what remains unverified.

Reuse the documented Python 3.12 environment and relevant native build tools.
Do not rebuild or broaden tests when no affected boundary justifies it. Keep
diagnostics optional and outside normal-play overhead; retain functional identity,
synchronization, lifecycle and recovery obligations. Do not relabel them as
diagnostics solely to remove a failing check.

Keep necessary working files, useful captures, current qualification inputs,
dependency pins and rollback records under their documented local locations.
Requested cleanup must identify verified obsolete outputs and record removals;
neither this guide nor a file classification authorizes deletion.
