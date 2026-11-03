# Run241 — Windows file-open wait research

## Findings

The long activation stall is inside the Windows kernel file-open operation,not the C++ stream constructor,model production or GPU draw. The precise kernel-side holder remains unresolved;kernel wait tracing is blocked by the current agent token's missing system-profiling privilege.

Three standalone Strict,three-owner,600-frame fixtures were used;no SFC launched:

| Fixture | Result |
| --- | --- |
| `20261031-232811-378490-return-fixture` | Fast activation: default stream construction2.8us,open5.7115ms. Rendering passed. WPR attempt failed before recording with0xc5585011;the already-running standalone fixture completed normally. |
| `20261031-233106-971898-return-fixture` | Default stream construction2.1us,open5.7597821s.30bounded main-thread samples show `ntdll!NtCreateFile`. Rendering passed. |
| `20261031-233506-532105-return-fixture` | Default stream construction4.2us,open7.3804849s.30bounded samples identify `NtCreateFile` requesting the exact session's `gpu/renderer-activate.bin`,with `CreateFileW` and host/static-runtime caller frames. No vendor user-mode frame intervenes in this captured chain. Rendering passed. |

Sampled runs are diagnostic reproductions,not performance comparisons:the external sampler briefly suspends only the owned renderer main thread to capture context/unwind. First full stack sample~6.4ms,subsequent~0.5ms each;do not use these runs as unperturbed timing benchmarks. No SFC thread was sampled or suspended. All renderer jobs exit0 with remaining_owned_processes0;600frames,three owners,zero pixel/state errors. Existing vendor teardown warning retained.

A separate plain-process control used the same104-byte payload,atomic producer rename andeight fresh files:four Win32 opens,four C++ stream opens. All validated;open0.386–0.510ms. This control did not reproduce the wait without Remix,but does not prove that Remix causes it:directory/timing/process context differ and the problem is intermittent.

## Research and limits

- Microsoft's [basic_ifstream documentation](https://learn.microsoft.com/en-us/cpp/standard-library/basic-ifstream-class?view=msvc-170) separates stream/base construction from file-buffer open. Installed MSVC14.51 sources (`fstream`,`__msvc_filebuf.hpp`,`crt/src/stl/fiopen.cpp`) show the native wide-file open and optional end seek;there is no deliberate multi-second retry in those inspected paths. New markers separate those operations.
- Microsoft's [StackWalk64 documentation](https://learn.microsoft.com/en-us/windows/win32/api/dbghelp/nf-dbghelp-stackwalk64) supports the external bounded sampler. It reads an explicitly verified owned `d3d9_direct_host.exe` PID from its session readiness receipt. No injection,context writes or remote calls. Microsoft symbol APIs are called from one sampler thread. Raw addresses/names remain ignored local evidence.
- Microsoft's [oplock documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/breaking-oplocks) establishes that file-open operations can wait on oplock break acknowledgement. Filesystem filters are another candidate;neither is established by the user-mode stack. Do not label this a Defender/NVIDIA/NTFS bug without a kernel-side trace.
- Read-only Defender operational events were accessible outside the filesystem restrictions,but did not identify the requested file or establish causality. Presence of protection/cloud events is not proof of interference. Filter enumeration (`fltmc filters`) was denied. No protection was disabled or excluded.
- [WPR documented memory-mode recording](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/wpr-command-line-options) was attempted using exported GeneralProfile with system/event buffers reduced to96/16MiB. WPR was not already recording. It rejected profiling permission;no trace session remained active. The token lacks `SeSystemProfilePrivilege`;sandbox escalation does not supply a full administrator token.

## Smallest remaining action

Use the prepared `artifacts/player-replacement/run241/trace_activation.ps1` from the established Administrator PowerShell parent. It checks elevation and refuses to interfere with an existing WPR session,launches only the standalone fixture,starts the reduced-memory trace late in the synthetic60-second idle,saves after first verified pixels,and stops its own trace on failure. Full workflow bounded150seconds plus existing fixture watchdog/trace finalization. A unique local evidence folder is created;no game or security-policy changes. Kernel stacks are needed to distinguish the responsible filter/lock/IO wait. No further unprivileged GPU repetition is justified.

The prepared trace and timing binaries are local evidence under the existing20GB allowance,not public repository material. Evidence inventory after investigation18,784,227,780bytes (~1.22GB headroom);the trace memory buffer is112MiB. Existing runtime output/scene limits and appearance remain unchanged.

## Changes and evidence

Only additional implementation edit beyond Run240:split the equivalent stream constructor/open to place an optional timing marker between them. /W4 /WX host build and git diff --check pass. Gameplay qualification fingerprints must be refreshed before another gameplay checkout;these standalone runs do not qualify a performance fix. No commit/push.

Raw diagnostics/scripts/controls: `artifacts/player-replacement/run241/`. The stack helper and plain-open probe are ignored diagnostic artifacts,not normal-path components. `sample-result.json`,`sample2-result.json`,`activation-stacks.txt`,`activation-stacks2.txt`,`plain-open-results.txt` retain the observations. WPR failure and absent privilege are an actual environment blocker,not automatic approval review rejection.
