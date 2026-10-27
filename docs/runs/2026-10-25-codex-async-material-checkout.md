# Run194 — optional asynchronous-material gameplay checkout prepared

Local October25, UTC run names October26. Parent `93e8dba`. Sponsor authorized
implementation of the next bounded checkout after Run193. M1 performance work
continues; API remains parked. Fuel Guard attached. **READY FOR SPONSOR RUNTIME
TEST**, not SFC PASS, renderer replacement or sub-two-second startup completion.
No game launched, client configuration changed, source assets replaced, or work
staged/committed/pushed during this run.

## Completed implementation

- `tools/remix_runtime/async_material_checkout.py`: explicit separate relay using
  verified candidate1.6.1 runtime/host/header, existing parallel base-first
  preparation, four-group bounded enhancement IO and one complete enhanced stage
  per asset. Existing `material_library.flat` publishes definitions and rebases
  image paths; no new loader or SDK geometry calls. No all-ship barrier.
- `tools/remix_runtime/parallel_assets.py`: cancel queued per-owner alias consumers
  before shared dependencies can be released. Already-running tasks retain their
  submitted references; other owners retain shared dependency entries. This is now
  integrated, rather than Run193's probe-only correction.
- `tools/remix_runtime/multi_scene_relay.py` and `live_owner_timing.py`: select the
  backend per relay, never by mutating normal module-global runtime paths. The
  candidate child explicitly receives async loading True in config/environment,
  overriding an inherited False only for that child. Existing early-start renderer
  is mandatory; inputs recorded in `gpu/loading-inputs.json`.
- `tools/remix_runtime/qualify_async_material.py`: separate qualification receipt
  and gameplay preflight. Keeps normal qualification as a prerequisite, rejects
  monkeypatched Run193 probes and mixed rendering policies, binds exact
  source/binary/config/backend, and checks actual content/identity/output/cleanup.
  Full-interval delivery must have no gap over two records, separately from the
  existing settled600-frame check. This is a preparation floor, not a universal
  zero-flicker claim.
- `run_return_fixture.py`, `run_return_game.py` and
  `tools/d3d9_proof/start_d3d9_multiship_session.ps1`: default-off
  `--async-material-checkout` / `-AsyncMaterialCheckout`, mode selection and backend
  receipts. Excludes the older `-ExperimentalParallelAssets` and Test mode. Normal
  launcher keeps1.5.2 and has been independently requalified.
- `tests/test_async_material_checkout.py`: nine targeted regression cases cover
  queued/running/shared dependency lifetimes, independent completed-stage
  publication, child-only configuration, policy rejection, early delivery gaps,
  wrong launch modes, and content matching despite reordered worker completion.
- `tools/d3d9_proof/README.md`, this record, the
  [probe definition](../reconnaissance/probes/D3D9-ASYNC-MATERIAL-001.md),
  [evidence](../reconnaissance/evidence/20261025-async-material-checkout.json),
  HANDOFF/STATUS and checked Obsidian snapshot document operation and next action.

Same native semantic hooks, owner epochs, captured geometry, primary/enhanced
images, camera conversion, ordinary D3D9 submission and synchronized GPU return.
Diagnostic geometry hook remains disabled. Actual output completion, ownership,
ACK and stale-frame rules retained; no stale-pixel hold/prediction added. Existing
light/material/image/quality settings and camera-left offset unchanged. Original
ship drawing, UI and gameplay remain enabled. No Toolkit or imported model template.

The supported material route and packaged/source caveat are established in
[Run193](2026-10-25-codex-candidate-hot-reload-qualification.md) and
[NVIDIA's worker hot-reload implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/commit/25d18f6b692ca762d4236ffc6373f1bbd91e7a14).
No vendor internals patched, missing materials accepted, arbitrary initial-load
wait introduced, or appearance settings retuned. Packaged5a7eec84 versus public
release-linked0a6cd5b remains a source-parity caveat.

## Offline evidence and adjudication

Four actual standalone GPU runs, all completed native/fixture exits with exact
native HUD/scene checks, zero graphics-state errors and resize/recreation coverage.
No actual SFC gameplay during these tests.

| UTC run prefix, suffix `-return-fixture` | Scope | First matched output | Final initial distinct admission | Full post-start omissions / longest | Settled window |
|---|---|---:|---:|---:|---:|
| 20261026-015529-935115 | First integration, before checker correction | 3.115s | 3.853s | 9 / 1 | Passed fixture |
| 20261026-015852-091719 | Final-source normal1.5.2 control | 9.455s | 9.403s | Recorded in evidence | Passed normal gate |
| 20261026-020046-223248 | Final-source candidate initial/shared assets | 3.206s | 3.956s | 0 / 0 | 600/600 |
| 20261026-020227-512666 | Final-source candidate with late distinct asset | 3.556s | Late admission7.207s | 1 / 1 | 596/600 |

Times start at first asset discovery. The normal control's slow first output is
preserved; this is not a statistical benchmark or proof of a threefold speedup.
First output does not establish all ships displayed. **Under-two-second loading
remains OPEN**, independently of the material-update continuity improvement.

Initial first checker rejected `assets/2/scene.bin`, but the renderer itself had
completed normally. Diagnosis found RCA and FDD preparation finished in reversed
order. All381 selected files matched after associating captured model/geometry
content instead of worker folder order. That harness defect does not invalidate
the rendering/content evidence; its old source locks do not qualify the final
checkout. Final-source controls were repeated after fixing/testing the checker.

Final initial/late controls each acknowledged four owners sharing three distinct
assets, with independent draw counters, zero invalid/rejected/partial assets and
clean drained workers. Initial381 geometry/image/material files exact against the
accepted archived reference. Late control differs only in captured frame ID of one
scene packet; other geometry/UV/transform/image/material bytes exact. Runtime logs
confirm async True, initial-pixel uploads, renderer-thread admission and ordinary
D3D9 rather than SDK mesh submission. Completed material publications: three each.
The original rendering and GPU output synchronization were not bypassed to improve
the measurements.

### Validation actually performed

- **542 main Python tests PASS** in9.410s, including nine new checkout regressions.
- Isolated matching candidate host x64 `/O2 /fp:precise /W4 /WX` rebuild PASS;
  normal native host/runtime unchanged. Build/source/header receipt refreshed.
- Native light discovery queue/decoder and actual native worker/shared publication
  qualification refreshed normally. No source-lock stamps manually edited.
- Normal multiship qualifier reran its actual Test/Performance native identity
  fixtures, wire/native pixel/state tests, and current light gate. Its initial
  attempt correctly rejected stale light qualification after the launcher edit;
  the existing worker tests were run before retrying. Normal gate now PASS.
- Separate integrated checkout initial/late qualification PASS. Its receipt is
  `artifacts/d3d9-proof/async-material/qualification.json`; normal receipt is not
  replaced by a candidate proof.
- Both normal and checkout read-only game preflights PASS; launcher PowerShell
  parser PASS; final AST/JSON/reference/diff checks. No full615-test rerun or new
  gameplay/client-hash runtime result claimed. Existing client preflight checks
  still pass, no client artifacts touched.

Useful evidence is in each named run, `artifacts/candidate-hot-reload/run194-*`
logs and the versioned evidence summary. Six generated duplicate asset trees
(three historical, preliminary integration and both final candidate controls)
were ZIP archived only after per-file SHA verification. Raw packets/logs/BMPs,
current normal qualification fixture015852, old accepted normal221209 and golden
fixtures retained. Archive filenames retain the helper's legacy `run193-` prefix;
the explicit Run194 evidence receipts identify their actual scope. Restore archived
asset members with hash verification only if re-running content inspection; normal
checkout preflight verifies retained result hashes/qualification and does not need
these disposable generated trees.

Existing20GB ledger cap and1GiB standalone reservation retained. Existing scene,
image, worker memory, logging,90-second tactical and285-second workflow bounds
unchanged. No owned game, renderer, fixture or bounded-job process remains.
Changes are unstaged and uncommitted on parent93e8dba.

## Prepared sponsor procedure

Use the established elevated PowerShell parent:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_multiship_session.ps1" -AsyncMaterialCheckout
```

Enter the usual skirmish. Expect textured camera-left copies alongside the original
ships with the existing visual settings; no magenta or timed on/off cycle. Briefly
keep both visible, switch cameras, move and turn normally. A fighter/shuttle launch
is useful if convenient. Follow the existing exit request. Confirm appearance,
continuity and unchanged HUD/targeting/controls. The runner performs normal
restoration/proxy/client-hash checks after exit. Omit the flag to use the independently
qualified normal runtime again.

**Exact next action:** sponsor runs this opt-in checkout, then review actual SFC
appearance, complete-interval returned delivery, startup/late-asset timings,
cleanup and unchanged client hashes before any normal-runtime promotion.
