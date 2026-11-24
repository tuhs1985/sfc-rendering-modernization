# Development evidence compaction — November 23, 2026

Sponsor approved sharing duplicated assets first and reviewing superseded
captures, resolved diagnostic traces and repeated builds. This is maintenance;
UE native insertion remains 17/30 and no gameplay was started. The separate
OpenSpec change is compact-development-evidence.

## Results

| Action | Result |
| --- | --- |
| Share identical images in successful older runtime runs | 1,198 redundant files across 89 groups; 368,279,552 bytes measured disk recovery |
| Share identical readbacks in completed qualified standalone UE tests | 101 redundant files across 20 groups; 799,064,064 bytes measured disk recovery |
| Retire resolved SFC-23 raw startup traces/full-system CSV | 2,633,326,752 logical bytes; focused analysis/timelines remain |
| Remove superseded first UE proof project/Binaries | 789,620,509 logical bytes; source/content, packaged proof and its debug symbols remain |
| Total physical free-space increase | 4,590,313,472 bytes, approximately 4.6 GB |

No shared image path or pixel byte was deleted. Each group was SHA-256-verified,
then atomically replaced with hard links to one canonical file at its existing
path. Resulting groups are read-only. Original per-alias modification times are
recorded before metadata becomes shared. Hard links were verified after
application: a second dry-run reports 1,299 already shared files and zero work.

Sharing is only for immutable, completed evidence. Do not edit these files in
place: every alias shares storage. Removing an individual link does not remove
the other names. Current final native-pool test folders were excluded from the
new UE readback selection. Raw traces for unresolved investigations and the
recently accessed ZIPs remain untouched.

SFC-23 was declared resolved by the sponsor on November 6; the diagnosis and
resolution are retained in docs/reconnaissance/sfc23-startup-capture.md. Its three
large startup.etl files and one full-system CPU CSV were retired. The old raw
trace paths are intentionally unavailable, not a new collection failure.

## Repeatable tool and boundaries

tools/asset_diagnostics/share_evidence.py is explicit offline maintenance, not a
runtime dependency. Inventory and application are separate, dry-run is default,
and application requires an exclusive operation ledger. Inventory selects only
successful older dated runs, excludes failed/unfinalized runs and already linked
files, and accepts only image/texture payloads. Arbitrary reviewed groups can
also be supplied for qualified offline evidence.

The tool refuses outside-artifacts and linked-directory paths, validates every
group before mutation, rechecks source metadata, and uses same-volume atomic
replacement. Replacement failure preserves the original file. No automatic
deletion/compaction was added to the coordinator or normal launcher. The existing
20 GB allowance and logical-path accounting are unchanged; hard-link savings do
not silently expand the permitted logical evidence footprint.

Six real-file tests pass in the Windows desktop execution context. Creating a
hard link is denied by the app's restricted process; that environment failure
was separately observed and not treated as a tool defect or permission to
change protection settings. No Defender settings or drivers were changed.

## Verification and ledger

- Current alpha ZIP, both current UE executables and final native-pool results
  retain their prior SHA-256 hashes.
- Actual native light/scene worker qualification passes. It was explicitly
  refreshed because its development source inventory includes asset-diagnostics
  tools; the native application code/binary did not change in this pass.
- Read-only UE launcher preflight passes; no SFC or renderer starts.
- Counted evidence: 14,765,716,136 bytes. After the unchanged 570,425,344-byte
  reservation, 4,663,858,520 bytes remain within the 20 GB allowance.
- Local plans/operation records are under artifacts/workspace-cleanup-20261123:
  duplicate-frozen-images.json, shared-images.jsonl, duplicate-qualified-ue-readbacks.json,
  shared-ue-readbacks.jsonl, second-pass-plan.json, second-pass-removed.json and
  second-pass-verification.json.
- No files staged, committed or pushed. New maintenance tool, tests and planning
  records remain reviewable alongside the existing uncommitted UE work.
