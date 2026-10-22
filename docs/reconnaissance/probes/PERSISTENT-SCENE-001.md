# PERSISTENT-SCENE-001 — player instance across camera changes

Run105 comparison uses the SAMElauncher/actions/bounds below. One backend
grade/coverage pass is combined;appearance and safety checks unchanged. Expect
the same textured player copy. Report whether return feels better/same/worse;
no manual timestamps needed. Review afterward and move on per sponsor's bounded
optimization decision. This is not a new simulation-discovery or visual test.

2026-10-21, Run103; prepared, NOT gameplay-confirmed. Contract:
[persistent scene](../persistent-scene-contract.md).

## Question

Does the existing textured player-copy remain resident, consume current
simulation pose and return at its current location without visibility-driven
epoch/asset churn? Separately measure remaining output deadline misses. This
is not another offscreen-position discovery run or original-ship replacement.

## Launch and safety

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_persistent_scene_session.ps1"
```

`-CheckOnly` checks source/binary-locked qualification without starting SFC or
the renderer. The full launcher uses the established elevated-parent workflow,
verified separate test copy and normal PS5-to-modern-PowerShell forwarding.
No new UAC/security setting, original-client write or original-draw suppression.
Default-off `SFC_PERSISTENT_SCENE=1` applies only to owned test child processes;
legacy runners do not acquire the new destruction hook.

Before hooks: existing asset qualification and shared channels are prepared.
New source header v2, fixed 32-owner registry, existing 16 MiB mapping, bounded
surface pool. No fixed-Hz current-pose cap. Callback storage is preallocated;
worker handles evidence outside callbacks and joins before storage release.
Current-user-only access, PID/path/hash checks and existing fail-open behavior
remain mandatory. Do not bypass a stale qualification receipt.

90-second tactical observation, five-minute prepared workflow; 32 MiB combined
logs (16 MiB warning), 128 MiB image/output-resource limits, 20 GB aggregate.
No exhaustive geometry or continuous screenshots. Geometric observation hook
`0x006AB410` stays OFF. All lighting/material/image settings stay as configured.

## Sponsor actions

Enter the familiar two-ship skirmish with the qualified FCA player model. Keep
both ships alive. Expect the usual textured extra player ship/camera-left
offset, not a new effect or replacement. Follow printed and audible cues:

- 15 seconds, one cue: accelerate own ship and leave it moving.
- 25 seconds, two HIGH cues: select the enemy camera.
- 40 seconds, three HIGH cues: return to own ship.
- 50 seconds, one cue: gently turn own ship.
- 60/75 seconds: repeat enemy/own camera at two/three HIGH cues.
- 80 seconds, one cue: hold steady.
- Exit normally only at the final two LOW-beep exit request after the capture
  window/restoration phase. Report any injected-copy blips and game issues.

No timestamps, assembly inspection or manual administrative actions needed.
If the wrong model is selected, do not pretend it is the player; preserve partial.

## Evidence and adjudication

Retain native `gate/PERSISTENT-SCENE-001.json`, lifecycle/source timing, actual
camera/pose/revision records, fresh asset packets, native light provenance,
D3D9/GPU receiver timing, result/configuration/hashes and restoration records.
Counters cover admitted/destroyed/rejected, pose/offscreen updates, publications,
failed updates, update QPC total/max/frequency and joined-worker stop.

Runtime acceptance requires current motion/camera correspondence, unchanged
living identity and asset generation across camera gaps, no camera-triggered
reload/rebind, normal game operation, bounded output, clean hook restoration/
unload/normal exit and original/copied client hashes. Rejection/timing gaps must
be counted and interpreted, not hidden by indefinitely held stale frames.
Synthetic counters alone cannot pass this probe. Actual destruction invocation
is a separate bounded follow-up unless this run genuinely exercises it.

If seamless return remains unconfirmed, classify PARTIAL and isolate whether
camera qualification, pose rejection, lifetime, lighting freshness or GPU
deadline caused it. Do not redesign the bridge or repeat position discovery
without contradictory evidence. Multi-object display follows initial evidence
review; registering 32 entries does not establish rendering 32 ships.
