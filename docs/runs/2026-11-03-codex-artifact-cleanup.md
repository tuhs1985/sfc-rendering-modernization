# Run288 — delete obsolete generated artifacts

Sponsor explicitly requested substantial deletion rather than more archival.

Deleted 23,722 files / 7,557,782,691 logical bytes(7.56GB).
Measured filesystem free space increased 7,236,894,720 bytes(7.24GB):
207588679680→214825574400B. Concurrent/system allocation can affect free-space
measurements; do not confuse logical lengths with compressed disk allocation.

## Selection

-3.37GB obsolete generated-output archives; excluded archives containing recognized raw captures/traces or source-code/settings snapshots.
-2.34GB old decoded/derived texture copies.
-1.22GB superseded preview meshes, masks and returned-image outputs.
-0.63GB obsolete generated GPU inputs; small redundant per-run executable copies.

Loose output removal was restricted to dated October runs BEFORE October31.
All selected final absolute paths were checked under the exact runtime runs or
archive directories before deletion. No recursive folder removal. Current
qualification files and exact artifact references in maintained source were
protected. The complete per-file deletion/reason/size ledger is local:
`artifacts/workspace-cleanup-20261103/deleted.json`. Inventory/plan, source
fingerprints and verification results are alongside it. This was DELETION;
old archive receipts may now refer to intentionally pruned outputs. Do not
attempt to restore those archives or imply they still exist. Rebuild obsolete
generated fixtures if needed; consult this record before interpreting missing
old generated outputs as a new fault.

Kept original gate captures, rendering surveys, unique trace/raw archives,
recent damage/sponsor evidence, existing source/history and uncommitted work,
current settings, active build outputs, qualification inputs, dependency pins,
Game Assets/References and both game installations.16,090,372B of small
archive-only result/manifest/analysis/summary JSON was extracted as supplemental
metadata before deleting generated bulk. Existing loose run summaries/logs and
versioned findings were retained.

## Verification

- Tracked and selected user-file SHA256 comparison:no changes during cleanup.
- Damage-enabled native replacement read-only launcher preflight PASS;no game or renderer launched.
-673Python tests PASS after recheck. Initial suite had one transient Windows
 ReplaceFileW1175 error;no missing artifact. Unmodified suite passed on repeat.
 No renderer/material/source implementation changed to accommodate cleanup.
- No staging,commit,push,dependency update or game setting changes.

Active work remains Run287 damage checkout. A newer sponsor run folder
`20261104-043317-245721-in-game` was noticed and preserved;not analyzed during
this cleanup-only request. Next:review that run when sponsor reports it ready.
