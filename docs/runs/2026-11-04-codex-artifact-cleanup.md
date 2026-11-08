# Run295 — Obsolete generated-output cleanup

Sponsor requested another project-folder cleanup. Deleted8,926obsolete generated
files:3,271,724,236logical bytes(~3.27GB). Measured disk-free increase:
3,241,152,512bytes(~3.24GB),209,810,808,832→213,051,961,344bytes.

## Selection and preservation

-3,208,622,284bytes of old generated GPU inputs/derived image copies.
-63,101,952bytes of closed historical per-run executable copies.
-All removal was individual files in dated runtime runs before20261104.
  Every resolved absolute target was checked beneath the exact runtime runs
  directory,with reparse/symlink checks and recorded-size verification before
  deletion. No recursive directory removal and no archive repacking.
-Preserved every current-day run,including campaign evidence,damage comparisons,
  accepted GPU proofs and failed startup evidence. Original gate/mesh/state
  captures,raw diagnostic timelines,traces,all archives,comparison images,
  source-referenced historical runs and exact qualification inputs retained.
-Current builds,dependencies,pinned runtimes,user/source files,Git history,
  current settings,Game Assets/References and both game installations untouched.
  No game/renderer was running. No staging,commit or push.

Local inventory,selection,per-file deletion ledger and source fingerprints:
`artifacts/workspace-cleanup-20261104/`. Missing generated copies listed in
`deleted.json` were intentionally pruned;rebuild obsolete fixtures if necessary.
Do not interpret them as new capture or renderer failures.

## Verification and unrelated existing blocker

All1,499fingerprinted tracked/untracked non-artifact source/user files unchanged
during cleanup. Full684Python tests PASS on recheck. Initial test pass encountered
known transient Windows ReplaceFileW1175in the material-publication held-reader
test;the unmodified suite passed on repeat. No missing-input errors or code changes.

Read-only launcher preflight is BLOCKED by the pre-existing campaign preference
change:copied `sfc.ini` no longer matches its frozen prepared hash. The Run294
review already identified only PlayerName differing from the accepted baseline.
Original INI still matches the frozen prepared hash. Neither INI was edited by
this cleanup. This is unrelated to removed artifacts. Preserve the preference
and address the overly broad campaign-config freeze separately before the next
launch;do not disable all baseline/client verification or silently overwrite it.

Rendering work remains Run294's multi-mission review:one reported dropout and
gray KFF wing appearance awaiting a focused comparison. Cleanup makes no new
rendering/campaign compatibility claim.
