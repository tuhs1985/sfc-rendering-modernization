## Context

This maintenance scope follows the sponsor's explicit approval to share
duplicated test assets and review resolved traces. It is separate from the
active UE insertion change and does not claim further renderer progress.

## Decisions

Use standard NTFS hard links for SHA-256-identical frozen images, preserving all
existing names/bytes rather than introducing a runtime cache or changing packet
formats. The canonical file remains in its original evidence folder. Applying
requires an explicit reviewed manifest and exclusive audit ledger. Groups are
validated before atomic replacement, changes are rechecked, symbolic/junction
paths and paths outside artifacts are refused, and completed groups become
read-only. Interrupted work remains byte-correct and its operations are logged.
No source data or package files are selected automatically.

Inventory is separate from applying. It scans only successful dated older runtime
runs, excludes failed/current/unfinalized runs and already shared files, and
only considers image/texture payloads. Nothing imports this tool during play.
The existing conservative budget still counts every logical path, even linked
ones; sharing saves physical disk without silently changing the cap.

Only the raw SFC-23 startup traces/full-system CSV are retired: the sponsor marked
that issue resolved on November 6, and focused extracted analysis/timelines remain.
Unresolved traces and recent ZIPs stay. Old proof project/Binaries is rebuildable;
the packaged proof, debug symbols, original source/content and logs remain.

## Risks

In-place edits to hard-linked evidence would affect every alias; read-only mode
and restricting selection to frozen completed runs prevent ordinary overwrites.
Do not use this tool on active working sets. Original per-alias modification time
is recorded in the ledger before aliases share canonical file metadata.
Hard-link access is restricted in the app's constrained process; actual Windows
boundary tests and maintenance use the approved desktop execution path.

## Verification

Six focused actual-file tests cover dry-run, link/repeat, changed bytes, atomic
replace failure, boundary refusal and inventory selection. Actual data is
rechecked against the reviewed manifest after sharing. Launcher preflight and
protected package hashes are verified. No GPU/gameplay campaign is needed for
a development-only file maintenance tool; current runtime boundaries are not
modified. Detailed results belong to the linked cleanup run record.
