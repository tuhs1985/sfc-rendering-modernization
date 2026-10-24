# Run143 — post-cleanup regression review; full rollback ZIP released

Sponsor reports regression good and authorizes deleting the ZIP if evidence
agrees. Reviewed `artifacts/remix-runtime/runs/20261024-160129-809815-in-game`
without altering raw evidence. This is a cleanup regression adjudication, not
a new milestone, loading optimization or universal model-coverage claim.

## Verified execution

- Three fresh assets KFF, FCA and FMS admitted; respective owner/revision draw
  counts 4,713 / 4,713 / 2,792. No asset partials/rejections or header, packet,
  identity, decode or projection failures. Persistent registry: 17,421 position
  updates, including 10,845 offscreen; zero failed updates.
- 4,692 matching game compositions; synchronized-buffer failures zero,
  max recorded age 22.656ms. There were 107 without-ship records, two warmup
  and one reset; sponsor's good appearance is not interpreted as zero omissions.
- Native owned job exit0/stop_reason0, no remaining owned processes, peak
  scratch 92,964,570 bytes. Renderer exit0. Controller exit0, hooks restored,
  component unloaded, no controller left running. Original critical files and
  launcher settings unchanged; copied proxy restored. Launcher verifies test
  child path/disk identity and ends `CHILD_EXIT code=0`.
- Runtime report is still PARTIAL with exact retained error:
  `Normal game exit not yet confirmed; do not kill SFC`.
  Source initially waits up to30s after exit cue, then retains the exception
  even when final cleanup subsequently confirms normal exit. Final
  `normal_game_exit=true`, complete report and launcher exit0 corroborate safe
  late exit. This timing caveat does not invalidate the targeted cleanup
  regression; do not rewrite the raw PARTIAL as an unconditional runner PASS.
- Combined with sponsor observation, cleanup regression ACCEPTED. No evidence
  that removing the old Toolkit damaged the current in-game path. No source
  fix to the exit-wait/reporting behavior is included or required for deletion.

## Authorized archive removal

Deleted ONLY
`C:\Project\RTXRemix-Standalone\rollback-20261024-115425\portable-toolkit-full.zip`
after verifying exact resolved path, non-reparse file, size 2,245,407,607 bytes
and SHA256 `5247602b31eb5fdc3400d5d1fddaa7d0f5b69be973bf0b41e998845e3a019e51`.
Absence confirmed. This is permanent file deletion, not Recycle Bin recovery.

Keep original vendor ZIP
`C:\Project\RTXRemix-Standalone\download\rtx-remix-1.6.0-dev-main.3f23f80a.zip`,
the full backup's small manifest/verification records, all saved jobs, managed
Toolkit, pinned runtimes and game evidence. The deleted archive can no longer
restore the old tree's local changes; original vendor ZIP restores vendor
content only. Run142's full-rollback instructions are historical, NOT presently
usable. Historical preview/inspection tools remain retired.

No stage/commit/push, renderer/config changes, game launch or new capture.
Prior cleanup docs preserved unstaged; this record and newest HANDOFF added.
Fast validation: parsed final run/analysis/job results, controller/component/
launcher logs, deletion identity/absence checks and `git diff --check`.

Exact next action: resume the previously approved bounded startup-loading
profiling investigation with installed Nsight; keep current D3D9/runtime
baseline and vendor material semantics unchanged until evidence supports a fix.
