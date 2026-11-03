# Run248 — receiver-launch history audit; kernel trace prepared

## Evidence review

Compared297retained startup profiles (each source log bounded2MiB). Four materials_enabled-to-receiver_started intervals exceed one second:Run244 ExtraFrame5002.191ms,Run245 ExtraFrame5002.315ms,Run245 sampled Strict5002.698ms,Run247gameplay5001.408ms. Earlier retained profiles back to October24 show fast launch;all four observed stalls occur in the latest startup-ticket investigation. This temporal association deserves attention;do not say the delay was simply hidden by old diagnostics or declare cleanup unrelated. It does not establish which change or system condition caused it.

Compared Run246 fast and Run247 slow gameplay manifests:build_hashes,gate_build_hashes,accepted/copied critical hashes,launcher settings,pipeline policy,timing policy and backend dependency receipts have no differences. Same build/configuration supports both3.891ms and5001.1004ms CreateProcessW measurements. The unknown is intermittent,not a deterministic requirement to build many ships.

Git history shows OutputPeer.start's CreateProcessW flags,explicit receiver path,command construction and no-handle-inheritance policy already existed in0fc1300(October21). HEAD7320eae already launches the receiver after warm activation,scene loading and material enabling,as current source does. Working-tree differences there are opt-in QPC markers,not launch relocation,priority,environment-selection or security-policy changes. The shared-ticket change does add session-mapping attachment/lifetime checks before that point;inspection finds bounded reads,CAS,handle waits/unmapping,not an intentional five-second wait. No causal exclusion follows from this static review.

Existing Defender Operational events over23:18–23:32local time:cloud intelligence updates,healthy-client reports and a UX ToastOrSsoTrigger configuration event. No matching threat/ASR/CFA block event appears. Cloud events do not name the receiver or establish the five-second cause. No settings changed by this investigation. Full event export stays local in artifacts/player-replacement/run248/defender-events.json.

Run245's29/30samples already locate the wait inside NtCreateUserProcess. Microsoft documents that driver process-creation callbacks execute in the creating thread,and its security documentation describes antimalware process-creation scanning. These establish a possible mechanism,not attribution to Defender or any specific installed driver:

- [Microsoft process-notification interface](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutineex)
- [Microsoft process-creation security discussion](https://www.microsoft.com/en-us/security/blog/2022/06/30/using-process-creation-properties-to-catch-evasion-techniques/)

## Next evidence and actual execution blocker

Current process has no full administrator token or SeSystemProfilePrivilege;WPR is not recording. Existing general/file-filter traces did not capture this later reproduced process-creation stall. Another ordinary gameplay run or more user-mode samples would repeat established evidence. Exact Windows-side attribution needs a narrow kernel process/wait/filter trace from the sponsor's established Administrator PowerShell.

Prepared artifacts/player-replacement/run248/trace_receiver_startup.ps1 and trace_receiver_startup.py with receiver-startup.wprp. **Not executed here.** Windows profile-details successfully parses it as Memory mode. Python syntax and PowerShell parsing checked;live recording/finalization remain unqualified until executed.

- Standalone existing native-player fixture,not SFC. It uses same renderer/receiver and one retained player;it does not establish multi-ship correctness. Selecting the smaller existing fixture preserves288MiB fixture reservation plus128MiB trace-output reservation under20GB;not a change to gameplay capacities.
- Reads existing startup cell read-only;no obsolete activation/readiness files. Starts tracing50seconds after private readiness during the existing60second simulated menu interval;stops8seconds after observed acceptance or20seconds after trace starts. Maximum observer150seconds;existing fixture/job cleanup watchdog retained.
- WPR32MiB circular memory buffers,process/thread/loader/context-switch/sample/file/filter events and relevant stacks. No sequential file-mode capture. Finalization compressed,skipPdbGen,no new symbol downloads. A128MiB final-output check reports partial if exceeded;buffer budget is bounded,but final merge metadata means this is a validation ceiling,not a mathematically guaranteed final file size.
- Refuses existing/unknown WPR session,nonadministrator token,running SFC or insufficient evidence reservation before starting. Stops only its owned trace on normal/error cleanup. Captures no game screenshots or asset payloads through ETW;system trace may contain local process/module/file identifiers and remains local.
- Existing Microsoft guidance recommends memory mode to limit size:[logging mode](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/logging-mode),[WPR command options](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/wpr-command-line-options).

No production implementation edits,security changes,new gameplay run,staging or commit. The previous gameplay checkout remains functionally accepted. Early receiver preparation remains proposed mitigation only;do not change startup ordering before reviewing this cause evidence.

## Sponsor action

From the existing Administrator PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\artifacts\player-replacement\run248\trace_receiver_startup.ps1"
```

No SFC/manual gameplay actions. Usually under two minutes. A fast receiver launch is still useful comparison evidence;inspect result before requesting any repeat.
