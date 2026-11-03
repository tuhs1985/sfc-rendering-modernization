# Run268 — Defender file-open wait directly explains the first live frame delay

## Confirmed finding

The sponsor's v2 trace successfully captured a **3060.2391 ms Defender file-open wait** on a Remix runtime worker. The same interval overlaps **2834.436 ms of the 2843.615 ms first-live completion interval** (about 99.68%). This is direct kernel wait/reply attribution, rather than a guess based on the dome filename or nearby Defender activity.

The run uses the exact pre-effect-light renderer already established in Run266. It does not show that the new effect-light code introduced the wait. Run256 recorded the corresponding dome-file wait before the effect integration. No changed Defender rule, protection setting or specific scan trigger has been established.

## Trace validity and test result

- Trace: `artifacts/player-replacement/run266/trace-20261102-053522/dome-startup.etl`, 70,994,861 bytes.
- Activation-edge-v2 receipt: recording began before original activation; trace and cleanup errors null. Recording stopped seven seconds after activation. WPR finalization itself took additional time; this is separate from the recorded first-frame wait.
- Trace duration 7.6428624 seconds, zero reported lost events or buffers. Raw switch coverage independently spans QPC6496682967393..6496754365251, with 785,983 switches overall and 268,813 inside the completion interval.
- Fixture: `20261102-053525-839935-return-fixture`; GPU PID21312, exit0, remaining owned processes0. First live source200033, completion2843.615ms. Native fixture completes600frames, eightowners, two zero-mismatch depth/text checks and state_errors0.
- The final supervisor still reports the documented eight-asset diagnostic versus standard three-owner expectation mismatch. Do not promote this diagnostic into a new normal production qualification.
- No new game run, symbols download, security setting or production rendering change was needed for analysis. Only cached local Microsoft symbols were used.

## Matched wait and reply

Host PID21312, runtime worker TID10256:

```text
runtime → UCRT fopen/open → CreateFileW → NtCreateFile
 → FLTMGR post-create callbacks → WdFilter.sys
 → FltSendMessage → cancellable wait → KeWaitForMultipleObjects
```

Readying/reply chain:

```text
MsMpEng.exe PID17464, TID21960
 → MpRtp.dll → fltLib.dll → NtDeviceIoControlFile
 → FLTMGR FltpMsgDispatch → FltpFilterReply → KeSetEvent
```

Raw worker switch-out: QPC6496683603688. Resume:6496714206172. At10MHz this is3060.2484ms off-CPU, agreeing with WPA's3060.2391ms blocked plus9.3µs ready-to-run. Completion interval:6496685861812..6496714297962. The Defender wait starts before the host polls its query and ends shortly before that query completes.

The large delay is therefore not ordinary GPU rendering, asset-service processing, fleet complexity or scheduler starvation. The runtime worker is waiting for Defender's service reply during a file open. Other shorter Defender file-open waits are also present, but they must not be combined into an unsupported total or used to attribute the separate material-publication sharing error.

## What remains unknown

This profile captures process/thread/wait stacks, not FileIO pathname events. It directly identifies a runtime file-open Defender wait; it does **not independently record the filename** for this specific opening. Earlier bounded worker samples repeatedly identified the tiny generated dome DDS on the corresponding first-live path. Keep that corroboration separate from this trace's direct attribution.

NVIDIA private function symbols and Defender's private scan logic are unavailable. The trace does not establish which scan rule, cloud lookup, cache state or file-reputation condition made the reply slow. It does not establish a malware classification, a protection-policy change, or why a specific earlier successful run was fast. No claim that NTFS compression or hardware capacity caused this wait.

## Consequence for the fix

The existing runtime path supplies a dome image by filename, and we generate another per-session copy of the same tiny white image. Moving that open onto a worker does not keep the renderer's command stream from waiting for the resource. An earlier ordinary read/reused file helped in Run266 diagnostics, but is not a readiness guarantee.

The scoped next implementation should reuse an immutable, content-identified environment resource and prepare/retain its actual supported Remix light resource before live-frame admission. Prove actual runtime completion, handle cancellation and preserve the exact light/configuration identity. Preparation must not be declared ready merely because the CPU wrote/read a file or drew an unrelated warm-up triangle. Preserve Defender; do not use exclusions, disable GI, extend completion guards, introduce arbitrary warm-up-frame counts or patch NVIDIA internals. First qualify immediate and delayed activation using the existing standalone fixture before requesting another large fleet run.

No fix is implemented in this analysis. The separate physical-hull32 submission limit remains open. Effects stay parked/off.

## Evidence and handoff

`artifacts/player-replacement/run268/defender-file-open-cause.json` preserves the selected full wait/reply stacks and independent raw timing. Reproducible raw reader source/executable, decoded table/profile, analysis script and export log remain local. Original trace and failed v1 evidence are retained. No owned renderer/game processes remain. Handoff/status updated; changes unstaged and uncommitted.
