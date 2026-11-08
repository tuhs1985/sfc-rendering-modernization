# BRK receiver-to-worker integration correction

November 8, 2026. Sponsor's second checkout:
`artifacts/remix-runtime/runs/20261108-053954-509269-in-game`.

## What failed, and correction to the prior diagnosis

The latest error is again `Recovery service: Unsupported semantic origin/math
dispatch`, not a different error string. The active service calls
`receiver.drain()` before polling the preparation relay. That receiver is
`present_calibration.Receiver`, whose `drain` still called intact-only
`decode_mesh`. It rejected indexed debris before acknowledgement and worker
admission. The initial review correctly found an additional worker mismatch,
but did not establish that worker as the first failing stage. The prior fix
resolved that downstream defect while leaving this upstream rejection intact.

This corrects the scope of the previous diagnosis; do not treat two repeated
gameplay failures as evidence that Remix cannot render the fragments. Both
captures contain four valid FCA pieces/6,370 triangles, but neither demonstrates
debris renderer admission. The actual service ordering is visible in
`live_owner_timing.Relay.start_service`.

## Change

- `present_calibration.Receiver` now accepts explicit keyword-only
  `break_models=False`. The game runner passes its existing validated BRK flag
  when constructing this receiver, before the service starts.
- Enabled mode routes received packets through the dedicated strict
  `decode_runtime_mesh(..., allow_break=True)` path. Normal/legacy calibration
  stays intact-only by default. No change to the offline calibration-analysis
  decoder or legacy single-ship preview is implied.
- Owner/revision/session transport validation, immutable revision hashes,
  capacity bounds, retention policy and acknowledgement ordering remain.
  Malformed debris is rejected without acknowledging or recording its revision.
- The earlier parallel-worker correction remains necessary and unchanged.

No new hooks, renderer modes, material conversion, appearance settings, output
limits, waits or fallback policy. All changes remain unstaged/uncommitted.

## Verification of the connected path

**66 targeted tests PASS:** break transport 7; calibration/receiver 12; startup
safety 15; parallel preparation 26; native cohort 6. The actual current-user
mapping tests ran in the desktop session.

The mixed intact/debris preparation regression now publishes each raw packet
into the actual shared-memory channel and calls the real receiver before
submitting it to `Pipeline`. It checks ACKs, revision retention with decoded
asset caching disabled (normal multiship policy), actual worker decode, base
bundle production and all enhanced groups. The native x86 worker test now uses
this same real receiver rather than bypassing it with a direct decoder call.
Separate tests confirm disabled mode and malformed metadata cannot advance ACKs.

All seven saved captures from the latest failed run were replayed through the
actual shared-memory receiver and production parallel preparation. All seven
revisions were acknowledged; six unique assets became ready and the duplicate
FCA became a shared alias. Each of the four pieces became base-ready and
completed every enhanced group (19,19,27,18 groups for revisions4–7), covering
6,370 triangles. Original saved packets remain unchanged.

Local report: `artifacts/break-live/receiver-worker-fix-20261108/review.json`.
Replay uses synthetic finite camera/pose and real locally resolved images with
damage mode ON. Its approximately1.305seconds is offline CPU preparation, not
live destruction-to-display, GPU admission or a general performance claim.
No SFC or renderer was launched for this replay.

Pinned candidate build/source receipt refreshed; existing successful600-frame
Strict/ExtraFrame GPU evidence revalidated, not rerun. Read-only BRK preflight
PASS, damage ON. Focused source/document checks PASS. The new connected-path
evidence supersedes the earlier worker-only verification as the relevant
regression for this failure.

## Latest live cleanup and remaining acceptance

The latest game exited normally (launcher exit0), renderer exit0 and receiver
result0. Controller did not remain running; copied proxy restored. Original
client and launcher settings unchanged. Controlled live component removal was
not confirmed: controller records target exit first. The supervisor's PARTIAL
classification remains because the service failed; clean teardown is not
successful debris rendering. No additional rollback was required for this run.

Same BRK launcher is prepared for a retry. Verify actual fragment rendering,
indexed native suppression, motion and retirement; the now-correct input path
does not establish those later live stages. Keep destruction alpha acceptance
open and preserve both failed runs. No extra discovery capture is needed.
