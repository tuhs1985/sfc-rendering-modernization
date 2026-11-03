# Run267 — Failed trace trigger corrected at the actual activation boundary

## Sponsor attempt

Reviewed `artifacts/player-replacement/run266/trace-20261102-052802`. Its receipt explicitly records `trace_saved=false`, zero trace bytes, and `Missed pre-activation window`. No ETL was produced; do not claim kernel attribution from this attempt.

The fixture nevertheless completed 600 frames and two zero-mismatch native depth/text pixel checks, with eight owners. Its first live output waited **2609.104 ms**, and the slow-completion record reports 2553.964 ms polling pause, 52.484 ms asset service and 1.886 ms query calls. This is another completion-stage stall, not independently proved to be the dome file because no worker/kernel trace was collected here. The final supervisor's known three-owner expectation reports `Independent multi-owner pixels/shared-asset delivery incomplete`; the native fixture itself exits zero. Preserve the distinction.

## Launcher defect

The first observer waited until 58 seconds after renderer readiness. However `SourceTimingFixture` starts its 60-second menu-like idle after attaching its sources, independently of the later renderer-ready event. In this run readiness was observed at observer elapsed 10.859 seconds, while activation was observed at 68.343 seconds: actual readiness age approximately **57.561 seconds**, already before the observer's 58-second trigger.

This is our diagnostic timing defect. It neither validates nor invalidates the separate historical first-frame observations. Replacing 58 with another estimated offset would leave the same architectural mistake.

## Correction

The existing PowerShell command now calls `trace_dome_wait_v2.py`. This diagnostic supervisor wraps the existing Python `warm_start.activate` function:

1. Run WPR start synchronously and require successful acknowledgement.
2. Call the original activation with the exact unchanged channel, environment and session arguments.
3. Save the trace seven seconds after that activation. A separate initial 12-second watchdog covers an activation exception/stall. Drain the stop worker on teardown.

No readiness-clock estimate, polling trigger, new transport, native hook or production source edit is involved. Only the standalone diagnostic's supervisor briefly pauses before activating the historical renderer. Its existing startup ticket validation, fixture deadlines, GPU ownership and native pixel checks remain intact. Existing WPR sessions are rejected before launch. Existing trace buffer/output/evidence bounds and Defender protection remain unchanged.

The original v1 script and failed receipts remain preserved. Kernel trace collection is still pending because this Codex execution does not have an Administrator token. Sponsor uses the same command from their existing Administrator PowerShell; no SFC/gameplay actions are needed.

## Checks

Seven focused tests pass: recording precedes original activation; exact arguments and return value preserved; WPR start failure prevents activation; invalid activation saves the owned trace; timer/finish cannot stop twice; duplicate activation rejected; no activation never stops somebody else's trace. The seven-second timer is attached to the activation edge, not renderer readiness. PowerShell parser passes. No owned game/renderer processes remain after the sponsor attempt.

No normal source, renderer executable, configuration or game file was changed. No commit or staging. Status and authoritative handoff updated. Next: review the v2 trace's exact pending command-thread wait/reply stacks and trace coverage before attributing a Windows component or choosing a production fix.
