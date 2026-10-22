# D3D9-LIFECYCLE-001 — camera gap versus sponsor-confirmed destruction

Status: prepared bounded diagnostic, runtime adjudication pending. M1 CONTINUES.
Authority: approved M1 plan, current D3D9 additive execution plan, Run92/93/94.
This is NOT native death detection and does NOT implement epoch recovery.

## Question and controlled comparison

Compare an alive selected player ship leaving/returning to the render path with
its later sponsor-confirmed destruction. Preserve observation epochs and fresh
asset associations throughout, rather than stopping after100records per owner.
Keep existing semantic hooks/ABI, original rendering, geometry-hook OFF, current
camera-left offset and frozen lighting/material/image/quality configuration.
Known Federation FCA player fixture is still required; selection is NOT a generic
native player flag. The copy may disappear permanently after camera return due
to Run92's existing pinned-epoch defect. Continue this diagnostic anyway.

## Launch and sponsor actions

Use established elevated testing parent; no new UAC/security changes. Entry:
`tools/d3d9_proof/start_d3d9_lifecycle_session.ps1`.
`-CheckOnly` verifies dependencies without launching anything.
Copied game only, verified process path; accepted installation stays untouched.

Enter usual two-ship skirmish with the Federation cruiser. Keep ships alive while
the extra image prepares. Automatic tactical gate and first-image readiness start
the timed instructions; no manual timestamps.

| Cue | Requested action |
| --- | --- |
| First15seconds | Settle the view; keep your ship alive. |
| One beep,15s | Hold ship/camera still. |
| Two high beeps,25s | Switch to enemy camera; leave own ship out of view, alive. |
| Three high beeps,40s | Return to own ship; keep alive another20s. |
| Four high beeps,60s | Destroy own ship using usual method; stay in mission. |
| Two low beeps,after capture/controlled removal | Exit SFC normally. |

Afterward sponsor reports whether camera return occurred while alive, whether own
ship actually exploded, and any game/render/control problems. Cues record REQUESTS,
not proof that an action happened. If game forces mission exit, preserve partial
evidence; do not represent process-exit reclamation as controlled unload.

## Capture contract and limits

- Default-off `--lifecycle-capture`, permitted only with `--d3d9-additive`.
  Child-only `SFC_LIFECYCLE_CAPTURE=1`; normal runner clears inherited override.
- Fresh geometry/resource packets remain existing bounded capture, at most8asset
  revisions in this calibration workflow. No raw object memory/guessed health flag.
- Existing96word validated owner records; worker retains at most20Hz detail,
  2700records per table slot,16MiB total. Normal tuning still keeps100records.
  Existing34ms producer throttle means actual retained cadence can be below20Hz.
- Independent256record fixed transition ring (96KiB), prefaulted before hooks.
  Owner epoch, revision or status changes queued under existing try-lock; no
  waiting/allocation/disk access in callbacks. No overwrite of unread transitions.
- Worker emits `LIFECYCLE-001-events.jsonl`, hard1MiB; journal overflow, output
  saturation, contention drops and undrained records are explicit counters.
  Retirement status2 means observation absence, NOT actual engine destruction.
- `LIVE-SCENE-001-updates.jsonl`, asset packet/association manifests and worker
  summary retained. Existing exact-frame renderer, current-user mapping, native
  light latest files, watchdogs and stale-output safeguards unchanged.
-90s formal observation; at most30s existing preparation within120s semantic
  watchdog; five-minute prepared workflow ceiling. Combined non-image evidence
 32MiB/warn16MiB; image128MiB/warn64MiB; aggregate20GB. No continuous image dumps.
- Producer disabled/callbacks drained before worker stop; final journal drain,
  join before storage unmap. Existing proxy/config rollback and client hashes.

## Offline checks / evidence interpretation

`build_light_discovery.ps1` rebuilds only dedicated observer variant and tests;
`qualify_lifecycle_capture.py` runs actual worker with synthetic owners. It checks
late detail beyond100records, immediately coalesced retirement/new epoch,
fixed-queue overflow/no overwrite and stop/drain. Synthetic contention is forced;
any additional contention is reported, not misrepresented as lossless capture.
Normal and tuning observer regressions remain required. Actual-proxy standalone
GPU fixture and additive qualification protect existing image-return behavior.
Lifecycle preflight separately requires matching native-worker qualification.

Runtime analysis is `lifecycle_capture.analyze(gate_directory)` and appears in
`result.json`. Missing summary/events, malformed data, drops or saturation produce
PARTIAL. Even complete observations say `OBSERVATIONS_READY_NOT_DEATH_PROOF`.
Static: render-absence retirement rule CONFIRMED. Runtime: recorded transitions
CONFIRMED only for their observed meaning. Sponsor-confirmed destruction is human
evidence; correlation remains inference unless an independent death signal is
qualified. No hidden pointer/death assumption or new formal TRL claim.

Preserve raw runtime evidence, archive only verified generated fixture copies.
Next engineering action after comparison: decide whether an independent native
lifetime observation is needed; safe content-qualified fresh-epoch rebind does
not require treating render absence as death. Do not remove retirement safeguards.
