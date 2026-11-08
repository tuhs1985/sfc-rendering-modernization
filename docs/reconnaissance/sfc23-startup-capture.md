# SFC-23 startup comparison

Reopened November 6, 2026. The user reports a delay of 20 seconds or more on the first SFC launch after a restart or a day of idle time, regardless of the launcher used. The cause is open. Start with the normal SFC shortcut to isolate the game startup path.

## Capture

After a restart or a long idle period that usually reproduces the issue, run the first command from Administrator PowerShell. `-Launch` starts the accepted `StarFleetOP.exe` with its game folder as the working directory as soon as recording starts. It records the launch request and its return. The request goes through the signed-in Explorer desktop so the game gets the desktop launch context. This comparison uses direct game startup. Use the same mode for both passes.

Once the menu accepts input, return to the console and press **R** to save the trace. Exit the game normally and run the repeat command promptly in the same boot. To compare a specific shortcut or SFCLauncher Play action, omit `-Launch` on both passes and start it at `TRACE READY`. In that mode **L** marks the approximate time before switching to the launcher.

```powershell
$trace = 'C:\Project\SFC-Modernize Engine\tools\recon\trace_sfc23_startup.ps1'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $trace -Pass First -Launch
# After saving the first trace and exiting SFC normally:
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $trace -Pass Repeat -Launch
```

The script streams WPR events to disk to retain the beginning of startup. It polls the trace size every 250 ms and requests a stop at 768 MiB or 65 seconds, whichever comes first. Finalization can increase the file size, and traces above 1 GiB are flagged for review. It saves traces and a UTC timeline under `artifacts/player-replacement/sfc23/`. It refuses to start when SFC or an existing WPR capture is active. The **R** marker includes the time to switch windows, so treat it as an upper bound on menu readiness. The script observes the game window separately from the marker.

## Review

Compare both timelines for the same executable path and boot timestamp. Check trace loss and coverage before assigning a cause. In WPA, correlate process creation, image loads, UI-thread waits and readying stacks, CPU usage, and disk and file activity against the delay. If the delay precedes game process creation, inspect the launch path. If it occurs in the process, identify the blocked operation and corroborate it with the repeat trace. A known delay in a different experiment does not establish the cause here.

`-CheckOnly -Launch` verified the revised WPR profile, idle recorder, executable path and Explorer launch interface. Live capture and the direct game launch still need the user's Administrator desktop session. See [Microsoft's WPR command reference](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/wpr-command-line-options) and [Explorer desktop launching](https://devblogs.microsoft.com/oldnewthing/20131118-00/?p=2643).

## November 6 first comparison

Both launches used the same accepted `StarFleetOP.exe` path, the same persistent SFCLauncher parent and the same Windows boot. The first launch was about 24 hours and 48 minutes after boot. The user confirmed the hang reproduced. The first recorder timed out, so only the repeat has a menu-ready marker.

| Observation | First | Repeat |
| --- | ---: | ---: |
| Trace ready to game process creation | 33.20 s | 4.79 s |
| Process creation to first observed window | 0.16 s | 0.10 s |
| Process creation to menu marker | — | 13.20 s |

Trace-ready time includes user interaction. The difference in that row cannot be assigned to the launcher or game. The first memory trace's earliest reliable context-switch timestamp was 36.79 seconds from ETL start, about 3.52 seconds after the game process was created. The creation event appears only as rundown. The repeat retained actual process and primary-thread creation events. Both report zero lost events, which does not establish memory-buffer coverage.

The retained first trace contains ReShade shader/cache I/O and game sound initialization about 3.3 seconds after process creation. The repeat contains comparable ReShade and sound work. Those events alone did not attribute the hang.

## November 6 post-reboot direct launch

`20261106-054737-918-First` saved a complete 35.89-second ETL with zero reported lost buffers or events. The file finalized at 1,557,135,360 bytes. The size warning followed a successful save. The polling threshold did not bound final size on this run. The user skipped the repeat after seeing the warning.

Explorer's launch request preceded game process creation by 120 ms. The main thread was TID 2988 in PID 2904. The raw context-switch analysis found 36 waits of at least 10 ms ending with a wakeup by Microsoft Defender PID 5928, totaling 19.11 seconds off CPU. The largest was 1.221 seconds during mission-script file activity for `Assets/scripts/Met_6Patrol.scr`. Xperf corroborated the wait boundary, `WdFilter.sys` and `FltSendMessage` on the blocked stack, and `MsMpEng.exe` waking the game thread. ReShade finished its initial logged setup roughly 3.2 seconds after process creation. The trace therefore identifies Defender file scanning on SFC's startup thread as a major cause in this run.

The affected script uses WOF compression in the accepted install. The verified test copy has 107 uncompressed files in its scripts directory. Compression's contribution has not been isolated. A subsequent comparison can use the uncompressed test copy while keeping Defender enabled and the accepted install read-only.

## November 6 local resolution

The sponsor added a Defender folder exclusion for `C:\Project\SFC-Remix-Return-Test\Assets\scripts` and reported no 20-second pause on the first launch after a fresh restart. The sponsor considers the recurring slowdown resolved on this setup. The trace identifies Defender scanning as the cause of the stall. Why that scan took so long remains unknown. Parked with no further capture planned.

For a lightweight warm timing sample, add `-TimingOnly` to `-Pass Repeat -Launch`. This records launch, process and menu markers in `timeline.json` without a kernel trace. Use the same launch path and record when the repeat was run. The prior warm capture used the same game executable via SFCLauncher, so it is a separate launch-path comparison. Both new entry points passed `-CheckOnly`. Local analysis is alongside the post-reboot ETL in `main-waits.txt`, `longest-wait-start.txt`, and `ReShade.log`.
