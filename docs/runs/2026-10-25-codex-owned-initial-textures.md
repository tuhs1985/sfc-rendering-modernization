# Run188 — owned initial-pixel staging integrated and qualified for experimental checkout

## Result

Implemented Run187's documented staging alternative in the actual shared Renderer,
not another diagnostic host. Native D3D9Ex and Remix use initial pixels directly;
classic native D3D9 rejects that optional creation contract and uses the existing
staged upload. Geometry, images, materials, rendering/output synchronization and
original SFC drawing remain unchanged.

**READY for the existing explicit experimental gameplay checkout**, not a default
promotion or full startup/streaming PASS. Final-source standalone tests retain
known returned-layer gaps. No actual SFC game was launched in this work.

## Ownership, compatibility and activation

- `d3d9_replay.cpp`: `TextureUpload::StagedLock` remains the constructor default;
  `InitialData` creates one-mip, tightly packed BGRA SYSTEMMEM textures from the
  existing pixel payload, then uses the unchanged UpdateTexture call.
  [Microsoft creation contract](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-createtexture#remarks),
  [UpdateTexture contract](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-updatetexture).
- Renderer owns the source vectors. Prepared vectors move into `uploadBacking`,
  without another image copy; disk-loaded inputs move in the same way. Backing is
  declared before all COM members, so it is destroyed after them. Caller containers
  may be destroyed before drawing. No borrowed worker-local pixel pointer or
  changed file data. Existing two-copy resident accounting/256MiB limit remains;
  the owned CPU data occupies its CPU-source share alongside the GPU copy. Existing
  per-asset decoded-image bounds and bounded temporary staging remain.
- Only D3DERR_INVALIDCALL from the optional initial-data creation triggers the
  old staging mechanism. One rejection disables further attempts for that Renderer;
  allocation/device failures remain errors. No unsafe per-device pointer cache.
  Counters distinguish accepted initial uploads, staged uploads and rejection.
  This is an upload-method fallback, not replacement with an original/wrong ship.
- `d3d9_direct_host.cpp` parses `SFC_D3D9_INITIAL_TEXTURE_DATA`, reports actual policy,
  and passes it to bootstrap/cohort construction. `multi_scene_runtime.h` applies
  the same policy to later fresh content and logs per-asset upload counts.
- Both worker launch paths explicitly set the variable: normal relay0;
  experimental progressive relay1. `progressive_scene_relay.py` reports actual
  native activation and upload counters. No switch leaves normal gameplay policy
  unchanged. Existing `-ExperimentalParallelAssets` selects the new path as well
  as the already-authorized parallel/progressive work.
- `run_return_fixture.py --texture-upload inherit|staged-lock|initial-data` supports
  serial offline comparison. Explicit overrides require performance multi-ship.
  No new gameplay switch, native hook, wire format, graphics thread, vendor patch,
  SDK/runtime upgrade, material configuration or image conversion was introduced.

## Native and offline validation

- `build_resource_policy.ps1` builds/tests actual system D3D9/Ex in **x86 and x64**.
  Each reports301193checks, exact old/new pixels, exact classic/Ex output,
  reset/recreation parity, moved source ownership,3fast Ex constructions and
  1classic fallback. Caller vectors are cleared before drawing. These are actual
  GPU/device tests, with Remix/ReShade/DXVK absent.
- Initial classic-device test correctly failed D3DERR_INVALIDCALL before the
  compatibility path was added. The finished tests demonstrate the response;
  no test expectation was relaxed to ignore a failed upload.
- Asset-service native test uses InitialData during a pending output query,
  including a three-pixel-wide image: bound resources and pixels stay exact,
  source buffers move into ownership, wrong-thread/reentry guards remain.
  Final warning-as-error x64 build passes this23check test plus loaded-light11,
  deferred diagnostics, worker-poll and combined-post65checks.
- **615Python tests PASS**:533main+36recon+13survey+6effects+5API+22early-model.
  New checks cover explicit mode/report wiring and invalid offline override rejection.
  An intermediate run read old native receipts before the expanded proof existed;
  rerunning after native completion passed all suites. No gate was bypassed.
- Normal native-light qualification remains current. New normal multiship
  qualification requires initial-data pixel/ownership evidence from both native
  architectures before accepting the updated consumer source.

## Integrated Remix controls — same final source/settings/runtime

| Fixture | Upload path | GPU admission for larger two contents | First matching output | Settled window | All post-start omitted layers |
| --- | --- | --- | ---: | ---: | ---: |
| 220718-726135 | staged control | 13.776/5.992ms | 6.267430s | 594/600 | 80 |
| 220919-119346 | initial data | 8.202/3.682ms | 6.107465s | 594/600 | 79 |
| 221059-269516 | initial data,late asset | 6.281/6.006ms | 3.815770s initial scene | 594/600 | 167 |

Full names: `artifacts/remix-runtime/runs/20261025-...-return-fixture`.
Four owners/three distinct contents, no invalid/rejected/partial assets, normal
owned exits and native HUD/scene/resize/recreation checks pass in all3controls.
Each initial-data run reports **107initial uploads,0staged,0unsupported** across
the three content assets. Thus Remix really used the integrated fast mechanism;
it did not silently fall back or just print an enabled option.

Initial pair's381scene/texture/DDS/material file hashes match exactly. Final image
comparison in the same ship region has mean absolute RGB error~0.16/255,
239pixels>10out of273600; not bit-exact Remix pixels or proof of early material
readiness. All existing light/material/image/quality settings preserved.

The1.48s stall did not recur in this staged control either. Therefore this pair
does **not** establish a1.48s whole-pipeline speedup; Run187 supplies the reproduced
call attribution/control. Here the known lock is absent from the107fast uploads,
but output latency is still high. First matching output is not every pending ship.
Native CPU preparation for larger contents remains~0.8–0.9s; its contributors
were not investigated in this bounded upload increment.

Full audit still matters: initial pair longest omission79/78records (1.334/1.309s
QPC span). Late run longest94records/1.602s, despite good settled output. These are
missing returned layers, not measured SFC freezes. No seamless streaming, sub2s,
universal asset coverage or milestone-completion claim.

Final **normal-policy** fixture221209-968233:594/600, real normal exit, exact
native HUD/scene, no state errors, resize/recreation. Qualification renewed through
the existing adjudicator with final source/binary locks; experimental read-only
gameplay preflight PASS. No direct receipt editing or experimental default promotion.

## Evidence, cleanup and repository discipline

- Curated: `docs/reconnaissance/evidence/20261025-owned-initial-textures.json`.
  Raw results/console/audits/BMPs remain in the named run folders; analysis/hash
  comparison at `artifacts/staging-integration/analysis.json`.
- Generated asset duplicates archived only after SHA256 verification, including
  three experimental controls and five superseded reference/control trees.
  Receipts/restoration paths: `artifacts/staging-integration/*-archive.json`;
  ZIPs: `artifacts/remix-runtime/archives/run188-*-assets.zip`.
  Total1149160434B→71259444B. Raw evidence, accepted222711golden inputs and final
  current221209qualification fixture stay loose. No game/client file deleted.
- Existing ledger18,536,125,529B plus isolated analysis/probe trees6,783,042B:
  combined18,542,908,571B<20GB, leaving headroom for checkout. One comparison
  preflight deferred until completed duplicates were archived; no cap increase.
- Historical Run187 generator targets pre-integration Renderer source and has
  frozen executed derivatives. Do not regenerate it blindly against this new
  constructor; use this integrated fixture's explicit upload-policy control.
- No active game/owned renderer/channel remains. Fuel Guard attached, credits
  still authorized. HEAD9ff2d3d; all prior/current changes unstaged/uncommitted;
  no commit/push.

Changed implementation/test files this run: `tools/d3d9_proof/d3d9_replay.cpp`,
`d3d9_direct_host.cpp`, `multi_scene_runtime.h`; `tools/remix_runtime/`
`live_owner_timing.py`, `multi_scene_relay.py`, `progressive_scene_relay.py`,
`run_return_fixture.py`, `qualify_multiship.py`; `tests/d3d9_asset_service_tests.cpp`,
`d3d9_resource_policy_tests.cpp`, `test_parallel_assets.py`. Documentation: this
record, curated evidence, HANDOFF/STATUS, D3D9 README and Obsidian tracker.

## Prepared checkout and exact next action

Use the established elevated parent:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_multiship_session.ps1" -ExperimentalParallelAssets
```

Enter the usual skirmish. Same textured ships, offset and accepted appearance;
normal camera/movement is sufficient. Exit normally at the runner's request.
No manual timestamps, shader settings or deliberate on/off cycle requested.
The test checks compatibility of the integrated upload path; arrival below2s or
elimination of material/camera flicker is not promised.

**Exact next action:** review that experimental gameplay evidence for actual fast
uploads, source/owner identity, visible behavior, normal cleanup and bounds before
any normal-policy promotion; then isolate remaining CPU preparation/output waits
as a separate bounded increment.
