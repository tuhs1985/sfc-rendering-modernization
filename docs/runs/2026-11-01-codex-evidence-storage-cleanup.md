# Run263 — Evidence reservation restored; generated-support consolidation

Sponsor reported launcher rejection after `Recovered prior interrupted test`. The recovery receipt confirms proxy/config restoration and absent game. The following exception was the independent20GB aggregate evidence reservation check,not a failed second cleanup. Native multi-ship launch reserves544MiB before starting any new processes.

## Audit and cleanup

The evidence allowance was using19.540GB at this checkout's initial cleanup. After the first small archive pass,the audit found11.935GB in runtime run folders,4.392GB in archives and2.201GB in investigation records,plus the other counted evidence roots. Much of the run-folder size was duplicated support binaries and synthetic images,not unique captured game state.

- Losslessly archived closed successful-run converted DDS/texture copies with per-file SHA256 verification and recovery manifests,as in earlier evidence housekeeping.
- Consolidated **1,652old closed-run generated support files**,3,135,371,896raw bytes,into a **44,798,782byte content-addressed ZIP** containing360distinct file contents. Manifest preserves every original path,size and hash. All ZIP contents and all loose originals were verified before removing the loose copies.
- Selection is restricted to old202610run folders with result.json and explicit generated support names:copied dxgi.dll,synthetic fixture-ship BMPs,fixture/return test executables and runner-host snapshots. Qualification/build reference paths were collected and excluded. Current dependencies,source/configuration,original game assets,captured geometry/state,logs,rollback files and recent stress evidence were not selected.
- Removed252.402MiB of rebuildable Windows symbol-processing `.symcache` files from closed Run241/242 investigations,with no active trace-analysis tool. Original trace files,symbol files and analysis records remain. Cache deletion ran during support consolidation,so that script's before/after delta includes it;do not double-count those figures.

Final measured evidence usage: **16,032,139,170bytes**,leaving **3,967,860,830bytes** under the unchanged20,000,000,000byte allowance. Net reduction from the initial19,540,310,527bytes is **3,508,171,357bytes** (minor later receipt growth excluded). No allowance increase,Defender change,NTFS recompression of active runtime files or blanket evidence deletion.

## Recovery and validation

Local receipts/scripts are in `artifacts/player-replacement/run263`. `closed-support-manifest.json` maps original paths to SHA256 ZIP entries. To restore one exact archived generated path,use the bundled Python with `artifacts/player-replacement/run263/restore_closed_support.py` and the manifest's repository-relative path. The helper verifies the full archive and selected contents,restricts output to old run folders and refuses to overwrite different files.

Current native multi-ship read-only preflight passes after cleanup. It verifies existing source/binary/evidence pins and copied baseline and starts no SFC/renderer. A recovered sample ZIP member was independently hash-checked. Whitespace checks pass. No renderer code was changed for this storage task.

**Next remains the hull fix:** the isolated32-entry physical-hull submission array is still unfixed;do not present restored launcher availability as permission to repeat the same oversized carrier test unchanged. Effect lights remain disabled per sponsor scope correction. Light-emission recorder/integration remain pending. Changes unstaged/uncommitted.
