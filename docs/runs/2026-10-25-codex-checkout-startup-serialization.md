# Run195 — repair checkout startup audit serialization

Sponsor's attempted checkout failed at
`artifacts/remix-runtime/runs/20261026-021701-097349-in-game` with
`Object of type WindowsPath is not JSON serializable`.
This is a launcher/audit-data defect, not a rendering result or user setup error.
The previous read-only preflight passed because it never serialized that returned
qualification. Run194's actual GPU evidence remains useful; its gameplay-ready
claim did not cover this failed startup boundary.

## Root cause and correction

`qualify_async_material.require_qualification()` verified the backend correctly,
then added its private backend dictionary, containing Path objects, to the returned
public qualification. `run_return_game.py` subsequently copied that entire result
into `manifest.json` as `full_support_qualification`. Its JSON serialization failed
after the observation-only host was ready but before the SFC launcher was invoked.
The separately serialized backend metadata had already worked, concealing the
second path through the full qualification object.

- `tools/remix_runtime/qualify_async_material.py`: return the existing serialized
  backend receipt in public qualification data. Verifier internals retain their
  Path objects; no global JSON fallback or silent stringification of unknown data.
- `tools/remix_runtime/run_return_game.py`: serialize the qualification during
  preflight, before proxy installation/host/game launch. Read-only startup checking
  now exercises the boundary that was previously skipped.
- `tests/test_async_material_checkout.py`: regression calls the actual qualifier
  with Path-bearing verifier inputs and serializes/round-trips the same full-support
  and backend metadata shape. It fails with the previous return value.

No engine hook, geometry, image/material/light/quality configuration, renderer
algorithm, synchronization policy or client artifact changed. The backend's string
paths remain valid explicit command arguments; selection is still per relay.

## Failed-run disposition and safety

The retained result records `target_pid=null`: SFC was not launched. Observation
host exited0, `broad_proxy_restored=true`, `original_critical_unchanged=true` and
`launcher_settings_unchanged=true`. Accepted/test client hashes are preserved in
that result. Missing tactical/persistent evidence is expected for pre-game failure;
do not classify it as a semantic or gameplay failure. No game was killed for this
repair. No owned game/renderer/fixture/guard process remained at final inventory.

## Validation and renewed qualifications

- **543 main Python tests PASS** in9.919s, including ten checkout tests and the new
  exact serialization regression.
- Actual current qualification plus the failed run's manifest fields serialize
  and round-trip successfully in
  `artifacts/candidate-hot-reload/run195-startup-metadata.json`. This is a local
  audit-data test; it does not install a proxy or launch a game.
- Matching pinned candidate host/header rebuilt through the established x64/WX
  build procedure. Normal host/runtime unchanged. Native-light worker qualification
  refreshed through its actual native tests, not edited source-lock stamps.
- Normal final-source GPU fixture
  `20261026-022038-032829-return-fixture` completed; normal qualifier's actual
  Test/Performance native identity checks and normal graphics gates passed.
- Candidate final-source initial
  `20261026-022127-888583-return-fixture`: four owner ACKs/three captured assets,
  all381 selected asset files exact,598/600 settled, two isolated full-interval
  post-start omissions; no long gap.
- Candidate final-source late asset
  `20261026-022221-868658-return-fixture`:381 files matched except capture frame ID,
 596/600 settled, two isolated post-start omissions. Both candidate fixtures have
  native HUD/scene exact, state errors0, resize/recreate, no invalid/rejected/partial
  assets, normal owned exits and drained workers.
- Both normal and checkout actual read-only gameplay commands PASS after renewed
  qualifications, now including serialization. Source/config/binary checks remain
  strict. No actual SFC test was launched by Codex.

The two old completed duplicate asset trees and two new candidate trees were
SHA-verified ZIP archived; raw logs/BMPs/capture packets and the newest normal
fixture remain. Receipts identify archive names (the helper retains its legacy
`run193-` prefix). Existing20GB cap, source/native output limits,90-second tactical
window and285-second workflow unchanged. Exact sizes/checks are in the
[versioned evidence](../reconnaissance/evidence/20261025-checkout-startup-serialization.json).

HEAD remains93e8dba; this correction and prior Run194 implementation remain
unstaged/uncommitted. HANDOFF/STATUS and checked Obsidian snapshot updated.
Startup-under-two-seconds remains open; this repairs the launcher, not performance.

**Exact next action:** retry the same opt-in gameplay command, then inspect actual
SFC rendering/appearance, camera continuity, cleanup and client hashes:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_multiship_session.ps1" -AsyncMaterialCheckout
```

Same expected textured camera-left copies, original ships retained, existing visual
settings and exit request. No magenta/on-off cycle or manual timestamps. Do not
interpret this corrected preflight as completed gameplay acceptance.
