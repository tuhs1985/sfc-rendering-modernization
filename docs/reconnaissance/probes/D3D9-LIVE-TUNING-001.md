# D3D9-LIVE-TUNING-001

Default-off live controls on the established ordinary-D3D9/Remix1.6.1 checkout.
See [Run204](../../runs/2026-10-26-codex-current-d3d9-live-tuning.md) for dependency
pins, files, baseline restoration, operating limits, tests and remaining claims.

Trigger: dedicated light-tuning launcher or the multi-ship launcher's `-Tuning`.
Inputs: fresh semantic assets/state, canonical rendering/lights TOMLs. Source
geometry hook stays disabled. Output: additive textured ships through the existing
pre-effects D3D11 compositor. Original ships/gameplay stay intact.

Offline qualification uses `run_return_fixture.py --multi-ship
--multi-ship-resources --prewarm --startup-profile --pipeline-mode performance
--async-material-checkout --live-tuning`, then `qualify_d3d9_tuning.py` against
revision3. The fixture changes its own profile, never the sponsor's settings.

Runtime: usual skirmish, tune and save controls, normal exit.1800second tactical
and1980second total bounds; minimal summaries, existing20GB overall/image/queue
bounds. No screenshot stream, manual timestamps, original suppression, Toolkit
startup or automatic factory reset. Actual extended gameplay remains pending.
