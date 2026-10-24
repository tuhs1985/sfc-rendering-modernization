# Run149 — work-folder audit and cleanup

## Scope and outcome

User requested auditing the work folder and deleting old/unneeded files before
the next material investigation. Cleanup only; no renderer implementation or
gameplay run. Read current handoff/Run148. FuelGuard attached through existing
trusted hook; no daemon/helper/agent spawned.

Approximately **5.9GB reclaimed** before small audit/receipt overhead. Existing
uncommitted source/tests/docs/configuration preserved; no staging/commit/push.
No source-code retirement guessed from age alone: older diagnostic workflows
still referenced by regression checks, qualifications or evidence were retained.

## Audit and retention decisions

Initial artifact inventory: Remix-runtime21.190GB (includes dependencies),
D3D9-proof1.080GB, D3D9-intercept0.613GB; other collections smaller. Runtime run
folders15.842GB, dominated by generated DDS8.307GB and assorted binary packets/
uploads4.026GB, not a giant log file. Originals, required captures and dependencies
were not selected for deletion just because old.

Preserved:

- Actual repository `.git`, all source/scripts/tests/documentation and dirty work.
- Accepted `Game Assets`, `References`, M1/pre-M0 capture collections, original
  per-run gate/source packets, geometry/UVs, configs, logs/results and screenshots.
- Managed Toolkit and pinned1.5.2/isolated1.6.1 dependency installations/binaries.
- Six fixture roots referenced by current qualification receipts, including final
  normal `20261024-164956-518231-return-fixture`, kept raw. No qualification reset.
- Current material-analysis scripts, metrics, per-run restore manifests and NVIDIA
  one-shot material capture. No active investigation input removed.
- Final three performance benchmarks and their shared-light proof; these supersede
  the two earlier GPU preparation-output copies removed below.

## Removed permanently: disposable and superseded copies

-207compiler/cache/test-temp files2,514,980bytes, including root `m0_probe.obj`
 and Python bytecode caches. Temporary directories were resolved/checked inside
 the workspace before recursive removal. No authored source in cache inventory.
- Two superseded benchmark `gpu` trees under
 `artifacts/d3d9-proof/performance-mode-tests/20261023-215040-126036-performance`
 and `20261023-215046-995048-test`:515files each,
192,615,091+192,615,195bytes. Original gate packets and result.json retained in
 each parent, so these generated outputs can be rebuilt; no ZIP retained.
- Redundant `artifacts/github-verify-20261018` publication-verification clone:
656files12,828,059bytes including hidden Git files. Before removal, status was
 entirely clean INCLUDING ignored/untracked files, and HEADd9c7445 equalled its
 actual tracked upstream `origin/master`. Main repository/history untouched.
 This is a re-clonable verification copy, not an additional project worktree.
 Initial guard incorrectly tried origin/main and safely stopped before deletion;
 actual upstream was then inspected and used, never guessed/reset.
- Obsolete ignored `artifacts/backup_retired_toolkit.py`3,667bytes, a one-off
 helper for the already deleted old Toolkit tree/rollback. Current Toolkit,
 dependencies, original vendor download and earlier cleanup records retained.

These disposable files were deleted without payload backups. Detailed exact
path/size/SHA manifests live under `artifacts/workspace-cleanup-20261024/`;
those manifests are provenance, NOT recovery payloads.

## Historical generated evidence: compacted, not discarded

102additional historical run image sets:5,883,562,448loose bytes compressed to
373,268,322ZIP bytes, net5,510,294,126bytes before restore-receipt overhead.
Every entry was SHA256checked after decompression BEFORE each exact loose source
file was removed; source SHA rechecked immediately before deletion. Partial-run
payloads were archived as partial evidence, never relabeled successful tests.

Only generated `gpu/**/*.dds` and `texture-N.bin` selected, excluding vendor
`captures` directories, existing archived sets and protected qualified fixtures.
Raw captures, geometry, configs, logs, BMPs and associations stay loose. Tiny
single-file sets can have slightly larger ZIP overhead; total saving above is
net across all102sets, not a claim each ZIP is smaller.

Archives under `artifacts/remix-runtime/archives`; owning run's
`generated-images-archive.json` lists archive SHA and every entry's exact
relative restore path/size/SHA. Restore into THAT run directory before attempting
old image decoding; missing loose DDS after compaction is not capture corruption.
Verify archive hash first; do not overwrite changed files during restoration.
Existing Runs145–148 compaction receipts remain unchanged.

Ignored audit scripts: `artifacts/audit-clean-workspace.ps1` (plan then apply),
`artifacts/delete-retired-workspace-copies.ps1`. Detailed audit directory retains
plan/protected source snapshot/archived set totals/deletion manifests/summary.
Targets constrained to exact workspace/artifact descendants, reparse points
rejected, main workspace and broad roots never recursive deletion targets.

## Validation and final state

- All1,028preexisting source/test/doc/root file hashes matched before this
  deliberate documentation/handoff update. No existing uncommitted work lost.
- Both current multi-ship Performance and Test read-only game preflights PASS.
  No game, renderer or routine UAC launched by validation; protected current
  source/binary/config/client qualifications remain valid.
-24targeted tests PASS0.219s, then full495Python tests PASS8.228s.
  Existing Pillow getdata deprecation warnings only; no test failure. Temporary
  workspace TEMP/TMP used, bytecode disabled for validation; no global settings.
- `git diff --check` passes; index empty. Current HEADfe2eaf7, prior dirty files
  preserved; current versionable edits this record and HANDOFF only.
- Governed capture/evidence storage after cleanup13,256,574,897bytes, well below
  unchanged20GB cap; dependencies excluded by the established storage function,
  not newly reclassified to manufacture capacity.
- No capture/game process was active before cleanup; no runtime session created.
  Full old Toolkit rollback ZIP remains deleted per earlier user instruction;
  this cleanup does not recreate or silently remove another rollback payload.

Exact next action remains Run148's larger three-content/four-owner late-arrival
fixture with an explicit replacement-disable control and matched material-response
checks. No sponsor gameplay required for that offline investigation. Do not start
a runtime upgrade, flattening repair or broad discovery merely because space is
now available.
