# Run243 — Defender activation-file delay confirmed

## Root cause demonstrated

Sponsor completed the focused Microsoft Minifilter capture in `artifacts/player-replacement/run242/file-filter-trace-20261101-012250/` (UTC folder name; sponsor-local date2026-10-31). Standalone fixture: `20261101-012254-316417-return-fixture`. No SFC launched.

Native xperf `minifilterdelay -min100000` identifies **WdFilter.sys** handling CREATE/open for the exact session's104-byte `gpu/renderer-activate.bin`:

| Measurement | Duration |
| --- | --- |
| Host open operation |6.0096834s|
| WdFilter callback/operation delay |6.009536s|
| Difference |0.0001474s|

Filter call/return trace timestamps8,765,537–14,775,073us. This accounts for~99.9975%of the measured open wait. It is direct filename/timing attribution,not mere presence of Defender in an unrelated stack. The previous general trace's NTFS-lock finding remains withdrawn;this is the new evidence establishing the delay in Defender's filesystem filter.

The same trace records WdFilter CREATE delays101.516ms and107.277ms for two staging texture files. Those are separate from the six-second activation stall. This establishes the cause in the focused reproduction;earlier activation stalls did not retain filter timings,so their identical attribution remains an inference.

## What this does and does not mean

[Microsoft's Defender performance documentation](https://learn.microsoft.com/en-us/defender-endpoint/performance-analyzer-reference) explicitly treats file/process scan performance as a diagnosable cost. [Microsoft's protection documentation](https://github.com/MicrosoftDocs/defender-docs/blob/public/defender-endpoint/microsoft-defender-endpoint-antivirus-performance-mode.md) describes real-time inspection on file open. The trace establishes a delay inside WdFilter;it does not expose which internal scan rule,reputation lookup,queue or cloud decision consumed the time. Do not assert unsigned binaries,injection or the packet contents were specifically flagged.

Defender Operational event query succeeded with no matching1116/1117threat events or1121–1124ASR/CFA block/audit events in01:22:40–01:25:00UTC. This is absence of matching events in that checked window,not proof that every internal security check is known. The file open eventually succeeds. No evidence here establishes malware detection/quarantine or a requirement for a false-positive submission.

Compression is already verified OFF for current project/output/exact activation file. Do not alter compression or protection settings to address this result.

## Smallest next implementation

Move the immutable startup activation ticket and readiness notification onto the existing bounded,current-user session bridge. Preserve its session/PID/model/source/content/activation checks and passive renderer warm-up ordering. Remove the activation-file open from the latency-critical startup handoff;this is ordinary in-memory IPC,not a protection exclusion. No scene/material/lighting redesign,new renderer refresh cap or appearance tuning needed.

Keep immutable texture preparation/reuse outside the frame-critical path. The two texture-open delays are real but do not justify a new asset system in this increment. A stable distributable package must later be tested with protection enabled;signing/reputation considerations are independent and do not guarantee elimination of scanning latency. No broad Defender exclusions or protection disablement is proposed.

This review does not implement the IPC change or claim a startup speedup. Next gameplay qualification must refresh current diagnostic-build fingerprints after the actual change.

## Validation and evidence

600standalone frames,three owners,two pixel checks with zero mismatches,zero state errors,normal child/renderer0,remaining_owned_processes0. WPR is no longer recording. No new runs/builds during this review. Logs/source settings unchanged. All repository changes remain unstaged/uncommitted.

- `artifacts/player-replacement/run243/root-cause.json`: numeric comparison,archive and detection-query receipts.
- `artifacts/player-replacement/run242/file-filter-trace-20261101-012250/filter-delays.txt`: native analyzer's exact path/filter/timing report.
- Same folder `defender-detection-events.json`: successful empty event query with explicit status/time window.
- Same folder `activation-archive.json` and `activation-etl.zip`: recoverable raw trace,streaming SHA256verified after lossless archive,before deleting the loose copy.

## Diagnostic/storage failure and cleanup

The file-mode observer failed its intended192/256MiB trace bound:raw trace4,500,488,192bytes. This is a diagnostic harness defect,not a renderer failure. The exact executed script is preserved as `artifacts/player-replacement/run243/trace_activation_filters.executed.txt` (SHA256A1C8941FB7DED29DA866EC4B567241EB9F375FAD53765126FB6B5A0B6766A5D5). The launcher is retired with an immediate explanatory stop;do not rerun it. No further discovery capture is required for the activation cause.

Raw evidence was archived losslessly to521,279,294bytes,verified by decompressed SHA256matching the original,then its exact loose copy removed. Five closed successful diagnostic fixture generated image sets were also losslessly archived with per-file hash verification and restoration receipts (~282MBreclaimed). No raw observations,geometry,captured packets,accepted game assets or relevant symbols discarded. These actions restore the existing20GB aggregate allowance;see current inventory in root-cause receipt. Raw traces/symbols/generated artifacts remain ignored/private. No commits or pushes.
