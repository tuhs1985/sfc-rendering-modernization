# D3D9-ADDITIVE-001 — fresh textured offset ship

LATEST2026-10-21:[Run92](../../runs/2026-10-21-codex-camera-switch-epoch-loss.md)
camera-away/back exposes missing owner-epoch recovery. Returning fresh FCA4/4
matches original2/2content,but renderer stays pinned2/2. NO corrected recovery
test ready. Do not bypass identity checks or treat previous READY as lifecycle PASS.

LATEST2026-10-21:[Run90](../../runs/2026-10-21-codex-texture-origin-and-viewport-scale.md)
READY same fixture/launcher. Compare saucer texture orientation and returned/native
size,not new appearance tuning. Correct native viewport placement,Remix-only DDS
row inversion;capture/ordinary UVs/model scale unchanged. Offline controls qualified.
Exit at runner cue to verify controlled unload;last run exited normally but its
controller reported process exit before removal. M1 CONTINUES,one selected ship.

LATEST2026-10-20:[Run89](../../runs/2026-10-20-codex-worker-efficiency-preparation.md)
is READY FOR ONE-SHIP SPONSOR TEST. Deferred bounded worker diagnostics,explicit
optimized precise builds,private250us query/input wait retain exact-frame admission
and actual GPU fences. Offline599/600,normal cleanup/state/resize PASS;actual SFC
camera stability not yet qualified. Current textures/materials/lights unchanged.
Sponsor20GB aggregate budget supersedes10GB;per-run90s/32MiB logs/image caps unchanged.
Use same Federation cruiser,brief static then normal/fast camera changes with player
visible;report flicker/initial-load delay,exit at cue. One ship only,no expansion.
Older preparation statements below are historical,not the current qualification.

Status: READY FOR CORRECTIVE SPONSOR TEST. [Run82](../../runs/2026-10-20-codex-offset-selection-and-delivery-triage.md)
supersedes [Run81](../../runs/2026-10-20-codex-normal-d3d9-material-binding.md).
Current [Run83](../../runs/2026-10-20-codex-camera-left-and-current-effects-profile.md)
supersedes preparation:camera-left/poolv2/background light cache,599/600offline
frames. Actual225915had~77%delivery/flicker;new build untested in SFC.
[Contract](../d3d9-additive-output-contract.md). Default OFF. First SFC run223526
delivery FAIL;current correction qualified offline only (588/600 fixed-window).

Question: can current raw owner/camera state, ordinary D3D9 geometry and existing
appearance policies deliver a matching GPU ship image inside the copied game?
Original drawing ON. No SDK geometry, Toolkit, suppression or stale-image hold.

## Preparation and sponsor operation

Source/binary/config receipt `artifacts/d3d9-proof/additive-qualification.json`
must match. Do not edit appearance TOMLs or rebuild after qualification. Accepted
and test client SHA2564D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Pinned runtime/header and full-event proxy unchanged from Run81. Preflight:
`tools/d3d9_proof/start_d3d9_offset_ship_session.ps1 -CheckOnly`, no launch.

From established elevated parent run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_offset_ship_session.ps1"
```

Enter SAME Federation-cruiser two-ship skirmish;keep both ships alive and visible.
Extra textured FCA should appear beside your cruiser. Selection uses explicit
offset_ship.toml model,not first render order or a proved native player flag.
Missing/duplicate configured models reject;no enemy fallback. Another player class
requires deliberate fixture-config edit and requalification before launch.
Runner names selected model. No magenta or automatic enable/disable cycle.
Copy is displaced toward camera-left each frame,not along fixed world-X. Current
lighting and material mapping remain enabled with same settings. No weapons scope.
Preparation up to30s; formal90s starts on first actual matching composition.
First15s find comfortable view; single LOW cue hold10s; prepare free camera at25s;
two HIGH cues at35s small camera movement15s; prepare ship movement at50s;
three HIGH at60s accelerate/gently turn20s; steady at80s. Two LOW EXIT cues:
exit SFC normally, not Task Manager. No timestamp/RE/UAC work requested.
Do not destroy either ship or pause. Report gaps/flicker and original HUD/control
behavior honestly; no requirement that first test be smooth to retain its evidence.

## Safety/evidence

Original geometry hook OFF. Same semantic hooks/automatic tactical gate. New pool
576B inside current-user16MiB mapping, two GPU surface sets,1920x1080,<=128MiB
output. Logs32MiB/warn16MiB; images128MiB/warn64MiB; aggregate10GB with192MiB
reservation.120s semantic watchdog/110s native input/120s GPU job/130s receiver
allow preparation plus90s formal test, overall<=285s/five minutes. No CPU frame
capture. Current frame/owner/revision/hash/nonce only; stale output omitted.
Worker completion requires D3D11.4 fence-event support;unsupported/device-lost
cases stop safely. No game callback wait added.

Test-copy full-event proxy installed transactionally, restored after normal game
exit. No accepted-install mutation/security weakening. Cleanup waits controlled
semantic restoration/unload and owned renderer exit; verify hashes/launcher settings.
Interrupted proxy recovery uses existing verified rollback; never overwrite unknown
proxy. If game remains running, rollback deferred and explicit error retained.

Preserve manifest, native-light latest files, raw source/Present audit, fresh asset/
image associations, material layer/config hashes, game pool stats, GPU timings and
normal-exit receipts. `result.json` is pending sponsor review, not automatic PASS.
Assess duration/delivery gaps, actual current-frame image submissions, shape/texture/
lighting, original behavior, cleanup and bounds separately. Archive generated
copies after analysis with decompressed SHA verification; preserve original packets.

Success here means additive return demonstrated under observed conditions only.
Recurring missed frames mean delivery still CONTINUES; do not relax identity or
begin original replacement. Stop for architectural adjudication if bounded
scheduling cannot deliver. No formal TRL4 or universal asset/UI coverage claim.
