# Run242 — sponsor Windows trace review;compression excluded,filter attribution still unresolved

Sponsor completed `artifacts/player-replacement/run241/admin-trace-20261101-003102/activation.etl` (UTC folder name; sponsor-local date remains2026-10-31). Fixture `20261101-003107-004277-return-fixture`:600frames,three owners,zero pixel/state errors,child0;renderer job0,remaining owned processes0. No SFC launched. Wrapper's final fixture-path receipt was absent;association is independently supported by session files/PID51776 and times. WPR is no longer recording.

## Verified outcome and correction

-104-byte activation-file open took6.2538056s;stream construction2.5us. Trace111,149,056bytes,23.2616855s window. Native trace statistics report0lost buffers/events.
- User suggested folder compression. Read-only attributes and `compact /Q /A` confirm current project root,artifact root,run GPU folder and exact activation file are **not compressed**. File stores104bytes in104bytes;new files in that output directory do not inherit compression. This excludes compression for this case,not every directory on the machine.
- The resolved main-thread stack contains `NtfsAcquireFcbWithPaging -> ExAcquireResourceExclusiveLite/ExpWaitForResource -> KeWaitForSingleObject`. **Important correction:** timestamp alignment places it before activation,not in the6.25s wait. It must not be cited as the cause of that wait. Earlier commentary's provisional NTFS-lock attribution is withdrawn.
- Main thread38488 has36recorded context switches and17ready records confined to the first0.1596s of tracing.43stack records include later process creation/shutdown but **zero stack/switch/ready records inside the activation interval** (QPC5450134837287–5450197375368,10MHz). Native ProcessTrace API confirms this independently of WPA export. The reason for the selective coverage gap is not established;do not equate header lost-events0with sufficient coverage of this wait.
- GeneralProfile did not enable FilterIO/FilterIOInit. Native minifilter-delay analysis reports no data. `WdFilter.sys` appears in an unrelated recorded stack,which is not evidence that Defender caused this delay. No malware detection/security rejection established.

## Analysis and permissions

Used installed Microsoft WPAExporter and xperf,then documented native [ProcessTrace](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-processtrace) to inspect raw events when table exports were incomplete. Trimmed-profile rejection,ROI-export warnings and an invalid metadata event are retained;raw native records/status0are the coverage authority. No new gameplay or GPU runs were performed in this review.

Automatic approval review initially rejected downloading public symbols because module/build identifiers would go to Microsoft. Sponsor explicitly approved that lookup. Microsoft public symbols were then downloaded;trace/game assets/chats stayed local. Local-symbol attempts preceded approval. No security exclusions/settings changed.

A broad xperf symbol decode unexpectedly cached an unrelated685,797,376-byte Edge PDB,temporarily exceeding the20GB aggregate by~97MB. That re-downloadable unrelated cache file was removed after exact containment checks;cleanup receipt retained. No trace/input or relevant kernel symbols deleted. Two closed Run240fixture generated image sets were archived losslessly with per-file SHA256verification before loose copies were removed (~113MBreclaimed);logs,geometry and original assets unchanged. Further analysis should use local cached symbols or restrict symbol acquisition to needed modules. Do not allow broad automatic whole-trace symbol downloads again.

## Prepared focused capture

`artifacts/player-replacement/run242/trace_activation_filters.ps1` replaces GeneralProfile with Microsoft's exported **Minifilter** profile (FileIO,FilterIO,FilterIOInit,FileCreate/FileOpEnd and filter-callback stacks,plus native antimalware providers),not an invented hook. See [Microsoft built-in recording profiles](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/built-in-recording-profiles) and [Minifilter diagnostics](https://learn.microsoft.com/en-us/windows-hardware/test/assessments/minifilter-diagnostics).

Uses file recording instead of circular memory,96/16MiB buffers,192MiB recording stop threshold,256MiB final trace check,late startup during synthetic idle,and stops12s after activation signal or verified pixels. Existing150s observer bound/owned fixture cleanup remain. Unique evidence folder,elevation/existing-session checks,no SFC,no security policy changes. PowerShell parser and WPR profile parser pass;not executed here because full administrator token remains necessary.

**Next sponsor action:** run focused capture from existing Administrator PowerShell. Then correlate the exact activation filename's create/complete times and filter callback durations. This is needed to distinguish a filter delay from filesystem contention without guessing. Current trace does not justify blaming Defender,changing compression or tuning models. Pipeline behavior unchanged;no commit/push.

Review evidence: `artifacts/player-replacement/run242/trace-review.json`,raw ETL/native record exports in Run241. Keep raw trace/symbols/generated exports ignored and private.
