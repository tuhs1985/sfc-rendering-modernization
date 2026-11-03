# Run252 — early passive output receiver implemented

## What changed

Reviewed current D3D9 host,output IPC,GameOutputWriter,Run251's direct Defender attribution and the completed shared-memory startup ticket before editing. Receiver creation now occurs after existing private renderer warm-up but **before** warm_start.wait and shared startup readiness. No CreateProcessW remains after activation/asset preparation. Host checks receiver liveness during the existing bounded warm-wait pump.

New versioned bootstrap uses the existing192-byte output mapping and128-byte packet area before any GPU packet,with the original current-user ACL and ready/done events. No extra IPC allocation or notification mechanism. It is Boot -> Passive -> Activate -> idle,then the original output/ACK lifecycle. [Contract](../reconnaissance/early-output-receiver-contract.md).

**Late identity:** prewarmed receiver cannot inherit the final asset SHA256 or offset. It independently reads the existing supervisor-owned accepted startup ticket,validates source session/game/supervisor/host identity,checksum and accepted state,then binds exact asset bytes and float offset explicitly to GameOutputWriter. Parent checks the already-accepted asset identity and returned receipt against a held snapshot. Stale inherited values are ignored in early mode;no fallback to guessed/default identity. No game pool/device/shared GPU images exist during passive waiting. Actual rendered pool asset/session readback matches accepted values in both final fixtures.

M1StartW/LiveChannel configuration bootstrap unchanged. Neither host nor receiver needs M1 to attach first. Existing ticket,asset/camera/fence/resource ownership and native suppression/fallback mechanisms preserved. No renderer/material/image/light settings changed.

Passive wait has its own285-second receiver bound and remains subject to existing host180-second activation/enclosing workflow limits. Active-work deadline begins once at successful receiver activation;original offline/live/game/tuning durations preserved. No per-frame cap or wait added to SFC. Explicit cancellation before first output is normal0with separate cancellation/zero-frame evidence;rendering acceptance still requires actual frames. Parent death/malformed activation rejects;host detects failed receiver and native behavior remains available.

## Validation

-29actual x86/x64 real-receiver IPC cases:no GPU/SFC. Normal,immediate publication,stale inherited asset/offset,cancel before warm wait/cancel while waiting,CRC/session/zero-asset/different-valid-asset/wrong-host rejection,receiver-side invalid-ticket rejection,parent death,receiver failure and source-game death. One61-second passive wait exceeds the old standalone active60-second duration,then activates and shuts down normally. No GPU pool published in any pre-output test.
-18bootstrap identity/checksum/lifetime checks on each architecture;existing output wire31,source timing18,game-output649 and deferred-diagnostic checks pass. Existing actual startup ticket22consumer cases pass unchanged. Python timing11,warm startup5,async-material13,native-cohort3 pass. One material regression initially hit restricted temporary-directory access;rerun with normal filesystem access passes,no test/code bypass.
-Final actual GPU fixtures,600frames each/three owners/two distinct assets/shared third:ExtraFrame with60-second menu `20261101-132739-762821-return-fixture`,Strict immediate `20261101-133152-493569-return-fixture`. Both pass independent pixel/depth/native-text checks,zero state errors and normal exits/job remaining_owned_processes0. No SFC launched automatically. Preliminary immediate fixture132352also passed before the final parent-side identity guard;final pair controls acceptance.
-Receiver/host/probes built /W4 /WX. Final build after adding the reproducible test builder produces byte-identical host SHA256 `5885D74826A8DCB9FF9FC17A2A183E8213C047C82757FA4D0B947BC913D5EAF9`,matching final GPU-tested binary. Native cohort/light qualifications refreshed;normal all-ship launcher read-only preflight passes. git diff --check passes.
-Defender antivirus,realtime and behavior protection remain enabled. Existing appearance hashes recorded;no configuration edits. No new discovery trace/security exception.

## Measurements:creation and valid output are separate

QPC measurements,not physical scanout. Final fixtures differ in timing policy/menu/cache conditions;not a controlled FPS comparison. Creation did not reproduce Run251's long security wait in these samples;the structural ordering,not elimination of Defender's work,is the proved change.

| Final fixture | Receiver CreateProcessW | Receiver prepared before activation | Activation receipt | Activation to first valid cohort output | Asset discovery to native insertion |
| --- | ---: | ---: | ---: | ---: | ---: |
|Immediate Strict|3.764ms|0.356ms|0.128ms|712.677ms|3579.809ms|
|60s delayed ExtraFrame|4.975ms|57472.781ms|0.410ms|3357.886ms|3544.446ms|

The immediate fixture discovers assets before cold preparation is complete;2.859s of its discovery-to-valid-output interval precedes activation. Passive receiver still accepts already-published activation correctly. Delayed fixture proves receiver preparation is completed during the menu wait and is not repeated when assets arrive. Old captured wait3277.501ms(process callback3275.995ms)was after activation;new traces put process creation entirely before startup readiness/activation. An OS launch stall can still delay cold preparation,especially when no menu time exists;it no longer waits for asset readiness before beginning.

**Remaining later cost:** delayed run spends2752.005ms between materials_enabled and renderer_assets_started,after receiver activation;scene read/hash and profiler costs are sub-millisecond. This range includes existing initial Renderer/light/hull/cohort setup. Exact responsible call unproven;no Defender/GPU/material attribution or unrelated fix attempted. Do not claim consistent sub-two-second whole startup. Immediate run's post-activation valid output0.713s and delayed run3.358s must both be reported.

## Compatibility, evidence and limits

Packet128/channel192/game-pool576sizes,GPU surface ownership/fences and native fallbacks unchanged. Legacy1.5.2 D3D9 host rebuilt against pinned headers;no legacy GPU campaign. Default late OutputPeer caller retains automatic activation/source environment behavior.

Parked API host compile check exposed a **pre-existing current-worktree mismatch**:ApiRenderer lacks initialDataUploads/stagedUploads/initialDataUnsupported now referenced by multi_scene_runtime diagnostics. No API source was changed or fake counters added;failed compile does not refresh its qualification. Its old compiled binary is not compatible with the new bootstrap and must not be paired with the rebuilt receiver. Keep API path parked until that compile/requalification is separately addressed. Active pinned1.6.1 D3D9 path is qualified.

Evidence:artifacts/player-replacement/run252/startup-comparison.json,final-build-identity.json,appearance-hashes.json,defender-status.json;receiver-startup/qualification.json and per-case logs;original GPU run reports/packets. No continuous screenshots or traces. Two storage preflight stops occurred before execution;no checks bypassed.

Restored20GB evidence reservation by lossless verified closed converted-texture/DDS archives:135.7MiB and211.9MiB reclaimed. Source captures,geometry,original game assets and logs unchanged;per-run restore manifests/archives retained. Existing five-minute workflow,90second tactical capture and image/output caps unchanged.

## Next exact action

Sponsor gameplay checkout through the existing Administrator PowerShell launcher:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\native_insertion\start_native_multiship_session.ps1"
```

No offset/manual timestamps needed. Review source-to-insertion timing,late pool identity,camera transitions and cleanup after the run. Further performance work should isolate the separate existing post-activation setup cost,not repeat Defender discovery or change appearance. Leave implementation unstaged/uncommitted.
