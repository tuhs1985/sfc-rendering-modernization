# Run106 — synchronized one-frame buffer implementation

Started 2026-10-21; finalized 2026-10-22 America/New_York. HEAD `0fc1300`,
branch `codex/github-sanitized`, index empty. Run103–105 source/docs already
unstaged/uncommitted; preserved, not silently attributed to this increment.
Read HANDOFF and operating convention, approved M1 plan/current gate amendment,
Run105 and existing native host/receiver/compositor/timing code. Fuel Guard
attached successfully; no helper, agent, stage, commit, push or new architecture.

## Question and decision

Can one bounded extra presentation frame absorb returned-image deadline misses
without placing an old ship on a new camera scene? Save native color, depth,
identity/camera provenance together and display only their matching returned
ship. Default-off, separate launcher. No prediction, Reflex, stale-camera hold,
gameplay pause, forced rate limit, appearance change or original suppression.
See [contract](../reconnaissance/synchronized-buffer-contract.md) and
[probe](../reconnaissance/probes/D3D9-SYNC-BUFFER-001.md).

CONFIRMED offline: native scene/HUD pixels and depth retained, correct immutable
saved metadata paired to output, finite limits, disable/re-enable/state/resize/
shutdown safe. STRONG HYPOTHESIS: improves SFC camera-transition continuity.
Actual SFC buffered controls and visible continuity remain UNTESTED. Typical
saved-scene age ~17 ms is not measured physical input-to-photon latency.

## Exact files created/modified in this increment

New:

- `tools/d3d9_proof/synchronized_frame.h`: one-frame admission/audit contract.
- `tools/remix_runtime/scene_frame_buffer.h`: two GPU color/depth history slots.
- `tools/remix_runtime/synchronized_buffer.py`: strict bounded audit decoder.
- `tools/remix_runtime/qualify_synchronized_buffer.py`: separate locked gate.
- `tools/d3d9_proof/start_d3d9_buffered_scene_session.ps1`: opt-in PS5 launcher.
- `tools/d3d9_proof/build_synchronized_buffer.ps1`: x86/x64 GPU tests.
- `tests/d3d9_synchronized_buffer_tests.cpp`, `tests/test_synchronized_buffer.py`.
- This run, contract, probe, curated evidence JSON; HANDOFF new checkpoint.

Modified:

- `tools/remix_runtime/d3d9_game_receiver.h`: saved-frame matching, ready current
  output retained for next frame, bounded audit, failure containment/worker stop.
- `tools/remix_runtime/ship_triplet_compositor.h`: optional resolved-depth input.
- `tools/remix_runtime/return_addon.cpp`: explicit original target to receiver.
- `tools/remix_runtime/live_owner_timing.py`: explicit buffered-mode audit save.
- `tools/remix_runtime/run_return_game.py`, `start_return_image_session.ps1`:
  default-off option/preflight/child environment; freeform comparison workflow.
- `tools/remix_runtime/return_fixture.cpp`, `source_timing_fixture.h`: standalone
  short-lead pacing, exact native HUD/scene pixel markers, disable/re-enable.
- `tools/remix_runtime/run_return_fixture.py`: opt-in fixture, narrow atomic
  rename inventory race handling (FileNotFound only; permissions still fail).
- `tools/remix_runtime/additive_qualification.py`, `qualify_persistent_scene.py`:
  buffered evidence cannot certify/overwrite unbuffered display qualification.

No semantic ABI/hook/address change. Existing semantic render gate4162B9,
manager supplied6F4/composed6B0 and persistent simulation pose remain unchanged;
diagnostic geometry hook OFF, original drawing ON, actual destructor opt-in
4158C1 still not exercised in this task. Existing one-player display backend,
32-owner registry, retained geometry/textures/settings remain intact.

## Tools, reproducible validation and results

Existing bundled Python, modern pwsh, VS18 x86/x64 `/O2 /W4 /WX /fp:precise
/Brepro`, pinned Remix1.5.2/D3D9 worker and D3D11/ReShade return path unchanged.
Host GPU/shared-map/build tests use scoped elevated execution, not weakened
Windows policy. PS5 wrapper remains supported.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/build_synchronized_buffer.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/remix_runtime/build_return_probe.ps1
python -m unittest discover -s tests -p 'test_*.py'
python tools/remix_runtime/run_return_fixture.py --d3d9-additive --persistent-scene --rebind-owner --synchronized-buffer
python tools/remix_runtime/run_return_fixture.py --d3d9-additive --persistent-scene --rebind-owner
python tools/remix_runtime/light_discovery.py
python tools/remix_runtime/qualify_persistent_scene.py --fixture artifacts/remix-runtime/runs/20261022-035622-504453-return-fixture
python tools/remix_runtime/qualify_synchronized_buffer.py --fixture artifacts/remix-runtime/runs/20261022-035401-772393-return-fixture
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/start_d3d9_buffered_scene_session.ps1 -CheckOnly
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/start_d3d9_persistent_scene_session.ps1 -CheckOnly
git diff --check
```

- 424 Python tests PASS. x86 23 + x64 23 actual GPU checks PASS at1920×1080:
  saved full color/native HUD markers, independent metadata, MS8 closest depth,
  NaN/Inf/out-of-range safety, state/reset and shader compatibility. Tests also
  reject expired/nonadjacent frames, identity changes and audit saturation.
- Return native builds PASS: wire37/depth13/broad14/calibration22. Both final
  launcher read-only preflights PASS; no game launched by those checks.
- Final buffered fixture `20261022-035401-772393-return-fixture`: 592/600 fixed
  window; 593 total paired, 4 without ship, 4 warmup, 1 reset; 602 audit records,
  zero failed/dropped. Three owner:revision epochs 3:3,12:12,13:13 handled.
  Source1904 rows/952 pairs, anomaly counters zero, median lead ~3.3–3.6 ms.
  Saved scene age p50 16.965 ms/p95 17.459/max26.830. Exact scene/HUD marker
  frame200271, changed152698pixels, untouched border, state_errors0, disable/
  re-enable/resize/recreate safe, owned exits normal. No automatic recreation
  recovery claim. Vendor40 common-device-object warning persists historically.
- Final unbuffered fixture `20261022-035622-504453-return-fixture`:595/600,
  source1892 rows/946 pairs, anomaly counters0, median lead ~16.3ms, state0,
  safe resize/recreate/exit. DIFFERENT lead by design: not a controlled performance
  comparison and not proof buffered mode is faster or more reliable in SFC.
- First partial fixture034334-991280: valid exact scene/HUD pixels but supervisor
  file enumeration raced worker's atomic `.pending` rename. Fixed only missing
  file inventory race and added test; permission failures are NOT hidden.
  Intermediate034523-090839 passed; final safety version rerun above.
- Temporary compiler DWORD/type mismatch corrected before final build. A user
  game process temporarily locked launcher output; waited for normal exit,
  never killed it or restored its active proxies manually.

## Concurrent actual SFC observation — NOT buffered evidence

Sponsor independently ran `20261022-034936-435486-in-game` with old unbuffered
camera_return_alive settings. Normal exit, gate controlled unload, unchanged
clients and proxy restoration PASS; 5378 drawn,3 stale,0 retired,0 invalid.
Sponsor: “your updates worked nicely fyi, no delay with camera model reload!”
Record as useful persistent-path observation only, not causal evidence for the
new buffer or a universal seamless claim. No buffered SFC run yet.

## Bounds, cleanup and final state

One adjacent game frame plus50ms hard expiry. 33,177,600 additional GPU bytes;
conservative output resources116,121,600bytes below128MiB. Audit589,888bytes,
8192records. Existing90second/five-minute/log/scene limits retained; freeform
movement, final two LOW exit beeps. Original path progresses if late; no stale
picture hold. Unsupported dimensions/device recreation safely omit effect.

Four fixture generated-input/binary sets recoverably compressed with existing
`archive_fixture_binaries.ps1` using modern pwsh; ZIP contents/hash verified
before removing exact generated copies. Raw packets/logs/results retained.
Archives in `artifacts/remix-runtime/archives/`, same run names plus`-binaries.zip`:

-034334-991280:166F32680BAFAF7E5CC7F655E5126D053CC5CCECADCD700C01045140D021942B
  (partial explicitly not promoted).
-034523-090839:FAD2EC91FC8BF998981ABB6258582E1B3FBCC360C6EDD16E6698E55BCDE11ECD.
-035401-772393:234B3B4EE9D44C8E5E79E4EE43CDA5C406AB3810BC7D3C5FC8C6871AC2EF6C91.
-035622-504453:DB1101C91F3032F36E0BD41DEB47AFD0B1DC2E48C78932662BC30E5753EEFB03.

Each removed82,200,824 generated bytes recoverably; archives about6.87MB each.
Total artifacts12,478,504,110bytes at final inventory, below authorized20GB.
Original and copied `StarFleetOP.exe` both SHA256
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Copied proxy restored SHA256
`E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7`.
No active owned game/fixture/host/receiver processes; no mapping/session must
survive restart. New launch creates fresh IDs. Source/docs unstaged/uncommitted,
index empty, HEAD0fc1300, no push; ignored generated captures/binaries stay local.

Exact next action: sponsor runs the new buffered-scene launcher once, plays
normally with camera switches, exits normally at final request; then adjudicate
paired audit, responsiveness and continuity against the unbuffered evidence.
