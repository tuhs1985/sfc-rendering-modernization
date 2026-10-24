# Run142 — commit and retire redundant portable Toolkit

**Later disposition:** [Run143](2026-10-24-codex-cleanup-regression.md) accepted
the post-cleanup regression and permanently deleted the full rollback ZIP on
user instruction. Backup creation/verification below remains historical fact;
full-archive restoration instructions are no longer executable. Original vendor
download and small manifests remain, but do not preserve old local changes.

User authorized committing current work, cleanup with rollback preparation, then
a sponsor game test. No new renderer implementation or Toolkit migration.

## Pre-cleanup checkpoint

Committed existing source, tests and durable evidence as
`fe2eaf76b756f4aa1fab3353cec44d42f85fd771`
(`Implement retained multiship pipeline and document startup investigations`).
No push requested/performed. Versionable text/code only; ignored proprietary
dependencies, game assets, generated captures and backups remain outside Git.
Entire selected branch publication audit: 21 commits, 1,195 unique blobs,
15,503,335 blob bytes; zero blocked or credential-review findings. This is a
heuristic check, not a guarantee of universal secret detection.

## Scope and rollback

Only `C:\Project\RTXRemix`, the extracted 1.6.0-dev Toolkit, is retired. Preserve
the managed `C:\Program Files\NVIDIA Corporation\RTX Remix`, both pinned project
Remix 1.5.2 dependency trees, all `C:\Project\RemixJobs`, original download ZIP,
per-user preferences and current SFC/client installations.

Backup directory: `C:\Project\RTXRemix-Standalone\rollback-20261024-115425`.
`portable-toolkit-full.zip` preserves the CURRENT tree, including local patches,
generated files and empty directories, rather than assuming the original vendor
download is enough. `manifest.json` records each original file's size, time and
SHA256; `verification.json` records the final archive hash and verification.
Verification decompresses every file and compares size/SHA256 with bytes read
from the source, then checks the source inventory did not change. No source
removal is permitted before that verification succeeds.

Rollback: close the Toolkit, confirm `C:\Project\RTXRemix` is absent (never
overwrite another installation), verify the archive SHA256 against
`verification.json`, create that exact empty directory and extract the full ZIP
there. Verify each extracted file against `manifest.json` before using the old
tools. The original vendor ZIP is also retained but is NOT a substitute for this
full current-tree backup. Backup is outside the repository and separate from the
20GB governed runtime-evidence budget; no new game/GPU capture was taken.

Historical `run_mesh_preview.py`, `run_remix_ingest.py` and
`tools/d3d9_proof/inspect_intercept.py` are explicitly retired pending rollback or
separate managed-Toolkit qualification. Their source/version/path guards remain
unchanged. Retirement notices in both tool READMEs supersede their old launch
instructions. No unqualified path replacement, junction or runtime upgrade.

## Validation and disposition

Pre-removal: 488 Python tests PASS (8.729s); Performance and Test read-only
multi-ship game preflights PASS. Source qualification unchanged: only README/
run/handoff documentation changes after the checkpoint commit. Saved jobs before
cleanup: 2,287 files / 130,965,303 bytes; full per-file SHA256 snapshot saved to
`artifacts/d3d9-proof/cleanup-jobs-before.json`. Managed VERSION/Kit executable
and both pinned runtime DLL hashes recorded in `cleanup-protected-before.json`.

Final backup/removal verification and post-cleanup results are recorded below.
No gameplay claim can be made until sponsor runs the unchanged multi-ship test.
Sub-two-second loading target remains OPEN; cleanup is not a performance fix.

## Completed result

- Full backup verified in 159.703s: 42,472 files / 4,914,104,839 source bytes;
  compressed archive 2,245,407,607 bytes. Archive SHA256
  `5247602b31eb5fdc3400d5d1fddaa7d0f5b69be973bf0b41e998845e3a019e51`.
  Archive plus manifest/verification total 2,257,634,296 bytes; net file-byte
  reduction 2,656,470,543 (~2.66GB). Actual disk allocation/reclaim can differ.
- Before recursive removal, exact resolved target, no running Kit process,
  no reparse entries, file count/size and archive SHA256 were checked again.
  ONLY `C:\Project\RTXRemix` removed; absence confirmed. Recoverable from the
  verified full backup above. No uninstall of the managed application.
- After removal, all 2,287 saved job hashes and protected managed VERSION/Kit
  executable / both pinned runtime DLL hashes match their pre-cleanup values.
- Post-removal 488 Python tests PASS (7.869s). Both Performance and Test game
  preflights PASS: client/dependency/source qualifications accepted, no game or
  renderer launched. Existing native/GPU qualification is retained, not rerun
  or represented as new gameplay validation. `git diff --check` PASS.
- Cleanup changed documentation only: this record, authoritative HANDOFF,
  `tools/remix_ingest/README.md`, `tools/d3d9_proof/README.md`. These follow-up
  changes remain unstaged after the requested pre-cleanup commit; no push.
  Backup/inventory scripts and hash snapshots remain ignored local artifacts.
- No live test/debugger/server session left by this run. No source/runtime,
  appearance settings, client assets, driver or security policies modified.

Exact next action: sponsor launches the existing multi-ship session, checks
normal ships/HUD/controls and returned textured ships, then exits at the runner's
request. This is a post-cleanup regression run, not another architecture proof:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_multiship_session.ps1"
```
