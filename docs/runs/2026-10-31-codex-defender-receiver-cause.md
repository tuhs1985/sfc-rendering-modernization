# Run251 — Defender process-creation wait directly identified

## Confirmed cause in captured launch

Sponsor trace `artifacts/player-replacement/run248/trace-20261101-035523/receiver-startup.etl`(65,588,992bytes),fixture `20261101-035527-482764-return-fixture`. Observer attached before activation,started at actual readiness age50.150s and stopped after child receiver.log appeared. No SFC gameplay in this diagnostic.

Host PID36092,main thread6084. Measured CreateProcessW begins QPC5572766762095 and returns5572799537107 at10MHz: **3277.5012ms**. This run does not reproduce the exact five-second duration,but stalls at the same call.

Unlike the previous small-buffer trace,raw global CSwitch events span5572689878589..5572804355607 with364253events inside the exact call interval. Header11.779s,zero reported lost events/buffers. Raw coverage is checked independently of the loss counter;the wait is retained.

### Wait and reply chain

Main thread switches out at5572766768666,becomes ready at5572799528617 and resumes at5572799528671. Thus blocked **3275.9951ms**,then ready-to-run5.4microseconds. These raw times match the precise-CPU export's7.6958598..10.9718603s interval.

Switch-out stack:

```text
host -> CreateProcessW -> NtCreateUserProcess
 -> PspInsertThread -> PspCallProcessNotifyRoutines
 -> WdFilter.sys [three frames;private symbols unavailable]
 -> FLTMGR!FltSendMessage
 -> FsRtlCancellableWaitForMultipleObjects -> KeWaitForMultipleObjects
```

Readying/reply stack:

```text
MsMpEng.exe PID17464,thread21776
 -> MpRtp.dll -> fltLib.dll -> NtDeviceIoControlFile
 -> FLTMGR!FltpMsgDispatch -> FltpFilterReply -> KeSetEvent
```

**Defender's process-creation callback is synchronously waiting for its service's reply.** That wait accounts for99.954%of this measured CreateProcessW interval. This is direct attribution from retained wait/reply stacks and matched timing,not proximity of a security event or an unrelated driver frame.

The specific internal scan/rule/reputation/cloud policy remains unknown. No matching threat/ASR/CFA block event in the checked03:55–03:58UTC window(one other event). No evidence that the project was classified as malware. Do not claim signing,Defender exclusions or a configuration change would solve it. Earlier five-second waits occur at the same call but lack their own retained kernel attribution;this trace directly proves the3276mscase.

## Relationship to prior findings

- Run243 independently proved Defender holding the activation-file open. Shared-memory startup ticket eliminated that operation;it remains correct.
- This later receiver-process creation is a distinct protected operation. Same code/settings can launch it in3.891ms(Run246)or stall(Run247/standalonecases). No direct launch-call ordering change was found in cleanup;all retained slow cases are recent,so historical causality remains unproven.
- It is not model conversion,texture preparation,CPU diagnostics or GPU rendering time. It is also not a game compatibility failure:the fixture renders and exits correctly afterward.

## Verification and preserved evidence

`run251/defender-process-create-cause.json` contains full exported wait/reply rows and clocks. `main-wait-raw-summary.txt` independently records switch/ready clocks. Native OpenTrace/ProcessTrace decoder/status0,raw host events,main-thread HTML summary,precise CPU CSV,trace statistics and local export log retained in run251. Existing local Windows symbols used;no new downloads. Exporter emitted a command-option/unused ROI warning,but produced the main-thread table;raw clock matching and kernel-module stacks independently support the result. One unrelated invalid-event warning in summaries names another process;it does not remove this wait's verified raw events.

Fixture passes600frames,two pixel/depth/text verifications,zero state errors,child/host0,normal owned exit. Job receipt remaining_owned_processes0,peak scratch98,995,126bytes. WPR status:not recording. Current AntivirusEnabled,RealTimeProtectionEnabled,BehaviorMonitorEnabled all true. No security/renderer/material changes or new agent runtime campaign.

## Next engineering step

No further discovery trace required. Prepare the session-owned output receiver/channel during launch preparation rather than after fresh assets are ready. Keep it passive until activation,retain session identity/process-death/cancellation validation,and start active-work timeout at activation. This removes a blocking Windows-protected operation from first-ship readiness without weakening Defender. It overlaps/moves the security wait;it does not eliminate or bypass the underlying security check. Do not add another rendering architecture or alter materials to address this.

Implementation of early receiver startup is **not done in this review**. Preserve existing accepted gameplay pipeline. Record stable release/signing/Defender compatibility as later distribution evaluation,not an unproven fix. No further sponsor action needed for diagnosis. Changes unstaged/uncommitted.
