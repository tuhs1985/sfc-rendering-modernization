# Native replacement recovery policy

Run260 implements sponsor policy: recoverable gaps use original drawing and retry; they do not disable replacement for the session.

| Condition | Scope and action |
| --- | --- |
| Missing/late output, unsupported owner or pre-commit target rejection | Original drawing for the affected admission; existing fixed deadline and next-frame retry remain. |
| Overlapping/nested coordinator invocation | Pass that invocation through unchanged. Do not disturb the outer decision or disable other ships. |
| Owner becomes unqualified after its first insertion | Block additional suppression for that owner/frame. Other owners remain active. Fresh next-frame qualification retries normally. |
| Later mesh arguments, caller, revision or identity disagree | Leave that invocation native; block further suppression for that owner/frame and retry next frame. Do not reassign an old output to a different identity. |
| Failure to write the validated suppression argument | Terminal: suppression cannot reliably be applied after insertion. Record reason/frame/owner and stop new replacement commits. |
| Unexpected exception crossing the return dispatch, or failed GPU output-resource handling | Terminal: resource/state integrity is not established. Record reason/frame/owner where available; preserve existing resource retention, drain and fallback. |
| Sponsor exit, explicit disable or shutdown | Existing orderly cleanup and resource lifetime rules. Not an error-triggered replacement failure. |

Already queued colour/depth writes cannot be undone. A later mismatched invocation is passed through, so the affected frame may contain both the inserted image and some native geometry. This is a bounded frame-local compromise, not stale-pose reuse. Recovery does not authorize suppression of an unqualified list, cancel a GPU lease prematurely, reconstruct cached assets or change refresh timing.

## Evidence contract

Native-gate version1 retains its 256-byte header, 128-byte record and shared offsets. The existing 96-byte reserved header area now contains recovery schema1: three cumulative retry counters (overlap, owner changed, submission changed), last retry reason/frame/owner and first terminal reason/frame/owner. Retry recording uses fixed storage and atomic updates only. Terminal reasons:1 suppression write,2 dispatch exception,3 output resource failure. Normal lifecycle stop does not set a terminal reason. A live read of last-event fields is advisory; authoritative evidence is saved after callback drain.

Present appends only a newly initialized, not-yet-presented source record while the gate is active. Offline analysis also excludes repeated `(generation, frame, start)` identities from commit/timing totals, exposing raw and repeated counts separately and preserving original binary logs. Terminal partial flags produce explicit partial reports even if earlier replacements succeeded.

No new hook, worker, per-frame file access, wait, refresh cap, prediction, material change or GPU-pool layout is introduced.
