# SFC project continuity in Obsidian

Use the installed `obsidian-cli` and `obsidian-markdown` skills. Target the existing vault `Obsidian Vault` and folder `02 - Projects/Coding Projects/SFC Modernization Project`. Confirm the vault location with `vaults verbose`. On this workstation it is `C:\Users\rober\OneDrive\Documents\Obsidian Vault`.

The desktop app must be running in the same Windows session as the CLI. Use `obsidian` if the terminal resolves it, or the installed Windows redirector as shown below. If the sandbox cannot connect to the desktop app, use the approved desktop-session execution path. If the CLI remains unavailable, record pending documentation updates in the repository handoff and report the limitation.

```powershell
$cli = Join-Path $env:LOCALAPPDATA 'Programs\obsidian\Obsidian.com'
$vault = 'vault=Obsidian Vault'
$folder = '02 - Projects/Coding Projects/SFC Modernization Project'
$tracker = "$folder/SFC Modernization - Status Tracker.md"
$parkingLot = "$folder/Parking Lot.md"
$restart = "$folder/Project Parking Note.md"

& $cli vaults verbose
& $cli $vault files "folder=$folder"
& $cli $vault read "path=$tracker"
# Read the restart note when it appears in the project inventory.
& $cli $vault read "path=$restart"
```

Pass the vault first and the exact vault-relative `path=` for each note operation. Use `help <command>` for local syntax. The [official Obsidian CLI guide](https://obsidian.md/help/cli) documents commands and newline escaping.

## Start or resume a session

Read the current Status Tracker and the Project Parking Note if it exists. Consult the Parking Lot when reopening a deferred idea. Compare this context with `git status --short`, the current revision and the latest [repository handoff](HANDOFF.md). Resolve disagreements against actual files and evidence. Distinguish work in the working tree from commits on the remote.

## Record progress or defer an idea

- **Status Tracker** — Append a dated entry when a milestone, technical finding or implementation status materially changes. Include evidence, validation and the next action. Keep prior entries and internal links. Refresh the existing `updated` and `checkpoint` properties when the current checkpoint changes.
- **Parking Lot** — Append or update a single entry when the user defers an idea. Capture the reason, what should reopen it and the first practical step. Update `updated` on substantive changes. Parking an idea records intent for later review.

Use CLI `append` for new entries and `property:set` for properties. Pass Markdown text as one `content=` argument with `\n` for newlines. Read back each write and check the new entry and properties. Use wikilinks for vault notes and repository paths or links for engineering evidence.

## Park a session

Create `Project Parking Note.md` in the same project folder on the first actual session close. Maintain it as the current restart brief. Read it before refreshing it and preserve user annotations and existing properties. Keep deferred ideas in the Parking Lot and detailed history in the tracker or Git handoff.

- **Restart Brief** — Exactly two substantive prose paragraphs. The first describes current state and what is verified or open. The second gives precise restart steps, including the relevant repository checkpoint, prerequisite and first command or check.
- **Session Summary** — A compact list of completed work, decisions, validation results and unresolved issues. Include links to `[[SFC Modernization - Status Tracker]]` and `[[Parking Lot]]` where relevant.

These updates run as part of normal agent sessions, using the existing notes and repository instructions.
