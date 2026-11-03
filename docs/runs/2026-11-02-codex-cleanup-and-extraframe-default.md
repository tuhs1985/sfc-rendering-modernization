# Run277 — ExtraFrame default and evidence cleanup

Sponsor requested cleanup before another normal run and a permanent ExtraFrame selection.

## Launcher

`tools/native_insertion/start_native_multiship_session.ps1` now defaults to ExtraFrame. Both PowerShell5 forwarding and the normal PowerShell7 path pass the selected policy explicitly. `-TimingPolicy Strict` remains available for comparison. No renderer, resource contract, frame cap or appearance setting changed. `-CompletionDiagnostics` remains opt-in and is absent from the ordinary command:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\native_insertion\start_native_multiship_session.ps1"
```

Basic performance records, ownership checks, cleanup and existing test duration remain. This is not a zero-logging or unlimited-play launcher.

## Cleanup

Losslessly compressed generated GPU DDS copies from29older closed tests. Recent gameplay/stress runs and current standalone qualification cases remain loose. Selection requires completed game or fixture processes and owned GPU job remaining0; both successful and partial older results are eligible, because the archive preserves exact bytes and their failure evidence remains unchanged. Cutoff is20261102-120000UTC. Qualification/build-referenced file paths are excluded.

Every selected file is hashed, compressed, fully decompressed and hash-verified, then rechecked loose before unlinking. Resolved targets must remain under the original runtime-run directory and have no symlink/reparse parents. Archive staging is bounded by remaining allowance. No recursive directory deletion or cross-shell deletion. Logs, original captures/geometry/state, configuration, rollback files, dependencies, traces and game installations are preserved.

- Before:19,517,619,192bytes.
- After:18,287,270,206bytes.
- Reclaimed:1,230,358,116bytes(about1.23GB).
- Free within unchanged20GB allowance:1,712,729,794bytes(about1.71GB), sufficient for the normal570,425,344byte next-run reservation.

Small later receipt growth is excluded from these point-in-time figures. This is evidence-budget space, not total disk free space or NTFS compression of active files.

## Recovery and checks

Archives are in `artifacts/remix-runtime/archives/*-run277-dds.zip`. Each affected original run retains `run277-dds-archive.json`, identifying archive path/hash and each member's original run-relative name, size and SHA256. To restore, verify the archive hash, extract the selected member to that original run-relative path, and verify its recorded hash; do not overwrite a different existing file. All archived bytes were independently verified before the loose copies were removed.

Local plan/progress/receipts and compactor are retained under `artifacts/player-replacement/run277/`. Summary records the two cleanup passes without double-counting. Nothing is published automatically.

PowerShell AST parsing confirms ExtraFrame default with Strict override retained. Reproducible host build remains byte-identical `EC6CB79A36838EF8254F726202AD1B0B9DA24365F16969083602F06C24CD37A4`. Source qualification refreshed for the launcher-only default change using existing unchanged rendering evidence; no new GPU/gameplay test was needed. Actual read-only ExtraFrame performance-mode preflight passes with optional completion diagnostics off. No game/renderer launched during validation. Whitespace checks pass. Changes unstaged/uncommitted; unrelated memory audit preserved.
