# Run186 — renderer-thread asset servicing during output waits

## Result and scope

Implemented the Run185 next action. Ready assets can now be serviced between
bootstrap Presents and while waiting for real render queries, postprocess fences
and receiver acknowledgement, on the existing renderer thread. No game run was
needed. This removes a confirmed scheduling restriction; **it did not improve
first matching output delivery in the measured A/B**. The sub-two-second target
and non-disruptive late-material consumption remain OPEN.

Fuel Guard attached; available credits remain authorized. HEAD9ff2d3d, previous
dirty work preserved. Nothing staged, committed or pushed.

## Implementation and contract

- `tools/d3d9_proof/asset_service.h`: optional, thread-checked, non-reentrant
  callback into the existing `MultiSceneRuntime.assets()`. Existing asynchronous
  CPU preparation and one-admission-per-service-pass bounds remain. No extra
  graphics thread, draw callback or SFC hook is added.
- `d3d9_direct_host.cpp`: service at safe loop boundaries, after bootstrap
  Presents, and pending D3D9 query polls. Exactly two startup timing records:
  bootstrap and first actual cohort. Timings split draw/Present, copy submission,
  query readiness, postprocess and peer ACK. Service time is cumulative and must
  not be interpreted as one frame's cost.
- `worker_gpu_fence.h` and `output_producer.h`: optional service during pending
  waits, retaining actual completion events/queries, five-second GPU deadline,
  ten-second ACK deadline, output identity and surface ownership. Disabled mode
  retains previous waiting behavior. No timer is treated as GPU completion.
- `multi_scene_relay.py` and `live_owner_timing.py`: explicitly set
  `SFC_D3D9_ADMISSION_SERVICE=0` for normal policy,1 for the experimental relay.
  `progressive_scene_relay.py` opts in and reports actual native activation,
  publication retries and bounded output-stage timings.
- `run_return_fixture.py`: offline A/B selector
  `--asset-admission-service inherit|on|off`; explicit override requires
  `--parallel-assets`. Gameplay remains the existing explicit
  `-ExperimentalParallelAssets` option. The normal launcher is unchanged.
- Final review found the pre-existing `d3d9_replay.cpp::require` diagnostic count
  was non-atomic and shared by asynchronous asset preparation and the renderer.
  It is now thread-local; every validation decision still executes, but printed
  diagnostic totals describe the calling thread. No shared atomic increment or
  lock was added to the per-element parser. The measured A/B above precedes this
  independent correction; its source/binary pair was identical to itself.
- First enabled trial exposed Windows sharing contention when Remix read the
  material master during atomic replacement. Progressive publication now retries
  `PermissionError` on a later coordinator cycle, retaining current base/stage.
  No sleeps, deletion, asset regeneration or security changes. Persistent
  contention fails after5s; completed input reservations release only after
  successful publication. This is a harness correction, not proof of a runtime
  material-consumption fix.

Official contract: [Microsoft GetData](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3dquery9-getdata)
and [D3D9 queries](https://learn.microsoft.com/en-us/windows/win32/direct3d9/queries).
Pending S_FALSE and genuine ready S_OK remain distinct; D3DGETDATA_FLUSH and device
failure handling remain. Servicing assets is not a replacement for synchronization.

## Validation and measurements

Matched-source serial controls use the same pinned runtime, accepted settings,
three captured contents/four owners, source/binary locks and final asset files:

| Metric | Service OFF,211540-658236 | Service ON,211621-407455 |
| --- | ---: | ---: |
| First native asset admission, from first discovery | 3.874415s | 3.052775s |
| Third distinct asset admission | 5.280009s | 5.354936s |
| First matching returned frame | 5.3306225s | 5.6701498s |
| Bootstrap draw/Present total | 683.669ms | 3208.787ms |
| First cohort query wait | 1387.356ms | 10.424ms |
| Settled delivery window | 596/600 | 596/600 |
| All post-start omitted returned layers | 68 | 73 |
| Longest omission run | 67records/1.139s span | 72records/1.212s span |

These are one serial pair, not a statistically controlled benchmark or physical
display timestamps. First native admission improved; first matching output did
not. Work moved into bootstrap rather than disappearing. Copy submission was
microseconds, postprocess around1–2ms and first peer startup around185–199ms.
Long startup Present and GPU readiness are CONFIRMED measured intervals; their
internal texture/shader/material contributions remain UNASSIGNED. Do not claim
the whole interval is texture verification, shader compilation or GPU upload.
The bootstrap still uses the prior24-Present policy; that is our policy, not an
NVIDIA requirement. No new warm-up policy was introduced.

Both controls acknowledged4owners, rejected0assets, recorded no partial, exited
normally and passed exact native HUD/scene, resize/recreation and state checks.
Final scene/texture/material file hash sets are identical. Each retried one
material-master publication successfully. Enabled service actually ran during
bootstrap/query/post/peer/boundaries;46ms cumulative callback time over the full
run. Do not infer individual runtime function costs from this total.

Late-asset enabled fixture211727-354654: first initial matching frame3.343795s,
4owners/3contents/shared asset,0rejected/partial,595/600 settled window and normal
exit/state/resize/recreation. **220post-start omissions**, longest85records/1.492s
span. This preserves the known streaming limitation; a good settled window is
not a full-interval stability PASS. These are omitted returned layers, not
established SFC frame loss or freezes. No sponsor observation is invented.

Earlier210911OFF and211016ON retained as preliminary evidence; the latter failed
on material-master sharing. It is not used as an A/B timing result or renderer
semantic failure. Final controls above include the retry correction.

- New `tests/d3d9_asset_service_tests.cpp`: **23native checks PASS**, actual system
  D3D9Ex with the shared Renderer. Bound VB/IB/texture/FVF/offset/stride and prior
  pixels exact after admission, real query complete, wrong-thread call rejected,
  disabled/reentrant/throw cleanup paths checked. The rejected secondary thread
  makes no graphics calls.
- `build_direct64.ps1` runs this test plus existing loaded-light11, deferred,
  worker-poll and combined-post65 checks; x64 warning-as-error build PASS.
- `build_receiver.ps1` x86 build/regressions PASS: wire29/source18/output649 plus
  deferred checks. Shared fence default path qualified.
- **613Python tests PASS**:531main,36recon,13survey,6effects,5API,22early-model.
  Includes publication contention/retry and explicit activation/reporting checks.
  Initial restricted TEMP failure was environmental; rerun with existing writable
  project TEMP passed. No production permission or security setting changed.
- Initial normal-policy fixture211854-055409:592/600, normal owned exits, exact
  native HUD/scene, no state errors and resize/recreate. Normal multiship receipt
  renewed using `qualify_multiship.py`, not edited or bypassed. Experimental
  read-only gameplay preflight PASS; no SFC launched.

Final counter-corrected x64 build reran all native checks successfully. Enabled
closing fixture212507-564682:596/600,4ack/0rejected/partial, normal exits, exact
HUD/scene and resize/recreation. Final asset file hashes equal the matched pair.
First matching returned layer3.205461s, but third distinct native admission was
later5.297245s: **first matching output is not proof that all pending ships are
already displayed**. That run had108post-start omissions. One later resource
admission spent1483.098ms in the existing Renderer construction/upload block;
cumulative service time1.5068124s. This confirms a servicing callback can still
block inside native resource realization; it is not a guaranteed nonblocking
upload API. Exact Create/Lock/Update/runtime contributions need attribution.
Do not attribute this run's different startup time to the counter correction.

Final normal-policy fixture212600-861396:593/600, normal owned exits, exact native
HUD/scene, no state errors and resize/recreation. Normal qualification renewed
again from this final-source fixture; experimental read-only preflight PASS.

## Evidence, repository state and next action

Curated timings: `docs/reconnaissance/evidence/20261025-renderer-admission-service.json`.
Full analysis: `artifacts/initial-readiness/run186-admission-service.json`.
Raw result/audit/console/capture data remain under the named
`artifacts/remix-runtime/runs/20261025-...-return-fixture` folders. Duplicate
generated asset trees from the five experimental controls are recoverably archived
in `artifacts/remix-runtime/archives/run186-generated-assets.zip`; per-file hashes
and restoration paths are in `artifacts/initial-readiness/run186-generated-archive.json`.
Accepted222711golden inputs and final normal qualification fixture stay loose.
Existing20GB aggregate evidence policy retained; installed dependencies/test copies
are distinct from that existing ledger. Logs retain32MiB combined limit.

Additional changed files this run: `tests/test_parallel_assets.py`,
`tools/remix_runtime/check_parallel_assets.py`, this run record, curated evidence,
`docs/HANDOFF.md`, `docs/STATUS.md`, and `tools/d3d9_proof/README.md`.
Existing native semantic hooks/protocol/runtime/SDK/settings/client assets unchanged.
Generated archive:628,611,037B→39,104,992B,1792files, each SHA256 verified before
removing only the archived generated copies. Final aggregate evidence ledger
18,615,357,321B, below20,000,000,000B, including closing fixtures.
No active owned process/channel remains; all changes unstaged/uncommitted.

**Exact next action:** use the pinned runtime's documented profiling/source to
attribute the blocking bootstrap Present/query and Renderer resource-creation
work; preserve final material pixels and compare a supported consumption change
offline before another sponsor run. Do not promote servicing as a startup speedup,
remove synchronization, patch runtime internals, resume parked geometry API work,
or repeat gameplay just to verify this scheduling change.
