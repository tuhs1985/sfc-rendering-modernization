# Run55 — import unchanged approved CDD

Date: 2026-10-18 America/New_York. Sponsor asks to include a copy of the CDD.
Starting HEAD d9c74451efa5a772e4115db5050014dbf8d79eab on
codex/github-sanitized; Run54 README/HANDOFF edits and untracked run record already
present, unstaged. Preserved all that work. Fuel Guard attached through trusted
hook receipt; no daemon started.

Used PowerShell Get-Content/Get-Item, Copy-Item and Get-FileHash on the sponsor's
previously identified OneDrive Obsidian requirements document. Copied only that
Markdown file into docs/requirements under its original filename. Copy-Item used
for exact-byte preservation, not reconstruction or editing of baseline text.
External original unchanged. No templates, vault configuration or chats copied.

Source and copy: 49,909 bytes; SHA256
BF5384D2586601AAA28DB36970937A3B40F598E12002B3450BF2E7D9562FA352.
Matches the original hash in approved SFC-GATE-20261014 as independent existing
provenance. Frontmatter identifies version1.0/approved2026-09-03. CONFIRMED exact
copy, not a new requirements version or approval decision.

Created docs/requirements/README.md with provenance, unchanged-baseline rule,
amendment precedence and external template wiki-link explanation. Updated README
to link the included baseline instead of claiming it was absent. Updated newest
HANDOFF checkpoint and created this record. No code/config/runtime changes.

Validation: source/copy SHA256 and length equality; version/status and amendment
hash comparison; README and requirements-index local Markdown links checked with
URL decoding; git diff --check. All PASS. Existing Run54 262-test PASS remains
applicable; no tests/gameplay rerun for this exact document-copy-only task.

Final state: README.md and docs/HANDOFF.md modified; Run54 record, this Run55
record and docs/requirements/ untracked; nothing staged, committed or pushed.
No blocker. Exact next action: sponsor reviews combined README/CDD documentation
update before authorizing commit/publication. Never edit requirements to reconcile
historical implementation status; use approved amendments and current evidence.
