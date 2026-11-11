# SFC Modernize agent instructions

These instructions apply to the entire repository.

## Start here

- Use [CONTRIBUTING.md](CONTRIBUTING.md) for Git/documentation conventions, [the repository map](docs/REPOSITORY_MAP.md) for current file ownership, and [the migration roadmap](docs/REPOSITORY_MIGRATION.md) for separately scoped future moves. Classification does not authorize relocation or deletion.
- Read the newest checkpoint in [docs/HANDOFF.md](docs/HANDOFF.md) when resuming integration work or investigating a prior run. Use [docs/STATUS.md](docs/STATUS.md) for open and parked items and [docs/DIAGNOSTICS.md](docs/DIAGNOSTICS.md) for capture and troubleshooting procedures.
- Check `git status --short` before editing. Preserve existing user changes and keep the patch focused on the request. Stage, commit, or push only when the user requests it.
- Put changing run results, limitations, and next steps in the handoff or a linked run record. Keep standing project rules here.

## Obsidian project continuity

- At the start of a new SFC engineering session, read the existing Status Tracker and latest Project Parking Note, if present, through the official Obsidian CLI. Reconcile them with Git status and the repository handoff before engineering work.
- Update the existing Status Tracker after meaningful verified changes. Record user-deferred ideas in the existing Parking Lot. When the user parks or ends a session, write the Project Parking Note with exactly two substantive Restart Brief paragraphs followed by a compact Session Summary.
- Use the installed Obsidian CLI and Markdown skills and the exact vault and note paths in [the Obsidian workflow](docs/OBSIDIAN.md). Limit writes to the existing SFC project folder. Git and the repository handoff govern implementation and evidence. Obsidian holds project context and restart information.

## Game installations and runtime

- Treat the accepted SFC installation and original game assets as read-only. Use the verified test copy and the repository launchers for live integration work. Consult the [README](README.md) for setup and launch commands.
- Preserve client, proxy, dependency, and graphics configuration checks. Investigate failed preflights through the documented preparation or recovery path. Keep game-saved player names in the test copy. Compare other protected settings against the independently verified baseline.
- Preserve user appearance settings and saved preferences. Normal play uses the untimed launcher with bounded recording. Use timed tests or additional capture flags for a specific diagnostic question.
- Restore the test copy through the verified recovery workflow after interrupted runs. Confirm SFC has exited before restoring its files. Limit process cleanup to helpers owned by the run.

## Verification and evidence

- Use the Windows Python environment documented in the README. Run checks appropriate to the change. For launcher or renderer work, verify the normal entry point and the relevant qualification records. Use read-only preflight before a live run.
- Exercise the actual process or file boundary when a fix depends on it. Record offline, standalone GPU, and live gameplay results separately. State what remains unverified.
- Keep raw captures, useful comparison images, current qualification inputs, dependency pins, rollback files, and recent run evidence. During requested cleanup, remove only verified obsolete generated files and record what was removed.
- Keep proprietary game assets, runtime binaries, private settings, and local captures out of Git. Check the staged file list before any requested commit.
