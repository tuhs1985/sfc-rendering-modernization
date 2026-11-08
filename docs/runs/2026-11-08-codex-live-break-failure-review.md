# Live BRK checkout — active preparation decoder mismatch

**Diagnosis refinement:** [second-run receiver review](2026-11-08-codex-break-receiver-fix.md)
establishes that the shared-memory receiver rejects debris before the worker is
polled. The worker defect reproduced below was real, but was not established
as the first live rejection. Retain this record as the original worker analysis.

Reviewed November 8, 2026 America/New_York. Sponsor reports the BRK test did
not work. Evidence: `artifacts/remix-runtime/runs/20261108-051449-466309-in-game`.
This is a read-only failure analysis plus documented copied-install recovery;
no production source/settings change, game launch or new capture.

## Finding

**Confirmed integration defect:** the active progressive/parallel asset worker
still calls the intact-only `live_scene.decode_mesh` in
`tools/remix_runtime/parallel_assets.py`, `Pipeline.decode`. The earlier debris
implementation updated `multi_scene_relay.Relay.identify_asset` to call
`break_scene.decode_runtime_mesh`, but the normal async-material checkout uses
`progressive_scene_relay.Relay`, which replaces that preparer with `Pipeline`.
Thus the active path never benefits from the updated admission function.

The source captured all four valid FCA debris pieces. The worker rejected their
indexed origin `0x0042EA92` as if it had to be the intact origin `0x0042E55D`,
raising `Unsupported semantic origin/math dispatch`. Captured math-dispatch
words are all zero; this result is not evidence of unsupported arithmetic.
The coordinator surfaced the preparation exception as a recovery-service error
and stopped enhanced rendering. No debris asset reached renderer admission.
This does not establish a Remix rejection or unsupported destruction geometry.

## Reproduction from the actual saved input

Called the existing `Pipeline.decode` directly with each saved packet and its
captured owner/model/source/revision. No mocks of the decoder or checksum.
Also decoded the same packet/reference pairs with the dedicated decoder and
`allow_break=True`.

| Saved asset revision | Source | Piece / triangles | Dedicated admission | Actual parallel-worker admission |
| --- | --- | --- | --- | --- |
| 1 | KFF intact | 452 triangles | PASS | PASS |
| 2 | FCA intact | intact | PASS | PASS |
| 3 | FCA intact | intact | PASS | PASS |
| 4 | FCA_BRK | 1 / 889 | PASS | origin error |
| 5 | FCA_BRK | 3 / 1,669 | PASS | origin error |
| 6 | FCA_BRK | 0 / 2,923 | PASS | origin error |
| 7 | FCA_BRK | 2 / 889 | PASS | origin error |

Debris partitions cover 6,370 triangles, matching the qualified FCA partition.
All four carry separate high-bit epochs, original source/resource associations
and parent epoch 2. The actual worker reproduction is decisive without another
discovery run. Initial analysis omitted the `tools/d3d9_proof` import directory
and produced a local `mesh_checksum` import error; corrected the review context
and reran against the real native checksum. That first local setup result is
not the gameplay failure or evidence of a packaged dependency defect.

## What worked before the stop

- Three intact instances were admitted (KFF and two FCA instances). Native
  receipts show 2,797 insertions/list suppressions, all for intact owners.
- Gate retained 1,245 frame records, with 1,208 insertion frames and 37 original
  frames. No recorded timeout misses, stale/invalid gate transactions or partial
  gate commits. Different frame/list/owner counters are not interchangeable.
- Median source-to-presentation callback age 15.502 ms; p95 native-frame elapsed
  16.895 ms. These describe intact operation before failure, not debris
  performance or scanout latency.
- Four fresh debris packets and references were saved. Renderer state reports
  only three ready assets; no debris insertion receipt is present.
- `submission_changed=9014` and a high-bit last owner are retained in native
  recovery counters. They do not establish a second root cause: the fragments
  were never prepared/admitted. Reassess indexed suppression only after the
  actual preparation path works.

## Cleanup

The original run result is PARTIAL. At finalization SFC was still running;
proxy rollback was correctly deferred and the controller was left to observe
game exit. The later controller log reports target exit before controlled
component removal. The renderer/receiver ended normally; receiver result 0.
The accepted installation and launcher settings remained unchanged.

At review no SFC, return host, D3D9 host, receiver or controller process remained.
Confirmed `windows_processes.game_running()` is false, then ran the existing
`recover_broad_session.py` for this exact run. Recovery verified the rollback
hashes and protected copied files, restored the proxy/configuration and saved
`recovery.json` with `proxy_restored=true`, `config_restored=true`, and
`game_absent_verified=true`. Historical failure evidence is unchanged.

## Smallest correction and missing test

Route `Pipeline.decode` through the same strict `decode_runtime_mesh` dispatch,
passing the relay's explicit break-mode flag. Keep intact admission unchanged,
require full debris metadata, and keep indexed admission closed when disabled.
Do not remove origin validation or reinterpret break input as an intact mesh.

Add a test that submits debris through the actual parallel worker decode and
its preparation/service boundary, alongside intact input, disabled mode and
malformed metadata. Earlier focused tests exercised the dedicated decoder and
`Pipeline._basic` with an already-decoded mesh, so they missed this active-path
gap. A baseline intact 600-frame replay cannot prove fresh debris preparation.

Then refresh relevant builds/qualification, check read-only preflight and run
the same BRK checkout. No new gameplay discovery, material tuning, renderer
upgrade or full trace is needed to diagnose this defect. Live debris remains
unaccepted and an alpha functional blocker until corrected and checked.
